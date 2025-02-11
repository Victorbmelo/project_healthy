import random
from src.device_connectors._device_factory import DeviceEntity

ENTITY_TYPE = 'sensor'
SERVICE_NAME = 'body_temp_check'


class BodyTemperatureSensor(DeviceEntity):
    def __init__(self, *args, **kwargs):

        super().__init__(entity_type=ENTITY_TYPE, service_name=SERVICE_NAME, *args, **kwargs)

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
            self.mqtt_handler.publish(self.mqtt_topic, str(b_temp))
            print(f"Sending data: {data}, to {self.mqtt_topic}.")
        else:
            print("MQTT topic not set. Data not sent.")
