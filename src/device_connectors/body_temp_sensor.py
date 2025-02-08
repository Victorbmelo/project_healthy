import random
from src.device_connectors._device_factory import DeviceEntity

ENTITY_TYPE = 'sensor'
SERVICE_NAME = 'body_temp_check'


class BodyTemperatureSensor(DeviceEntity):
    def __init__(self):
        super().__init__(entity_type=ENTITY_TYPE, service_name=SERVICE_NAME)

    def read_data(self):
        """
        Simulate body temperature in °C.
        """
        temperature = round(random.uniform(36.0, 38.0), 2)
        print(f"Body Temperature Sensor - Data read: {temperature}°C")
        return temperature

    def send_data(self, b_temp):
        if self.mqtt_topic:
            data = {'body_temperature': b_temp}
            self.mqtt_handler.publish(self.mqtt_topic, str(data))
        else:
            print("MQTT topic not set. Data not sent.")
