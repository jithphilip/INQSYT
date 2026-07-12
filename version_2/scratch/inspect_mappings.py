import pandas as pd

df = pd.read_csv("data/retriever_evaluation_queries.csv")
unique_mappings = df.groupby(["intent_label", "reference_chunk_id"]).size().reset_index(name="count")
for idx, row in unique_mappings.iterrows():
    print(f"'{row['intent_label']}': '{row['reference_chunk_id']}',")
