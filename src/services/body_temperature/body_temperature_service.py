import json
from src.mqtt.mqtt_handler import MqttHandler

class BodyTemperatureService:
    MQTT_TOPIC = '/+/bodytemperature/+/+/+'

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
            if temperature > 39.5:
                alert_str = "High fever detected! Turning on red lamp and playing sound on the speaker..."
                data["alert_message"] = alert_str
                print(alert_str)
                client.publish(send_topic, json.dumps(data))
            elif temperature > 38.0:
                alert_str = "Fever detected! Sending alert to Telegram bot and dashboard..."
                data["alert_message"] = alert_str
                print(alert_str)
                client.publish(send_topic, json.dumps(data))

    def start(self):
        mqtt = MqttHandler(client_id='body-temperature-service')
        mqtt._client.on_message = self.on_message
        mqtt.connect()
        mqtt.subscribe(self.MQTT_TOPIC)
        print(f"Body Temperature Service started and subscribed to {self.MQTT_TOPIC}")
        try:
            pass
        except KeyboardInterrupt:
            mqtt.close()
            print("Body Temperature Service stopped.")
