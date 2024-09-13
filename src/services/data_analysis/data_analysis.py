import joblib

# Load the model from the file
svm_model = joblib.load('project_healthy/src/services/data_analysis/svm_model.pkl')

# Now you can use svm_model to make predictions
# Example:
new_data = [[130, 39]]  # New sample with blood pressure and body temperature
prediction = svm_model.predict(new_data)
print(f"Prediction: {prediction}")
