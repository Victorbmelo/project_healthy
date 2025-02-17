import datetime
import json
import os
import requests

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from src.mqtt.mqtt_handler import MqttHandler

DB_CONNECTOR_URL = os.getenv("DB_CONNECTOR_URL", "http://localhost:8080")
BROKER_MQTT_URL = os.getenv('BROKER_MQTT_URL', "http://localhost")
BROKER_MQTT_PORT = os.getenv('BROKER_MQTT_PORT', 1883)


class AirConditioningService:
    MQTT_TOPIC = '+/air_conditioning/+/+'

    def __init__(self):
        pass

    def on_message(self, client, userdata, msg):
        rcvd_topic = msg.topic
        patient_id, service_name, device_id, entity_id = rcvd_topic.lstrip('/').split('/')
        send_topic = f"{patient_id}/alert"
        payload = json.loads(msg.payload.decode())
        print(f"[AirConditioningService] Received: {payload} on {rcvd_topic}")

        if isinstance(payload, int):
            humidity = payload
        else:
            try:
                humidity = int(payload)
            except:
                return
        timestamp_now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
        request_payload = {
            'last_reading': str(humidity),
            'last_reading_timestamp': timestamp_now
        }
        r = requests.put(f"{DB_CONNECTOR_URL}/entity?entity_id={entity_id}", json=request_payload)
        print(f"[AirConditioningService] PUT Request entity_id: {entity_id}, response: {r}")

        data = {
            "patient_id": int(patient_id),
            "entity_id": int(entity_id),
            "value": humidity,
            "timestamp": timestamp_now,
            "message": None
        }

        if humidity > 65:
            alert_str = f"Humidity {humidity}% too high..."
            data["message"] = alert_str
            print("[AirConditioningService] " + alert_str)
            client.publish(send_topic, json.dumps(data))
        elif humidity < 15:
            alert_str = f"Humidity {humidity}% too low..."
            data["message"] = alert_str
            print("[AirConditioningService] " + alert_str)
            client.publish(send_topic, json.dumps(data))

    def start(self):
        mqtt = MqttHandler(client_id='air-conditioning-service', broker=BROKER_MQTT_URL, port=int(BROKER_MQTT_PORT))
        mqtt._client.on_message = self.on_message
        mqtt.connect()
        mqtt.subscribe(self.MQTT_TOPIC)
        print(f"[AirConditioningService] Air Conditioning Service started and subscribed to {self.MQTT_TOPIC}")
        try:
            mqtt._client.loop_forever()
        except KeyboardInterrupt:
            mqtt.close()
            print("[AirConditioningService] Air Conditioning Service stopped.")

if __name__ == "__main__":
    service = AirConditioningService()
    service.start()
