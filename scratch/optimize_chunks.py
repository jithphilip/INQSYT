import json
import os

intents_file = r'c:\Users\Anupam Dasgupta\Desktop\INQSYT\Main_Data\Intents\intents_schema.json'
chunks_file = r'c:\Users\Anupam Dasgupta\Desktop\INQSYT\Main_Data\Chunks\Chunks.jsonl'
output_chunks_file = r'c:\Users\Anupam Dasgupta\Desktop\INQSYT\Main_Data\Chunks\chunks_optimised.jsonl'
output_intents_file = r'c:\Users\Anupam Dasgupta\Desktop\INQSYT\Main_Data\Intents\intents_schema_optimised.json'

deletions = {
    'cancel_items_and_orders_001', 'change_your_order_information_001', 'archived_orders_001',
    'add_delete_and_manage_addresses_001', 'manage_an_email_address_already_in_use_error_001',
    'multiple_addresses_001', 'print_an_invoice_001', 'about_security_codes_001',
    'change_your_password_001', 'recover_your_account_after_twostep_verification_fails_001',
    'reset_your_password_001', 'verify_your_email_for_a_new_account_001', 'what_is_twostep_verification_001',
    'approve_a_teens_order_001', 'removing_a_teen_login_from_an_amazon_household_001',
    'set_order_approvals_for_a_teen_login_001', 'add_a_shopping_profile_001',
    'check_your_gift_card_balance_001', 'manage_your_amazon_accounts_on_mobile_devices_001',
    'sign_out_of_your_amazon_account_in_the_amazon_shopping_001',
    'sign_out_of_your_amazon_account_on_the_amazon_website_001', 'use_login_with_amazon_001',
    'use_switch_accounts_001', 'what_are_mobile_phone_number_accounts_001',
    'change_your_account_settings_001', 'change_your_language_preference_001',
    'manage_a_multiple_accounts_use_the_same_email_error_001',
    'manage_thirdparty_apps_and_services_with_data_access_th_001', 'unsubscribe_from_amazon_marketing_001',
    'request_the_closure_of_your_account_and_the_deletion_of_001', 'change_your_default_payment_methods_001',
    'manage_payment_methods_001', 'manage_your_backup_payment_methods_001',
    'select_your_card_currency_for_amazon_currency_converter_001', 'resolve_a_declined_payment_001',
    'identifying_a_scam_001', 'unknown_amazon_payment_charges_009'
}

merges = {
    'amz_can_merged': ['amz_can_001', 'amz_can_002'],
    'amz_ord_merged': ['amz_ord_001', 'amz_ord_002'],
    'amz_rep_merged': ['amz_rep_001', 'amz_rep_002'],
    'billing_shipping_merged': ['billing_shipping_addresses_001', 'billing_shipping_addresses_002'],
    'what_happens_close_account_merged': ['what_happens_when_i_close_my_account_001', 'what_happens_when_i_close_my_account_002', 'what_happens_when_i_close_my_account_003'],
    'currency_converter_merged': ['about_currency_of_preference_on_international_shopping_001', 'amazon_currency_converter_exchange_rates_001', 'amazon_currency_converter_requirements_001'],
    'unknown_charges_merged': [f'unknown_amazon_payment_charges_00{i}' for i in range(1, 9)],
    'report_scam_merged': ['amz_sec_001', 'amz_sec_002', 'amz_sec_003', 'amz_sec_004', 'report_a_scam_001'],
    'scam_trends_merged': [f'scam_trends_00{i}' for i in range(1, 8)],
    'return_windows_merged': ['amz_ret_003', 'amz_ret_004', 'amz_ret_005', 'amz_ret_006', 'amz_ret_007'],
    'non_returnable_merged': ['amz_ret_008', 'amz_ret_009'],
    'packaging_shipment_merged': ['amz_ret_011', 'amz_ret_012'],
    'special_segment_returns_merged': ['amz_seg_001', 'amz_seg_002', 'amz_seg_003'],
    'third_party_returns_merged': ['amz_seg_004', 'amz_seg_005'],
    'fees_deductions_merged': ['amz_fee_001', 'amz_fee_002', 'amz_fee_003', 'amz_fee_004', 'amz_fee_005'],
    'intl_shipping_methods_merged': ['amz_int_001', 'amz_int_002', 'amz_int_003'],
    'special_returns_merged': ['amz_int_005', 'amz_int_006', 'amz_int_007'],
    'amz_acc_merged': ['amz_acc_001', 'amz_acc_002']
}

