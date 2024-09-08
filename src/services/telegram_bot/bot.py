import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
import time
from MyMQTT import *
import paho.mqtt.client as PahoMQTT


user_credentials = {
    "user1": {"password": "P@ssw0rd123", "chat_ID": ""},
    "user2": {"password": "Qw3rtY!89", "chat_ID": ""},
    "user3": {"password": "Secur3@987", "chat_ID": ""},
    "user4": {"password": "Adm1n#456", "chat_ID": ""},
    "user5": {"password": "PassW0rd!76", "chat_ID": ""}
}


patients_ID = {
    "12345": [70,38.5],
    "6789": [60,40],
    
}

historical_data = {
    "12345": [
        {"day": 1, "blood_pressure": 120, "temperature": 37.1},
        {"day": 2, "blood_pressure": 125, "temperature": 37.3},
        {"day": 3, "blood_pressure": 118, "temperature": 37.0},
        {"day": 4, "blood_pressure": 122, "temperature": 37.2},
        {"day": 5, "blood_pressure": 121, "temperature": 37.4}
    ],
    "6789": [
        {"day": 1, "blood_pressure": 130, "temperature": 38.0},
        {"day": 2, "blood_pressure": 128, "temperature": 37.9},
        {"day": 3, "blood_pressure": 132, "temperature": 38.1},
        {"day": 4, "blood_pressure": 129, "temperature": 38.0},
        {"day": 5, "blood_pressure": 131, "temperature": 38.2}
    ]
}



            
            


class HealthmonitorBot:
    def __init__(self, token, broker, port, topic):
        # Local token
        self.tokenBot = token
        self.bot = telepot.Bot(self.tokenBot)
        self.client = MyMQTT("telegramBotClientID", broker, port, None)
        self.client.start()
        self.topic = topic
        self.__message = {'bn': "telegramBot",
                          'e':
                          [
                              {'n': 'switch', 'v': '', 't': '', 'u': 'bool'},
                          ]
                          }
        MessageLoop(self.bot, {'chat': self.on_chat_message,
                               'callback_query': self.on_callback_query}).run_as_thread()

    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']
        
        if message == "/start":
            self.bot.sendMessage(chat_ID, text='Welcome to healthcare monitor')
            self.bot.sendMessage(chat_ID, text='please enter your username and password: for example \nuser:sample \npassword:sample')
        elif "user:" in message and "password:" in message:
            # Splitting the string by new lines
            lines = message.splitlines()
            if len(lines) == 2:

                input_user = lines[0].replace("user:", "", 1)
                input_password = lines[1].replace("password:", "", 1)
                
            else:
                self.bot.sendMessage(chat_ID, text='the format is wrong')

            if input_user in user_credentials:
                if user_credentials[input_user]["password"] == input_password:
                    user_credentials[input_user]["chat_ID"] = chat_ID
                    self.bot.sendMessage(chat_ID, text=f"Hi {input_user}, you can monitor your patients health.")  
                    self.bot.sendMessage(chat_ID, text='please enter your patient ID, for example: \n/patient:ID')
                else:
                    self.bot.sendMessage(chat_ID, text=f"the password is incorrect")
            else:
                self.bot.sendMessage(chat_ID, text=f"the user is not correct")
        elif "/patient:" in message:
            input_patient_ID = message.replace("/patient:", "", 1)
            if input_patient_ID in patients_ID:
                buttons = [[InlineKeyboardButton(text=f'blood pressure', callback_data=f'blood_pressure:{input_patient_ID}'), 
                    InlineKeyboardButton(text=f'temperature', callback_data=f'temperature:{input_patient_ID}')]]
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                self.bot.sendMessage(chat_ID, text='What do you want to monitor', reply_markup=keyboard)   
            
            else:
                self.bot.sendMessage(chat_ID, text=f"the patient's ID does not exist")

        else:
            self.bot.sendMessage(chat_ID, text="Command not supported")
        

    #this function will run when you get something from keyboard or from other API(microservice)  you get something
    
    def on_callback_query(self,msg):
        #chat_ID is the ID of user who sends messages to bot
        #query_data is the command that is sent from keyboard or microservice to the bot
        query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')
        
        if "historical_data:blood_pressure:" in query_data:
            input_patient_ID = query_data.replace("historical_data:blood_pressure:", "", 1)
            historical_data_message_blood_pressure = ""
            for item in historical_data[input_patient_ID]:
                historical_data_message_blood_pressure =  historical_data_message_blood_pressure + f'day: {item["day"]} - blood_pressure: {item["blood_pressure"]}\n' 
            self.bot.sendMessage(chat_ID, text=historical_data_message_blood_pressure) 
        
        elif "current_data:blood_pressure:" in query_data:
            input_patient_ID = query_data.replace("current_data:blood_pressure:", "", 1)
            self.bot.sendMessage(chat_ID, text=f'blood pressure of patient with ID {input_patient_ID} is: {patients_ID[input_patient_ID][0]}') 
        
        elif "historical_data:temperature:" in query_data:
            input_patient_ID = query_data.replace("historical_data:temperature:", "", 1)
            historical_data_message_temperature = ""
            for item in historical_data[input_patient_ID]:
                historical_data_message_temperature =  historical_data_message_temperature + f'day: {item["day"]} - temperature: {item["temperature"]}\n' 
            self.bot.sendMessage(chat_ID, text=historical_data_message_temperature) 
        
        elif "current_data:temperature:" in query_data:
            input_patient_ID = query_data.replace("current_data:temperature:", "", 1)
            self.bot.sendMessage(chat_ID, text=f'temprature of patient with ID {input_patient_ID} is: {patients_ID[input_patient_ID][1]}') 
        
        elif "blood_pressure:" in query_data:
            input_patient_ID = query_data.replace("blood_pressure:", "", 1)
            ####this should be connected to Victor Code (patient history API) to call blood pressure
            buttons = [[InlineKeyboardButton(text=f'current data', callback_data=f'current_data:blood_pressure:{input_patient_ID}'), 
                InlineKeyboardButton(text=f'historical data', callback_data=f'historical_data:blood_pressure:{input_patient_ID}')]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text='Do you want to monitor current data or historical data', reply_markup=keyboard) 

        elif "temperature:" in query_data:
            input_patient_ID = query_data.replace("temperature:", "", 1)
            ####this should be connected to Victor Code (patient history API) to call blood pressure
            buttons = [[InlineKeyboardButton(text=f'current data', callback_data=f'current_data:temperature:{input_patient_ID}'), 
                InlineKeyboardButton(text=f'historical data', callback_data=f'historical_data:temperature:{input_patient_ID}')]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text='Do you want to monitor current data or historical data', reply_markup=keyboard) 
        
        




            


        
        payload = self.__message.copy()
        payload['e'][0]['v'] = query_data
        payload['e'][0]['t'] = time.time()
        #self.client.myPublish(self.topic, payload)
        #self.bot.sendMessage(chat_ID, text=f"Led switched {query_data}")

    ### To do
    




    def user_log_in(self, user, password, chat_ID):
        if user_credentials[user]:
            self.bot.sendMessage(chat_ID, text=f"user exist")
        else:
            self.bot.sendMessage(chat_ID,text=f"user does not exist")

