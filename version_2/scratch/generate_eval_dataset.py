import json
import pandas as pd

with open("data/intents_queries.json", "r", encoding="utf-8") as f:
    intents = json.load(f)

# Old mapping dictionary
old_mapping = {
    'check_customs_regulations': 'customs_regs_001',
    'check_delivery_delay': 'late_delivery_007',
    'check_delivery_rules': 'delivery_windows_001',
    'check_international_returns': 'amz_int_001',
    'check_promotional_balance': 'check_your_credit_and_benefit_balances_001',
    'check_restocking_fees': 'amz_fee_001',
    'check_return_eligibility': 'amz_ret_001',
    'check_shipping_policies': 'fulfilled_by_amazon_001',
    'check_tax_rates': 'about_us_state_sales_and_use_taxes_001',
    'close_account': 'request_the_closure_of_your_account_and_the_deletion_of_001',
    'contact_support': 'amazon_currency_converter_supported_currencies_001',
    'convert_currency': 'about_currency_of_preference_on_international_shopping_001',
    'identify_phishing_scams': 'how_to_identify_fake_emails_001',
    'investigate_unknown_charge': 'unknown_amazon_payment_charges_001',
    'manage_account_settings': 'about_the_spanish_language_experience_001',
    'manage_delivery_alerts': 'manage_shipment_text_updates_001',
    'manage_notifications': 'availability_alerts_001',
    'manage_profile_settings': 'add_a_shopping_profile_001',
    'manage_teen_account': 'approve_a_teens_order_001',
    'manage_wallet_cards': 'amz_acc_001',
    'modify_address': 'add_delete_and_manage_addresses_001',
    'modify_order': 'amz_can_001',
    'report_missing_item': 'missing_item_from_order_001',
    'report_missing_package': 'missing_package_delivered_002',
    'report_payment_scam': 'amz_sec_001',
    'request_bereavement_support': 'bereavement_support_001',
    'reset_password': 'about_security_codes_001',
    'resolve_declined_payment': 'resolve_a_declined_payment_001',
    'resolve_undeliverable_package': 'undeliverable_package_001',
    'submit_feedback': 'amazon_consumer_surveys_001',
    'submit_legal_poa': 'power_of_attorneypoa_support_001',
    'track_package': 'map_tracking_001',
    'view_invoice': 'print_an_invoice_001'
}

# New mappings for the split intents
new_mapping = {
    'track_refund_status': 'amz_track_002',
    'refund_processing': 'amz_ref_001'
}

# Combine mappings
mapping = {**old_mapping, **new_mapping}

records = []
for item in intents:
    intent_name = item["intent"]
    chunk_id = mapping.get(intent_name)
    if not chunk_id:
        if item.get("source_chunks"):
            chunk_id = item["source_chunks"][0]
        else:
            chunk_id = "unknown"
        print(f"Warning: No mapping found for intent '{intent_name}'. Using fallback: '{chunk_id}'")
        
    queries = item.get("sample_queries", [])
    for q in queries:
        records.append({
            "query": q.strip(),
            "reference_chunk_id": chunk_id,
            "intent_label": intent_name
        })

df_new = pd.DataFrame(records)
df_new.to_csv("data/retriever_evaluation_queries.csv", index=False)
print(f"Successfully generated and saved {len(df_new)} queries to data/retriever_evaluation_queries.csv")
