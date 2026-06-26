import pandas as pd

df = pd.read_csv(r"c:\Users\Anupam Dasgupta\Desktop\INQSYT\Main_Data\classifier_training_dataset.csv")
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"\nFirst 5 rows:")
print(df.head().to_string())
print(f"\nIntent distribution:")
print(df["intent"].value_counts().to_string())
