import random
from src.device_connectors._device_factory import DeviceEntity

ENTITY_TYPE = 'sensor'
SERVICE_NAME = 'blood_pressure'


class BloodPressureSensor(DeviceEntity):
    def __init__(self):
        super().__init__(entity_type=ENTITY_TYPE, service_name=SERVICE_NAME)

    def read_data(self):
        """
        Simulate blood pressure in mmHg.
        """
        systolic = random.randint(90, 140)
        diastolic = random.randint(60, 90)
        blood_pressure = f"{systolic}/{diastolic}"
        print(f"Blood Pressure Sensor - Data read: {blood_pressure} mmHg")
        return blood_pressure

    def send_data(self, blood_press):
        if self.mqtt_topic:
            data = {'blood_pressure': blood_press}
            self.mqtt_handler.publish(self.mqtt_topic, data)
        else:
            print("MQTT topic not set. Data not sent.")
