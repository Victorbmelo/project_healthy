#############https://www.kaggle.com/datasets/s3programmer/disease-diagnosis-dataset
########the above address is the address through which the dataset is downloaded
import numpy as np
import joblib
import requests
import cherrypy
import json
import os
###### The URLs in the code to be able to change easily
thingspeak_URL = "http://localhost:8081"
dashboard_socket = 8082

# Load trained models
# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))


## Here we can decide the model created with Random forest algorithm to be used or SVM algorithm
model_health_path = os.path.join(script_dir, "model_health_rf.pkl")  
model_severity_path = os.path.join(script_dir, "model_severity_rf.pkl")
# Load models
model_health = joblib.load(model_health_path)
model_severity = joblib.load(model_severity_path)

# Generate a single random heart rate (Fixed for this run)
# By changing this heart rate the output of ML analysis will change
fixed_heart_rate = np.random.randint(60, 90)  # Random heart rate between 60 and 100 bpm 
print(f"Simulated Heart Rate (Fixed for this run): {fixed_heart_rate}")

def find_sensor_data(data, sensor_name):
    #This is a Helper function to find sensor data across multiple devices.
    ### Here we may have several devices and the BP or BT can be in any device ID
    sensor_values = []
    for device in data:
        for sensor in device['Sensors']:
            if sensor['Name'] == sensor_name:
                sensor_values.extend(sensor['Values'])
    return sensor_values if sensor_values else None

## Extract the latest values from Thinkspeak JSON response
def extract_latest_values(data):
    body_temp_values = find_sensor_data(data, "body_temperature")
    systolic_bp_values = find_sensor_data(data, "blood_pressure")

    body_temp = float(body_temp_values[-1]['value']) if body_temp_values else None
    systolic_bp = float(systolic_bp_values[-1]['value']) if systolic_bp_values else None

    print(f"Extracted from ThingSpeak: BP={systolic_bp}, Temp={body_temp}")
    return body_temp, systolic_bp

# Get latest blood pressure and body temperature from ThinkSpeak
def get_thingspeak_data(passport_code):
    url = f"{thingspeak_URL}/thingspeak?passport_code={passport_code}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return extract_latest_values(data)
        else:
            print(f"Error: Received status code {response.status_code} from ThingSpeak.")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to connect to ThingSpeak - {e}")
        return None, None

# Predict health status and severity
def predict_health_status_and_severity(body_temp, systolic_bp):
    
    # Prepare the input data
    input_data = np.array([[fixed_heart_rate, body_temp, systolic_bp]])

    try:
        # Predict health status
        health_prediction = model_health.predict(input_data)[0]
        health_status = "Healthy" if health_prediction == 0 else "Unhealthy"

        # Predict severity if unhealthy
        severity_status = "healthy"
        if health_status == "Unhealthy":
            severity_prediction = model_severity.predict(input_data)[0]
            severity_mapping = {0: "Unhealthy_Mild", 1: "Unhealthy_Moderate", 2: "Unhealthy_Severe"}
            health_status = severity_mapping.get(severity_prediction, "unhealthy_unknown")

        #print the values used for machine learning
        print(f"Prediction: HR={fixed_heart_rate}, BP={systolic_bp}, Temp={body_temp}, Status={health_status}")

        return {
            "heartRate": fixed_heart_rate,
            "bloodPressure": systolic_bp,
            "temperature": body_temp,
            "status": health_status
        }
    except Exception as e:
        print(f"Prediction Error: {e}")
        return {"error": "Prediction failed"}

# CherryPy server to connect with the dashboard
class DashboardConnection:
    exposed = True

    def GET(self, *uri, **params):
        print("URI:", uri)
        print(" Params:", params)

        if "passport_code" not in params:
            return json.dumps({"error": "passport_code is required"})

        passport_code = params["passport_code"]
        print(f"Received Passport Code: {passport_code}")

        # Get latest BP and Body Temperature from ThingSpeak
        body_temp , systolic_bp = get_thingspeak_data(passport_code)

        if systolic_bp is None or body_temp is None:
            return json.dumps({"error": "Failed to retrieve data from ThingSpeak"})

        # Run the prediction model
        result = predict_health_status_and_severity(body_temp, systolic_bp)

        # Send the result back to the dashboard
        return json.dumps(result)

if __name__ == "__main__":
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }

    cherrypy.tree.mount(DashboardConnection(), '/', conf)  ## same as the name of the class name
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': dashboard_socket})
    cherrypy.engine.start()
    cherrypy.engine.block()
