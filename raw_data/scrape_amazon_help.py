"""
Amazon Help Page Scraper
========================
Uses Playwright to visit Amazon help pages, extract article content,
and save each as a markdown file in raw_data/<category>/.

Usage:
    1. Add your URLs to urls_to_scrape.txt (one per line)
       Format: category | page_name | url
       Example: Shipping and Delivery | About Two-Day Shipping | https://www.amazon.com/gp/help/customer/display.html?nodeId=468520

    2. Run: python scrape_amazon_help.py
"""

import os
import re
import time
import json
from playwright.sync_api import sync_playwright
from markdownify import markdownify as md

# ===========================
# CONFIGURATION
# ===========================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "raw_data")
URLS_FILE = os.path.join(SCRIPT_DIR, "urls_to_scrape.txt")


def load_urls_from_file(filepath):
    """
    Read URLs from a text file.
    Format per line:  category | page_name | url
    Lines starting with # are comments, blank lines are skipped.
    """
    pages = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            parts = [p.strip() for p in line.split("|")]
            
            if len(parts) < 3:
                print(f"WARNING (line {line_num}): Expected 3 fields (category | page_name | url), got {len(parts)}. Skipping: {line}")
                continue
            
            category = parts[0]
            page_name = parts[1]
            url = parts[2]
            
            if not url.startswith("http"):
                print(f"WARNING (line {line_num}): Invalid URL, skipping: {url}")
                continue
            
            pages.append((category, page_name, url))
    
    return pages


def sanitize_filename(name, max_len=80):
    """Create a safe filename from a page title."""
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    if len(name) > max_len:
        name = name[:max_len].strip()
    return name


def extract_article_content(page):
    """Extract the main help article content from an Amazon help page.
    Returns proper markdown with headers, lists, bold text, tables, etc."""
    
    # Wait for the page to fully load
    page.wait_for_load_state("domcontentloaded")
    time.sleep(2.5)
    
    # Try to get the page title from the heading
    title = None
    title_selectors = ["h1", ".help-title", "#title", "[data-csa-c-content-id] h1"]
    for sel in title_selectors:
        try:
            el = page.query_selector(sel)
            if el:
                t = el.inner_text().strip()
                if t and len(t) > 2:
                    title = t
                    break
        except Exception:
            continue
    
    # Remove unwanted page elements before extracting content
    page.evaluate("""
        document.querySelectorAll(
            'header, nav, footer, #navbar, #nav-main, #navFooter, #rhf, '
            + 'script, style, noscript, iframe, .nav-sprite, #nav-belt, '
            + '#nav-main, #navFooter, .a-popover, #rhf-container'
        ).forEach(el => el.remove());
    """)
    
    # Try multiple selectors for Amazon's help page content (get HTML, not text)
    selectors = [
        "#help-content",
        ".help-content",
        '[data-csa-c-content-id="help-content"]',
        ".cs-help-content",
        ".cs-help-landing",
        "#a-page .a-section",
        ".a-box-inner",
        "main",
        "#main-content",
    ]
    
    html_content = None
    for selector in selectors:
        try:
            el = page.query_selector(selector)
            if el:
                html = el.inner_html()
                # Check that it has meaningful text content
                text_check = el.inner_text().strip()
                if len(text_check) > 50:
                    html_content = html
                    break
        except Exception:
            continue
    
    if not html_content:
        # Fallback: get body HTML
        try:
            el = page.query_selector("body")
            if el:
                html_content = el.inner_html()
        except Exception:
            return None, title
    
    if not html_content:
        return None, title
    
    # Convert HTML to proper markdown (preserves headers, lists, bold, tables, etc.)
    content = md(
        html_content,
        heading_style="ATX",
        bullets="-",
        strip=["img", "a"],  # Remove images and links but keep their text
    )
    
    # Clean up the markdown
    lines = content.split('\n')
    cleaned_lines = []
    skip_patterns = [
        "Skip to main content",
        "Hello, sign in",
        "Returns & Orders",
        "Deliver to",
        "Back to top",
        "Get to Know Us",
        "Make Money with Us",
        "Amazon Payment Products",
        "Let Us Help You",
        "© 1996-",
        "Conditions of Use",
        "Privacy Notice",
        "Your Ads Privacy Choices",
        "Was this information helpful?",
        "Thank you for your feedback",
        "Do you need more help?",
        "Search the help library",
        "Need more help?",
    ]
    
    for line in lines:
        stripped = line.strip()
        if any(pattern in stripped for pattern in skip_patterns):
            continue
        cleaned_lines.append(line)  # Keep original indentation
    
    # Remove excessive blank lines (3+ in a row → 2)
    content = '\n'.join(cleaned_lines)
    content = re.sub(r'\n{3,}', '\n\n', content).strip()
    
    return content, title


def scrape_help_pages():
    """Main scraping function."""
    
    # Load URLs
    if not os.path.exists(URLS_FILE):
        print(f"ERROR: URL file not found: {URLS_FILE}")
        print(f"Please create it with the format:")
        print(f"  category | page_name | url")
        return
    
    pages = load_urls_from_file(URLS_FILE)
    
    if not pages:
        print("No URLs found in the file. Nothing to scrape.")
        return
    
    print(f"Found {len(pages)} URLs to scrape.\n")
    
    # Track results
    results = {"success": [], "failed": [], "skipped": []}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 720},
        )
        
        page = context.new_page()
        
        for i, (category, page_name, url) in enumerate(pages):
            # Create category directory
            category_dir = os.path.join(OUTPUT_DIR, category)
            os.makedirs(category_dir, exist_ok=True)
            
            # Use the user-provided page_name as the filename
            filename = sanitize_filename(page_name) + ".md"
            
            print(f"[{i+1}/{len(pages)}] Scraping: {page_name}")
            
            try:
                page.goto(url, timeout=30000)
                content, title = extract_article_content(page)
                
                # Use page_name as the heading if no H1 found
                if not title:
                    title = page_name
                filepath = os.path.join(category_dir, filename)
                
                # Avoid overwriting
                if os.path.exists(filepath):
                    print(f"  -> SKIP (file already exists): {filename}")
                    results["skipped"].append(title)
                    continue
                
                if content and len(content.strip()) > 100:
                    md_content = f"# {title}\n\n{content}"
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(md_content)
                    
                    print(f"  -> Saved: {filename} ({len(content)} chars)")
                    results["success"].append(title)
                else:
                    print(f"  -> FAILED (no content or too short)")
                    results["failed"].append({"title": title, "url": url})
                
                # Polite delay
                time.sleep(1.5)
                
            except Exception as e:
                print(f"  -> ERROR: {str(e)[:120]}")
                results["failed"].append({"title": str(url), "url": url})
                time.sleep(2)
        
        browser.close()
    
    # Summary
    print("\n" + "=" * 50)
    print("SCRAPING COMPLETE")
    print("=" * 50)
    print(f"Success:  {len(results['success'])}")
    print(f"Skipped:  {len(results['skipped'])}")
    print(f"Failed:   {len(results['failed'])}")
    
    if results["failed"]:
        print("\nFailed pages:")
        for item in results["failed"]:
            print(f"  - {item['url']}")
    
    # Save log
    log_path = os.path.join(OUTPUT_DIR, "scrape_log.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nLog saved to: {log_path}")


if __name__ == "__main__":
    scrape_help_pages()
