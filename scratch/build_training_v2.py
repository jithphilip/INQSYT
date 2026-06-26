"""
V2 - Efficient pipeline to build classifier_training_dataset_v2.csv
Uses streaming mode for UCSD dataset and processes in batches.
"""

import os
import sys
import json
import re
import csv
import random
import pandas as pd
import numpy as np
from collections import Counter, defaultdict

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
WS = r"c:\Users\Anupam Dasgupta\Desktop\INQSYT"
RAW_DIR = os.path.join(WS, "raw_data")
MAIN_DATA = os.path.join(WS, "Main_Data")
INTENTS_FILE = os.path.join(MAIN_DATA, "intents_schema.json")
V1_FILE = os.path.join(MAIN_DATA, "classifier_training_dataset.csv")
EVAL_FILE = os.path.join(MAIN_DATA, "eval_dataset.csv")
OUTPUT_FILE = os.path.join(MAIN_DATA, "classifier_training_dataset_v2.csv")

TARGET_TOTAL = 10000

os.makedirs(RAW_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# STEP 1: Load intent taxonomy
# ---------------------------------------------------------------------------
print("=" * 60)
print("STEP 1: Loading intent taxonomy")
print("=" * 60)
with open(INTENTS_FILE, "r", encoding="utf-8") as f:
    intents_schema = json.load(f)

intent_names = [it["intent"] for it in intents_schema]
intent_descriptions = {it["intent"]: it["description"] for it in intents_schema}
print(f"Loaded {len(intent_names)} intents")

# ---------------------------------------------------------------------------
# STEP 2: Load existing datasets for dedup
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("STEP 2: Loading existing datasets for deduplication")
print("=" * 60)
v1_df = pd.read_csv(V1_FILE)
eval_df = pd.read_csv(EVAL_FILE)

existing_questions = set()
for q in v1_df["question"].tolist():
    existing_questions.add(str(q).strip().lower())
for q in eval_df["question"].tolist():
    existing_questions.add(str(q).strip().lower())

v1_intent_counts = Counter(v1_df["intent label"].tolist())
new_queries_needed = TARGET_TOTAL - len(v1_df)
print(f"V1: {len(v1_df)} queries | Eval: {len(eval_df)} | Need: {new_queries_needed} new")

# ---------------------------------------------------------------------------
# KEYWORD CLASSIFIER
# ---------------------------------------------------------------------------
INTENT_KEYWORDS = {
    "modify_order": [
        r"\b(cancel|cancell?ation|modify|change|edit|alter|update)\b.*\b(order|purchase|item|cart|shipment)\b",
        r"\b(order|purchase|item)\b.*\b(cancel|change|modify|edit|update)\b",
        r"\bstop.*(ship|deliver|order)\b",
        r"\b(don'?t|do not)\s+(want|need)\b.*\b(order|item)\b",
    ],
    "modify_address": [
        r"\b(change|update|edit|fix|correct|modify)\b.*\b(address|destination|shipping.?address|delivery.?address)\b",
        r"\b(address)\b.*\b(change|update|wrong|incorrect|typo|mistake)\b",
        r"\b(ship|deliver).*\b(wrong|different|new)\s*(address|location|place)\b",
    ],
    "view_invoice": [
        r"\b(invoice|receipt|billing\s*statement|tax\s*receipt|vat\s*invoice)\b",
        r"\b(print|download|view|get|need)\b.*\b(invoice|receipt)\b",
    ],
    "submit_feedback": [
        r"\b(feedback|survey|satisfaction|rate\s+your)\b",
        r"\b(machine\s*translation|chat\s*language)\b",
    ],
    "reset_password": [
        r"\b(password)\b.*\b(reset|forgot|change|recover|can'?t|unable|trouble|problem)\b",
        r"\b(can'?t|cannot|unable)\b.*\b(sign|log)\s*(in|into)\b",
        r"\b(two.?step|2.?step|mfa|2fa|verification\s*code|security\s*code)\b",
        r"\b(locked\s*out|account\s*locked)\b",
    ],
    "manage_teen_account": [
        r"\b(teen|teenager|child|kid|minor)\b.*\b(account|login|order|approval|household)\b",
    ],
    "manage_profile_settings": [
        r"\b(profile|shopping\s*profile|switch\s*account|sign\s*out|log\s*out)\b",
    ],
    "manage_account_settings": [
        r"\b(language\s*preference|unsubscribe|marketing\s*email|third.?party\s*app|account\s*settings)\b",
    ],
    "close_account": [
        r"\b(close|delete|deactivate|remove|shut\s*down)\b.*\b(account|my\s*account|amazon\s*account)\b",
        r"\b(account)\b.*\b(close|delete|deactivate|closure)\b",
    ],
    "manage_wallet_cards": [
        r"\b(credit\s*card|debit\s*card|payment\s*method|wallet|bank\s*card)\b.*\b(add|remove|update|change|manage|delete|edit)\b",
        r"\b(add|remove|update|change)\b.*\b(credit\s*card|debit\s*card|payment\s*method|card)\b",
        r"\bgift\s*card\s*balance\b",
        r"\bdefault\s*payment\b",
    ],
    "convert_currency": [
        r"\b(currency|exchange\s*rate|convert|conversion)\b.*\b(dollar|euro|pound|yen|rate|payment)\b",
        r"\b(foreign|international)\b.*\b(currency|payment)\b",
    ],
    "resolve_declined_payment": [
        r"\b(declined|rejected|failed|refused)\b.*\b(payment|transaction|card|charge)\b",
        r"\b(payment|card|transaction)\b.*\b(declined|rejected|failed|refused)\b",
    ],
    "investigate_unknown_charge": [
        r"\b(unknown|unrecognized|unauthorized|suspicious|mystery|unexpected)\b.*\b(charge|payment|transaction|debit)\b",
        r"\bcharged\b.*\b(twice|double|extra)\b",
    ],
    "report_payment_scam": [
        r"\b(scam|fraud)\b.*\b(payment|money|gift\s*card|wire|transfer)\b",
        r"\breport\b.*\b(scam|fraud)\b",
    ],
    "check_return_eligibility": [
        r"\b(return|send\s*back|exchange)\b.*\b(item|product|order|purchase|eligible|policy|window)\b",
        r"\b(can\s*i|how\s*(do\s*i|to))\b.*\breturn\b",
        r"\breturn\s*(policy|window|period|eligib|request)\b",
    ],
    "check_restocking_fees": [
        r"\b(restocking|restock)\b.*\b(fee|charge)\b",
        r"\breturn\b.*\b(fee|charge|deduction|penalty)\b",
    ],
    "check_international_returns": [
        r"\b(international|overseas|cross.?border|foreign)\b.*\b(return|ship\s*back)\b",
        r"\breturn\b.*\b(international|overseas|another\s*country)\b",
    ],
    "track_refund": [
        r"\b(refund|money\s*back|reimburse|credit\s*back)\b",
        r"\b(where|when|how\s*long|status|track)\b.*\brefund\b",
    ],
    "check_promotional_balance": [
        r"\b(promotional|promo)\b.*\b(balance|credit|benefit)\b",
    ],
    "track_package": [
        r"\b(track|tracking|where\s*is|locate)\b.*\b(package|parcel|shipment|order|delivery)\b",
        r"\bdelivery\s*(status|update|confirmation|photo)\b",
        r"\bmap\s*tracking\b",
    ],
    "manage_delivery_alerts": [
        r"\b(notification|alert|text\s*update|sms|push)\b.*\b(delivery|shipping|tracking)\b",
        r"\b(turn\s*off|disable|stop)\b.*\b(text|sms|notification|alert)\b",
    ],
    "check_delivery_delay": [
        r"\b(late|delayed|slow|overdue|stuck)\b.*\b(delivery|package|shipment|order)\b",
        r"\b(package|delivery|shipment|order)\b.*\b(late|delayed|hasn'?t\s*arrived|not\s*arrived|still\s*waiting)\b",
        r"\bmissing\s*tracking\b",
    ],
    "resolve_undeliverable_package": [
        r"\b(undeliverable|returned\s*to\s*sender|couldn'?t\s*deliver|failed\s*delivery)\b",
    ],
    "check_delivery_rules": [
        r"\b(delivery\s*window|otp\s*delivery|secure\s*delivery)\b",
        r"\b(prison|correctional)\b.*\b(delivery|ship)\b",
    ],
    "contact_support": [
        r"\b(contact|call|reach|speak|talk\s*to)\b.*\b(support|customer\s*service|help|representative|agent)\b",
        r"\b(phone\s*number|help\s*line|hotline|chat\s*support|live\s*chat)\b",
    ],
    "request_bereavement_support": [
        r"\b(deceased|death|died|passed\s*away|bereavement)\b.*\b(account|amazon)\b",
    ],
    "submit_legal_poa": [
        r"\b(power\s*of\s*attorney|poa|legal\s*document|legal\s*authorization)\b",
    ],
    "report_missing_package": [
        r"\b(missing|lost|stolen|not\s*received|never\s*arrived)\b.*\b(package|parcel|delivery|order)\b",
        r"\b(delivered|says\s*delivered)\b.*\b(not|never|didn'?t)\b.*\b(receive|get|find)\b",
    ],
    "report_missing_item": [
        r"\b(missing|absent|not\s*included)\b.*\b(item|part|piece|component|accessory)\b",
        r"\bempty\s*(box|package)\b",
    ],
    "check_customs_regulations": [
        r"\b(customs?|import\s*duty|import\s*tax|clearance|pccc|cuil)\b",
    ],
    "check_shipping_policies": [
        r"\b(shipping\s*policy|shipping\s*to)\b.*\b(hotel|forwarder|freight|po\s*box)\b",
        r"\bsignature\s*(required|on\s*delivery)\b",
        r"\bfulfilled\s*by\s*amazon\b|\bfba\b",
    ],
    "identify_phishing_scams": [
        r"\b(phishing|fake|spoof|suspicious)\b.*\b(email|message|text|sms|call|website|link)\b",
        r"\b(email|text|message|call)\b.*\b(fake|phishing|scam|suspicious|legit)\b",
    ],
    "check_tax_rates": [
        r"\b(sales\s*tax|vat|use\s*tax|tax\s*rate|tax\s*exempt)\b",
        r"\b(how\s*much)\b.*\btax\b",
    ],
    "manage_notifications": [
        r"\b(email\s*preference|newsletter|notification\s*setting|restock\s*alert)\b",
        r"\b(unsubscribe|opt.?out)\b.*\b(email|newsletter)\b",
        r"\b(out\s*of\s*stock|back\s*in\s*stock|availability)\b.*\b(alert|notification|notify)\b",
    ],
}

# Pre-compile all patterns for speed
COMPILED_PATTERNS = {}
for intent, patterns in INTENT_KEYWORDS.items():
    COMPILED_PATTERNS[intent] = [re.compile(p, re.IGNORECASE) for p in patterns]

def classify_by_keywords(text):
    """Fast keyword classification."""
    matches = []
    for intent, patterns in COMPILED_PATTERNS.items():
        for p in patterns:
            if p.search(text):
                matches.append(intent)
                break
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        return matches[0]  # first match wins
    return None

# ---------------------------------------------------------------------------
# STEP 3: Stream UCSD Amazon Q&A dataset
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("STEP 3: Streaming UCSD Amazon Q&A dataset")
print("=" * 60)

from datasets import load_dataset

labeled_queries = []
processed = 0
matched = 0

print("Streaming embedding-data/Amazon-QA ...")
try:
    ds = load_dataset("embedding-data/Amazon-QA", split="train", streaming=True)
    
    for example in ds:
        processed += 1
        if processed % 100000 == 0:
            print(f"  Processed {processed:,} rows, matched {matched} so far...")
        
        # Extract question text
        # This dataset has 'query' column with list of strings
        query_val = example.get("query", None)
        if query_val is None:
            # Try other column names
            for key in example.keys():
                if "query" in key.lower() or "question" in key.lower():
                    query_val = example[key]
                    break
        
        if query_val is None:
            if processed == 1:
                print(f"  Columns: {list(example.keys())}")
                print(f"  Sample: {example}")
            continue
        
        # Handle list vs string
        if isinstance(query_val, list):
            texts = [str(t).strip() for t in query_val if isinstance(t, str)]
        elif isinstance(query_val, str):
            texts = [query_val.strip()]
        else:
            continue
        
        for text in texts:
            words = text.split()
            if not (4 <= len(words) <= 50):
                continue
            if text.lower() in existing_questions:
                continue
            
            intent = classify_by_keywords(text)
            if intent:
                labeled_queries.append({"question": text, "intent label": intent})
                existing_questions.add(text.lower())
                matched += 1
        
        # Early stop: we have enough candidates (2x what we need)
        if matched >= new_queries_needed * 2:
            print(f"  Reached {matched} matches, stopping early.")
            break

except Exception as e:
    print(f"Error streaming UCSD dataset: {e}")
    import traceback
    traceback.print_exc()

print(f"\nProcessed {processed:,} UCSD rows total")
print(f"Matched {matched} queries with intent labels")

# Save raw matched queries
if labeled_queries:
    raw_df = pd.DataFrame(labeled_queries)
    raw_path = os.path.join(RAW_DIR, "ucsd_labeled_queries.csv")
    raw_df.to_csv(raw_path, index=False)
    print(f"Saved raw labeled queries to: {raw_path}")

# ---------------------------------------------------------------------------
# STEP 4: Try Twitter dataset (alternative sources)
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("STEP 4: Trying Twitter dataset alternatives")
print("=" * 60)

twitter_labeled = []
twitter_matched = 0

# Try different HuggingFace repos
twitter_repos = [
    "TNE-AI/customer-support-on-twitter-conversation",
    "Alaeddin0/customer_support_twitter",
    "inria-soda/tabular-benchmark",  # skip this one
]

for repo in twitter_repos[:2]:  # Try first two
    print(f"  Trying: {repo} ...")
    try:
        tw_ds = load_dataset(repo, split="train", streaming=True)
        tw_processed = 0
        
        for example in tw_ds:
            tw_processed += 1
            if tw_processed == 1:
                print(f"    Columns: {list(example.keys())}")
                print(f"    Sample row: {dict(list(example.items())[:5])}")
            
            if tw_processed % 50000 == 0:
                print(f"    Processed {tw_processed:,}, matched {twitter_matched}")
            
            # Try to find text column
            text = None
            for key in ["text", "tweet_text", "message", "content", "conversation"]:
                if key in example:
                    val = example[key]
                    if isinstance(val, str):
                        text = val
                    elif isinstance(val, list) and len(val) > 0:
                        # Take customer messages only
                        text = " ".join([str(v) for v in val if isinstance(v, str)][:1])
                    break
            
            if not text:
                continue
            
            # Check if Amazon-related
            text_lower = text.lower()
            if not any(kw in text_lower for kw in ["amazon", "order", "package", "delivery", "refund", "return", "ship", "track", "cancel", "payment", "account"]):
                continue
            
            # Clean tweet
            text = re.sub(r"https?://\S+", "", text)
            text = re.sub(r"@\w+", "", text)
            text = re.sub(r"^RT\s*:?\s*", "", text)
            text = re.sub(r"#", "", text)
            text = re.sub(r"\s+", " ", text).strip()
            
            words = text.split()
            if not (5 <= len(words) <= 50):
                continue
            if text.lower() in existing_questions:
                continue
            
            intent = classify_by_keywords(text)
            if intent:
                twitter_labeled.append({"question": text, "intent label": intent})
                existing_questions.add(text.lower())
                twitter_matched += 1
            
            if twitter_matched >= 3000:
                print(f"    Reached {twitter_matched} matches, stopping.")
                break
            
            if tw_processed >= 500000:
                print(f"    Processed 500K rows, stopping.")
                break
        
        print(f"  {repo}: processed {tw_processed}, matched {twitter_matched}")
        if twitter_matched > 0:
            break  # Got data from this repo, no need to try others
            
    except Exception as e:
        print(f"  Error with {repo}: {e}")
        continue

print(f"\nTotal Twitter matches: {twitter_matched}")

if twitter_labeled:
    tw_df = pd.DataFrame(twitter_labeled)
    tw_path = os.path.join(RAW_DIR, "twitter_labeled_queries.csv")
    tw_df.to_csv(tw_path, index=False)
    print(f"Saved Twitter labeled queries to: {tw_path}")

# ---------------------------------------------------------------------------
# STEP 5: Combine all new queries
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("STEP 5: Combining all new queries")
print("=" * 60)

all_new = labeled_queries + twitter_labeled
random.seed(42)
random.shuffle(all_new)
print(f"Total new labeled queries: {len(all_new)}")

# Count per intent
new_intent_counts = Counter()
new_by_intent = defaultdict(list)
for item in all_new:
    new_intent_counts[item["intent label"]] += 1
    new_by_intent[item["intent label"]].append(item)

print(f"\nNew queries by intent:")
for intent in intent_names:
    cnt = new_intent_counts.get(intent, 0)
    print(f"  {intent}: {cnt}")

# ---------------------------------------------------------------------------
# STEP 6: Balance to reach target
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("STEP 6: Balancing to target {TARGET_TOTAL}")
print("=" * 60)

target_per_intent = TARGET_TOTAL // len(intent_names)  # ~294
print(f"Target per intent: ~{target_per_intent}")

sampled_new = []
for intent in intent_names:
    v1_count = v1_intent_counts.get(intent, 0)
    available_new = len(new_by_intent.get(intent, []))
    needed = max(0, target_per_intent - v1_count)
    take = min(needed, available_new)
    
    if take > 0:
        sampled = random.sample(new_by_intent[intent], take)
        sampled_new.extend(sampled)
    
    total = v1_count + take
    print(f"  {intent}: v1={v1_count} + new={take} = {total}" + 
          (" [GAP: {0}]".format(target_per_intent - total) if total < target_per_intent else ""))

current_total = len(v1_df) + len(sampled_new)
gap = TARGET_TOTAL - current_total
print(f"\nAfter balancing: {current_total} queries (gap: {gap})")

# If there's a gap, try to fill it by over-sampling from intents that have excess
if gap > 0:
    print(f"\nFilling gap of {gap} by over-sampling from available intents...")
    # Find intents with surplus new data
    surplus_intents = []
    for intent in intent_names:
        v1_count = v1_intent_counts.get(intent, 0)
        already_taken = sum(1 for s in sampled_new if s["intent label"] == intent)
        available = len(new_by_intent.get(intent, [])) - already_taken
        if available > 0:
            surplus_intents.append((intent, available))
    
    surplus_intents.sort(key=lambda x: x[1], reverse=True)
    
    filled = 0
    for intent, available in surplus_intents:
        if filled >= gap:
            break
        already_taken_ids = set()
        for i, s in enumerate(sampled_new):
            if s["intent label"] == intent:
                already_taken_ids.add(id(s))
        
        remaining = [q for q in new_by_intent[intent] if id(q) not in already_taken_ids]
        # Don't also take ones already sampled
        already_texts = set(s["question"].lower() for s in sampled_new if s["intent label"] == intent)
        remaining = [q for q in remaining if q["question"].lower() not in already_texts]
        
        take_extra = min(len(remaining), gap - filled, 50)  # cap at 50 extra per intent
        if take_extra > 0:
            extra = random.sample(remaining, take_extra)
            sampled_new.extend(extra)
            filled += take_extra
            print(f"  +{take_extra} from {intent}")
    
    print(f"  Filled {filled} extra queries")

# ---------------------------------------------------------------------------
# STEP 7: Build and save v2
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("STEP 7: Building classifier_training_dataset_v2.csv")
print("=" * 60)

v1_records = v1_df[["question", "intent label"]].to_dict("records")
all_records = v1_records + sampled_new
random.shuffle(all_records)

v2_df = pd.DataFrame(all_records)
print(f"V2 shape: {v2_df.shape}")

# Remove any duplicates
before = len(v2_df)
v2_df = v2_df.drop_duplicates(subset=["question"], keep="first")
print(f"Removed {before - len(v2_df)} duplicates")

# Remove overlap with eval
eval_qs = set(eval_df["question"].str.lower().str.strip())
overlap = v2_df["question"].str.lower().str.strip().isin(eval_qs)
if overlap.sum() > 0:
    print(f"Removing {overlap.sum()} queries overlapping with eval set")
    v2_df = v2_df[~overlap]

v2_df.to_csv(OUTPUT_FILE, index=False)
print(f"\nSaved: {OUTPUT_FILE}")

# ---------------------------------------------------------------------------
# STEP 8: Final validation
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("FINAL SUMMARY")
print("=" * 60)
print(f"V2 total queries: {len(v2_df)}")
print(f"V2 intents: {len(v2_df['intent label'].unique())}")

v2_counts = v2_df["intent label"].value_counts()
print(f"Min per intent: {v2_counts.min()} ({v2_counts.idxmin()})")
print(f"Max per intent: {v2_counts.max()} ({v2_counts.idxmax()})")
print(f"Mean per intent: {v2_counts.mean():.1f}")

missing_intents = set(intent_names) - set(v2_df["intent label"].unique())
if missing_intents:
    print(f"WARNING - Missing intents: {missing_intents}")
else:
    print(f"✓ All {len(intent_names)} intents covered")

print(f"\nFull distribution:")
for intent in intent_names:
    cnt = v2_counts.get(intent, 0)
    bar = "#" * (cnt // 10)
    print(f"  {intent:40s}: {cnt:4d} {bar}")

# Save progress info
progress = {
    "v1_count": len(v1_df),
    "ucsd_matched": len(labeled_queries),
    "twitter_matched": len(twitter_labeled),
    "sampled_new": len(sampled_new),
    "v2_final": len(v2_df),
    "target": TARGET_TOTAL,
}
with open(os.path.join(RAW_DIR, "v2_build_progress.json"), "w") as f:
    json.dump(progress, f, indent=2)

print("\n✓ Done!")
