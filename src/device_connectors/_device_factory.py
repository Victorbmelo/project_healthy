import random
from abc import ABC
import requests
from src.database.sqlite_handler import DatabaseHandler
from src.mqtt.mqtt_handler import MqttHandler

API_BASE_URL = "http://localhost:8080"


## Base Classes ###
class Entity(ABC):
    """
    Abstract base class representing an entity within the system.
    """
    def __init__(self) -> None:
        """
        Initializes the base Entity class.
        """
        super().__init__()

    def set_mqtt_topic(self, passport_code):
        """
        Sets the MQTT topic for the entity. This method should be implemented by derived classes.
        """
        pass

    def read_data(self):
        """
        This method should be implemented by derived classes.
        """
        pass

    def send_data(self, data):
        """
        Sends data over MQTT. This method should be implemented by derived classes.
        """
        pass


class DeviceEntity(Entity):
    """
    Class representing a device entity (sensor or actuator).
    """
    def __init__(self, name, device_mac, entity_type, service_name, db_handler: DatabaseHandler, mqtt_handler: MqttHandler):
        """
        Initialize a device entity with specific attributes.
        """
        super().__init__()
        self.name = name
        self.device_mac = device_mac
        self.entity_type = entity_type
        self.service_name = service_name
        self.db_handler = db_handler
        self.mqtt_handler = mqtt_handler
        self.mqtt_topic = None
        print(f"[DeviceEntity] Initialized {entity_type} '{name}' for device {device_mac}")

    def set_mqtt_topic(self, passport_code):
        """
        Sets the MQTT topic for the entity by retrieving patient, device, entity,
        and service information via API calls and then upserting the corresponding endpoint.
        """
        print(f"[DeviceEntity] Setting MQTT topic for passport: {passport_code}")
        try:
            # 1. Get Patient info
            print(f"[DeviceEntity] Fetching patient info for passport: {passport_code}")
            patient_resp = requests.get(f"{API_BASE_URL}/patient", params={"passport_code": passport_code})
            patient_resp.raise_for_status()
            patient_data = patient_resp.json()

            if not patient_data:
                print(f"[DeviceEntity] No patient found for passport {passport_code}")
                return

            patient_id = patient_data[0]["patient_id"]
            print(f"[DeviceEntity] Found patient ID: {patient_id}")

            # 2. Get Device info
            print(f"[DeviceEntity] Fetching device {self.device_mac} for patient {patient_id}")
            device_resp = requests.get(f"{API_BASE_URL}/device", params={
                "patient_id": patient_id,
                "mac_address": self.device_mac
            })
            device_resp.raise_for_status()
            device_data = device_resp.json()

            if not device_data:
                print(f"[DeviceEntity] Device {self.device_mac} not registered for patient {patient_id}")
                return

            device_id = device_data[0]["device_id"]
            print(f"[DeviceEntity] Found device ID: {device_id}")

            # 3. Get Entity info
            print(f"[DeviceEntity] Locating entity {self.name} ({self.entity_type})")
            entity_params = {
                "device_id": device_id,
                "entity_name": self.name,
                "entity_type": self.entity_type
            }
            entity_resp = requests.get(f"{API_BASE_URL}/entity", params=entity_params)
            entity_resp.raise_for_status()
            entity_data = entity_resp.json()

            if not entity_data:
                print(f"[DeviceEntity] Entity not found in registry")
                return

            entity_id = entity_data[0]["entity_id"]
            print(f"[DeviceEntity] Entity ID resolved: {entity_id}")

            # Set MQTT topic
            self.mqtt_topic = f"{patient_id}/{self.service_name}/{device_id}/{entity_id}"
            print(f"[DeviceEntity] MQTT topic configured: {self.mqtt_topic}")

            # 4. Service lookup
            print(f"[DeviceEntity] Verifying service {self.service_name}")
            service_resp = requests.get(f"{API_BASE_URL}/service", params={"name": self.service_name})
            service_resp.raise_for_status()
            service_data = service_resp.json()

            if not service_data:
                print(f"[DeviceEntity] Service {self.service_name} not registered")
                return

            service_id = service_data[0]["service_id"]
            print(f"[DeviceEntity] Service ID resolved: {service_id}")

            # 5. Endpoint management
            print(f"[DeviceEntity] Managing endpoint for entity {entity_id}")
            endpoint_params = {"service_id": service_id, "entity_id": entity_id}
            endpoint_resp = requests.get(f"{API_BASE_URL}/endpoint", params=endpoint_params)
            endpoint_resp.raise_for_status()
            endpoint_data = endpoint_resp.json()

            if endpoint_data:
                endpoint_id = endpoint_data[0]["endpoint_id"]
                if endpoint_data[0].get("endpoint") != self.mqtt_topic:
                    print(f"[DeviceEntity] Updating existing endpoint {endpoint_id}")
                    update_payload = {
                        "service_id": service_id,
                        "entity_id": entity_id,
                        "endpoint": self.mqtt_topic
                    }
                    update_url = f"{API_BASE_URL}/endpoint?endpoint_id={endpoint_id}"
                    update_resp = requests.put(update_url, json=update_payload)
                    update_resp.raise_for_status()
                    print(f"[DeviceEntity] Endpoint updated successfully")
                else:
                    print(f"[DeviceEntity] Endpoint already matches current topic")
            else:
                print(f"[DeviceEntity] Creating new endpoint")
                payload = {
                    "service_id": service_id,
                    "entity_id": entity_id,
                    "endpoint": self.mqtt_topic
                }
                post_resp = requests.post(f"{API_BASE_URL}/endpoint", json=payload)
                post_resp.raise_for_status()
                print(f"[DeviceEntity] New endpoint created successfully")

        except requests.RequestException as e:
            print(f"[DeviceEntity] HTTP error occurred: {e}")
        except Exception as ex:
            print(f"[DeviceEntity] Critical error during setup: {ex}")

    def read_data(self):
        """
        Simulate data read (for sensors).
        """
        print(f"[DeviceEntity] Simulating sensor read for {self.name}")
        value = random.randint(0, 100)
        print(f"[DeviceEntity] Sensor reading: {value}°C")
        return value

    def receive_data(self):
        """
        Receive data (for actuators).
        """
        if self.mqtt_topic:
            print(f"[DeviceEntity] Subscribing to MQTT topic: {self.mqtt_topic}")
            self.mqtt_handler.subscribe(self.mqtt_topic)
        else:
            print(f"[DeviceEntity] MQTT topic not set - subscription skipped")

    def send_data(self, data):
        """
        Publish data to MQTT (for sensors or actuators).
        """
        if self.mqtt_topic:
            print(f"[DeviceEntity] Publishing to {self.mqtt_topic}: {data}")
            self.mqtt_handler.publish(self.mqtt_topic, data)
        else:
            print(f"[DeviceEntity] Cannot publish data - MQTT topic not set")


class Device(ABC):
    """
    Base class for all devices.
    """
    def __init__(self, device_mac, user_passport, device_name=None, location=None, entities=[]):
        """
        Initialize a generic device with necessary identifiers and handlers.
        """
        print(f"[Device] Initializing device {device_mac}")
        self.name = device_name
        self.device_mac = device_mac
        self.user_passport = user_passport
        self.location = location
        self.entities = entities
        print(f"[Device] Device initialized with {len(entities)} entities")

    def add_entity(self, entity: DeviceEntity):
        """
        Adds an entity to the device's list of entities.
        """
        print(f"[Device] Adding entity: {entity.name} to device: {self.device_mac}")
        self.entities.append(entity)
        print(f"[Device] Device now has {len(self.entities)} entities")
