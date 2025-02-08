from src.device_connectors._device_factory import DeviceEntity

ENTITY_TYPE = 'actuator'
SERVICE_NAME = 'action'


class ActionButton(DeviceEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(entity_type=ENTITY_TYPE, service_name=SERVICE_NAME, *args, **kwargs)

    def send_data(self, action):
        if self.mqtt_topic:
            if action == "press":
                print(f"Action Button - Button pressed")
                self.mqtt_handler.publish(self.mqtt_topic, "button_pressed")
            else:
                print(f"Unknown action: {action}")
        else:
            print("MQTT topic not set. Action not sent.")
