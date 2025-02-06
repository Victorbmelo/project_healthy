import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib  # Added for saving the trained models

class HealthPredictor:
    def __init__(self, training_file):
        self.training_file = training_file

        # Initialize models
        self.model_health = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model_severity = RandomForestClassifier(n_estimators=100, random_state=42)

        self.scaler = StandardScaler()

    def preprocess_training_data(self):
        """Load and preprocess real dataset for training"""
        file_path = r"D:\IOT_september_2024\git_project_healthy_main\src\ML\disease_diagnosis.csv"
        df = pd.read_csv(file_path)

        # Extract Systolic Blood Pressure (Upper BP)
        df[['Systolic_BP', 'Diastolic_BP']] = df['Blood_Pressure_mmHg'].str.split('/', expand=True).astype(float)

        # Convert diagnosis to binary classification (0 = Healthy, 1 = Unhealthy)
        df['Diagnosis_Binary'] = df['Diagnosis'].apply(lambda x: 0 if x == 'Healthy' else 1)

        # Convert severity to numerical scale (0 = Mild, 1 = Moderate, 2 = Severe)
        severity_mapping = {"Mild": 0, "Moderate": 1, "Severe": 2}
        df["Severity"] = df["Severity"].map(severity_mapping)

        # Select relevant features (Assuming Heart Rate is included in the dataset)
        df = df[['Heart_Rate_bpm', 'Body_Temperature_C', 'Systolic_BP', 'Severity', 'Diagnosis_Binary']]

        # Drop missing values
        df = df.dropna()

        # Feature & target selection
        X = df[['Heart_Rate_bpm', 'Body_Temperature_C', 'Systolic_BP']]
        y_health = df['Diagnosis_Binary']  # Healthy/Unhealthy
        y_severity = df['Severity']  # Severity (if unhealthy)

        # Split into training & test sets
        X_train, X_test, y_health_train, y_health_test = train_test_split(X, y_health, test_size=0.2, random_state=42)
        _, _, y_severity_train, y_severity_test = train_test_split(X, y_severity, test_size=0.2, random_state=42)

        # Normalize features
        self.scaler.fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train classification models
        self.model_health.fit(X_train_scaled, y_health_train)  # Healthy/Unhealthy model
        self.model_severity.fit(X_train_scaled, y_severity_train)  # Severity model

        # Save the trained models and scaler
        # Save the trained models and scaler to a specific directory
        joblib.dump(self.model_health, r"D:\IOT_september_2024\git_project_healthy_main\src\ML\model_health.pkl")
        joblib.dump(self.model_severity, r"D:\IOT_september_2024\git_project_healthy_main\src\ML\model_severity.pkl")
        joblib.dump(self.scaler, r"D:\IOT_september_2024\git_project_healthy_main\src\ML\scaler.pkl")


        print("✅ Models trained and saved successfully using real dataset!")

# Example Usage
training_file = "/mnt/data/disease_diagnosis.csv"  # Path to real dataset

predictor = HealthPredictor(training_file)
predictor.preprocess_training_data()  # Train the model with real data

print("✅ Model is ready to use for ThinkSpeak live data predictions!")
