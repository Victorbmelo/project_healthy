import time
import paho.mqtt.client as mqtt

BROKER_URL = 'localhost'
BROKER_PORT = 1883


class MqttHandler:
    def __init__(self, client_id, broker=BROKER_URL, port=BROKER_PORT, keepalive=60, username=None, password=None, tls=None):
        """
        Initialize the MQTT Handler.

        :param client_id: Unique client ID for the MQTT client
        :param str broker: Address of the MQTT broker
        :param int port: Port number of the MQTT broker (default is 1883)
        :param int keepalive: Keep-alive period in seconds (default is 60)
        :param str username: (Optional) Username for broker authentication
        :param str password: (Optional) Password for broker authentication
        :param dict tls: (Optional) TLS settings for secure communication (dictionary with 'ca_certs', 'certfile', 'keyfile')
        """
        self._client_id = client_id
        self._broker = broker
        self._port = port
        self._keepalive = keepalive
        self._username = username
        self._password = password
        self._tls = tls
        self._client = mqtt.Client(client_id=self._client_id)
        self._client.enable_logger()


        # Configure authentication if provided
        if username and password:
            self._client.username_pw_set(username, password)

        # Configure TLS if provided
        if tls:
            self._client.tls_set(tls['ca_certs'], tls['certfile'], tls['keyfile'])

        # Attach callbacks
        self._client.on_connect = self.on_connect
        self._client.on_disconnect = self.on_disconnect
        self._client.on_message = self.on_message
        self._client.on_subscribe = self.on_subscribe
        self._client.on_publish = self.on_publish

    def set_on_message_callback(self, function):
        self._client.on_message = function

    def connect(self):
        """
        Connect to the MQTT broker.
        """
        try:
            print(f"Connecting to MQTT broker {self._broker}:{self._port}")
            self._client.connect(self._broker, self._port, self._keepalive)
            self._client.loop_start()
        except Exception as e:
            print(f"Failed to connect to broker: {e}")

    def close(self):
        """
        Disconnect from the MQTT broker.
        """
        self._client.loop_stop()
        self._client.disconnect()
        print(f"Disconnected from MQTT broker {self._broker}")

    def subscribe(self, topic, qos=0):
        """
        Subscribe to a topic.

        :param topic: Topic to subscribe to
        :param qos: Quality of Service level (default is 0)
        """
        print(f"Subscribing to topic {topic} with QoS {qos}")
        self._client.subscribe(topic, qos)

    def publish(self, topic, payload, qos=0, retain=False):
        """
        Publish a message to a topic.

        :param topic: Topic to publish to
        :param payload: Message payload
        :param qos: Quality of Service level (default is 0)
        :param retain: Retain the message (default is False)
        """
        print(f"Publishing message to topic {topic} with QoS {qos}, retain={retain}")
        result = self._client.publish(topic, payload, qos, retain)
        result.wait_for_publish()

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback when the client connects to the broker.

        :param client: The client instance
        :param userdata: User-defined data of any type
        :param flags: Response flags sent by the broker
        :param rc: Connection result code
        """
        if rc == 0:
            print(f"Connected to MQTT broker {self._broker}")
        else:
            print(f"Failed to connect, return code {rc}")

    def on_disconnect(self, client, userdata, rc):
        """
        Callback when the client disconnects from the broker.

        :param client: The client instance
        :param userdata: User-defined data of any type
        :param rc: Disconnection result code
        """
        print(f"Disconnected from broker with return code {rc}")

    def on_message(self, client, userdata, message: mqtt.MQTTMessage):
        """
        Callback when a message is received from the broker.

        :param client: The client instance
        :param userdata: User-defined data of any type
        :param message: The message object containing topic, payload, etc.
        """
        print(f"Received message from {message.topic}: {message.payload.decode()}")

    def on_subscribe(self, client, userdata, mid, granted_qos):
        """
        Callback when the client subscribes to a topic.

        :param client: The client instance
        :param userdata: User-defined data of any type
        :param mid: Message ID
        :param granted_qos: QoS level granted by the broker
        """
        print(f"Subscribed to topic, message ID: {mid}, QoS: {granted_qos}")

    def on_publish(self, client, userdata, mid):
        """
        Callback when a message is published.

        :param client: The client instance
        :param userdata: User-defined data of any type
        :param mid: Message ID
        """
        print(f"Message published, message ID: {mid}")


# Example usage
if __name__ == "__main__":
    # Create MQTT Handler
    mqtt_handler = MqttHandler(
        client_id="sensor-client",
        broker="mqtt.example.com",
        port=1883,
        username="user",
        password="password"
    )

    # Connect to the broker
    mqtt_handler.connect()

    # Create a publisher for sensor data
    # Publish some dummy data