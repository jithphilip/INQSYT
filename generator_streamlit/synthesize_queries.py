import json
import os
import random
import pandas as pd

# Path configurations
ws_dir = r"c:\Users\Anupam Dasgupta\Desktop\INQSYT"
qa_path = os.path.join(ws_dir, "Main_Data", "Questions&Answers.csv")
chunks_path = os.path.join(ws_dir, "generator_streamlit", "Chunks_v3_intent.jsonl")
output_csv_path = os.path.join(ws_dir, "Main_Data", "queries.csv")
output_jsonl_path = os.path.join(ws_dir, "Main_Data", "queries.jsonl")

# 1. Load Chunks and their Metadata
chunks = []
chunk_by_id = {}
chunks_by_intent = {}

with open(chunks_path, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            rec = json.loads(line)
            chunks.append(rec)
            chunk_by_id[rec["chunk_id"]] = rec
            intent = rec["intent"]
            if intent not in chunks_by_intent:
                chunks_by_intent[intent] = []
            chunks_by_intent[intent].append(rec)

# 2. Load existing Questions & Answers
qa_df = pd.read_csv(qa_path)
print(f"Loaded {len(qa_df)} existing queries from Questions&Answers.csv")

# Map existing queries to new unified intent labels
existing_queries_by_intent = {}
for intent in chunks_by_intent:
    existing_queries_by_intent[intent] = []

for idx, row in qa_df.iterrows():
    cid = str(row["chunk id"]).strip()
    # Normalize ID match
    matched_chunk = chunk_by_id.get(cid)
    if not matched_chunk:
        for k, v in chunk_by_id.items():
            if k.lower() == cid.lower():
                matched_chunk = v
                break
    
    if matched_chunk:
        intent = matched_chunk["intent"]
        existing_queries_by_intent[intent].append({
            "question": row["question"],
            "chunk id": matched_chunk["chunk_id"],
            "intent label": intent,
            "doc title": matched_chunk["source_file"].replace(".md", ""),
            "chunk title": matched_chunk["chunk_title"],
            "correct_chunk": matched_chunk["chunk"],
            "answer": row["answer"] if pd.notna(row["answer"]) else matched_chunk["chunk"][:150]
        })

# 3. Dynamic Template-Based Query Generator
# Define rich templates per intent to ensure high-quality natural language variety
templates = {
    "track_order": [
        "How do I track my package for {synonym}?",
        "Where can I see the status of my order if it's {synonym}?",
        "Is there a way to verify the location of my parcel related to {synonym}?",
        "What should I do if my shipment is {synonym}?",
        "Can I check the delivery window or map for {synonym}?",
        "How will Amazon update me regarding {synonym}?",
        "Who do I contact if my package has a status of {synonym}?",
        "How do I set up alerts for my package regarding {synonym}?",
        "I need updates on {synonym}, where do I check?",
        "Why is there no tracking info showing for {synonym}?"
    ],
    "returns_refunds": [
        "What is the return policy for {synonym}?",
        "How long does it take to get a refund for {synonym}?",
        "Can I get a replacement or return my item if it's {synonym}?",
        "Are there any fees or partial deductions for returns of {synonym}?",
        "What are the rules regarding returning {synonym}?",
        "I received a damaged or wrong product, how do I initiate a return for {synonym}?",
        "Do I need the original packing slip or invoice for {synonym}?",
        "Can I return an order that is {synonym}?",
        "Is {synonym} eligible for a full refund or exchange?",
        "Where do I drop off my package for return shipping of {synonym}?"
    ],
    "shipping_delivery": [
        "What shipping methods are available for {synonym}?",
        "Does Amazon deliver packages to {synonym}?",
        "How do customs clearance and regulations work for {synonym}?",
        "Are there any shipping rules or address restrictions for {synonym}?",
        "What are the delivery terms and options for {synonym}?",
        "How long does standard shipping take for {synonym}?",
        "Can I get same-day or premium delivery for {synonym}?",
        "What happens if my package is returned to sender due to {synonym}?",
        "Who is the carrier in charge of delivering {synonym}?",
        "Are there any special addressing requirements for {synonym}?"
    ],
    "modify_order": [
        "How can I cancel my order or request a change for {synonym}?",
        "Can I update my shipping details or address for {synonym}?",
        "Is it possible to split my shipment or deliver to {synonym}?",
        "How do I change my payment method after checkout for {synonym}?",
        "What is the process to edit my order items before they ship for {synonym}?",
        "Can I stop a shipment or cancel it if it's already {synonym}?",
        "I made a mistake in my shipping address, how do I edit it for {synonym}?",
        "Is it too late to modify my order regarding {synonym}?",
        "How do I cancel a replacement request for {synonym}?",
        "How do I group my cart items to prevent multiple packages for {synonym}?"
    ],
    "payments_promotions": [
        "Why was my credit card declined for {synonym}?",
        "What payment options or methods can I use for {synonym}?",
        "How do I apply a promo code or discount for {synonym}?",
        "Where can I manage my gift cards or account balances for {synonym}?",
        "How do I update my billing address or credit card details for {synonym}?",
        "Are there any special promotions or loyalty points for {synonym}?",
        "Why is my promotional certificate not working for {synonym}?",
        "How do I get an invoice or billing receipt for {synonym}?",
        "Can I use PayPal or Apple Pay to purchase {synonym}?",
        "How do I close my Amazon account and transfer my balance for {synonym}?"
    ],
    "general_query": [
        "How do I sign up for availability restock notifications for {synonym}?",
        "Is it safe to share my account information regarding {synonym}?",
        "How do I report a suspicious email, scam, or fraud related to {synonym}?",
        "What should I do if I think my account was hacked regarding {synonym}?",
        "Where can I find help documentation for {synonym}?",
        "How do I contact customer support about {synonym}?",
        "Will Amazon ever call me asking for password or details about {synonym}?",
        "What are the security terms for protecting my info during {synonym}?",
        "Is there an email alert when an item is restocked for {synonym}?",
        "How do I recognize official Amazon communications regarding {synonym}?"
    ]
}

final_queries = []

# Keep track of generated questions to prevent duplicates
seen_questions = set()

# Process each intent
for intent, chunk_list in chunks_by_intent.items():
    print(f"Processing intent '{intent}':")
    # Start with existing queries
    intent_queries = list(existing_queries_by_intent[intent])
    for q in intent_queries:
        seen_questions.add(q["question"].lower().strip())
        
    initial_count = len(intent_queries)
    print(f"  - Existing queries: {initial_count}")
    
    needed = 200 - initial_count
    generated_count = 0
    
    # Random generator seed for stability
    random.seed(42)
    
    # Loop until we reach exactly 200 queries
    attempts = 0
    while len(intent_queries) < 200 and attempts < 10000:
        attempts += 1
        
        # Pick a random chunk for this intent
        chunk = random.choice(chunk_list)
        
        # Determine synonyms or key terms
        syns = chunk["metadata"].get("jargon_synonyms", [])
        if not syns:
            syns = [chunk["chunk_title"]]
            
        synonym = random.choice(syns)
        
        # Pick a random template for this intent
        template = random.choice(templates[intent])
        
        # Format the question
        question = template.format(synonym=synonym)
        
        # Apply slight capitalization and style variations to look human
        if random.random() > 0.7:
            question = question.lower()
        if random.random() > 0.8:
            question = question.replace("?", "")
            
        q_clean = question.lower().strip()
        if q_clean not in seen_questions:
            seen_questions.add(q_clean)
            
            # Formulate the response snippet
            ans = chunk["chunk"]
            if len(ans) > 200:
                ans = ans[:197] + "..."
                
            intent_queries.append({
                "question": question,
                "chunk id": chunk["chunk_id"],
                "intent label": intent,
                "doc title": chunk["source_file"].replace(".md", ""),
                "chunk title": chunk["chunk_title"],
                "correct_chunk": chunk["chunk"],
                "answer": ans
            })
            generated_count += 1
            
    print(f"  - Generated queries: {generated_count}")
    print(f"  - Total queries for '{intent}': {len(intent_queries)}")
    final_queries.extend(intent_queries)

# 4. Save output files
# Shuffle final queries so they are mixed in the file
random.shuffle(final_queries)

df_out = pd.DataFrame(final_queries)
df_out.to_csv(output_csv_path, index=False, encoding="utf-8")
print(f"\nSaved CSV database with {len(df_out)} queries to {output_csv_path}")

with open(output_jsonl_path, "w", encoding="utf-8") as f:
    for q in final_queries:
        f.write(json.dumps(q, ensure_ascii=False) + "\n")
print(f"Saved JSONL database with {len(final_queries)} queries to {output_jsonl_path}")

# Also save to root workspace directory as 'queries', 'queries.csv' and 'queries.jsonl'
root_csv_path = os.path.join(ws_dir, "queries.csv")
root_jsonl_path = os.path.join(ws_dir, "queries.jsonl")
root_no_ext_path = os.path.join(ws_dir, "queries")

df_out.to_csv(root_csv_path, index=False, encoding="utf-8")
print(f"Saved CSV database to root: {root_csv_path}")

with open(root_jsonl_path, "w", encoding="utf-8") as f:
    for q in final_queries:
        f.write(json.dumps(q, ensure_ascii=False) + "\n")
print(f"Saved JSONL database to root: {root_jsonl_path}")

df_out.to_csv(root_no_ext_path, index=False, encoding="utf-8")
print(f"Saved CSV database to root file 'queries' (no extension): {root_no_ext_path}")

print("\nDone successfully!")
