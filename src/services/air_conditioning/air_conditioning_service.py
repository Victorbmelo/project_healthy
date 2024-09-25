import json
from src.mqtt.mqtt_handler import MqttHandler

class AirConditioningService:
    MQTT_TOPIC = '/+/airconditioning/+/+/+'

    def __init__(self):
        pass

    def on_message(self, client, userdata, msg):
        rcvd_topic = msg.topic
        send_topic = f"{rcvd_topic}/alert"
        payload = json.loads(msg.payload.decode())
        print(f"Received: {payload} on {rcvd_topic}")
        data = {'data': payload, 'alert_message': ""}

        if 'temperature' in payload:
            temperature = payload['temperature']
            if temperature > 25:
                alert_str = "Temperature too high, adjusting air conditioning..."
                data["alert_message"] = alert_str
                print(alert_str)
                client.publish(send_topic, json.dumps(data))
            elif temperature < 18:
                alert_str = "Temperature too low, adjusting air conditioning..."
                data["alert_message"] = alert_str
                print(alert_str)
                client.publish(send_topic, json.dumps(data))
            else:
                print("Temperature is optimal, keeping current settings.")

    def start(self):
        mqtt = MqttHandler(client_id='air-conditioning-service')
        mqtt._client.on_message = self.on_message
        mqtt.connect()
        mqtt.subscribe(self.MQTT_TOPIC)
        print(f"Air Conditioning Service started and subscribed to {self.MQTT_TOPIC}")
        try:
            pass
        except KeyboardInterrupt:
            mqtt.close()
            print("Air Conditioning Service stopped.")
