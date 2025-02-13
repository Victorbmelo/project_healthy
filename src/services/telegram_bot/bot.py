import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
import time
from MyMQTT import *

class dbHandler:
    exposed = True

    @staticmethod
    def GetRequest(passport_code):
        url = f"http://localhost:8080/patient?passport_code={passport_code}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data if data else None
            return None
        except requests.exceptions.Timeout:
            print("Error: Request to patient API timed out.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error: Failed to connect to patient API - {e}")
            return None

class ThingSpeakHandler:
    @staticmethod
    def get_data(passport_code):
        url = f"http://localhost:8081/thingspeak?passport_code={passport_code}"
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
    def __init__(self, token, broker, port, topic):
        self.tokenBot = token
        self.bot = telepot.Bot(self.tokenBot)
        self.client = MyMQTT("telegramBotClientID", broker, port, None)
        self.client.start()
        self.topic = topic
        MessageLoop(self.bot, {'chat': self.on_chat_message, 'callback_query': self.on_callback_query}).run_as_thread()

    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']

        if message == "/start":
            self.bot.sendMessage(chat_ID, text='👋 Welcome to the **Healthcare Monitor** 🏥')
            self.bot.sendMessage(chat_ID, text='📄Please Enter the Passport Code of the Patient You Want to Monitor.')
        else:
            passport_code = message
            data = dbHandler.GetRequest(passport_code)

            if not data:
                self.bot.sendMessage(chat_ID, text="❌The Passport Code Does Not Exist.")
            else:
                self.bot.sendMessage(chat_ID, text="✅The Passport Code is Received Correctly.")
                # these are shown on bot
                buttons = [[
                    InlineKeyboardButton(text='🩺Blood Pressure', callback_data=f'blood_pressure:{passport_code}'),
                    InlineKeyboardButton(text='🌡️Temperature', callback_data=f'temperature:{passport_code}')
                ]]
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                self.bot.sendMessage(chat_ID, text='❤️What Do You Want to Monitor?', reply_markup=keyboard)

    
    #this function will run when you get something from keyboard or from other API(microservice)  you get something
    def on_callback_query(self, msg):
        query_ID, chat_ID, query_data = telepot.glance(msg, flavor='callback_query')
        self.bot.answerCallbackQuery(query_ID)

        passport_code = query_data.split(':')[-1]
        data = ThingSpeakHandler.get_data(passport_code)

        if not data:
            self.bot.sendMessage(chat_ID, text="Error retrieving data from ThingSpeak.")
            return

        print(f"Query Data: {query_data}")
        print(f"ThingSpeak Data: {data}")

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
            for sensor in data[0]['Sensors']:
                if sensor['Name'] == 'blood_pressure' and sensor['Values']:
                    current_value = sensor['Values'][-1]['value']
                    self.bot.sendMessage(chat_ID, text=f"Current Blood Pressure🩺: {current_value} mmHg")
                    return

        elif "historical_data:blood_pressure:" in query_data:
            historical_data_message = "Blood Pressure Historical Data🩺:\n"
            for sensor in data[0]['Sensors']:
                if sensor['Name'] == 'blood_pressure':
                    for item in sensor['Values']:
                        historical_data_message += f"{item['created_at']}: {item['value']} mmHg\n"
                    break
            self.bot.sendMessage(chat_ID, text=historical_data_message if historical_data_message.strip() else "No historical data available.")
            return

        elif "current_data:temperature:" in query_data:
            for sensor in data[0]['Sensors']:
                if sensor['Name'] == 'body_temperature' and sensor['Values']:
                    current_value = sensor['Values'][-1]['value']
                    self.bot.sendMessage(chat_ID, text=f"Current Body Temperature🌡️: {current_value}°C")
                    return

        elif "historical_data:temperature:" in query_data:
            historical_data_message = "Temperature Historical Data🌡️:\n"
            for sensor in data[0]['Sensors']:
                if sensor['Name'] == 'body_temperature':
                    for item in sensor['Values']:
                        historical_data_message += f"{item['created_at']}: {item['value']}°C\n"
                    break
            self.bot.sendMessage(chat_ID, text=historical_data_message if historical_data_message.strip() else "No historical data available.")
            return

if __name__ == "__main__":
    conf = json.load(open("D:/IOT_september_2024/git_project_healthy_main/project_healthy/src/services/telegram_bot/settings.json"))
    token = conf["telegramToken"]
    broker = conf["brokerIP"]
    port = conf["brokerPort"]
    topic = conf["mqttTopic"]
    sb = HealthmonitorBot(token, broker, port, topic)

    while True:
        time.sleep(2)
