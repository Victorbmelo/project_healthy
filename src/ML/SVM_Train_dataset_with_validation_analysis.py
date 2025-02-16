#############https://www.kaggle.com/datasets/s3programmer/disease-diagnosis-dataset
########The above address is the address through which the dataset is downloaded
##This code gives me a model using Suport Vactor Machine(SVM), I save the output in pkl format and use in "Project_ML_analysis"
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score
import joblib

class SVMHealthPredictor:
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

        # Train model using only training data
        self.model_health = SVC(probability=True, random_state=42)
        self.model_severity = SVC(probability=True, random_state=42)

        self.model_health.fit(X_train, y_health_train)
        self.model_severity.fit(X_train_s, y_severity_train)

        # Perform hyperparameter tuning on validation set
        param_grid_svm = {
            'C': [0.1, 5, 10],
            'kernel': ['linear', 'rbf']
        }

        grid_search_health_svm = GridSearchCV(SVC(probability=True, random_state=42), param_grid_svm, cv=3, scoring='accuracy')
        grid_search_health_svm.fit(X_val, y_health_val)

        grid_search_severity_svm = GridSearchCV(SVC(probability=True, random_state=42), param_grid_svm, cv=3, scoring='accuracy')
        grid_search_severity_svm.fit(X_val_s, y_severity_val)

        # Get best models from validation tuning
        self.model_health = grid_search_health_svm.best_estimator_
        self.model_severity = grid_search_severity_svm.best_estimator_

        # Get best parameters
        best_params_health = grid_search_health_svm.best_params_
        best_params_severity = grid_search_severity_svm.best_params_

        print("Best Parameters (SVM - Health Diagnosis):", best_params_health)
        print("Best Parameters (SVM - Severity Diagnosis):", best_params_severity)

        # Evaluate on test set using best parameters
        ## accuracy_score compute the percentage of correctly predicted labels compared to the total number of samples in the test set.
        y_health_test_pred_svm = self.model_health.predict(X_test)
        test_health_accuracy_svm = accuracy_score(y_health_test, y_health_test_pred_svm)

        y_severity_test_pred_svm = self.model_severity.predict(X_test_s)
        test_severity_accuracy_svm = accuracy_score(y_severity_test, y_severity_test_pred_svm)

        print("Test Accuracy (SVM - Health Diagnosis using Best Parameters):", test_health_accuracy_svm)
        print("Test Accuracy (SVM - Severity Diagnosis using Best Parameters):", test_severity_accuracy_svm)

        # Save models in the same directory as the training file
        #These models will be used later in the main code
        model_dir = os.path.dirname(self.training_file)
        health_model_path = os.path.join(model_dir, "model_health_svm.pkl")
        severity_model_path = os.path.join(model_dir, "model_severity_svm.pkl")

        joblib.dump(self.model_health, health_model_path)
        joblib.dump(self.model_severity, severity_model_path)

        print(f"Health model saved at: {health_model_path}")
        print(f"Severity model saved at: {severity_model_path}")

        # Plot test accuracy
        labels = ['Test-Health', 'Test-Severity']
        accuracies = [test_health_accuracy_svm, test_severity_accuracy_svm]

        plt.bar(labels, accuracies, color=['blue', 'orange'])
        plt.ylabel('Accuracy')
        plt.title('SVM Model Accuracy on Test Dataset')
        plt.ylim(0, 1)
        plt.show()


#Use this dataset to train model 
training_file = "D:/IOT_september_2024/project_healthy/src/ML/disease_diagnosis.csv"
predictor = SVMHealthPredictor(training_file)
predictor.preprocess_training_data()
