import random
from abc import ABC
from src.database.sqlite_handler import DatabaseHandler
from src.mqtt.mqtt_handler import MqttHandler

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

    def set_mqtt_topic(self, passport_code):
        """
        Sets the MQTT topic for the entity.
        """
        query_get_topic = f"""
            SELECT
                u.patient_id,
                d.device_id,
                e.entity_id
            FROM
                Patients u
            JOIN
                Devices d ON d.patient_id = u.patient_id
            JOIN
                DeviceEntities e ON e.device_id = d.device_id
            JOIN
                Services s ON s.service_id = e.service_id
            WHERE
                u.passport_code = '{passport_code}'
                AND d.mac_address = '{self.device_mac}'
                AND e.entity_name = '{self.name}'
                AND e.entity_type = '{self.entity_type}';
        """
        result = self.db_handler.query_data(query_get_topic)
        if result:
            patient_id, device_id, entity_id = result[0]
            self.mqtt_topic = f"/{patient_id}/{self.service_name}/{device_id}/{entity_id}"
            query_set_endpoint = f"""
                INSERT INTO Endpoints (service_id, entity_id, endpoint)
                VALUES (
                    (SELECT service_id FROM Services WHERE name = '{self.service_name}'),
                    {entity_id},
                    '{self.mqtt_topic}'
                )
                ON CONFLICT(service_id, entity_id)
                DO UPDATE SET endpoint = excluded.endpoint
                WHERE endpoint != excluded.endpoint;
            """
            self.db_handler.execute_query(query_set_endpoint)
        else:
            print(f"No topic could be set for query {query_get_topic} \nCheck the entity details.")

    def read_data(self):
        """
        Simulate data read (for sensors).
        """
        value = random.randint(0, 100)
        print(f"Data read: {value}°C")
        return value

    def send_data(self, data):
        """
        Publish data to MQTT (for sensors or actuators).
        """
        if self.mqtt_topic:
            self.mqtt_handler.publish(self.mqtt_topic, data)
            print(f"Data sent to MQTT topic {self.mqtt_topic}: {data}")
        else:
            print("MQTT topic is not set. Data not sent.")


class Device(ABC):
    """
    Base class for all devices.
    """
    def __init__(self, device_mac, user_passport, device_name=None, location=None, entities=[]):
        """
        Initialize a generic device with necessary identifiers and handlers.
        """
        self.name = device_name
        self.device_mac = device_mac
        self.user_passport = user_passport
        self.location = location
        self.entities = entities  # List of associated device entities (sensors/actuators)

    def add_entity(self, entity: DeviceEntity):
        """
        Adds an entity to the device's list of entities.
        """
        self.entities.append(entity)
