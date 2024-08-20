import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
 # read data of patient's health
 
data = pd.read_csv('patient_data.csv')

#'Temperature', 'BloodPressure'
X = data[['Temperature', 'BloodPressure']]
y = data['Condition'] 

#Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#
# Train the linear regression model
model = LinearRegression()
model.fit(X_train, y_train)

#Make predictions
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")

# predict future conditions
new_data = np.array([[36.5, 120]]) 
predicted_condition = model.predict(new_data)