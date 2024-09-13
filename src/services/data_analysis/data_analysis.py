import joblib
import requests
import json
import paho.mqtt.client as mqtt

# Load the trained model
svm_model = joblib.load('svm_model.pkl')

# ThingSpeak API parameters
API_KEY = 'YOUR_API_KEY'
CHANNEL_ID = 'YOUR_CHANNEL_ID'
FIELD_BP = 'FIELD_FOR_BLOOD_PRESSURE'  # Replace with your actual field number for blood pressure
FIELD_BT = 'FIELD_FOR_BODY_TEMPERATURE'  # Replace with your actual field number for body temperature

# MQTT broker information
MQTT_BROKER = 'YOUR_MQTT_BROKER_URL'  # e.g., 'test.mosquitto.org'
MQTT_PORT = 1883
PATIENT_ID = '12345'  # Example patient ID

# Function to publish message to MQTT
def publish_mqtt(topic, message):
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.publish(topic, message)
    client.disconnect()

# Fetch the data from ThingSpeak
url = f'https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={API_KEY}&results=1'
response = requests.get(url)

if response.status_code == 200:
    data = json.loads(response.text)
    
    # Extract the latest blood pressure and body temperature
    feeds = data['feeds'][0]
    blood_pressure = float(feeds[f'field{FIELD_BP}'])  # Extract field for blood pressure
    body_temperature = float(feeds[f'field{FIELD_BT}'])  # Extract field for body temperature
    
    # Prepare the new data for prediction
    new_data = [[blood_pressure, body_temperature]]
    
    # Make a prediction using the trained SVM model
    prediction = svm_model.predict(new_data)
    
    # Define MQTT topic
    mqtt_topic = f"alarm/patient/{PATIENT_ID}"
    
    # Send the dangerous status via MQTT
    if prediction == 1:
        message = f"Dangerous situation detected for patient {PATIENT_ID} (BP: {blood_pressure}, Temp: {body_temperature})"
        publish_mqtt(mqtt_topic, message)
        print("MQTT message sent:", message)
    else:
        message = f"Safe situation for patient {PATIENT_ID} (BP: {blood_pressure}, Temp: {body_temperature})"
        publish_mqtt(mqtt_topic, message)
        print("MQTT message sent:", message)
else:
    print(f"Failed to fetch data from ThingSpeak. Status Code: {response.status_code}")

## we shoudl get the alarm from broker