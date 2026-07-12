with open("data/chunks_v2_completed.jsonl", "r", encoding="utf-8") as f:
    text = f.read()

fixed_text = text.replace('"cmissing_package_delivered_002hunk_title"', '"chunk_title"')

with open("data/chunks_v2_completed.jsonl", "w", encoding="utf-8") as f:
    f.write(fixed_text)

print("Typo fixed successfully.")
