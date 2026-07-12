import json

with open("data/chunks_v2_completed.jsonl", "r", encoding="utf-8") as f:
    content = f.read()

decoder = json.JSONDecoder(strict=False)
pos = 0
len_c = len(content)
idx_count = 0
standard_keys = {'chunk_id', 'chunk_title', 'source_file', 'chunk', 'metadata'}

while pos < len_c:
    while pos < len_c and content[pos].isspace():
        pos += 1
    if pos >= len_c:
        break
    obj, idx = decoder.raw_decode(content, pos)
    idx_count += 1
    
    non_standard = set(obj.keys()) - standard_keys
    if non_standard:
        print(f"Record {idx_count} ('{obj.get('chunk_id', 'unknown')}') has non-standard keys: {list(non_standard)}")
        
    pos = idx

print(f"Finished checking {idx_count} records.")
