import cherrypy
import json
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import requests
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

class HistoricalData:
    exposed = True

    def GET(self, *uri, **params):
        print("URI:", uri)
        print("Params:", params)
        
        #handle get request received
        patientReceived = params["patient_id"]
        entityReceived=  params["entity_id"]
        
        #Make a get request to thinkspeak
        url = f"http://localhost:8081/thinkspeak?entity_id={entityReceived}"# I need this API address to get data
        
         
         # Send a GET request
        response = requests.get(url)
       
        data=response.json()
        print(data)
        #Ml Processing
        dataset = pd.DataFrame(data)
        print(dataset)
        #the rest of Ml
        ########################
         #Make a get request to thinkspeak
        url = f"http://localhost:8081/device"# I need this API address to get data

         # Send a GET request
        response2 = requests.get(url)
       
        listDevices=response2.json()
        
        devices= []


        for d in listDevices:
            if d["patient_id"] == int(patientReceived):
                devices.append(d["device_id"])

        print(devices)               

        url = f"http://localhost:8081/entity"# I need this API address to get data

         # Send a GET request
        response2 = requests.get(url)
        
        
        return json.dumps({"data": data}).encode("UTF-8")
         
        

       
                 

if __name__ == "__main__":
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }

    # Mounting the application
    cherrypy.tree.mount(HistoricalData(), '/', conf)

    # Server configuration
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})  # Listen on all interfaces
    cherrypy.config.update({'server.socket_port': 8080})  # Set the port number

    # Start CherryPy engine
    cherrypy.engine.start()
    cherrypy.engine.block()