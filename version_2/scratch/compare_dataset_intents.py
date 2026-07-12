import json
import pandas as pd

with open("data/intents_queries.json", "r", encoding="utf-8") as f:
    intents = json.load(f)

df = pd.read_csv("data/qa_dataset.csv")

qa_intents = set(df["intent"].unique())
json_intents = set(i["intent"] for i in intents)

print(f"Number of unique intents in qa_dataset: {len(qa_intents)}")
print(f"Number of unique intents in intents_queries.json: {len(json_intents)}")

mismatch_qa_to_json = qa_intents - json_intents
mismatch_json_to_qa = json_intents - qa_intents

print(f"Intents in qa_dataset but not in intents_queries.json: {mismatch_qa_to_json}")
print(f"Intents in intents_queries.json but not in qa_dataset: {mismatch_json_to_qa}")
