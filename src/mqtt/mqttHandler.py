import requests
import paho.mqtt.client as mqtt
from services.thingspeak_adapter import ThingSpeakAdapter

THINGSPEAK_API_URL = 'mqtt3.thingspeak.com'
SEND_METHOD = 'MQTT'


class MQTTHandler:
    def __init__(self, mqtt_broker_local='localhost', mqtt_port_local=1883, mqtt_broker_thingspeak=THINGSPEAK_API_URL, mqtt_port_thingspeak=1883):
        """
        Initialize the MQTTHandler instance with local and ThingSpeak MQTT configurations.

        :param str mqtt_broker_local: The address of the local MQTT broker.
        :param int mqtt_port_local: The port number for the local MQTT broker.
        :param str mqtt_broker_thingspeak: The address of the ThingSpeak MQTT broker.
        :param int mqtt_port_thingspeak: The port number for the ThingSpeak MQTT broker.
        """
        self.tspk_adpt = ThingSpeakAdapter()

        self.mqtt_broker_local = mqtt_broker_local
        self.mqtt_port_local = mqtt_port_local
        self.mqtt_broker_thingspeak = mqtt_broker_thingspeak
        self.mqtt_port_thingspeak = mqtt_port_thingspeak

        self.mqtt_client_local = mqtt.Client()
        self.mqtt_client_thingspeak = None

        # Initialize the local MQTT client
        self.setup_local_mqtt_client()
        self.mqtt_client_local.loop_start()

        # Initialize the ThingSpeak MQTT client if needed
        if SEND_METHOD == 'MQTT':
            self.setup_thingspeak_mqtt_client()

    def setup_local_mqtt_client(self):
        """
        Set up and connect the local MQTT client to the specified broker.

        :return: None
        """
        self.mqtt_client_local.on_connect = self.on_connect
        self.mqtt_client_local.on_message = self.on_message
        self.mqtt_client_local.connect(self.mqtt_broker_local, self.mqtt_port_local, 60)

    def setup_thingspeak_mqtt_client(self):
        """
        Initialize the MQTT client for ThingSpeak and connect it to the broker.

        :return: None
        """
        self.mqtt_client_thingspeak = mqtt.Client()
        self.mqtt_client_thingspeak.connect(self.mqtt_broker_thingspeak, self.mqtt_port_thingspeak, 60)
        self.mqtt_client_thingspeak.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback for when the local MQTT client connects to the broker.
        """
        print(f"Connected to local MQTT broker with result code {rc}")
        client.subscribe("+/+/+/+/+/+")

    def on_message(self, client, userdata, msg):
        """
        Callback for handling the event when the MQTT client successfully connects to the local broker.

        :param mqtt.Client client: The MQTT client instance that is connecting.
        :param userdata: The private user data as set in Client() or userdata_set().
        :param dict flags: Response flags sent by the broker.
        :param int rc: The connection result.
        :return: None
        """
        try:
            user_id, service_name, device_mac, entity_type, entity_id = msg.topic.split('/')
            channel_key, field_id = self.tspk_adpt.get_thingspeak_channel_field(
                user_id=user_id, device_mac=device_mac, entity_type=entity_type, entity_id=entity_id
            )
            message_received = msg.payload.decode('utf-8')

            if channel_key and field_id:
                if SEND_METHOD == 'REST':
                    self.send_data_to_thingspeak_rest(channel_key, field_id, message_received)
                elif SEND_METHOD == 'MQTT':
                    self.send_data_to_thingspeak_mqtt(channel_key, field_id, message_received)
                else:
                    print("Invalid ThingSpeak method configured.")
            else:
                print(f"No channel or field ID found for topic: {msg.topic}")

        except Exception as e:
            print(f"Error processing message from topic {msg.topic}: {e}")

    def send_data_to_thingspeak_rest(self, channel_key, field_id, message_received):
        """
        Send data to ThingSpeak using the REST API.

        :param str channel_key: The API key for the ThingSpeak channel.
        :param int field_id: The field ID in the ThingSpeak channel where data should be sent.
        :param str message_received: The data message to be sent to ThingSpeak.
        :return: None
        """
        rest_payload = {
            'api_key': channel_key,
            f'field{field_id}': message_received
        }
        try:
            rest_response = requests.post(THINGSPEAK_API_URL, params=rest_payload)
            print(f"Data sent to ThingSpeak REST API: {rest_response.status_code}, Response: {rest_response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send data to ThingSpeak REST API: {e}")

    def send_data_to_thingspeak_mqtt(self, channel_key, field_id, message_received):
        """
        Send data to ThingSpeak using the MQTT protocol.

        :param str channel_key: The API key for the ThingSpeak channel.
        :param int field_id: The field ID in the ThingSpeak channel where data should be sent.
        :param str message_received: The data message to be sent to ThingSpeak.
        :return: None
        """
        mqtt_topic = f"channels/{channel_key}/publishfields/field{field_id}"
        self.mqtt_client_thingspeak.publish(mqtt_topic, payload=str(message_received), qos=0)
        print(f"Data sent to ThingSpeak MQTT broker: Topic: {mqtt_topic}, Payload: {message_received}")

    def close(self):
        """
        Close the MQTT clients and the database connection.

        :return: None
        """
        # Stop the local MQTT client loop and disconnect
        if self.mqtt_client_local:
            self.mqtt_client_local.loop_stop()
            self.mqtt_client_local.disconnect()
            print("Disconnected from local MQTT broker.")

        # Stop the ThingSpeak MQTT client loop and disconnect if it was set up
        if self.mqtt_client_thingspeak:
            self.mqtt_client_thingspeak.loop_stop()
            self.mqtt_client_thingspeak.disconnect()
            print("Disconnected from ThingSpeak MQTT broker.")

        # Close the database connection
        if self.tspk_adpt._db:
            self.tspk_adpt._db.close()
            print("ThingSpeakAdapter Database connection closed.")

if __name__ == "__main__":
    # Init
    mqtt_handler = MQTTHandler()

    try:
        pass
    except KeyboardInterrupt:
        print("Interrupted by user, closing connections.")
    finally:
        mqtt_handler.close()
