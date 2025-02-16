import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
import time
from MyMQTT import *
import matplotlib.pyplot as plt
import io
import numpy as np
import os

###### The URLs in the code to be able to change easily for dockerisation
thinkspeak_URL = "http://localhost:8081"
db_connector_URL = "http://localhost:8080"

class dbHandler:
    exposed = True
    ### Send passport code to dB connector
    @staticmethod
    def GetRequest(passport_code):
        url = f"{db_connector_URL}/patient?passport_code={passport_code}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()  ######Get data according to this passport_code
                return data if data else None
            return None
        except requests.exceptions.Timeout:
            print("Error: Request to patient API timed out.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error: Failed to connect to patient API - {e}")
            return None
    #####################################################################    
    ######This part is used to save chat_ID in the database using /telegrambot API  
    @staticmethod
    def SaveChatID(bot_token, chat_ID, patient_id):
        url = f"{db_connector_URL}/telegrambot"
        payload = {
            "bot_token": bot_token,
            "chat_id": str(chat_ID),
            "patient_id": int(patient_id)
        }
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                print(f"✅ Chat ID {chat_ID} saved for patient {patient_id}.")
            else:
                print(f"⚠️ Failed to save chat ID. Status Code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

    ########################################################
    ###Retrieve chat_ID from the database for a given patient ID   
    @staticmethod
    def GetChatID(patient_id):
        url = f"{db_connector_URL}/telegrambot?patient_id={patient_id}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(data)
                # return data[0].get("chat_id")
                return [chat["chat_id"] for chat in data] 
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

class ThingSpeakHandler:
    @staticmethod
    def get_data(passport_code):
        url = f"{thinkspeak_URL}/thingspeak?passport_code={passport_code}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: Received status code {response.status_code} from ThingSpeak API.")
                return None
        except requests.exceptions.Timeout:
            print("Error: Request to ThingSpeak API timed out.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error: Failed to connect to ThingSpeak API - {e}")
            return None

