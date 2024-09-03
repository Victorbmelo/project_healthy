import random
import time
import requests
import paho.mqtt.client as mqtt


MQTT_BROKER = "localhost"
MQTT_TOPIC = "environment/temperature"
MQTT_COMMAND_TOPIC = "ac/control"

THINGSPEAK_API_KEY = "1EQ3TK07SJHN8FSQ"
THINGSPEAK_URL = "https://api.thingspeak.com/update"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    temperature, humidity = map(float, msg.payload.decode().split(','))
    print(f"Received temperature: {temperature} °C, humidity: {humidity} %")

    # Envia a temperatura e umidade para o ThingSpeak
    data = {'api_key': THINGSPEAK_API_KEY, 'field1': temperature, 'field2': humidity}
    requests.get(THINGSPEAK_URL, params=data)

    # Ajusta o ar condicionado baseado na temperatura e umidade
    if temperature > 25:
        print("Temperature too high, adjusting air conditioning...")
        client.publish(MQTT_COMMAND_TOPIC, "set_cool")
    elif temperature < 18:
        print("Temperature too low, adjusting air conditioning...")
        client.publish(MQTT_COMMAND_TOPIC, "set_heat")
    else:
        print("Temperature is optimal, keeping current settings.")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, 1883, 60)
client.loop_forever()
