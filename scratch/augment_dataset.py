import pandas as pd

new_queries = [
    # modify_order (4 queries needed)
    ("I placed the order an hour ago but clicked the wrong color, is there any way I can swap it before it leaves the warehouse?", "amz_ord_merged", "modify_order"),
    ("Wait, my credit card was already charged for an item I just clicked cancel on. What happens next?", "amz_can_merged", "modify_order"),
    ("I need to replace my broken headphones under the warranty, but the return window closed last week.", "amz_rep_merged", "modify_order"),
    ("Can I change the delivery speed from standard to expedited on an order that's still pending?", "amz_ord_merged", "modify_order"),

    # modify_address (9 queries needed)
    ("I just moved and my Subscribe & Save orders are still going to the old apartment, how do I redirect all future shipments?", "billing_shipping_merged", "modify_address"),
    ("My company changed its billing address, but I want my packages to still come to my personal house. Where do I separate these?", "billing_shipping_merged", "modify_address"),
    ("Is there a way to permanently delete an ex-roommate's address from my drop-down list at checkout?", "billing_shipping_merged", "modify_address"),
    ("How do I update my default delivery location to my office address for weekday deliveries?", "billing_shipping_merged", "modify_address"),
    ("My credit card keeps getting declined because I forgot to update my billing zip code after moving.", "billing_shipping_merged", "modify_address"),
    ("I accidentally entered the wrong apartment number, can I fix the address before the courier gets here?", "billing_shipping_merged", "modify_address"),
    ("Where do I go to edit the shipping address for a gift I'm sending to my sister?", "billing_shipping_merged", "modify_address"),
    ("Can I have multiple default shipping addresses depending on which profile is buying something?", "billing_shipping_merged", "modify_address"),
    ("The post office says my street address is invalid, how do I edit it to match the standard format?", "billing_shipping_merged", "modify_address"),

    # close_account (9 queries needed)
    ("If I permanently delete my profile, do I instantly lose access to all the Kindle books I purchased over the years?", "what_happens_close_account_merged", "close_account"),
    ("I'm trying to close my late husband's account, but it says he has an active AWS balance. What do I do?", "amz_acc_merged", "close_account"),
    ("How do I shut down my account completely and wipe all my saved credit cards from the system?", "what_happens_close_account_merged", "close_account"),
    ("If I close my account, will my Alexa smart speakers stop working immediately?", "what_happens_close_account_merged", "close_account"),
    ("Can I temporarily deactivate my shopping account instead of deleting it permanently?", "what_happens_close_account_merged", "close_account"),
    ("I want to terminate my account because of privacy concerns, how do I initiate the deletion process?", "what_happens_close_account_merged", "close_account"),
    ("Will I still receive a refund for a returned item if I close my account today?", "what_happens_close_account_merged", "close_account"),
    ("How long does it take for my account data to be completely erased after I request closure?", "what_happens_close_account_merged", "close_account"),
    ("I have an outstanding Prime membership fee, can I still close my account without paying it?", "amz_acc_merged", "close_account"),

    # reset_password (9 queries needed)
    ("I got a new phone number so I can't receive the two-step verification text to reset my forgotten password.", "why_cant_i_sign_into_my_account_001", "reset_password"),
    ("My account is locked and every time I click 'Forgot Password' it sends an email to an inbox I can't access.", "why_cant_i_sign_into_my_account_001", "reset_password"),
    ("I keep entering my password correctly but it says 'suspicious activity detected' and forces me to reset.", "why_cant_i_sign_into_my_account_001", "reset_password"),
    ("How do I change my login password if I only use the mobile app and don't own a computer?", "why_cant_i_sign_into_my_account_001", "reset_password"),
    ("Is there a way to force a password reset on all devices that are currently logged into my account?", "why_cant_i_sign_into_my_account_001", "reset_password"),
    ("I received a password reset link but it expired before I could click it, what do I do now?", "why_cant_i_sign_into_my_account_001", "reset_password"),
    ("My browser autofilled the wrong password too many times and now I'm locked out, how do I unlock it?", "why_cant_i_sign_into_my_account_001", "reset_password"),
    ("Can customer service manually reset my password over the phone if I answer security questions?", "why_cant_i_sign_into_my_account_001", "reset_password"),
    ("I suspect someone hacked my account, what is the fastest way to change my login credentials?", "why_cant_i_sign_into_my_account_001", "reset_password"),

    # manage_teen_account (9 queries needed)
    ("My daughter just turned 13, can I give her her own login that uses my Prime shipping benefits but requires my approval for purchases?", "what_is_a_teen_login_001", "manage_teen_account"),
    ("How do I set spending limits on the teen profile I created for my son?", "what_is_a_teen_login_001", "manage_teen_account"),
    ("If my teenager buys an M-rated video game using their teen login, will it send a notification to my email first?", "what_is_a_teen_login_001", "manage_teen_account"),
    ("Can I convert a standard adult account into a teen account attached to my household?", "what_is_a_teen_login_001", "manage_teen_account"),
    ("What happens to the teen login and order history when they turn 18? Does it graduate to an adult account?", "what_is_a_teen_login_001", "manage_teen_account"),
    ("I want to share my Prime Video access with my 15-year-old, does the teen login feature support streaming?", "what_is_a_teen_login_001", "manage_teen_account"),
    ("Can a teen account use their own gift card balance without me having to approve every single order?", "what_is_a_teen_login_001", "manage_teen_account"),
    ("How do I completely remove a teenager's profile from my household settings?", "what_is_a_teen_login_001", "manage_teen_account"),
    ("Does the teen login allow them to hide their browsing history from the primary account holder?", "what_is_a_teen_login_001", "manage_teen_account"),

    # convert_currency (6 queries needed)
    ("My credit card doesn't charge foreign transaction fees, so how do I force checkout to charge me in British Pounds instead of Dollars?", "currency_converter_merged", "convert_currency"),
    ("I live in Canada but I'm buying a gift on the US site, will the currency converter give me a better exchange rate than my bank?", "currency_converter_merged", "convert_currency"),
    ("Why is the currency converter option greyed out when I try to pay with an Amazon gift card?", "currency_converter_merged", "convert_currency"),
    ("Does the currency converter automatically apply the exchange rate on the day of delivery or the day I place the order?", "currency_converter_merged", "convert_currency"),
    ("I want to see all prices displayed in Euros while browsing the store, how do I change my default currency?", "currency_converter_merged", "convert_currency"),
    ("If I return an item purchased using the currency converter, will I be refunded at today's exchange rate or the original rate?", "currency_converter_merged", "convert_currency"),

    # report_payment_scam (2 queries needed)
    ("Someone called me claiming to be from Amazon Support asking me to buy gift cards to fix an account suspension. I didn't buy them, but I want to report the phone number.", "report_scam_merged", "report_payment_scam"),
    ("I accidentally gave my credit card info to a fake website that looked exactly like Amazon, what should I do to protect my real account?", "avoiding_payment_scams_001", "report_payment_scam"),
]

df = pd.read_csv(r'c:\Users\Anupam Dasgupta\Desktop\INQSYT\Main_Data\Evaluation\eval_dataset_optimised.csv')
new_df = pd.DataFrame(new_queries, columns=['question', 'reference_chunk_id', 'intent'])

combined_df = pd.concat([df, new_df], ignore_index=True)
combined_df.to_csv(r'c:\Users\Anupam Dasgupta\Desktop\INQSYT\Main_Data\Evaluation\eval_dataset_optimised.csv', index=False)

print(f"Added {len(new_queries)} queries.")
print(f"New dataset size: {len(combined_df)}")
