import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import requests
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error


class HealthPredictor:
 
    def __init__(self, file_path):
        self.file_path = file_path
        self.model_bp = LinearRegression()
        self.model_bt = LinearRegression()
        self.df = None
    #Get Requests 

    

    def train_and_predict(self):
        # Load dataset
        #self.df = pd.read_csv(self.file_path)
       
        # Define the API endpoint
        url = "https://jsonplaceholder.typicode.com/posts/1"  # I need this API address to get data

        # Send a GET request
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            self.df = response.json()  # Convert response to JSON
            print("Response Data:", df)
        else:
            print("Failed to fetch data:", response.status_code)

        # Create past value features
        self.df['prev_blood_pressure'] = self.df['blood_pressure'].shift(1)
        self.df['prev_body_temperature'] = self.df['body_temperature'].shift(1)

        # Drop first row due to NaN values
        self.df = self.df.dropna()

        # Features (X) and target variables (y)
        X = self.df[['prev_blood_pressure', 'prev_body_temperature']]
        y_bp = self.df['blood_pressure']
        y_bt = self.df['body_temperature']

        # Split data
        X_train, X_test, y_bp_train, y_bp_test = train_test_split(X, y_bp, test_size=0.2, random_state=42)
        _, _, y_bt_train, y_bt_test = train_test_split(X, y_bt, test_size=0.2, random_state=42)

        # Train models
        self.model_bp.fit(X_train, y_bp_train)
        self.model_bt.fit(X_train, y_bt_train)

        # Predict on test data
        bp_predictions = self.model_bp.predict(X_test)
        bt_predictions = self.model_bt.predict(X_test)

        # Evaluation metrics
        print("Blood Pressure Prediction:")
        print(f"MAE: {mean_absolute_error(y_bp_test, bp_predictions)}")
        print(f"MSE: {mean_squared_error(y_bp_test, bp_predictions)}")

        print("\nBody Temperature Prediction:")
        print(f"MAE: {mean_absolute_error(y_bt_test, bt_predictions)}")
        print(f"MSE: {mean_squared_error(y_bt_test, bt_predictions)}")

        # Predict next value using last known data
        latest_values = self.df.iloc[-1][['blood_pressure', 'body_temperature']].values.reshape(1, -2)
        next_bp = self.model_bp.predict(latest_values)[0]
        next_bt = self.model_bt.predict(latest_values)[0]

        return next_bp, next_bt
    
