import os
import requests
import paho.mqtt.client as mqtt
import schedule
import time
from datetime import datetime

# Define the base URL for your API endpoints (update as needed)
DB_CONNECTOR_URL = os.getenv('DB_CONNECTOR_URL', 'http://localhost:8080')
BROKER_MQTT_URL = os.getenv('BROKER_MQTT_URL', 'mqtt3.thingspeak.com')
BROKER_MQTT_PORT = os.getenv('BROKER_MQTT_PORT', 1883)


class SchedulerService:
    def __init__(self, api_url, mqtt_broker, mqtt_port=1883):
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_client = mqtt.Client()
        print(f"[SchedulerService] Initialized with API: {api_url}, MQTT Broker: {mqtt_broker}:{mqtt_port}")

    def get_current_schedules(self):
        """
        Fetch all schedules for the current day from the API and then, using the current time,
        select those whose start_time or end_time is due (within a tolerance window).
        """
        current_dt = datetime.now()
        current_time = current_dt.time()
        current_day = current_dt.strftime("%A")
        tolerance_minutes = 1  # tolerance window of 1 minute

        # Fetch all schedules for the current day.
        params = {"day_of_week": current_day}
        print(f"[SchedulerService] Fetching schedules for {current_day}")
        try:
            response = requests.get(f"{DB_CONNECTOR_URL}/schedule", params=params)
            if response.status_code != 200:
                print(f"[SchedulerService] Error fetching schedules: HTTP {response.status_code}")
                return []
            schedules = response.json()
            print(f"[SchedulerService] Found {len(schedules)} schedules for {current_day}")

            # Helper function to convert a HH:MM time string to minutes since midnight.
            def to_minutes(time_str):
                t = datetime.strptime(time_str, "%H:%M").time()
                return t.hour * 60 + t.minute

            current_minutes = current_time.hour * 60 + current_time.minute
            triggered = []

            for sched in schedules:
                sched_start = to_minutes(sched["start_time"])
                # Check for an optional end_time.
                sched_end = to_minutes(sched["end_time"]) if sched.get("end_time") else None

                # If current time is within tolerance of the start time, fire the scheduled action.
                if abs(current_minutes - sched_start) < tolerance_minutes:
                    triggered.append({
                        "entity_id": sched["entity_id"],
                        "action": sched["action"],
                        "schedule_id": sched["schedule_id"],
                        "repeat": sched.get("repeat", 1)
                    })
                # If there's an end_time, check whether it is time to reverse the action.
                elif sched_end is not None and abs(current_minutes - sched_end) < tolerance_minutes:
                    # Reverse the action (assumes binary actions: ON becomes OFF, OFF becomes ON)
                    reverse_action = "OFF" if sched["action"] == "ON" else "ON"
                    triggered.append({
                        "entity_id": sched["entity_id"],
                        "action": reverse_action,
                        "schedule_id": sched["schedule_id"],
                        "repeat": sched.get("repeat", 1)
                    })

            return triggered

        except Exception as e:
            print(f"[SchedulerService] Failed to fetch schedules: {str(e)}")
            return []

    def send_mqtt_command(self, entity_id, action):
        print(f"[SchedulerService] Retrieving endpoint for entity {entity_id}")
        try:
            response = requests.get(f"{DB_CONNECTOR_URL}/endpoint", params={'entity_id': entity_id})
            if response.status_code != 200:
                print(f"[SchedulerService] Error getting endpoint: HTTP {response.status_code}")
                return

            endpoints = response.json()
            if not endpoints:
                print(f"[SchedulerService] No endpoint found for entity {entity_id}")
                return

            topic = endpoints[0]['endpoint']
            print(f"[SchedulerService] Sending {action} to {topic}")

            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.mqtt_client.publish(topic, action)
            self.mqtt_client.disconnect()
            print(f"[SchedulerService] Successfully sent {action} to {topic}")

        except Exception as e:
            print(f"[SchedulerService] Failed to send command: {str(e)}")

    def delete_schedule(self, schedule_id):
        """
        Deletes a schedule using the API if it is non-repeating.
        """
        try:
            response = requests.delete(f"{DB_CONNECTOR_URL}/schedule", params={"schedule_id": schedule_id})
            if response.status_code == 200:
                print(f"[SchedulerService] Schedule {schedule_id} deleted successfully")
            else:
                print(f"[SchedulerService] Failed to delete schedule {schedule_id}: HTTP {response.status_code}")
        except Exception as e:
            print(f"[SchedulerService] Error deleting schedule {schedule_id}: {e}")

    def check_schedules(self):
        print("[SchedulerService] Checking for scheduled actions...")
        # Get schedules that are due based on the current time.
        due_schedules = self.get_current_schedules()
        for sched in due_schedules:
            entity_id = sched["entity_id"]
            action = sched["action"]
            schedule_id = sched["schedule_id"]
            repeat = sched.get("repeat", 1)
            print(f"[SchedulerService] Processing schedule {schedule_id}: Entity {entity_id} -> {action}")
            self.send_mqtt_command(entity_id, action)

            # If the schedule is not repeating, delete it.
            if repeat in [0, False]:
                self.delete_schedule(schedule_id)
        if not due_schedules:
            print("[SchedulerService] No schedules due at the current time")

    def start_scheduler(self):
        print("[SchedulerService] Starting scheduler service")
        print("[SchedulerService] Schedule checks will run every minute")
        schedule.every().minute.do(self.check_schedules)

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[SchedulerService] Shutting down scheduler service")

if __name__ == "__main__":
    api_url = "http://your-api-url"           # update with your actual API URL
    mqtt_broker = "mqtt.broker.address"         # update with your MQTT broker address

    print("[SchedulerService] Initializing service instance")
    scheduler_service = SchedulerService(api_url, mqtt_broker)

    print("[SchedulerService] Starting main execution")
    scheduler_service.start_scheduler()
