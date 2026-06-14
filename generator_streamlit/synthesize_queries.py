import os
import csv
import json
import random

WS_DIR = r"c:\Users\Anupam Dasgupta\Desktop\INQSYT"
SCHEMA_PATH = os.path.join(WS_DIR, "generator_streamlit", "intents_schema.json")
OUTPUT_PATH = os.path.join(WS_DIR, "Main_Data", "queries.csv")

# Load new intents and sample queries from intents_schema.json
with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    schema = json.load(f)

INTENTS = [entry["intent"] for entry in schema]
seeds = {entry["intent"]: entry["sample_queries"] for entry in schema}

# Synonym expansion rules to enrich training dataset diversity
verb_synonyms = {
    "track": ["track", "locate", "find", "check the status of", "follow", "view"],
    "check": ["check", "see", "view", "find", "verify", "learn about", "look up"],
    "reset": ["reset", "change", "update", "troubleshoot", "fix", "recover"],
    "manage": ["manage", "update", "edit", "change", "configure", "set up"],
    "close": ["close", "delete", "deactivate", "terminate", "remove"],
    "report": ["report", "flag", "resolve", "notify Amazon of", "complain about"],
    "resolve": ["resolve", "fix", "troubleshoot", "retry", "rectify"],
    "convert": ["convert", "calculate", "check exchange rates for", "set card currency to"],
    "view": ["view", "print", "download", "find", "get a PDF of", "save"],
    "submit": ["submit", "send", "upload", "file", "register"],
    "identify": ["identify", "spot", "recognize", "detect", "report"],
    "investigate": ["investigate", "check", "report", "look into", "verify details of"],
    "request": ["request", "ask for", "contact support for", "apply for"],
    "modify": ["modify", "change", "edit", "update", "cancel", "adjust"],
    "contact": ["contact", "call", "chat", "reach", "open", "speak with", "talk to"]
}

noun_synonyms = {
    "order": ["order", "purchase", "shopping cart", "active order", "placed order"],
    "address": ["shipping address", "delivery address", "billing address", "saved address", "address book details"],
    "invoice": ["invoice PDF", "billing receipt", "order receipt", "tax invoice", "proof of purchase"],
    "feedback": ["feedback", "customer survey", "opinion", "satisfaction rating"],
    "password": ["password", "passcode", "login credentials", "login security details"],
    "teen account": ["teen account", "teen login", "teen approvals", "teen household profile"],
    "profile settings": ["profile settings", "shopping profile", "switch accounts", "app sign-out"],
    "account settings": ["account settings", "language preferences", "Spanish language option", "third-party data access"],
    "account": ["account", "Amazon shopping profile", "membership registration"],
    "wallet cards": ["wallet cards", "credit cards", "debit cards", "payment wallet", "backup payment card"],
    "currency": ["currency", "exchange rates", "converter settings", "card payment currency"],
    "declined payment": ["declined payment", "failed card charge", "declined credit card", "failed transaction"],
    "unknown charge": ["unknown charge", "unrecognized Amazon charge", "AMZ Prime billing fee", "unauthorized statement fee"],
    "payment scam": ["payment scam", "gift card fraud", "phishing attempt", "security scam alert"],
    "return eligibility": ["return eligibility", "return window limit", "non-returnable products", "30-day return policy"],
    "restocking fees": ["restocking fees", "damage deductions", "opened items return fees", "refund reduction rules"],
    "international returns": ["international returns", "overseas return labels", "international return shipping cost"],
    "refund": ["refund", "returned package status", "money-back timeline", "bank refund speed"],
    "promotional balance": ["promotional balance", "promotional credits", "reward points total", "benefit balance"],
    "package": ["package", "parcel", "shipment tracker", "photo proof of delivery"],
    "delivery alerts": ["delivery alerts", "shipment updates text", "SMS notifications", "push delivery alerts"],
    "delivery delay": ["delivery delay", "late package scan", "delayed carrier tracking", "missed delivery date"],
    "undeliverable package": ["undeliverable package", "return to sender status", "incorrect shipping address error"],
    "delivery rules": ["delivery rules", "OTP delivery code", "delivery time slots", "prison shipping rules"],
    "support": ["support", "live customer care", "support chat helpline", "customer support ticket"],
    "bereavement support": ["bereavement support", "deceased account closure", "family death estate settings"],
    "legal poa": ["legal poa", "power of attorney paperwork", "submitting poa documents"],
    "missing package": ["missing package", "package shows delivered but missing", "stolen package from doorstep"],
    "missing item": ["missing item", "missing order items", "item missing from inside my package", "empty Amazon shipping box"],
    "customs regulations": ["customs regulations", "passport ID for customs", "EZ WAY Taiwan login", "South Korea PCCC code"],
    "shipping policies": ["shipping policies", "hotel shipping rules", "freight forwarder deliveries", "signature on delivery requirement"],
    "phishing scams": ["phishing scams", "fake Amazon surveys", "suspicious email alerts", "identifying fake text messages"],
    "tax rates": ["tax rates", "sales tax calculation", "EU VAT rates", "tax on digital Kindle books"],
    "notifications": ["notifications", "Subscribe & Save alerts", "out of stock restock emails", "email alerts"]
}

