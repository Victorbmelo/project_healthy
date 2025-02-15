#############https://www.kaggle.com/datasets/s3programmer/disease-diagnosis-dataset
########The above address is the address through which the dataset is downloaded
##This code gives me a model using random Forest, I save the output in pkl format and use in "Project_ML_analysis"
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score
import joblib

class RFHealthPredictor:
    def __init__(self, training_file):
        self.training_file = training_file
        self.model_health = None
        self.model_severity = None
    
    def preprocess_training_data(self):
        # Load dataset
        df = pd.read_csv(self.training_file)

        # Split blood pressure into Systolic and Diastolic
        df[['Systolic_BP', 'Diastolic_BP']] = df['Blood_Pressure_mmHg'].str.split('/', expand=True).astype(float)

        # Convert categorical labels to numerical
        df['Diagnosis_Binary'] = df['Diagnosis'].apply(lambda x: 0 if x == 'Healthy' else 1)
        severity_mapping = {"Mild": 0, "Moderate": 1, "Severe": 2}
        df["Severity"] = df["Severity"].map(severity_mapping)

        # Select relevant features
        df = df[['Heart_Rate_bpm', 'Body_Temperature_C', 'Systolic_BP', 'Severity', 'Diagnosis_Binary']].dropna()

        # Define feature matrix and labels
        X = df[['Heart_Rate_bpm', 'Body_Temperature_C', 'Systolic_BP']]
        y_health = df['Diagnosis_Binary']
        y_severity = df['Severity']

        # Split into Train (60%), Validation (20%), and Test (20%)
        X_train, X_temp, y_health_train, y_temp_health = train_test_split(X, y_health, test_size=0.4, random_state=42)
        X_val, X_test, y_health_val, y_health_test = train_test_split(X_temp, y_temp_health, test_size=0.5, random_state=42)

        X_train_s, X_temp_s, y_severity_train, y_temp_severity = train_test_split(X, y_severity, test_size=0.4, random_state=42)
        X_val_s, X_test_s, y_severity_val, y_severity_test = train_test_split(X_temp_s, y_temp_severity, test_size=0.5, random_state=42)

        # Train initial Random Forest model
        self.model_health = RandomForestClassifier(random_state=42)
        self.model_severity = RandomForestClassifier(random_state=42)

        self.model_health.fit(X_train, y_health_train)
        self.model_severity.fit(X_train_s, y_severity_train)

        # Perform hyperparameter tuning on validation set
        param_grid_rf = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20],
            'min_samples_split': [2, 5, 10]
        }

        grid_search_health_rf = GridSearchCV(RandomForestClassifier(random_state=42), param_grid_rf, cv=3, scoring='accuracy')
        grid_search_health_rf.fit(X_val, y_health_val)

        grid_search_severity_rf = GridSearchCV(RandomForestClassifier(random_state=42), param_grid_rf, cv=3, scoring='accuracy')
        grid_search_severity_rf.fit(X_val_s, y_severity_val)

        # Get best models from validation tuning
        self.model_health = grid_search_health_rf.best_estimator_
        self.model_severity = grid_search_severity_rf.best_estimator_

        # Get best parameters
        best_params_health = grid_search_health_rf.best_params_
        best_params_severity = grid_search_severity_rf.best_params_

        print("Best Parameters (RF - Health Diagnosis):", best_params_health)
        print("Best Parameters (RF - Severity Diagnosis):", best_params_severity)

        # Evaluate on test set using best parameters
        y_health_test_pred_rf = self.model_health.predict(X_test)
        test_health_accuracy_rf = accuracy_score(y_health_test, y_health_test_pred_rf)

        y_severity_test_pred_rf = self.model_severity.predict(X_test_s)
        test_severity_accuracy_rf = accuracy_score(y_severity_test, y_severity_test_pred_rf)

        print("Test Accuracy (RF - Health Diagnosis using Best Parameters):", test_health_accuracy_rf)
        print("Test Accuracy (RF - Severity Diagnosis using Best Parameters):", test_severity_accuracy_rf)

        # Save models in the same directory as the training file
        ###These models will be used later in the main code
        model_dir = os.path.dirname(self.training_file)
        health_model_path = os.path.join(model_dir, "model_health_rf.pkl")
        severity_model_path = os.path.join(model_dir, "model_severity_rf.pkl")

        joblib.dump(self.model_health, health_model_path)
        joblib.dump(self.model_severity, severity_model_path)

        print(f"Health model saved at: {health_model_path}")
        print(f"Severity model saved at: {severity_model_path}")

        # Plot test accuracy
        labels = ['Test-Health', 'Test-Severity']
        accuracies = [test_health_accuracy_rf, test_severity_accuracy_rf]

        plt.bar(labels, accuracies, color=['green', 'red'])
        plt.ylabel('Accuracy')
        plt.title('Random Forest Model Accuracy on Test Dataset')
        plt.ylim(0, 1)
        plt.show()


training_file = "D:/IOT_september_2024/project_healthy/src/ML/disease_diagnosis.csv"
predictor = RFHealthPredictor(training_file)
predictor.preprocess_training_data()
