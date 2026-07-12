import json
import pandas as pd

def load_chunks():
    with open("data/Chunks.jsonl", "r", encoding="utf-8") as f:
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
chunk_queries = {}
for c in chunks:
    for q in c.get("metadata", {}).get("sample_queries", []):
        chunk_queries[q.strip().lower()] = (c["chunk_id"], c.get("category_path", ""))

with open("data/intents_queries.json", "r", encoding="utf-8") as f:
    intents = json.load(f)

intent_queries = {}
for i in intents:
    for q in i.get("sample_queries", []):
        intent_queries[q.strip().lower()] = i["intent"]

print(f"Total unique queries from chunks: {len(chunk_queries)}")
print(f"Total unique queries from intents: {len(intent_queries)}")

df_qa = pd.read_csv("data/qa_dataset.csv")
qa_in_chunks = sum(1 for q in df_qa["question"] if q.strip().lower() in chunk_queries)
qa_in_intents = sum(1 for q in df_qa["question"] if q.strip().lower() in intent_queries)
print(f"qa_dataset.csv queries found in chunks: {qa_in_chunks} / {len(df_qa)}")
print(f"qa_dataset.csv queries found in intents: {qa_in_intents} / {len(df_qa)}")

df_eval = pd.read_csv("data/retriever_evaluation_queries.csv")
eval_in_chunks = sum(1 for q in df_eval["query"] if q.strip().lower() in chunk_queries)
eval_in_intents = sum(1 for q in df_eval["query"] if q.strip().lower() in intent_queries)
print(f"retriever_evaluation_queries.csv queries found in chunks: {eval_in_chunks} / {len(df_eval)}")
print(f"retriever_evaluation_queries.csv queries found in intents: {eval_in_intents} / {len(df_eval)}")
