from database import db

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    transaction_amount = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False)
    transaction_channel = db.Column(db.String(50), nullable=False)
    is_fraud_predicted = db.Column(db.Boolean, nullable=False)
    fraud_source = db.Column(db.String(50), nullable=False)
    fraud_reason = db.Column(db.String(255), nullable=False)
    fraud_score = db.Column(db.Float, nullable=False)

class FraudReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), nullable=False)
    reporting_entity_id = db.Column(db.String(100), nullable=False)
    fraud_details = db.Column(db.String(500), nullable=False)
    is_fraud_reported = db.Column(db.Boolean, default=True)