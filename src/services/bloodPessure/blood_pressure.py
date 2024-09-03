import requests
import paho.mqtt.client as mqtt

# Configurações MQTT
MQTT_BROKER = "localhost"
MQTT_TOPIC = "patient/bloodpressure"
MQTT_ALERT_TOPIC = "alert/bloodpressure"

# Configurações ThingSpeak
THINGSPEAK_API_KEY = "XFY9PA7R7E563C4I"
THINGSPEAK_URL = "https://api.thingspeak.com/update"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    blood_pressure = float(msg.payload.decode())
    print(f"Received blood pressure: {blood_pressure} mmHg")

    # Envia a pressão arterial para o ThingSpeak
    data = {'api_key': THINGSPEAK_API_KEY, 'field1': blood_pressure}
    requests.get(THINGSPEAK_URL, params=data)

    # Verifica se a pressão está em um nível preocupante
    if blood_pressure > 140 or blood_pressure < 60:
        print("Abnormal blood pressure detected! Sending alert...")
        client.publish(MQTT_ALERT_TOPIC, f"Alert: blood pressure is {blood_pressure} mmHg")
        # Adicione aqui o código para ativar dispositivos ou enviar alertas via Telegram

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, 1883, 60)
client.loop_forever()
