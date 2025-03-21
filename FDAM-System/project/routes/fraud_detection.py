from flask import Blueprint, request, jsonify
import rule_engine  # ✅ Import the module, NOT the function directly
import joblib
import numpy as np
import pandas as pd
import time
from models import db, Transaction

# Create Blueprint
fraud_detection_bp = Blueprint("fraud_detection", __name__)

# Load the trained fraud detection model
fraud_model = joblib.load("fraud_model.pkl")

# Function to process a single transaction
def process_transaction(data):
    rule_result = apply_rules(data)
    
    if rule_result["is_fraud"]:
        fraud_source = "rule"
        fraud_reason = rule_result["reason"]
        fraud_score = 1.0
    else:
        features = [data["transaction_amount"],
                    data["transaction_payment_mode_anonymous"],
                    data["payment_gateway_bank_anonymous"],
                    data["payer_browser_anonymous"]]
        features = np.array(features).reshape(1, -1)
        fraud_score = fraud_model.predict_proba(features)[0][1]  # Probability score
        is_fraud = fraud_score > 0.7  # Threshold
        fraud_source = "model"
        fraud_reason = "AI-based prediction"

    # Store transaction in the database
    transaction = Transaction(
        transaction_id=data["transaction_id_anonymous"],
        transaction_amount=data["transaction_amount"],
        transaction_date=pd.to_datetime(data["transaction_date"]),
        transaction_channel=data["transaction_channel"],
        is_fraud_predicted=is_fraud,
        fraud_source=fraud_source,
        fraud_reason=fraud_reason,
        fraud_score=fraud_score
    )
    db.session.add(transaction)
    db.session.commit()

    return {
        "transaction_id": data["transaction_id_anonymous"],
        "is_fraud": is_fraud,
        "fraud_source": fraud_source,
        "fraud_reason": fraud_reason,
        "fraud_score": fraud_score
    }

# Real-time Fraud Detection API
@fraud_detection_bp.route("/fraud-detection", methods=["POST"])
def detect_fraud():
    start_time = time.time()
    data = request.json

    result = process_transaction(data)

    response_time = (time.time() - start_time) * 1000  # Convert to ms
    print(f"API Response Time: {response_time:.2f} ms")

    return jsonify(result)

# Batch Fraud Detection API
@fraud_detection_bp.route("/batch-fraud-detection", methods=["POST"])
def batch_fraud_detection():
    start_time = time.time()
    transactions = request.json.get("transactions", [])

    results = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_transaction, tx): tx for tx in transactions}
        for future in futures:
            result = future.result()
            results[result["transaction_id"]] = {
                "is_fraud": result["is_fraud"],
                "fraud_reason": result["fraud_reason"],
                "fraud_score": result["fraud_score"]
            }

    response_time = (time.time() - start_time) * 1000
    print(f"Batch API Response Time: {response_time:.2f} ms")

    return jsonify(results)

from flask import Blueprint, request, jsonify
import joblib
import numpy as np
import pandas as pd
import time
from models import db, Transaction
import rule_engine

# Create Blueprint
fraud_detection_bp = Blueprint("fraud_detection", __name__)

# Load trained model, scaler, and encoder
fraud_model = joblib.load("fraud_model.pkl")
scaler = joblib.load("scaler.pkl")
label_enc = joblib.load("label_encoder.pkl")

# Function to preprocess transaction data
def preprocess_transaction(data):
    """Prepares transaction data for ML model."""
    # Convert categorical values using label encoder
    data["transaction_channel"] = label_enc.transform([data["transaction_channel"]])[0]

    # Prepare feature array (ensure it matches training format)
    features = np.array([
        data["transaction_amount"],
        data["transaction_channel"],
        data["transaction_payment_mode_anonymous"],
        data["payment_gateway_bank_anonymous"],
        data["payer_browser_anonymous"]
    ]).reshape(1, -1)

    # Apply feature scaling
    return scaler.transform(features)

# Function to process a single transaction
def process_transaction(data):
    rule_result = apply_rules(data)
    
    if rule_result["is_fraud"]:
        fraud_source = "rule"
        fraud_reason = rule_result["reason"]
        fraud_score = 1.0
    else:
        # Preprocess transaction and predict fraud probability
        processed_features = preprocess_transaction(data)
        fraud_score = fraud_model.predict_proba(processed_features)[0][1]
        is_fraud = fraud_score > 0.7  # Threshold
        fraud_source = "model"
        fraud_reason = "AI-based prediction"

    # Store transaction in database
    transaction = Transaction(
        transaction_id=data["transaction_id_anonymous"],
        transaction_amount=data["transaction_amount"],
        transaction_date=pd.to_datetime(data["transaction_date"]),
        transaction_channel=data["transaction_channel"],
        is_fraud_predicted=is_fraud,
        fraud_source=fraud_source,
        fraud_reason=fraud_reason,
        fraud_score=fraud_score
    )
    db.session.add(transaction)
    db.session.commit()

    return {
        "transaction_id": data["transaction_id_anonymous"],
        "is_fraud": is_fraud,
        "fraud_source": fraud_source,
        "fraud_reason": fraud_reason,
        "fraud_score": fraud_score
    }

# Real-time Fraud Detection API
@fraud_detection_bp.route("/fraud-detection", methods=["POST"])
def detect_fraud():
    start_time = time.time()
    data = request.json

    result = process_transaction(data)

    response_time = (time.time() - start_time) * 1000  # Convert to ms
    print(f"API Response Time: {response_time:.2f} ms")

    return jsonify(result)

