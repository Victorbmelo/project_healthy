import random
from src.device_connectors._device_factory import DeviceEntity

ENTITY_TYPE = 'sensor'
SERVICE_NAME = 'air_conditioning'


class TemperatureHumiditySensor(DeviceEntity):
    def __init__(self):
        super().__init__(entity_type=ENTITY_TYPE, service_name=SERVICE_NAME)

    def read_data(self):
        """
        Simulate temperature and humidity.
        """
        temperature = round(random.uniform(15.0, 35.0), 2)
        humidity = random.randint(0, 100)
        print(f"Temperature: {temperature}°C, Humidity: {humidity}%")
        return temperature, humidity

    def send_data(self, temp, hum):
        if self.mqtt_topic:
            data = {'temperature': temp, 'humidity': hum}
            self.mqtt_handler.publish(self.mqtt_topic, data)
        else:
            print("MQTT topic not set. Data not sent.")
