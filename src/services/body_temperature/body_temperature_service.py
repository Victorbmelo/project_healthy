import datetime
import json
import os
import requests
from src.mqtt.mqtt_handler import MqttHandler

DB_CONNECTOR_URL = os.getenv("DB_CONNECTOR_URL", "http://localhost:8080")


class BodyTemperatureService:
    MQTT_TOPIC = '+/body_temp_check/+/+'


    def __init__(self):
        pass

    def on_message(self, client, userdata, msg):
        rcvd_topic = msg.topic
        patient_id, service_name, device_id, entity_id = rcvd_topic.lstrip('/').split('/')
        send_topic = f"{patient_id}/alert"
        payload = json.loads(msg.payload.decode())
        print(f"[BodyTemperatureService] Received: {payload} on {rcvd_topic}")

        if isinstance(payload, int):
            temperature = payload
        else:
            try:
                temperature = int(payload)
            except:
                return
        timestamp_now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
        request_payload = {
            'last_reading': str(temperature),
            'last_reading_timestamp': timestamp_now
        }
        r = requests.put(f"{DB_CONNECTOR_URL}/entity?entity_id={entity_id}", json=request_payload)
        print(f"[BodyTemperatureService] PUT Request entity_id: {entity_id}, response: {r}")

        data = {
            "patient_id": int(patient_id),
            "entity_id": int(entity_id),
            "value": temperature,
            "timestamp": timestamp_now,
            "message": None
        }

        if temperature > 39.5:
            alert_str = f"Warning! High fever detected, {temperature} degrees!"
            data["message"] = alert_str
            print("[BodyTemperatureService] " + alert_str)
            client.publish(send_topic, json.dumps(data))
        elif temperature > 37.0:
            alert_str = f"Warning! Fever detected, {temperature} degrees!"
            data["message"] = alert_str
            print("[BodyTemperatureService] " + alert_str)
            client.publish(send_topic, json.dumps(data))

    def start(self):
        mqtt = MqttHandler(client_id='body-temperature-service')
        mqtt._client.on_message = self.on_message
        mqtt.connect()
        mqtt.subscribe(self.MQTT_TOPIC)
        print(f"[BodyTemperatureService] Body Temperature Service started and subscribed to {self.MQTT_TOPIC}")
        try:
            pass
        except KeyboardInterrupt:
            mqtt.close()
            print("[BodyTemperatureService] Body Temperature Service stopped.")
