import json

intents_file = r'c:\Users\Anupam Dasgupta\Desktop\INQSYT\Main_Data\Intents\intents_schema.json'
chunks_file = r'c:\Users\Anupam Dasgupta\Desktop\INQSYT\Main_Data\Chunks\Chunks.jsonl'

with open(intents_file, 'r', encoding='utf-8') as f:
    schema = json.load(f)

target_intents = schema[:17]
target_chunks = set()
for intent in target_intents:
    for c in intent['source_chunks']:
        target_chunks.add(c)

chunk_data = {}
with open(chunks_file, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data['chunk_id'] in target_chunks:
            chunk_data[data['chunk_id']] = data

with open(r'c:\Users\Anupam Dasgupta\Desktop\INQSYT\scratch\chunk_review.txt', 'w', encoding='utf-8') as f:
    for intent in target_intents:
        intent_name = intent['intent']
        f.write('\n\n=== INTENT: ' + intent_name + ' ===\n')
        for cid in intent['source_chunks']:
            data = chunk_data.get(cid)
            if data:
                f.write('\n--- CHUNK ID: ' + cid + ' ---\n')
                f.write('TITLE: ' + str(data.get('chunk_title')) + '\n')
                text = str(data.get('chunk', ''))
                f.write('TEXT:\n' + text[:500] + '\n')
            else:
                f.write('\n--- CHUNK ID: ' + cid + ' (NOT FOUND) ---\n')
