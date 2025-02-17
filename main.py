import random
import signal
import sys
import time
import threading

from src.mqtt.mqtt_handler import MqttHandler
from src.database.sqlite_handler import DatabaseHandler

from src.services.air_conditioning.air_conditioning_service import AirConditioningService
from src.services.blood_pressure.blood_pressure_service import BloodPressureService
from src.services.body_temperature.body_temperature_service import BodyTemperatureService
from src.services.schedules.schedule_service import SchedulerService
from src.services.thingspeak.thingspeak_adapter import ThingSpeakAdapter

from src.device_connectors._device_factory import Device, DeviceEntity
from src.device_connectors.humidity_sensor import HumiditySensor
from src.device_connectors.body_temp_sensor import BodyTemperatureSensor
from src.device_connectors.blood_pressure_sensor import BloodPressureSensor
from src.device_connectors.lamp_actuator import LampActuator

stop_event = threading.Event()


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
        time_to_sleep = random.randint(20, 30)
        entity.send_data(entity.read_data())
        time.sleep(time_to_sleep)

def signal_handler(sig, frame):
    print("Shutting down...")
    stop_event.set()
    sys.exit(0)

# Register the signal handler for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)


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
    temp_humidity_sensor = HumiditySensor(name='Humidity Sensor', device_mac=device_mac1, db_handler=db_handler, mqtt_handler=mqtt_handler)
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
    action_button = LampActuator(name='Bedroom Lamp', device_mac=device_mac3, db_handler=db_handler, mqtt_handler=mqtt_handler)
    action_button.set_mqtt_topic(passport_code=patient_passport2)
    action_button.receive_data()


    # ================================================  Init ServiceManager
    service = SchedulerService('http://localhost:8080', 'localhost')
    t5 = threading.Thread(target=service.start_scheduler, args=[])
    t5.daemon = True
    # t5.start()

    # service_manager = ServiceManager()
    # service_manager.start_service('air_conditioning')
    # service_manager.start_service('blood_pressure')
    # service_manager.start_service('body_temperature')
    # service_manager.start_service('scheduler')
    # service_manager.start_service('thingspeak')

    # # Create and start threads
    threads = []
    sensors = [body_temp_sensor, temp_humidity_sensor, blood_pressure_sensor2, air_temp_sensor]
    for sensor in sensors:
        t = threading.Thread(target=simulate_sensors_data, args=[sensor])
        t.daemon = True
        t.start()
        threads.append(t)

    t5.start()
    threads.append(t5)

    # Wait for threads to finish (block main thread)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Main program interrupted. Stopping threads...")
        stop_event.set()
        for t in threads:
            t.join()  # Wait for threads to finish
        print("All threads stopped. Exiting.")


if __name__ == "__main__":
    main()