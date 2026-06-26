import os
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import re

ws = r'c:\Users\Anupam Dasgupta\Desktop\INQSYT'
chunks_path = os.path.join(ws, 'Main_Data', 'Chunks', 'chunks_v1_cleaned.jsonl')
index_out = os.path.join(ws, 'generator_streamlit', 'faiss_index_v1_cleaned_linearised.bin')

print(f"Loading chunks from {chunks_path}...")
chunks_df = pd.read_json(chunks_path, lines=True)

print("Loading BGE embedder...")
embedder = SentenceTransformer('BAAI/bge-base-en-v1.5')

def generate_topic(row):
    meta = row.get('metadata', {})
    cat_path = meta.get('category_path', '')
    
    parts = [p.strip() for p in cat_path.split(' > ')]
    if len(parts) >= 2:
        doc_name = parts[1]
    else:
        doc_name = row['source_file']
        
    doc_name = re.sub(r'\(\d+\)', '', doc_name)
    doc_name = doc_name.replace('.md', '').strip()
    doc_name = re.sub(r'that Shows a$', 'that Shows as Delivered', doc_name)
    doc_name = re.sub(r'Companies No$', 'Companies Not Affiliated with Amazon', doc_name)
    doc_name = re.sub(r'Text Up$', 'Text Updates', doc_name)
    doc_name = re.sub(r'Shipment Tra$', 'Shipment Tracking', doc_name)
    
    title = row['chunk_title'].strip()
    title = re.sub(r'^\d+\s*[-.]\s*', '', title).strip()
    
    if title.lower() in doc_name.lower():
        topic = f'Topic: {doc_name}'
    elif doc_name.lower() in title.lower():
        topic = f'Topic: {title}'
    else:
        topic = f'Topic: {doc_name} - {title}'
        
    return topic

texts = []
for _, row in chunks_df.iterrows():
    meta = row.get('metadata', {})
    queries = meta.get('sample_queries', [])
    syns = meta.get('jargon_synonyms', [])
    chunk_type = meta.get('chunk_type', 'text')
    
    category_path = meta.get('category_path', '')
    category = category_path.split(' > ')[0] if ' > ' in category_path else 'General Help'
    
    topic = generate_topic(row)
    search_text = f'{topic}\n'
    search_text += f"Category: {category} | Title: {row['chunk_title']} | Source: {row['source_file']}\n"
    search_text += f"Content: {row['chunk']}\n"
    
    # LINEARIZE MARKDOWN
    raw_md = ""
    if chunk_type == 'table' and meta.get('table_markdown'):
        raw_md = meta.get('table_markdown')
    elif chunk_type == 'list' and meta.get('list_markdown'):
        raw_md = meta.get('list_markdown')
        
    if raw_md:
        # Strip markdown syntax symbols to pack tokens densely
        flat = re.sub(r'[\r\n]+', ' ', raw_md)
        flat = re.sub(r'\|', ' ', flat)
        flat = re.sub(r'\*+', '', flat)
        flat = re.sub(r'-{3,}', '', flat)
        flat = re.sub(r'\s{2,}', ' ', flat).strip()
        search_text += f"Additional Context: {flat}\n"
    
    if syns:
        search_text += f"Keywords: {', '.join(syns)}\n"
    if queries:
        search_text += "Frequently Asked Questions:\n"
        for q in queries:
            search_text += f"- {q}\n"
    
    texts.append(search_text.strip())

print('Encoding chunks...')
embeddings = embedder.encode(
    texts,
    convert_to_numpy=True,
    show_progress_bar=True
).astype('float32')

print('Normalizing vectors...')
faiss.normalize_L2(embeddings)
dimension = embeddings.shape[1]

print('Building FlatIP FAISS index...')
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)

faiss.write_index(index, index_out)
print('FAISS index saved successfully to', index_out)
print(f'Indexed {index.ntotal} chunks.')
