import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
import time
from MyMQTT import *

user_credentials = {
    "user1": "P@ssw0rd123",
    "user2": "Qw3rtY!89",
    "user3": "Secur3@987",
    "user4": "Adm1n#456",
    "user5": "PassW0rd!76"
}

patients_ID = {
    "12345": [70,38.5],
    "6789": [60,40],
    
}



class SwitchBot:
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
        if message == "/switch":
            buttons = [[InlineKeyboardButton(text=f'ON 🟡', callback_data=f'on'), 
                    InlineKeyboardButton(text=f'OFF ⚪', callback_data=f'off')]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text='What do you want to do', reply_markup=keyboard)
        elif message == "/start":
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
                if user_credentials[input_user] == input_password:
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
        if "blood_pressure:" in query_data:
            


        
        payload = self.__message.copy()
        payload['e'][0]['v'] = query_data
        payload['e'][0]['t'] = time.time()
        self.client.myPublish(self.topic, payload)
        self.bot.sendMessage(chat_ID, text=f"Led switched {query_data}")

    ### To do
    




    def user_log_in(self, user, password, chat_ID):
        if user_credentials[user]:
            self.bot.sendMessage(chat_ID, text=f"user exist")
        else:
            self.bot.sendMessage(chat_ID,text=f"user does not exist")

        


if __name__ == "__main__":
    conf = json.load(open("settings.json"))
    token = conf["telegramToken"]

    # Echo bot
    #bot=EchoBot(token)

    # SimpleSwitchBot
    broker = conf["brokerIP"]
    port = conf["brokerPort"]
    topic = conf["mqttTopic"]
    #ssb = SimpleSwitchBot(token, broker, port, topic)
    sb=SwitchBot(token,broker,port,topic)

    while True:
        time.sleep(3)
