import pandas as pd

input_file = r'c:\Users\Anupam Dasgupta\Desktop\INQSYT\Main_Data\Evaluation\eval_dataset.csv'
output_file = r'c:\Users\Anupam Dasgupta\Desktop\INQSYT\Main_Data\Evaluation\eval_dataset_optimised.csv'

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

df = pd.read_csv(input_file)
original_len = len(df)

# Filter out deleted chunks
df = df[~df['reference_chunk_id'].isin(deletions)]
deleted_count = original_len - len(df)

# Map merged chunks
mapped_count = df['reference_chunk_id'].isin(merge_map.keys()).sum()
df['reference_chunk_id'] = df['reference_chunk_id'].apply(lambda x: merge_map.get(x, x))

# Save
df.to_csv(output_file, index=False)

print(f"Eval dataset optimized!")
print(f"Original records: {original_len}")
print(f"Deleted records (pointing to placeholder chunks): {deleted_count}")
print(f"Remapped records (pointing to merged chunks): {mapped_count}")
print(f"Final records: {len(df)}")
print(f"Saved to: {output_file}")
