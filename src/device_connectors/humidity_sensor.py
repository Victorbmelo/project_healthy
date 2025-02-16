import random
from src.device_connectors._device_factory import DeviceEntity

ENTITY_TYPE = 'sensor'
SERVICE_NAME = 'air_conditioning'


class HumiditySensor(DeviceEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(entity_type=ENTITY_TYPE, service_name=SERVICE_NAME, *args, **kwargs)

    def read_data(self):
        """
        Simulate humidity.
        """
        humidity = random.randint(0, 100)
        print(f"[HumiditySensor] Humidity: {humidity}%")
        return humidity

    def send_data(self, hum):
        if self.mqtt_topic:
            self.mqtt_handler.publish(self.mqtt_topic, hum)
        else:
            print("[HumiditySensor] MQTT topic not set. Data not sent.")
