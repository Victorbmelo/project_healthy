import cherrypy
import requests
import threading
from src.database.sqlite_handler import DatabaseHandler
from src.mqtt.mqtt_handler import MqttHandler

THINGSPEAK_API_READ_URL = "https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={api_key}"
THINGSPEAK_MQTT_URL = 'mqtt3.thingspeak.com'
THINGSPEAK_MQTT_PORT = 1883

class ThingSpeakAdapter:
    def __init__(self):
        self._local_mqtt = MqttHandler(client_id='local-thingspeak-adapter')
        self._local_mqtt.set_on_message_callback(self.on_message)

        self._thingspeak_mqtt = MqttHandler(
            client_id='CCwmLDwwLgY2HykqLggJGSE',
            username='CCwmLDwwLgY2HykqLggJGSE',
            password='RM31VxfZzZFM53UMW1QusAAw',
            broker=THINGSPEAK_MQTT_URL,
            port=THINGSPEAK_MQTT_PORT
        )
        self._thingspeak_mqtt.connect()
        self.start()

    def get_db_connection(self):
        db = DatabaseHandler(client_id='ThingSpeakAdapter')
        db.connect()
        return db

    @cherrypy.expose
    def index(self):
        return "ThingSpeak Adapter is running."

    @cherrypy.expose(alias='thingspeak')
    @cherrypy.tools.json_out()
    def get_device_data(self, patient_id=None, passport_code=None, device_id=None, mac_address=None):
        """
        If patient_id/passport_code and device_id/mac_address are provided, returns data for a single channel.
        If only patient_id/passport_code is provided, returns data for all channels (devices) associated with the patient.
        """
        try:
            db = self.get_db_connection()

            # If device_id or mac_address is provided: fetch a single channel
            if device_id is not None or mac_address is not None:
                channels = self.get_thingspeak_channel_info(db, patient_id, passport_code, device_id, mac_address)
                if not channels:
                    return {"error": "Channel info not found for device"}
                channel_key, channel_id, dev_id = channels[0]
                if not channel_id:
                    return {"error": "Channel ID not found for device"}
                ts_response = requests.get(THINGSPEAK_API_READ_URL.format(channel_id=channel_id, api_key=channel_key))
                ts_response.raise_for_status()
                ts_json = ts_response.json()
                return [self.transform_thingspeak_data(ts_json, dev_id)]
            else:
                # If only patient_id or passport_code is provided: fetch all channels for the patient
                channels = self.get_thingspeak_channel_info(db, patient_id, passport_code)
                if not channels:
                    return {"error": "No channels found for the patient"}
                data = []
                for channel_key, channel_id, dev_id in channels:
                    if not channel_id:
                        continue
                    try:
                        ts_response = requests.get(THINGSPEAK_API_READ_URL.format(channel_id=channel_id, api_key=channel_key))
                        ts_response.raise_for_status()
                        ts_json = ts_response.json()
                        device_data = self.transform_thingspeak_data(ts_json, dev_id)
                        data.append(device_data)
                    except Exception as e:
                        data.append({"Device_id": dev_id, "error": str(e)})
                return data

        except requests.RequestException as e:
            return {"error": f"Failed to fetch data: {e}"}
        except Exception as e:
            return {"error": f"An error occurred: {e}"}

    def get_thingspeak_channel_info(self, db, patient_id=None, passport_code=None, device_id=None, mac_address=None):
        """
        Returns a list of channel information:
        Each record contains: (thingspeak_channel_key, thingspeak_channel_id, device_id)
        Filtering is performed using patient_id/passport_code and/or device_id/mac_address.
        """
        query = """
            SELECT D.thingspeak_channel_key, D.thingspeak_channel_id, D.device_id
            FROM Devices D
            LEFT JOIN Patients P ON P.patient_id = D.patient_id
            WHERE
        """
        conditions = []
        params = []

        if patient_id is not None or passport_code is not None:
            conditions.append("(P.passport_code = ? OR P.patient_id = ?)")
            params.extend([passport_code, patient_id])
        if device_id is not None or mac_address is not None:
            conditions.append("(D.device_id = ? OR D.mac_address = ?)")
            params.extend([device_id, mac_address])
        if conditions:
            query += " AND ".join(conditions)
        else:
            query = query.strip().rstrip("WHERE")

        print("DEBUG:", query, params)
        result = db.query_data(query, params)
        print()
        print(result)
        print()
        return result if result else []

    def transform_thingspeak_data(self, ts_json, device_id):
        """
        Transforms the Thingspeak JSON into an intelligent format, grouping data from each sensor.
        Returns a dictionary in the format:
        {
            "Device_id": <device_id>,
            "Sensors": [
                {
                    "Name": <sensor_name>,
                    "Values": [
                        {"created_at": <timestamp>, "value": <value>},
                        ...
                    ]
                },
                ...
            ]
        }
        """
        channel = ts_json.get("channel", {})
        feeds = ts_json.get("feeds", [])

        # Map each field (field1, field2, ...) to the sensor name provided in the channel data
        sensors = {}
        for key, sensor_name in channel.items():
            if key.startswith("field") and sensor_name:
                sensors[key] = sensor_name

        # Initialize the structure for each sensor
        sensor_data = {sensor_name: [] for sensor_name in sensors.values()}

        # Iterate over feeds and group values for each sensor
        for feed in feeds:
            created_at = feed.get("created_at")
            for field_key, sensor_name in sensors.items():
                value = feed.get(field_key)
                if value is not None:
                    sensor_data[sensor_name].append({
                        "created_at": created_at,
                        "value": value
                    })

        # Prepare the sensor list for the return JSON
        sensors_list = [{"Name": name, "Values": values} for name, values in sensor_data.items()]

        return {"Device_id": device_id, "Sensors": sensors_list}

    def get_thingspeak_field_id(self, db, entity_id, device_id):
        """
        Retrieves or assigns a ThingSpeak field ID for an entity associated with a device.

        If the entity already has a `thingspeak_field_id`, it is returned.
        Otherwise, the function finds the next available field ID for the device and assigns it to the entity.
        """
        # Check if the entity already has an assigned field ID
        query = """
            SELECT thingspeak_field_id
            FROM DeviceEntities
            WHERE entity_id = ?
            AND thingspeak_field_id <> '';
        """
        result = db.query_data(query, (entity_id,))

        if result and result[0][0] is not None:
            print(f"[THINGSPEAK] Entity {entity_id} already has a ThingSpeak field ID: {result[0][0]}")
            print(f"[THINGSPEAK] Query {query}.")
            return result[0][0]

        # Retrieve assigned field IDs for the device
        fields_query = """
            SELECT thingspeak_field_id
            FROM DeviceEntities
            WHERE device_id = ?;
        """
        result = db.query_data(fields_query, (device_id,))

        if result:
            assigned_fields = [row[0] for row in result if row[0] is not None]
            field_id = max(assigned_fields) + 1 if assigned_fields else 1
            print(f"[THINGSPEAK] Found assigned field IDs for device {device_id}: {assigned_fields}")
            print(f"[THINGSPEAK] Assigning new ThingSpeak field ID: {field_id}")
        else:
            field_id = 1
            print(f"[THINGSPEAK] No ThingSpeak field IDs found for device {device_id}. Starting from {field_id}.")

        # Assign the new field ID to the entity
        update_query = """
            UPDATE DeviceEntities
            SET thingspeak_field_id = ?
            WHERE entity_id = ?;
        """
        db.execute_query(update_query, (field_id, entity_id))
        print(f"[THINGSPEAK] Successfully assigned ThingSpeak field ID {field_id} to entity {entity_id}.")

        return field_id

    def send_data_to_thingspeak_mqtt(self, channel_key, field_id, message):
        mqtt_topic = f"channels/{channel_key}/publish/fields/field{field_id}"
        self._thingspeak_mqtt.publish(mqtt_topic, payload=str(message), qos=0)

    def on_message(self, client, userdata, message):
        payload = message.payload.decode('utf-8')
        topic = message.topic
        try:
            db = self.get_db_connection()
            patient_id, service_name, device_id, entity_id = topic.lstrip('/').split('/')

            field_id = self.get_thingspeak_field_id(db, entity_id=entity_id, device_id=device_id)
            channels = self.get_thingspeak_channel_info(db, patient_id=patient_id, device_id=device_id)
            channel_key, channel_id, _ = channels[0]

            if channel_key and field_id:
                self.send_data_to_thingspeak_mqtt(channel_id, field_id, payload)
        except Exception as e:
            print(f"[THINGSPEAK] Error on_message: {e}")

    def start(self):
        self._local_mqtt.connect()
        threading.Thread(target=self._listen_to_entities, daemon=True).start()

    def start_server(self):
        cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8081})
        cherrypy.quickstart(self)

    def _listen_to_entities(self):
        self._local_mqtt.subscribe("/+/+/+/+")

if __name__ == "__main__":
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8080})
    cherrypy.quickstart(ThingSpeakAdapter())
