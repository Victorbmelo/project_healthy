### This code is a simple code to test the prediction for one single values of Blood pressure and Body temperature
###By this code I was comparing the results shown on dashboard and the output of this code
import numpy as np
import joblib
import os

# Load trained models
# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full paths to the model files
## Here we can decide the model created with Random forest algorithm to be used or SVM algorithm
model_health_path = os.path.join(script_dir, "model_health_rf.pkl")  
model_severity_path = os.path.join(script_dir, "model_severity_rf.pkl")
# Load models
model_health = joblib.load(model_health_path)
model_severity = joblib.load(model_severity_path)

# Simulate heart rate
def simulate_heart_rate():
    return np.random.randint(65, 66)  # Simulate heart rate between 60 and 100 bpm


# Predict health status and severity
def predict_health_status_and_severity(body_temp, systolic_bp):
    # Simulate heart rate
    heart_rate = simulate_heart_rate()



    # Prepare the input data
    input_data = np.array([[heart_rate, body_temp, systolic_bp]])  # No scaling required

    # Predict health status
    health_prediction = model_health.predict(input_data)[0]
    health_status = "Healthy" if health_prediction == 0 else "Unhealthy"

    # Predict severity if unhealthy
    severity = "N/A"
    if health_status == "Unhealthy":
        severity_prediction = model_severity.predict(input_data)[0]
        severity_mapping = {0: "Mild", 1: "Moderate", 2: "Severe"}
        severity = severity_mapping.get(severity_prediction, "Unknown")

    return {
        "Heart Rate (bpm)": heart_rate,
        "Systolic BP (mmHg)": systolic_bp,  # Original input for reference
        "Body Temperature (C)": body_temp,
        "Health Status": health_status,
        "Severity": severity
    }

# Single Values for measurements
systolic_bp = 144  #  systolic blood pressure
body_temp = 36.18  #  body temperature

result = predict_health_status_and_severity(body_temp, systolic_bp)

# Print the latest result
print("Latest Health Prediction Result:", result)

# Display health status
if result['Health Status'] == "Healthy":
    print("✅ You are Healthy!")
else:
    print(f"⚠️ You are Unhealthy. Severity: {result['Severity']}")
