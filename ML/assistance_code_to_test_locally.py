import cherrypy
import json

class HistoricalData:
    exposed = True

    def GET(self, *uri, **params):
        print("URI:", uri)
        print("Params:", params)

        # Check if the request is for "thingspeak"
        if uri and uri[0] == "thinkspeak":
            passport_code = params.get("passport_code")
            entity_id = params.get("entity_id")

            # Load the historical data from the JSON file
            with open("historic.json", "r") as file:
                data = json.load(file)

            # If no query parameters are provided, return all data
            if not entity_id :
                return json.dumps(data).encode("utf-8")

            # If query parameters are provided, filter the data
            if entity_id:
                result = None
                for entry in data:
                   
                    if entry["entity_id"] == int(entity_id):
                        result = entry["data"]
                        break

                if result:
                    return json.dumps(result).encode("utf-8")
                else:
                    return json.dumps({"error": "No data found for the given passport_code and device_id"}).encode("utf-8")
            else:
                return json.dumps({"error": "Missing passport_code or device_id"}).encode("utf-8")

        
        if uri and uri[0] == "entity":
            with open("Entity.json", "r") as file:
                dataDict = json.load(file)  # JSON to dict

            return json.dumps(dataDict).encode("utf-8")  #  Encode response as bytes

        
        if uri and uri[0] == "device":
            with open("device.json", "r") as file:
                dataDict = json.load(file)  # JSON to dict

            return json.dumps(dataDict).encode("utf-8")  #  Encode response as bytes

        if uri and uri[0] == "patient":
            with open("patient.json", "r") as file:
                dataDict = json.load(file)  # JSON to dict

            return json.dumps(dataDict).encode("utf-8")  #  Encode response as bytes

        return json.dumps({"error": "Invalid URI"}).encode("utf-8")  #  Handle invalid URIs properly
        

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
    cherrypy.config.update({'server.socket_port': 8081})  # Set the port number

    # Start CherryPy engine
    cherrypy.engine.start()
    cherrypy.engine.block()