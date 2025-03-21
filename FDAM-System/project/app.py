from flask import Flask, render_template
from database import db
from models import Transaction, FraudReport
from routes.fraud_detection import fraud_detection_bp
from routes.fraud_reporting import fraud_reporting_bp

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transactions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Register Blueprints
app.register_blueprint(fraud_detection_bp, url_prefix="/api")
app.register_blueprint(fraud_reporting_bp, url_prefix="/api")

# Serve Frontend Pages
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/fraud_detection")
def fraud_detection():
    return render_template("fraud_detection.html")

@app.route("/fraud_reporting")
def fraud_reporting():
    return render_template("fraud_reporting.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables exist
    app.run(debug=True)