class MySubscriber:
    def __init__(self, clientID,topic,broker):
        self.clientID = clientID
        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(clientID, True) 
        
        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived
        
        self.topic = topic
        self.messageBroker =broker 
        
    def start (self):
        #manage connection to broker
        self._paho_mqtt.connect(self.messageBroker, 1883)
        self._paho_mqtt.loop_start()
        # subscribe for a topic
        self._paho_mqtt.subscribe(self.topic, 2)
        
    def stop (self):
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()
        
    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print ("Connected to %s with result code: %d" % (self.messageBroker, rc))
        
    def myOnMessageReceived (self, paho_mqtt , userdata, msg):
        # A new message is received
        message = "Topic:'" + msg.topic+"', QoS: '"+str(msg.qos)+"' Message: '"+str(msg.payload) + "'"
        for user in user_credentials:
            sb.bot.sendMessage(user["chat_ID"], text= message)       


if __name__ == "__main__":
    conf = json.load(open("G:/IOT_september_2024/git_project_healthy_main/project_healthy/src/services/telegram_bot/settings.json"))
    token = conf["telegramToken"]

    # Echo bot
    #bot=EchoBot(token)

    # SimpleSwitchBot
    broker = conf["brokerIP"]
    port = conf["brokerPort"]
    topic = conf["mqttTopic"]
    #ssb = SimpleSwitchBot(token, broker, port, topic)
    sb = HealthmonitorBot(token,broker,port,topic)
    #subscriber = MySubscriber ("telegram bot","alert/bloodpressure", "local host")
    #subscriber.start()
    

    
    while True:
        time.sleep(3)
        #time sleep
        
