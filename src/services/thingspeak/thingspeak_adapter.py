import cherrypy
import random
import requests
import time
import threading

from src.database.sqlite_handler import DatabaseHandler
from src.mqtt.mqtt_handler import MqttHandler

# Set ThingSpeak
THINGSPEAK_API_READ_URL = "https://api.thingspeak.com/channels/{channel_id}/feeds.json"
THINGSPEAK_API_KEY = "YOUR_THINGSPEAK_API_KEY"
THINGSPEAK_MQTT_URL = 'mqtt3.thingspeak.com'
THINGSPEAK_MQTT_PORT = 1883


class ThingSpeakAdapter:
    def __init__(self):
        self._db = DatabaseHandler()
        self._db.connect()

        # MQTT connection for local and ThingSpeak MQTT broker
        self._local_mqtt = MqttHandler(
            client_id='local-thingspeak-adapter'
        )
        self._local_mqtt.connect()

        self._thingspeak_mqtt = MqttHandler(
            client_id='CCwmLDwwLgY2HykqLggJGSE',
            username='CCwmLDwwLgY2HykqLggJGSE',
            password='kmOtFoeMG7ZE1XLro6QG/uuE',
            broker=THINGSPEAK_MQTT_URL,
            port=THINGSPEAK_MQTT_PORT
        )
        self._thingspeak_mqtt.connect()

    @cherrypy.expose
    def index(self):
        return "ThingSpeak Adapter is running."

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_device_data(self, user, device_mac):
        try:
            channel_id = self.get_thingspeak_channel_id(user, device_mac)
            if not channel_id:
                return {"error": "Channel ID not found for device"}

            response = requests.get(THINGSPEAK_API_READ_URL.format(channel_id=channel_id), params={"api_key": THINGSPEAK_API_KEY})
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Failed to fetch data: {e}"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_sensor_data(self, user, device_mac, sensor_id):
        try:
            channel_id, field_id = self.get_thingspeak_channel_field(user, device_mac, "sensor", sensor_id)
            if not channel_id or not field_id:
                return {"error": "Channel or Field ID not found for sensor"}

            response = requests.get(THINGSPEAK_API_READ_URL.format(channel_id=channel_id), params={"api_key": THINGSPEAK_API_KEY})
            response.raise_for_status()
            feeds = response.json().get('feeds', [])
            return {f"field{field_id}": [feed.get(f"field{field_id}") for feed in feeds]}
        except requests.RequestException as e:
            return {"error": f"Failed to fetch sensor data: {e}"}

    def get_thingspeak_channel_field(self, user_passport_code, device_mac, entity_type, entity_id):
        """
        Retrieve the ThinkSpeak channel key and field ID for a specific device and entity type.

        :param str user_passport_code: The user passport code associated with the device.
        :param str device_mac: The MAC address of the device.
        :param str entity_type: The type of entity (sensor/actuator).
        :param str entity_id: The ID of the entity.
        :return: Tuple of (channel_key, field_id) or (None, None) if not found.
        """
        if entity_type not in {"sensor", "actuator"}:
            return None, None

        query = f"""
            SELECT D.thingspeak_channel_key, S.thingspeak_field_id
            FROM Devices D
            JOIN Sensors S ON D.id = S.device_id
            JOIN Users U ON D.user_id = U.id
            WHERE U.passport_code = ? AND D.mac_address = ? AND S.sensor_id = ?
        """
        result = self._db.query_data(query, (user_passport_code, device_mac, entity_id))
        if result:
            return result[0]
        return None, None

    def get_thingspeak_channel_id(self, user_passport_code, device_mac):
        """
        Retrieve the ThinkSpeak channel key for a specific device.

        :param str user: The user associated with the device.
        :param str device_mac: The MAC address of the device.
        :return: Channel key or None if not found.
        """
        query = """
            SELECT D.thingspeak_channel_key
            FROM Devices D
            JOIN Users U ON D.user_id = U.id
            WHERE U.passport_code = ? AND D.mac_address = ?
        """
        result = self._db.query_data(query, (user_passport_code, device_mac))
        if result:
            return result[0][0]
        return None

    def send_data_to_thingspeak_mqtt(self, channel_key, field_id, message):
        """
        Send data to ThingSpeak using the MQTT protocol.

        :param str channel_key: The API key for the ThingSpeak channel.
        :param int field_id: The field ID in the ThingSpeak channel where data should be sent.
        :param str message: The data message to be sent to ThingSpeak.
        :return: None
        """
        mqtt_topic = f"channels/{channel_key}/publish/fields/field{field_id}"
        self._thingspeak_mqtt.publish(mqtt_topic, payload=str(message), qos=0)
        print(f"Data sent to ThingSpeak MQTT broker: Topic: {mqtt_topic}, Payload: {message}")

    def start(self):
        """Start the simulation of sensor data readings and sending them to ThingSpeak."""
        threading.Thread(target=self._listen_to_entities, daemon=True).start()

    def _listen_to_entities(self):
        """Listen to sensor data published locally and send it to ThingSpeak via MQTT."""
        def on_message(client, userdata, message):
            # Simulate processing the incoming sensor data
            payload = message.payload.decode('utf-8')
            topic = message.topic
            print(f"Received message from {topic}: {payload}")

            # Extract params from the topic
            # topic format: <user_passport_code>/<service_name>/<device_mac>/<entity_type>[sensor|actuator]/<entity_id>
            user_passport_code, service_name, device_mac, entity_type, entity_id = topic.split('/')

            # Get the corresponding ThingSpeak channel and field information
            channel_key, field_id = self.get_thingspeak_channel_field(user_passport_code, device_mac, entity_type, entity_id)
            if channel_key and field_id:
                self.send_data_to_thingspeak_mqtt(channel_key, field_id, payload)

        # Subscribe to all entities topics
        self._local_mqtt.subscribe("/+/+/+/+/+")
        self._local_mqtt.set_on_message_callback(on_message)

        # Keep the thread running
        while True:
            time.sleep(1)


if __name__ == "__main__":
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8080})
    cherrypy.quickstart(ThingSpeakAdapter())
