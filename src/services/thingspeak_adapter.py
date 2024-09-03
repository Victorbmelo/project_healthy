import cherrypy
import requests
from database.sqliteHandler import DatabaseHandler

# Definições para ThinkSpeak
THINGSPEAK_API_READ_URL = "https://api.thingspeak.com/channels/{channel_id}/feeds.json"
THINGSPEAK_API_KEY = "YOUR_THINGSPEAK_API_KEY"


class ThingSpeakAdapter:
    def __init__(self):
        # Initialize the DatabaseHandler
        self._db = DatabaseHandler()
        self._db.connect()

    @cherrypy.expose
    def index(self):
        return "ThinkSpeak Adapter is running."

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_device_data(self, user, device_mac):
        """
        Retrieve the latest data from ThinkSpeak for a given device.
        """
        channel_id = self.get_thingspeak_channel_id(user, device_mac)
        if not channel_id:
            return {"error": "Channel ID not found for device"}

        response = requests.get(THINGSPEAK_API_READ_URL.format(channel_id=channel_id), params={"api_key": THINGSPEAK_API_KEY})
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to fetch data from ThinkSpeak"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_sensor_data(self, user, device_mac, sensor_id):
        """
        Retrieve specific sensor data from ThinkSpeak.
        """
        channel_id, field_id = self.get_thingspeak_channel_field(user, device_mac, "sensor", sensor_id)
        if not channel_id or not field_id:
            return {"error": "Channel or Field ID not found for sensor"}

        response = requests.get(THINGSPEAK_API_READ_URL.format(channel_id=channel_id), params={"api_key": THINGSPEAK_API_KEY})
        if response.status_code == 200:
            feeds = response.json().get('feeds', [])
            return {f"field{field_id}": [feed.get(f"field{field_id}") for feed in feeds]}
        else:
            return {"error": "Failed to fetch data from ThinkSpeak"}

    def get_thingspeak_channel_field(self, user=None, user_id=None, device_mac=None, entity_type=None, entity_id=None):
        """
        Retrieve the ThinkSpeak channel key and field ID for a specific device and entity type.

        :param str user: The username associated with the device (optional if user_id is provided).
        :param str user_id: The user ID associated with the device (optional if user is provided).
        :param str device_mac: The MAC address of the device.
        :param str entity_type: The type of entity (sensor/actuator).
        :param str entity_id: The ID of the entity.
        :return: Tuple of (channel_key, field_id) or (None, None) if not found.
        """
        if entity_type not in {"sensor", "actuator"}:
            return None, None

        if user_id is None and user is None:
            raise ValueError("Either 'user' or 'user_id' must be provided.")

        # Determine which user identifier to use
        user_id_query_param = None
        if user_id is not None:
            user_id_query_param = user_id
            user_query_condition = "U.id = ?"
        elif user is not None:
            user_query_condition = "U.name = ?"

        # Define queries based on entity_type
        if entity_type == "sensor":
            query = f"""
                SELECT D.thingspeak_channel_key, S.thingspeak_field_id
                FROM Devices D
                JOIN Sensors S ON D.id = S.device_id
                JOIN Users U ON D.user_id = U.id
                WHERE {user_query_condition} AND D.mac_address = ? AND S.sensor_id = ?
            """
            query_params = (user_id_query_param or user, device_mac, entity_id)
        elif entity_type == "actuator":
            query = f"""
                SELECT D.thingspeak_channel_key, A.thingspeak_field_id
                FROM Devices D
                JOIN Actuators A ON D.id = A.device_id
                JOIN Users U ON D.user_id = U.id
                WHERE {user_query_condition} AND D.mac_address = ? AND A.actuator_id = ?
            """
            query_params = (user_id_query_param or user, device_mac, entity_id)

        result = self._db.query_data(query, query_params)
        if result:
            return result[0]
        return None, None


    def get_thingspeak_channel_id(self, user, device_mac):
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
            WHERE U.name = ? AND D.mac_address = ?
        """
        with self._db.connection() as conn:
            result = self._db.query_data(query, (user, device_mac))
            if result:
                return result[0][0]
            return None


if __name__ == "__main__":
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8080})
    cherrypy.quickstart(ThingSpeakAdapter())
