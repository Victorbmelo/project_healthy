import os
import cherrypy
import requests
import threading
from src.mqtt.mqtt_handler import MqttHandler

# External Thingspeak constants
THINGSPEAK_API_READ_URL = os.getenv('THINGSPEAK_API_READ_URL', 'https://api.thingspeak.com/channels/{channel_id}/feeds.json')
THINGSPEAK_MQTT_URL = os.getenv('THINGSPEAK_MQTT_URL', 'mqtt3.thingspeak.com')
THINGSPEAK_MQTT_PORT = os.getenv('THINGSPEAK_MQTT_PORT', 1883)

# Define the base URL for your API endpoints (update as needed)
DB_CONNECTOR_URL = os.getenv('DB_CONNECTOR_URL', 'http://localhost:8080')

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

    @cherrypy.expose
    def index(self):
        return "ThingSpeak Adapter is running."

    @cherrypy.expose(alias='thingspeak')
    @cherrypy.tools.json_out()
    def get_device_data(self, patient_id=None, passport_code=None, device_id=None, mac_address=None,
                        results=None, days=None, minutes=None, start=None, end=None, timezone=None):
        """
        Retrieves data from the ThingSpeak API with optional filter parameters.

        If patient_id/passport_code and device_id/mac_address are provided, returns data for a single channel.
        If only patient_id/passport_code is provided, returns data for all channels (devices) associated with the patient.

        Optional Thingspeak filters:
            - results: (Optional) Number of entries to retrieve. The maximum number is 8,000. (integer)
            - days: (Optional) Number of 24-hour periods before now to include in response. The default is 1. (integer)
            - minutes: (Optional) Number of 60-second periods before now to include in response. The default is 1440. (integer)
            - start: (Optional) Start date in format YYYY-MM-DD%20HH:NN:SS. (datetime)
            - end: (Optional) End date in format YYYY-MM-DD%20HH:NN:SS. (datetime)
            - timezone: (Optional) Identifier from Time Zones Reference for this request. (string)
        """
        # Prepare Thingspeak filter parameters
        filter_params = {}
        if results is not None:
            filter_params["results"] = results
        if days is not None:
            filter_params["days"] = days
        if minutes is not None:
            filter_params["minutes"] = minutes
        if start is not None:
            filter_params["start"] = start
        if end is not None:
            filter_params["end"] = end
        if timezone is not None:
            filter_params["timezone"] = timezone

        # If device_id or mac_address is provided, fetch a single channel
        if device_id is not None or mac_address is not None:
            channels = self.get_thingspeak_channel_info(
                patient_id=patient_id,
                passport_code=passport_code,
                device_id=device_id,
                mac_address=mac_address
            )
            if not channels:
                return {"error": "Channel info not found for device"}
            channel_key, channel_id, dev_id = channels[0]
            if not channel_id:
                return {"error": "Channel ID not found for device"}

            # Build Thingspeak API URL and parameters
            url = THINGSPEAK_API_READ_URL.format(channel_id=channel_id)
            params = {"api_key": channel_key}
            params.update(filter_params)
            ts_response = requests.get(url, params=params)
            ts_response.raise_for_status()
            ts_json = ts_response.json()
            return [self.transform_thingspeak_data(ts_json, dev_id)]
        else:
            # If only patient_id or passport_code is provided: fetch all channels for the patient
            channels = self.get_thingspeak_channel_info(
                patient_id=patient_id,
                passport_code=passport_code
            )
            if not channels:
                return {"error": "No channels found for the patient"}
            data = []
            for channel_key, channel_id, dev_id in channels:
                if not channel_id:
                    continue
                try:
                    url = THINGSPEAK_API_READ_URL.format(channel_id=channel_id)
                    params = {"api_key": channel_key}
                    params.update(filter_params)
                    ts_response = requests.get(url, params=params)
                    ts_response.raise_for_status()
                    ts_json = ts_response.json()
                    device_data = self.transform_thingspeak_data(ts_json, dev_id)
                    data.append(device_data)
                except Exception as e:
                    data.append({"Device_id": dev_id, "error": str(e)})
            return data

    def get_thingspeak_channel_info(self, patient_id=None, passport_code=None, device_id=None, mac_address=None):
        """
        Returns a list of channel information by calling the API endpoints.
        Each record contains: (thingspeak_channel_key, thingspeak_channel_id, device_id)
        """
        # If patient_id is not provided but passport_code is, get patient info first
        if patient_id is None and passport_code is not None:
            url = f"{DB_CONNECTOR_URL}/patient"
            params = {"passport_code": passport_code}
            response = requests.get(url, params=params)
            response.raise_for_status()
            patient_data = response.json()
            if not patient_data:
                return []
            patient_id = patient_data[0].get("patient_id")

        # Query devices endpoint with the provided filters
        url = f"{DB_CONNECTOR_URL}/device"
        params = {}
        if patient_id is not None:
            params["patient_id"] = patient_id
        if device_id is not None:
            params["device_id"] = device_id
        if mac_address is not None:
            params["mac_address"] = mac_address
        response = requests.get(url, params=params)
        response.raise_for_status()
        devices = response.json()

        channels = []
        for dev in devices:
            channel_key = dev.get("thingspeak_channel_key")
            channel_id = dev.get("thingspeak_channel_id")
            dev_id = dev.get("device_id")
            if channel_key and channel_id:
                channels.append((channel_key, channel_id, dev_id))
        return channels

    def get_entity_names_for_device(self, device_id):
        """
        Retrieves a mapping from Thingspeak field keys to entity names for sensor entities of the given device.
        Uses the API endpoint to get the entities.
        """
        url = f"{DB_CONNECTOR_URL}/entity"
        params = {"device_id": device_id, "entity_type": "sensor"}
        response = requests.get(url, params=params)
        response.raise_for_status()
        rows = response.json()
        mapping = {}
        for row in rows:
            thingspeak_field_id = row.get("thingspeak_field_id")
            entity_name = row.get("entity_name")
            if thingspeak_field_id is not None and entity_name:
                key = f"field{thingspeak_field_id}"
                mapping[key] = entity_name
        return mapping

    def transform_thingspeak_data(self, ts_json, device_id, use_db_entity_name=False):
        """
        Transforms the Thingspeak JSON into a grouped sensor data format.
        Optionally uses the entity names from the API if use_db_entity_name is True.

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
        feeds = ts_json.get("feeds", {})

        sensors = {}
        if use_db_entity_name:
            # Get entity names mapping from the API
            db_entity_names = self.get_entity_names_for_device(device_id)
            for key, channel_value in channel.items():
                if key.startswith("field"):
                    sensor_name = db_entity_names.get(key, channel_value)
                    if sensor_name:
                        sensors[key] = sensor_name
        else:
            for key, sensor_name in channel.items():
                if key.startswith("field") and sensor_name:
                    sensors[key] = sensor_name

        # Initialize the structure for each sensor
        sensor_data = {sensor_name: [] for sensor_name in sensors.values()}

        # Group feed values by sensor
        for feed in feeds:
            created_at = feed.get("created_at")
            for field_key, sensor_name in sensors.items():
                value = feed.get(field_key)
                if value is not None:
                    sensor_data[sensor_name].append({
                        "created_at": created_at,
                        "value": value
                    })

        sensors_list = [{"Name": name, "Values": values} for name, values in sensor_data.items()]
        return {"Device_id": device_id, "Sensors": sensors_list}

    def get_thingspeak_field_id(self, entity_id, device_id):
        """
        Retrieves or assigns a ThingSpeak field ID for an entity via API calls.
        If the entity already has a `thingspeak_field_id`, it is returned.
        Otherwise, the next available field ID is determined and updated.
        """
        # Check if the entity already has an assigned field ID
        url = f"{DB_CONNECTOR_URL}/entity"
        params = {"entity_id": entity_id}
        response = requests.get(url, params=params)
        response.raise_for_status()
        records = response.json()
        if records:
            record = records[0]
            if record.get("thingspeak_field_id"):
                cherrypy.log("[THINGSPEAK] Entity {} already has a ThingSpeak field ID: {}".format(
                    entity_id, record.get("thingspeak_field_id")))
                return record.get("thingspeak_field_id")

        # Retrieve all entities for the device to find assigned field IDs
        url = f"{DB_CONNECTOR_URL}/entity"
        params = {"device_id": device_id}
        response = requests.get(url, params=params)
        response.raise_for_status()
        records = response.json()
        assigned_fields = []
        for rec in records:
            t_field = rec.get("thingspeak_field_id")
            if t_field not in (None, ""):
                assigned_fields.append(int(t_field))
        if assigned_fields:
            field_id = max(assigned_fields) + 1
        else:
            field_id = 1
        cherrypy.log("[THINGSPEAK] Assigning new ThingSpeak field ID: {}".format(field_id))

        # Update the entity with the new field ID via PUT
        url = f"{DB_CONNECTOR_URL}/entity?entity_id={entity_id}"
        payload = {"thingspeak_field_id": field_id}
        response = requests.put(url, json=payload)
        response.raise_for_status()
        return field_id

    def send_data_to_thingspeak_mqtt(self, channel_key, field_id, message):
        mqtt_topic = f"channels/{channel_key}/publish/fields/field{field_id}"
        self._thingspeak_mqtt.publish(mqtt_topic, payload=str(message), qos=0)

    def on_message(self, client, userdata, message):
        """
        Callback for local MQTT messages.
        Extracts patient, device, and entity info from the topic and uses APIs to:
            1. Get (or assign) the field ID.
            2. Fetch the Thingspeak channel info.
            3. Publish the data to Thingspeak via MQTT.
        """
        payload = message.payload.decode('utf-8')
        topic = message.topic
        try:
            patient_id, service_name, device_id, entity_id = topic.lstrip('/').split('/')
            field_id = self.get_thingspeak_field_id(entity_id, device_id)
            channels = self.get_thingspeak_channel_info(patient_id=patient_id, device_id=device_id)
            if channels:
                channel_key, channel_id, _ = channels[0]
                if channel_key and field_id:
                    self.send_data_to_thingspeak_mqtt(channel_id, field_id, payload)
        except Exception as e:
            cherrypy.log("[THINGSPEAK] Error on_message: {}".format(e))

    def start(self):
        self._local_mqtt.connect()
        threading.Thread(target=self._listen_to_entities, daemon=True).start()

    def start_server(self):
        cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8081})
        cherrypy.quickstart(self)

    def _listen_to_entities(self):
        self._local_mqtt.subscribe("+/+/+/+")


if __name__ == "__main__":
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8081})
    cherrypy.quickstart(ThingSpeakAdapter())