class HealthmonitorBot:
    def __init__(self, token, broker, port, topic ):
        self.tokenBot = token
        self.bot = telepot.Bot(self.tokenBot)
        self.client = MyMQTT("telegramBotClientID", broker, port, None)
        self.client.start()
        alert_topic = "+/alert"
        self.client.mySubscribe(alert_topic)
        MessageLoop(self.bot, {'chat': self.on_chat_message, 'callback_query': self.on_callback_query}).run_as_thread()
        self.client._paho_mqtt.on_message = self.notify

    ##Handles MQTT messages and alerts the correct patient via Telegram
    def notify(self, client, userdata, msg):
        try:
            topic = msg.topic
            msg = msg.payload.decode()  # Decode MQTT message
            print(f"🔔 Received Alert: {msg} on topic {topic}")
            ### Extract patient ID from topic format 'patient ID/alert'
            patient_id = topic.split("/alert")[0]  
            # Retrieve chat ID from the database
            chat_IDs = dbHandler.GetChatID(patient_id)
            for chat_ID in chat_IDs:
                if chat_ID:
                    alert_message = f"🚨 *Emergency Alert for this Patient!* 🚨\n{msg}"
                    self.bot.sendMessage(chat_ID, text=alert_message, parse_mode="Markdown")
                else:
                    print(f"[WARNING] No chat ID found for patient {patient_id}")

        except Exception as e:
            print(f"Error processing MQTT message: {e}")

    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']

        if message == "/start":
            self.bot.sendMessage(chat_ID, text='👋 Welcome to the **Healthcare Monitor** 🏥')
            self.bot.sendMessage(chat_ID, text='📄Please Enter the Passport Code of the Patient You Want to Monitor.')
    
        elif message.isalnum():
            passport_code = message
            data = dbHandler.GetRequest(passport_code)

            if not data:
                self.bot.sendMessage(chat_ID, text="❌The Passport Code Does Not Exist.")
            else:
                self.bot.sendMessage(chat_ID, text="✅The Passport Code is Received Correctly.")
                #self.bot.sendMessage(chat_ID, text=f"Your chat id is: {chat_ID}")
                patient_id = data[0]["patient_id"]
                dbHandler.SaveChatID(1, chat_ID, patient_id)

                # these are shown on bot
                buttons = [[
                    InlineKeyboardButton(text='🩺Blood Pressure', callback_data=f'blood_pressure:{passport_code}'),
                    InlineKeyboardButton(text='🌡️Temperature', callback_data=f'temperature:{passport_code}')
                ]]
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                self.bot.sendMessage(chat_ID, text='❤️What Do You Want to Monitor?', reply_markup=keyboard)
    
    #this function will run when you get something from keyboard 
    def on_callback_query(self, msg):
        query_ID, chat_ID, query_data = telepot.glance(msg, flavor='callback_query')
        self.bot.answerCallbackQuery(query_ID)
        print(chat_ID, "chat id here")

        passport_code = query_data.split(':')[-1]
        data = ThingSpeakHandler.get_data(passport_code)

        if not data:
            self.bot.sendMessage(chat_ID, text="Error retrieving data from ThingSpeak.")
            return

        print(f"Query Data: {query_data}")
        print(f"ThingSpeak Data: {data}")

        def find_sensor_data(sensor_name):
            """Helper function to find sensor data across multiple devices."""
            sensor_values = []
            for device in data:
                for sensor in device['Sensors']:
                    if sensor['Name'] == sensor_name:
                        sensor_values.extend(sensor['Values'])
            return sensor_values if sensor_values else None            
            

        if "blood_pressure:" in query_data and "current_data" not in query_data and "historical_data" not in query_data:
            buttons = [
                [InlineKeyboardButton(text='📊Current Data🩺', callback_data=f'current_data:blood_pressure:{passport_code}')],
                [InlineKeyboardButton(text='📜Historical Data🩺', callback_data=f'historical_data:blood_pressure:{passport_code}')]
            ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text='Choose the data type:', reply_markup=keyboard)

        elif "temperature:" in query_data and "current_data" not in query_data and "historical_data" not in query_data:
            buttons = [
                [InlineKeyboardButton(text='📊Current Data🌡️', callback_data=f'current_data:temperature:{passport_code}')],
                [InlineKeyboardButton(text='📜Historical Data🌡️', callback_data=f'historical_data:temperature:{passport_code}')]
            ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text='Choose the data type:', reply_markup=keyboard)

        elif "current_data:blood_pressure:" in query_data:
            values = find_sensor_data('blood_pressure')
            if values:
                current_value = values[-1]['value']
                self.bot.sendMessage(chat_ID, text=f"Current Blood Pressure🩺: {current_value} mmHg")
            else:
                self.bot.sendMessage(chat_ID, text="⚠️ No current blood pressure data found.")    

        # historical blood pressure
        elif "historical_data:blood_pressure:" in query_data:
            values = find_sensor_data('blood_pressure')
            if values:
                timestamps = [item['created_at'] for item in values]
                readings = [item['value'] for item in values]

                image_stream = self.plot_historical_data(timestamps, readings, "Blood Pressure Historical Data", "Blood Pressure (mmHg)")
                self.bot.sendPhoto(chat_ID, photo=image_stream)
            else:
                self.bot.sendMessage(chat_ID, text="⚠️ No historical blood pressure data found.")

            #current body temperature
        elif "current_data:temperature:" in query_data:
            values = find_sensor_data('body_temperature')
            if values:
                current_value = values[-1]['value']
                self.bot.sendMessage(chat_ID, text=f"🌡️ Current Body Temperature: {current_value}°C")
            else:
                self.bot.sendMessage(chat_ID, text="⚠️ No current body temperature data found.")

        #Retrieve historical body temperature
        elif "historical_data:temperature:" in query_data:
            values = find_sensor_data('body_temperature')
            if values:
                timestamps = [item['created_at'] for item in values]
                readings = [item['value'] for item in values]

                image_stream = self.plot_historical_data(timestamps, readings, "Body Temperature Historical Data", "Body Temperature (°C)")
                self.bot.sendPhoto(chat_ID, photo=image_stream)
            else:
                self.bot.sendMessage(chat_ID, text="⚠️ No historical temperature data found.")
    
    def plot_historical_data(self, timestamps, readings, title, ylabel):

        #### when I want to plot the graph in telegram bot since many datas make the graph invisible I only choose limited numbers
        MAX_POINTS = 20
        
        if not timestamps or not readings:
            print("[ERROR] No historical data available to plot.")
            return None
        if len(timestamps) > MAX_POINTS:
            indices = np.linspace(0, len(timestamps) - 1, MAX_POINTS, dtype=int)
            timestamps = [timestamps[i] for i in indices]
            readings = [readings[i] for i in indices]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(timestamps, readings, marker='o', linestyle='-', color='b', label=ylabel)
        ax.set_xlabel("Timestamp")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend()
        ax.grid(True)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        image_stream = io.BytesIO()
        plt.savefig(image_stream, format='png', bbox_inches='tight')
        image_stream.seek(0)

        return image_stream

if __name__ == "__main__":
    
    # Get the directory of the current script
    # add this code so the problem of setting.json was solved (not nevessary to use the local address)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(BASE_DIR, "settings.json")

    # Load JSON
    conf = json.load(open(config_path))
    token = conf["telegramToken"]
    broker = conf["brokerIP1"]
    port = conf["brokerPort"]
    topic = conf["mqttTopic"]
    sb = HealthmonitorBot(token, broker, port, topic)

    while True:
        time.sleep(3)
