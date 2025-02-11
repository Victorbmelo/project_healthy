import random
import time
import threading

from src.mqtt.mqtt_handler import MqttHandler
from src.database.sqlite_handler import DatabaseHandler

from src.services.air_conditioning.air_conditioning_service import AirConditioningService
from src.services.blood_pressure.blood_pressure_service import BloodPressureService
from src.services.body_temperature.body_temperature_service import BodyTemperatureService
from src.services.thingspeak.thingspeak_adapter import ThingSpeakAdapter

from src.device_connectors._device_factory import Device, DeviceEntity
from src.device_connectors.temperature_humidity_sensor import TemperatureHumiditySensor
from src.device_connectors.body_temp_sensor import BodyTemperatureSensor
from src.device_connectors.blood_pressure_sensor import BloodPressureSensor
from src.device_connectors.button_actuator import ActionButton


class ServiceManager:
    def __init__(self):
        self.mqtt_handler = MqttHandler('service-manager')
        self.thingspeak_adapter = ThingSpeakAdapter()

    def start_service(self, service_name):
        if service_name == 'air_conditioning':
            service = AirConditioningService()
            service.start()
        elif service_name == 'blood_pressure':
            service = BloodPressureService()
            service.start()
        elif service_name == 'body_temperature':
            service = BodyTemperatureService()
            service.start()
        elif service_name == 'thingspeak':
            self.thingspeak_adapter.start_server()
        else:
            print(f"Service {service_name} is not available.")


def simulate_sensors_data(entity: DeviceEntity):
    print(f"Starting Sensor Simulation for {entity.name}.")
    while True:
        time_to_sleep = random.randint(10, 20)
        entity.send_data(entity.read_data())
        time.sleep(time_to_sleep)


def main():
    db_handler = DatabaseHandler()
    db_handler.connect()
    db_handler.create_tables()

    mqtt_handler = MqttHandler('simulation')
    mqtt_handler.connect()

    # ===============================================  SETUP
    # ****************** PATIENT 1
    patient1 = 'Pedro Loa'
    patient_passport1 = 'P12345678'
    # --------- device 1
    device_name1 = 'RPi 4'
    device_mac1 = '001B44113A'
    device1 = Device(device_mac=device_mac1, user_passport=patient_passport1, device_name=device_name1)
    # ---------- Init sensors
    body_temp_sensor = BodyTemperatureSensor(name='Temperature Sensor', device_mac=device_mac1, db_handler=db_handler, mqtt_handler=mqtt_handler)
    body_temp_sensor.set_mqtt_topic(passport_code=patient_passport1)
    temp_humidity_sensor = TemperatureHumiditySensor(name='Humidity Sensor', device_mac=device_mac1, db_handler=db_handler, mqtt_handler=mqtt_handler)
    temp_humidity_sensor.set_mqtt_topic(passport_code=patient_passport1)
    blood_pressure_sensor2 = BloodPressureSensor(name='Blood Pressure2', device_mac=device_mac1, db_handler=db_handler, mqtt_handler=mqtt_handler)
    blood_pressure_sensor2.set_mqtt_topic(passport_code=patient_passport1)

    # ******************* PATIENT 2
    patient2 = 'Joao Town'
    patient_passport2 = 'P23456789'
    # ---------- device 2
    device_name2 = 'RPi Zero'
    device_mac2 = 'FF1B44113A'
    device2 = Device(device_mac=device_mac2, user_passport=patient_passport2, device_name=device_name2)
    # ---------- device 3
    device_name3 ='Arduino'
    device_mac3 = 'DD1B44113F'
    device3 = Device(device_mac=device_mac3, user_passport=patient_passport2, device_name=device_name3)
    # ---------- Init sensors
    blood_pressure_sensor = BloodPressureSensor(name='Blood Pressure', device_mac=device_mac2, db_handler=db_handler, mqtt_handler=mqtt_handler)
    blood_pressure_sensor.set_mqtt_topic(passport_code=patient_passport2)
    air_temp_sensor = BodyTemperatureSensor(name='Temperature Sensor2', device_mac=device_mac3, db_handler=db_handler, mqtt_handler=mqtt_handler)
    air_temp_sensor.set_mqtt_topic(passport_code=patient_passport2)
    # ---------- Init actuators
    # action_button = ActionButton(device_mac=device_mac3, db_handler=db_handler, mqtt_handler=mqtt_handler)
    # action_button.set_mqtt_topic(passport_code=user_passport2)


    # ================================================  Init ServiceManager
        # simulate readings and actions
    # t = threading.Thread(target=simulate_sensors_data, args=[body_temp_sensor])
    # t.daemon = True
    # t.start()
    # t2 = threading.Thread(target=simulate_sensors_data, args=[temp_humidity_sensor])
    # t2.daemon = True
    # t2.start()
    # t3 = threading.Thread(target=simulate_sensors_data, args=[blood_pressure_sensor2])
    # t3.daemon = True
    # t3.start()
    # t4 = threading.Thread(target=simulate_sensors_data, args=[air_temp_sensor])
    # t4.daemon = True
    # t4.start()
    # threading.Thread(target=simulate_sensors_data, args=[action_button]).start()

    service_manager = ServiceManager()
    # service_manager.start_service('air_conditioning')
    # service_manager.start_service('blood_pressure')
    # service_manager.start_service('body_temperature')
    service_manager.start_service('thingspeak')


if __name__ == "__main__":
    main()