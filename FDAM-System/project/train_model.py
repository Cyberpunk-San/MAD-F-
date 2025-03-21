import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

# Load dataset
file_path = "transactions_train.csv"  # Ensure this file is in the backend directory
if not os.path.exists(file_path):
    raise FileNotFoundError(f"The file {file_path} does not exist.")

df = pd.read_csv(file_path)

# Convert 'transaction_date' to datetime and extract useful time features
df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")  # Fix invalid dates
df["transaction_hour"] = df["transaction_date"].dt.hour  # Extract hour of transaction

# Drop irrelevant and non-numeric columns
df = df.drop(["transaction_id_anonymous", "payee_id_anonymous", "payer_email_anonymous", 
              "payee_ip_anonymous", "transaction_date"], axis=1)

# Handle missing values
df["transaction_amount"] = df["transaction_amount"].fillna(df["transaction_amount"].median())

# Encode categorical columns
label_enc = LabelEncoder()
df["transaction_channel"] = label_enc.fit_transform(df["transaction_channel"])

# Define features (X) and target variable (y)
X = df.drop(["is_fraud"], axis=1)
y = df["is_fraud"]

# Ensure all columns in X are numeric
for col in X.columns:
    if X[col].dtype == "object":
        try:
            X[col] = pd.to_numeric(X[col], errors="raise")
        except ValueError:
            # If conversion fails, encode the column
            X[col] = LabelEncoder().fit_transform(X[col])

# Split dataset into training & test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale numerical features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train a Random Forest classifier
model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))

# Save trained model and preprocessing objects
joblib.dump(model, "fraud_model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(label_enc, "label_encoder.pkl")

print("✅ Model saved as fraud_model.pkl")