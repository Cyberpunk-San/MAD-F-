# rule_engine.py

import datetime

previous_transactions = {}

def apply_rules(data):
    """Applies multiple rule-based fraud checks on transactions."""
    fraud_reasons = []

    if "transaction_amount" in data and data["transaction_amount"] > 10000:
        fraud_reasons.append("High transaction amount")
    elif "transaction_amount" in data and data["transaction_amount"] < 1:
        fraud_reasons.append("Suspiciously low transaction amount")

    valid_channels = ["online", "bank_transfer", "POS"]
    if "transaction_channel" in data and data["transaction_channel"] not in valid_channels:
        fraud_reasons.append("Unknown transaction channel")

    if "transaction_date" in data:
        transaction_time = datetime.datetime.strptime(data["transaction_date"], "%Y-%m-%d %H:%M:%S")
        payer_id = data.get("payer_email_anonymous", "unknown_payer")
        if payer_id in previous_transactions:
            last_time = previous_transactions[payer_id]
            time_diff = (transaction_time - last_time).total_seconds()
            if time_diff < 10:
                fraud_reasons.append("Multiple rapid transactions detected")
        previous_transactions[payer_id] = transaction_time

    if "payee_ip_anonymous" in data and "payer_email_anonymous" in data:
        if data["payee_ip_anonymous"][:5] != data["payer_email_anonymous"][:5]:
            fraud_reasons.append("Payee and payer IPs are from different regions")

    if "transaction_payment_mode_anonymous" in data and data["transaction_payment_mode_anonymous"] > 20:
        fraud_reasons.append("New or uncommon payment method used")

    if "failed_attempts" in data and data["failed_attempts"] > 3:
        fraud_reasons.append("Multiple failed attempts before success")

    risky_gateways = {5, 12, 18}
    if "payment_gateway_bank_anonymous" in data and data["payment_gateway_bank_anonymous"] in risky_gateways:
        fraud_reasons.append("High-risk payment gateway used")

    is_fraud = len(fraud_reasons) > 0

    return {
        "is_fraud": is_fraud,
        "reason": ", ".join(fraud_reasons) if is_fraud else "No rule-based fraud detected"
    }

