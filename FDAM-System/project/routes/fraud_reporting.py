from flask import Flask, request, jsonify, Blueprint
import joblib
import numpy as np
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor
from models import db, Transaction, FraudReport
import rule_engine

# Create a Blueprint for fraud reporting
fraud_reporting_bp = Blueprint('fraud_reporting', __name__)

# Load the trained fraud detection model
fraud_model = joblib.load('fraud_model.pkl')

# Rule Engine Implementation
def apply_rules(data):
    fraud_reasons = []
    if data['transaction_amount'] > 10000:
        fraud_reasons.append("High transaction amount")
    if data['transaction_channel'] not in ['online', 'bank_transfer', 'POS']:
        fraud_reasons.append("Unknown transaction channel")
    is_fraud = len(fraud_reasons) > 0
    return {"is_fraud": is_fraud, "reason": ", ".join(fraud_reasons) if is_fraud else "No rule-based fraud detected"}

# Define the route within the Blueprint
@fraud_reporting_bp.route('/report-fraud', methods=['POST'])
def report_fraud():
    data = request.json
    
    # Check if transaction exists
    transaction = Transaction.query.filter_by(transaction_id=data['transaction_id']).first()
    if not transaction:
        return jsonify({"transaction_id": data['transaction_id'], "reporting_acknowledged": False, "failure_code": 404}), 404
    
    # Store fraud report in database
    fraud_report = FraudReport(
        transaction_id=data['transaction_id'],
        reporting_entity_id=data['reporting_entity_id'],
        fraud_details=data['fraud_details']
    )
    db.session.add(fraud_report)
    db.session.commit()
    
    return jsonify({"transaction_id": data['transaction_id'], "reporting_acknowledged": True, "failure_code": 0})

# Optional: If you want to run this file independently for testing
if __name__ == '__main__':
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transactions.db'
    db.init_app(app)
    app.register_blueprint(fraud_reporting_bp, url_prefix="/api")
    app.run(debug=True)