templates = [
    "I want to {verb} my {noun}",
    "How do I {verb} the {noun}?",
    "Can you help me {verb} my {noun}?",
    "Please show me how to {verb} {noun}",
    "I need assistance to {verb} my {noun}",
    "Is it possible to {verb} this {noun}?",
    "What is the way to {verb} the {noun}?",
    "Can I {verb} {noun} on Amazon?",
    "I'm trying to {verb} my {noun}",
    "I need to {verb} {noun}"
]

def generate_queries_for_intent(intent, count=200):
    queries = set()
    
    # 1. Add hand-written seed queries from intents_schema
    if intent in seeds:
        for s in seeds[intent]:
            queries.add(s)
            
    # Split the intent by underscore to extract verb and noun keys
    parts = intent.split("_")
    verb_key = parts[0]
    noun_key = " ".join(parts[1:])
    
    # Resolve verb synonyms
    verbs = verb_synonyms.get(verb_key, [verb_key])
    
    # Resolve noun synonyms
    nouns = noun_synonyms.get(noun_key, [noun_key])
    
    # 2. Programmatically generate queries using templates
    attempts = 0
    while len(queries) < count and attempts < 20000:
        attempts += 1
        t = random.choice(templates)
        v = random.choice(verbs)
        n = random.choice(nouns)
        
        q = t.format(verb=v, noun=n)
        q = q[0].upper() + q[1:]  # Ensure proper capitalization
        queries.add(q)
        
    return list(queries)[:count]

def generate_and_save():
    variations_path = os.path.join(WS_DIR, "amazon_support_variations_per_seed_query.json")
    
    if os.path.exists(variations_path):
        print(f"Loading hand-written query variations from {variations_path}...")
        with open(variations_path, "r", encoding="utf-8") as f:
            variations_data = json.load(f)
            
        all_data = []
        for intent, seeds_list in variations_data.items():
            intent_queries = []
            for seed_obj in seeds_list:
                for q in seed_obj.get("variations", []):
                    # Clean and add unique queries
                    q_clean = q.strip()
                    if q_clean and q_clean not in intent_queries:
                        intent_queries.append(q_clean)
            
            print(f"  - Loaded {len(intent_queries)} unique variations for intent: '{intent}'")
            for q in intent_queries:
                all_data.append([q, intent])
    else:
        print(f"Warning: {variations_path} not found. Falling back to template-based generation...")
        all_data = []
        for intent in INTENTS:
            queries = generate_queries_for_intent(intent, count=200)
            print(f"  - Generated {len(queries)} queries for intent: '{intent}'")
            for q in queries:
                all_data.append([q, intent])
            
    # Shuffle dataset
    random.seed(42)
    random.shuffle(all_data)
    
    # Write to Main_Data/queries.csv
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["question", "intent label"])
        for row in all_data:
            writer.writerow(row)
            
    print(f"\nSuccessfully saved training dataset to {OUTPUT_PATH}")
    print(f"Total dataset size: {len(all_data)} queries.")

if __name__ == "__main__":
    generate_and_save()
