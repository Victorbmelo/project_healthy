import cherrypy
import json
import time
import datetime
import pytz
import RPi.GPIO as GPIO
import subprocess

from dht11 import DHT11
from src.api.stepCountHandler import StepCount
from src.database.sqliteHandler import Database

# db = Database()

# Set up GPIO pins for sensors
DHT_PIN = 4
DYP_PIN = 18

# Set interval for readings
READING_INTERVAL = 30 #* 60  # 30 minutes in seconds

# Initialize the DHT11 sensor object
dht11 = DHT11(DHT_PIN)

# Read DHT11 sensor for temperature and humidity
def read_dht11():
    temperature = None
    humidity = None
    result = dht11.read()
    if result.is_valid():
        temperature = result.temperature
        humidity = result.humidity
    return humidity, temperature

# Read DYP-ME003 sensor for presence
def read_dyp_me003():
    presence = GPIO.input(DYP_PIN)
    return presence

# Set up CherryPy server to retrieve MAC address
class MACServer(object):
    @cherrypy.expose
    def index(self):
        output = subprocess.check_output(['ifconfig', 'wlan0'])
        return str(output)

if __name__ == '__main__':
    # db.create_table()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DYP_PIN, GPIO.IN)
    GPIO.setwarnings(False)

    # Start CherryPy server
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }
    cherrypy.tree.mount(StepCount(), '/step', conf)
    cherrypy.tree.mount(MACServer(), '/mac', conf)
    cherrypy.engine.start()

    # Read sensor data at regular intervals and write to file
    while True:
        humidity, temperature = read_dht11()
        presence = read_dyp_me003()
        # Create JSON object with sensor data and timestamp
        print('data', humidity, temperature)
        data = {
            'temperature': temperature,
            'humidity': humidity,
            'presence': presence,
            'timestamp': datetime.datetime.now().astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S%z")
        }
        # Write sensor data to file
        with open('sensor_data.json', 'a') as f:
            f.write(json.dumps(data) + '\n')
            print('file saved')
        time.sleep(READING_INTERVAL)
