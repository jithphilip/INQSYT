import json

# 1. Load intents schema
with open("data/intents_schema_v2.json", "r", encoding="utf-8") as f:
    intents = json.load(f)

# 2. Fix the mappings
for i in intents:
    if i["intent"] == "check_customs_regulations":
        i["source_chunks"] = ["customs_regs_001", "customs_regs_002", "customs_regs_003"]
        print("Fixed check_customs_regulations source_chunks.")
        
    elif i["intent"] == "check_shipping_policies":
        # Replace hotel_delivery_merged_01 with hotel_delivery_001
        chunks = i["source_chunks"]
        fixed_chunks = [c if c != "hotel_delivery_merged_01" else "hotel_delivery_001" for c in chunks]
        i["source_chunks"] = fixed_chunks
        print("Fixed check_shipping_policies source_chunks.")

# 3. Save it back
with open("data/intents_schema_v2.json", "w", encoding="utf-8") as f:
    json.dump(intents, f, indent=4)

print("Intents schema v2 fixed successfully.")
