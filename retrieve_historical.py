import cherrypy
import json
import sqlite3
from datetime import datetime

class HistoricalData:
    exposed = True
    
    class HistoricalData:
        exposed = True
    
    def GET(self, *uri, **params):
        # Database connection
        conn = sqlite3.connect('sensors.db')  # Replace with your actual database path
        cursor = conn.cursor()
        
        # Ensure start_date and end_date are provided in the request
        if 'start_date' not in params or 'end_date' not in params:
            cherrypy.response.status = 400  # Bad Request
            return json.dumps({"status": "error", "message": "start_date and end_date are required"})
        
        try:
            # Convert start_date and end_date from timestamp to datetime string
            start_date = datetime.fromtimestamp(int(params['start_date']) / 1000).strftime('%Y-%m-%d %H:%M:%S')
            end_date = datetime.fromtimestamp(int(params['end_date']) / 1000).strftime('%Y-%m-%d %H:%M:%S')
            print("debug  ")
            print(start_date)
            print(end_date)
        except (ValueError, KeyError):
            cherrypy.response.status = 400
            return json.dumps({"status": "error", "message": "Invalid timestamp format"})
        
        # Determine the sensor type from the URL (e.g., temperature, humidity, bloodpressure)
        if uri and uri[0] in ['Temperature', 'Humidity', 'Blood Pressure']:
            sensor_type = uri[0]
            print(sensor_type)
            # Query to retrieve sensor data based on sensor_type and date range
            query = """
            SELECT sensor_id, sensor_type, device_id, last_reading, last_reading_timestamp, thingspeak_field_it 
            FROM sensors
            WHERE sensor_type = ? AND last_reading_timestamp BETWEEN ? AND ?
            """
            cursor.execute(query, (sensor_type, start_date, end_date))
            rows = cursor.fetchall()

            # Prepare the data as a list of dictionaries
            data = []
            for row in rows:
                data.append({
                    "sensor_id": row[0],
                    "sensor_type": row[1],
                    "device_id": row[2],
                    "last_reading": row[3],
                    "last_reading_timestamp": row[4],
                    "thingspeak_field_it": row[5]
                })

            conn.close()
            return json.dumps(data)
        else:
            conn.close()
            cherrypy.response.status = 404  # Not Found
            return json.dumps({"status": "error", "message": "Sensor type not found"})


if __name__ == "__main__":
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }
    # Mounting the application
    cherrypy.tree.mount(HistoricalData(), '/historical', conf)

    # Server configuration
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})  # Listening on all available network interfaces
    cherrypy.config.update({'server.socket_port': 8080})  # Set the port number

    # Start CherryPy engine
    cherrypy.engine.start()
    cherrypy.engine.block()
