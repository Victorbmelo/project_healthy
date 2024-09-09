import random
import time
import requests

THINGSPEAK_API_KEY = "3V25SV0ZSM19IAXY"
THINGSPEAK_URL = "https://api.thingspeak.com/update"

def check_body_temperature():
    while True:
        # Simulate
        temperature = round(random.uniform(35.0, 41.0), 1)
        print(f"Current body temperature: {temperature} °C")

        # Send to ThingSpeak
        data = {'api_key': THINGSPEAK_API_KEY, 'field1': temperature}
        requests.get(THINGSPEAK_URL, params=data)

        # Simulate ML
        if temperature > 39.5:
            print("High fever detected! Turning on red lamp and playing sound on the speaker...")
            # Telegram and device connector
        elif temperature > 38.0:
            print("Fever detected! Sending alert to Telegram bot and dashboard...")
            # Telegram code and device connector

        time.sleep(10)  # Espera 10 segundos antes de próxima leitura


if __name__ == '__main__':
    check_body_temperature()
