import datetime
import json
import os
import requests
from src.mqtt.mqtt_handler import MqttHandler

DB_CONNECTOR_URL = os.getenv("DB_CONNECTOR_URL", "http://localhost:8080")


class BloodPressureService:
    MQTT_TOPIC = '+/blood_pressure/+/+'

    def __init__(self):
        pass

    def on_message(self, client, userdata, msg):
        rcvd_topic = msg.topic
        patient_id, service_name, device_id, entity_id = rcvd_topic.lstrip('/').split('/')
        send_topic = f"{patient_id}/alert"
        payload = json.loads(msg.payload.decode())
        print(f"[BloodPressureService] Received: {payload} on {rcvd_topic}")

        if isinstance(payload, int):
            blood_pressure = payload
        else:
            try:
                blood_pressure = int(payload)
            except:
                return
        timestamp_now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
        request_payload = {
            'last_reading': str(blood_pressure),
            'last_reading_timestamp': timestamp_now
        }
        r = requests.put(f"{DB_CONNECTOR_URL}/entity?entity_id={entity_id}", json=request_payload)
        print(f"[BloodPressureService] PUT Request entity_id: {entity_id}, response: {r}")

        data = {
            "patient_id": int(patient_id),
            "entity_id": int(entity_id),
            "value": blood_pressure,
            "timestamp": timestamp_now,
            "message": None
        }
        if blood_pressure > 140 or blood_pressure < 60:
            alert_str = "Abnormal blood pressure detected! Sending alert..."
            data["message"] = alert_str
            print("[BloodPressureService] " + alert_str)
            client.publish(send_topic, json.dumps(data))

    def start(self):
        mqtt = MqttHandler(client_id='blood-pressure-service')
        mqtt._client.on_message = self.on_message
        mqtt.connect()
        mqtt.subscribe(self.MQTT_TOPIC)
        print(f"[BloodPressureService] Blood Pressure Service started and subscribed to {self.MQTT_TOPIC}")
        try:
            pass
        except KeyboardInterrupt:
            mqtt.close()
            print("[BloodPressureService] Blood Pressure Service stopped.")
