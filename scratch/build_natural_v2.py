"""
Build V2 dataset using ONLY real, scraped queries to reach the 10,000 target.
No templates are used. The dataset is balanced as much as possible, but where
niche intents lack real scraped data, the remaining quota is filled using
real scraped queries from other intents.
"""
import os
import json
import random
import pandas as pd
from collections import Counter

WS = r"c:\Users\Anupam Dasgupta\Desktop\INQSYT"
MAIN_DATA = os.path.join(WS, "Main_Data")
RAW_DIR = os.path.join(WS, "raw_data")

V1_FILE = os.path.join(MAIN_DATA, "classifier_training_dataset.csv")
EVAL_FILE = os.path.join(MAIN_DATA, "eval_dataset.csv")
INTENTS_FILE = os.path.join(MAIN_DATA, "intents_schema.json")
OUTPUT_FILE = os.path.join(MAIN_DATA, "classifier_training_dataset_v2.csv")

TARGET_TOTAL = 10000

# 1. Load data
v1_df = pd.read_csv(V1_FILE)
eval_df = pd.read_csv(EVAL_FILE)

# Load the raw scraped datasets
ucsd_df = pd.read_csv(os.path.join(RAW_DIR, "ucsd_labeled_queries.csv"))
twitter_df = pd.read_csv(os.path.join(RAW_DIR, "twitter_labeled_queries.csv"))

# Combine scraped
scraped_df = pd.concat([ucsd_df, twitter_df], ignore_index=True)
scraped_records = scraped_df.to_dict('records')

with open(INTENTS_FILE, "r", encoding="utf-8") as f:
    intents_schema = json.load(f)
intent_names = [it["intent"] for it in intents_schema]

# 2. Find existing eval queries to exclude
existing_eval_qs = set(eval_df["question"].str.lower().str.strip())
existing_v1_qs = set(v1_df["question"].str.lower().str.strip())

# Filter scraped to remove overlaps
valid_scraped = []
for r in scraped_records:
    q = str(r["question"]).strip().lower()
    if q not in existing_eval_qs and q not in existing_v1_qs:
        valid_scraped.append(r)
        existing_v1_qs.add(q) # prevent duplicates within scraped

print(f"V1 size: {len(v1_df)}")
print(f"Total valid scraped queries available: {len(valid_scraped)}")

# 3. Group scraped queries by intent
scraped_by_intent = {intent: [] for intent in intent_names}
for r in valid_scraped:
    scraped_by_intent[r["intent label"]].append(r)

v1_counts = Counter(v1_df["intent label"])

# 4. We need to add exactly (TARGET_TOTAL - len(v1_df)) queries
needed = TARGET_TOTAL - len(v1_df)
print(f"Queries needed to reach {TARGET_TOTAL}: {needed}")

sampled_new = []
intents_to_fill = list(intent_names)

# We want to distribute the `needed` amount fairly across intents.
# We'll do this in a round-robin or proportionate way, pulling from scraped_by_intent.

# Shuffle the pools
for intent in intent_names:
    random.seed(42)
    random.shuffle(scraped_by_intent[intent])

while needed > 0 and any(len(scraped_by_intent[i]) > 0 for i in intents_to_fill):
    # Determine how many to take per intent in this round
    # We try to keep them balanced by filling the ones with the lowest total count first
    
    # Calculate current total per intent
    current_totals = {i: v1_counts.get(i, 0) + sum(1 for s in sampled_new if s["intent label"] == i) for i in intent_names}
    
    # Sort intents by their current total (lowest first)
    intents_to_fill.sort(key=lambda x: current_totals[x])
    
    # Take one query from the intent with the lowest total, if available
    took_any = False
    for intent in intents_to_fill:
        if len(scraped_by_intent[intent]) > 0:
            sampled_new.append(scraped_by_intent[intent].pop(0))
            needed -= 1
            took_any = True
            break
            
    if not took_any:
        break # No more scraped queries available anywhere

print(f"Sampled {len(sampled_new)} new queries from scraped data.")

# 5. Combine and Save
all_records = v1_df.to_dict('records') + sampled_new
random.shuffle(all_records)

v2_final = pd.DataFrame(all_records)
v2_final.to_csv(OUTPUT_FILE, index=False)

print(f"\nFinal V2 dataset size: {len(v2_final)}")
final_counts = v2_final["intent label"].value_counts()
print("\nDistribution:")
for intent in intent_names:
    print(f"  {intent:40s}: {final_counts.get(intent, 0)}")

print(f"\nMin per intent: {final_counts.min()} ({final_counts.idxmin()})")
print(f"Max per intent: {final_counts.max()} ({final_counts.idxmax()})")
print(f"Mean per intent: {final_counts.mean():.1f}")