# Reverse mapping: old_chunk_id -> new_merged_id
merge_map = {}
for merged_id, constituent_ids in merges.items():
    for cid in constituent_ids:
        merge_map[cid] = merged_id

all_chunks = {}
with open(chunks_file, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        all_chunks[data['chunk_id']] = data

final_chunks = {}

# Process merges
for merged_id, constituent_ids in merges.items():
    merged_data = {
        'chunk_id': merged_id,
        'chunk_title': f"Merged: {all_chunks[constituent_ids[0]]['chunk_title']} and others",
        'source_file': all_chunks[constituent_ids[0]]['source_file'],
        'chunk': '',
        'metadata': {
            'chunk_type': 'merged',
            'table_markdown': None,
            'list_markdown': None,
            'sample_queries': [],
            'jargon_synonyms': [],
            'category_path': all_chunks[constituent_ids[0]]['metadata'].get('category_path', '')
        }
    }
    texts = []
    queries = set()
    jargon = set()
    for cid in constituent_ids:
        if cid in all_chunks:
            c = all_chunks[cid]
            texts.append(f"--- {c['chunk_title']} ---\n{c.get('chunk', '')}")
            queries.update(c.get('metadata', {}).get('sample_queries', []))
            jargon.update(c.get('metadata', {}).get('jargon_synonyms', []))
            
    merged_data['chunk'] = '\n\n'.join(texts)
    merged_data['metadata']['sample_queries'] = list(queries)
    merged_data['metadata']['jargon_synonyms'] = list(jargon)
    final_chunks[merged_id] = merged_data

# Process regular chunks
for cid, data in all_chunks.items():
    if cid in deletions:
        continue
    if cid in merge_map:
        continue
    final_chunks[cid] = data

# Write optimised chunks
with open(output_chunks_file, 'w', encoding='utf-8') as f:
    for cid, data in final_chunks.items():
        f.write(json.dumps(data) + '\n')

# Process intents
with open(intents_file, 'r', encoding='utf-8') as f:
    schema = json.load(f)

for intent in schema:
    new_chunks = []
    for cid in intent.get('source_chunks', []):
        if cid in deletions:
            continue
        elif cid in merge_map:
            new_id = merge_map[cid]
            if new_id not in new_chunks:
                new_chunks.append(new_id)
        else:
            new_chunks.append(cid)
            
    # Fix the miscategorized amz_acc chunks
    if intent['intent'] == 'manage_wallet_cards':
        if 'amz_acc_merged' in new_chunks:
            new_chunks.remove('amz_acc_merged')
    elif intent['intent'] == 'close_account':
        if 'amz_acc_merged' not in new_chunks and any('amz_acc' in c for c in intents_file): # Just add it to close_account
            pass # We will do it explicitly below

    intent['source_chunks'] = new_chunks

# Explicitly add amz_acc_merged to close_account if missing
for intent in schema:
    if intent['intent'] == 'close_account':
        if 'amz_acc_merged' not in intent['source_chunks']:
            intent['source_chunks'].append('amz_acc_merged')

with open(output_intents_file, 'w', encoding='utf-8') as f:
    json.dump(schema, f, indent=4)

print("Optimization complete!")
print(f"Original chunks: {len(all_chunks)}")
print(f"Optimised chunks: {len(final_chunks)}")
print(f"Created: {output_chunks_file}")
print(f"Created: {output_intents_file}")
