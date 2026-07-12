import json
import pandas as pd

def load_chunks():
    with open("data/chunks_v2_completed.jsonl", "r", encoding="utf-8") as f:
        content = f.read()
    decoder = json.JSONDecoder(strict=False)
    pos = 0
    chunks = []
    len_c = len(content)
    while pos < len_c:
        while pos < len_c and content[pos].isspace():
            pos += 1
        if pos >= len_c:
            break
        obj, idx = decoder.raw_decode(content, pos)
        chunks.append(obj)
        pos = idx
    return chunks

chunks = load_chunks()
chunk_ids = set(c["chunk_id"] for c in chunks)

with open("data/intents_schema_v2.json", "r", encoding="utf-8") as f:
    intents = json.load(f)
intent_names = set(i["intent"] for i in intents)

df_eval = pd.read_csv("data/eval_dataset_v2.csv")

qa_intents = set(df_eval["intent"].unique())
qa_chunks = set(df_eval["reference_chunk_id"].unique())

print(f"Unique intents in eval_dataset_v2: {len(qa_intents)}")
print(f"Unique intents in intents_schema_v2: {len(intent_names)}")
print(f"Mismatched intents (eval dataset vs schema): {qa_intents - intent_names}")

print(f"Unique chunks in eval_dataset_v2: {len(qa_chunks)}")
print(f"Unique chunks in chunks_v2_completed: {len(chunk_ids)}")
print(f"Mismatched chunks (eval dataset vs chunks DB): {qa_chunks - chunk_ids}")
