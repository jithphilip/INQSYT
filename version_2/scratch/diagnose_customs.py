import json

with open("data/intents_schema_v2.json", "r", encoding="utf-8") as f:
    intents = json.load(f)

for i in intents:
    if i["intent"] in ["check_customs_regulations", "check_shipping_policies"]:
        print(f"Intent: {i['intent']}")
        print(f"Description: {i.get('description')}")
        print(f"Source Chunks: {i.get('source_chunks')}")
        print("-" * 45)
