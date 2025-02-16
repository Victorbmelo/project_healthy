import datetime
import requests
from src.device_connectors._device_factory import DeviceEntity

ENTITY_TYPE = 'actuator'
SERVICE_NAME = 'action'
API_BASE_URL = 'http://localhost:8080'  # Update with your API URL

class LampActuator(DeviceEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(entity_type=ENTITY_TYPE, service_name=SERVICE_NAME, *args, **kwargs)
        self.state = "OFF"
        self.entity_id = None
        self.patient_id = None
        self.device_id = None

    def receive_data(self):
        """Handle incoming MQTT commands"""
        super().receive_data()

        def command_handler(client, userdata, message):
            payload = message.payload.decode()
            rcvd_topic = message.topic
            patient_id, service_name, device_id, entity_id = rcvd_topic.lstrip('/').split('/')
            action = payload.upper()
            if action in ["ON", "OFF"]:
                print(f"[LampActuator] Received {action} command for {self.name}")
                self._update_actuator_state(entity_id, action)
            else:
                print(f"[LampActuator] Invalid command: {payload}")

        if self.mqtt_topic:
            self.mqtt_handler.client.message_callback_add(self.mqtt_topic, command_handler)

    def _update_actuator_state(self, entity_id, action):
        """Update both physical device and API state"""
        try:
            # Update physical state
            self.state = action
            if action == "ON":
                self._activate_hardware()
            else:
                self._deactivate_hardware()

            # Update API state
            timestamp_now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
            request_payload = {
                'last_reading': action,
                'last_reading_timestamp': timestamp_now
            }
            r = requests.put(f"{API_BASE_URL}/entity", params={'entity_id': entity_id}, json=request_payload)
            if r.status_code != 200:
                print(f"[SchedulerService] Error fetching schedules: HTTP {r.status_code} - {r.json()}")

            # Send confirmation
            self.send_data(action)

        except Exception as e:
            print(f"[LampActuator] Error updating state: {str(e)}")

    def _activate_hardware(self):
        """Implement actual hardware activation here"""
        # GPIO control or relay activation logic
        print("[LampActuator] Physical actuator turned ON")

    def _deactivate_hardware(self):
        """Implement actual hardware deactivation here"""
        # GPIO control or relay deactivation logic
        print("[LampActuator] Physical actuator turned OFF")

    def read_data(self):
        """Return current state through API"""
        try:
            res = requests.get(f"{API_BASE_URL}/entity", params={'entity_id': self.entity_id})
            return res.json()[0].get('last_reading', 'OFF')
        except Exception as e:
            print(f"[LampActuator] Error reading state: {str(e)}")
            return 'ERROR'