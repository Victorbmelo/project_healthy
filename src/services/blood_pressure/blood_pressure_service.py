import json
from src.mqtt.mqtt_handler import MqttHandler

class BloodPressureService:
    MQTT_TOPIC = '/+/bloodpressure/+/+/+'

    def __init__(self):
        pass

    def on_message(self, client, userdata, msg):
        rcvd_topic = msg.topic
        send_topic = f"{rcvd_topic}/alert"
        payload = json.loads(msg.payload.decode())
        print(f"Received: {payload} on {rcvd_topic}")
        data = {'data': payload, 'alert_message': ""}

        if 'bloodPressure' in payload:
            blood_pressure = payload['bloodPressure']
            if blood_pressure > 140 or blood_pressure < 60:
                alert_str = "Abnormal blood pressure detected! Sending alert..."
                data["alert_message"] = alert_str
                print(alert_str)
                client.publish(send_topic, json.dumps(data))

    def start(self):
        mqtt = MqttHandler(client_id='blood-pressure-service')
        mqtt._client.on_message = self.on_message
        mqtt.connect()
        mqtt.subscribe(self.MQTT_TOPIC)
        print(f"Blood Pressure Service started and subscribed to {self.MQTT_TOPIC}")
        try:
            pass
        except KeyboardInterrupt:
            mqtt.close()
            print("Blood Pressure Service stopped.")
