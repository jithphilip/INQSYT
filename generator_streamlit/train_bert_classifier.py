import os
import json
import torch
import numpy as np
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INQSYT_DIR = os.path.dirname(CURRENT_DIR)
QUERIES_CSV_PATH = os.path.join(INQSYT_DIR, "Main_Data", "queries.csv")
MODEL_SAVE_DIR = os.path.join(CURRENT_DIR, "bert_classifier")

class QueryDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=64):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]

        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'label': torch.tensor(label, dtype=torch.long)
        }

def train_bert():
    # 1. Load dataset
    if not os.path.exists(QUERIES_CSV_PATH):
        print(f"Error: {QUERIES_CSV_PATH} not found.")
        return

    print(f"Loading training queries from {QUERIES_CSV_PATH}...")
    df = pd.read_csv(QUERIES_CSV_PATH)
    
    texts = df["question"].tolist()
    labels_raw = df["intent label"].tolist()
    
    # Encode labels
    le = LabelEncoder()
    labels = le.fit_transform(labels_raw)
    num_classes = len(le.classes_)
    
    print(f"Loaded {len(texts)} queries across {num_classes} intents.")
    
    # 2. Split dataset
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    # 3. Load tokenizer and model
    model_name = "distilbert-base-uncased"
    print(f"Loading tokenizer and model for {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_classes)
    
    # 4. Prepare data loaders
    train_dataset = QueryDataset(train_texts, train_labels, tokenizer)
    val_dataset = QueryDataset(val_texts, val_labels, tokenizer)
    
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
    
    # 5. Set device and optimizer
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")
    model = model.to(device)
    
    optimizer = AdamW(model.parameters(), lr=3e-5, weight_decay=0.01)
    
    # 6. Training Loop
    epochs = 4
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        for batch in train_loader:
            optimizer.zero_grad()
            
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            targets = batch['label'].to(device)
            
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=targets
            )
            
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
        avg_train_loss = total_loss / len(train_loader)
        
        # Validation
        model.eval()
        correct_predictions = 0
        total_predictions = 0
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                targets = batch['label'].to(device)
                
                outputs = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )
                
                preds = torch.argmax(outputs.logits, dim=1)
                correct_predictions += torch.sum(preds == targets).item()
                total_predictions += targets.size(0)
                
        val_acc = correct_predictions / total_predictions
        print(f"Epoch {epoch+1}/{epochs} | Train Loss: {avg_train_loss:.4f} | Val Accuracy: {val_acc:.4f}")
        
    # 7. Classification Report on validation set
    print("\nRunning final validation evaluation...")
    model.eval()
    all_preds = []
    all_targets = []
    
    with torch.no_grad():
        for batch in val_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            targets = batch['label'].to(device)
            
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask
            )
            
            preds = torch.argmax(outputs.logits, dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(targets.cpu().numpy())
            
    print("\nClassification Report (Validation Set):")
    print(classification_report(all_targets, all_preds, target_names=le.classes_))
    
    # 8. Save Model
    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)
    print(f"Saving model and tokenizer to {MODEL_SAVE_DIR}...")
    model.save_pretrained(MODEL_SAVE_DIR)
    tokenizer.save_pretrained(MODEL_SAVE_DIR)
    
    # Save label encoder classes
    meta_path = os.path.join(MODEL_SAVE_DIR, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "classes": le.classes_.tolist()
        }, f, indent=2)
        
    print("Done! BERT classifier trained and saved successfully.")

if __name__ == "__main__":
    train_bert()
