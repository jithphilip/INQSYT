import pandas as pd

df = pd.read_csv("data/qa_dataset.csv")

# 1. Map old track_refund intent to the split ones
track_refund_status_queries = [
    "How do I check the status of my returned package refund?",
    "Where do I track my refund transaction?",
    "How to check if my refund was sent to my credit card?",
    "Where is my refund receipt in my account details?",
    "How do I track a refund sent to my gift card balance?",
    "Where do I find my return refund confirmation?"
]

refund_processing_queries = [
    "How long does a refund take to credit to my bank account?",
    "I shipped my return, when will my refund be issued?",
    "Why has my refund not appeared in my bank account yet?",
    "What is the average processing time for return refunds?"
]

# Apply intent mapping
for q in track_refund_status_queries:
    df.loc[df["question"] == q, "intent"] = "track_refund_status"

for q in refund_processing_queries:
    df.loc[df["question"] == q, "intent"] = "refund_processing"

# 2. Map missing chunk IDs to their replacements
chunk_replacements = {
    # South Korea PCCC & Argentina CUIL are in customs_regs_003
    "How do I enter my PCCC code for South Korea customs clearance?": ("customs_regs_003", "check_customs_regulations"),
    "How do I clear my Amazon shipment in Argentina using my CUIL ID?": ("customs_regs_003", "check_customs_regulations"),
    "What is the personal customs clearance code requirement?": ("customs_regs_003", "check_customs_regulations"),
    
    # Delayed package at carrier facility maps to missing_tracking_information_003
    "Why is my package delayed at the carrier facility?": ("missing_tracking_information_003", "check_delivery_delay"),
    
    # Undeliverable package reasons vs reordering
    "Why was my package marked as undeliverable?": ("undeliverable_package_003", "resolve_undeliverable_package"),
    "How do I correct my address for an undeliverable order?": ("undeliverable_package_001", "resolve_undeliverable_package"),
    "Who do I contact if my carrier says undeliverable?": ("undeliverable_package_001", "resolve_undeliverable_package"),
    
    # Missing items maps to missing_item_from_order_001/002/003
    "I only received half of my order, who do I contact?": ("missing_item_from_order_002", "report_missing_item"),
    "How to claim a refund for a missing item in a package?": ("missing_item_from_order_002", "report_missing_item"),
    "My delivery was short one item, how to get a replacement?": ("missing_item_from_order_002", "report_missing_item"),
    "The shipping envelope was empty when it was delivered.": ("missing_item_from_order_001", "report_missing_item"),
    "Where do I report a missing item from a multi-item package?": ("missing_item_from_order_002", "report_missing_item"),
    
    # Commercial warehouse delivery
    "Can my order be delivered to a commercial warehouse?": ("third_party_company_delivery_001", "check_shipping_policies"),
    
    # US state sales tax calculated in about_us_state_sales_and_use_taxes_001
    "Why did my order tax change during checkout?": ("about_us_state_sales_and_use_taxes_001", "check_tax_rates"),
    "What is the sales tax rate for my delivery address?": ("about_us_state_sales_and_use_taxes_001", "check_tax_rates"),
    "How do I apply for a tax-exempt purchase?": ("about_us_state_sales_and_use_taxes_001", "check_tax_rates"),
    "Where can I find tax calculation details for my transaction?": ("about_us_state_sales_and_use_taxes_001", "check_tax_rates"),
    "Does Amazon charge tax on gift card purchases?": ("about_us_state_sales_and_use_taxes_001", "check_tax_rates"),
    "Where do I see the tax breakdown of my invoice?": ("about_us_state_sales_and_use_taxes_001", "check_tax_rates")
}

# Apply chunk and intent replacements
for question, (chunk_id, intent_label) in chunk_replacements.items():
    df.loc[df["question"] == question, "reference_chunk_id"] = chunk_id
    df.loc[df["question"] == question, "intent"] = intent_label

df.to_csv("data/qa_dataset.csv", index=False)
print("Successfully fixed qa_dataset.csv!")
