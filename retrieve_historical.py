import cherrypy
import json
import sqlite3
from datetime import datetime

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
        except (ValueError, KeyError):
            cherrypy.response.status = 400
            return json.dumps({"status": "error", "message": "Invalid timestamp format"})
        
        # Determine the sensor type from the URL (e.g., Temperature, Humidity, Blood Pressure)
        if uri and uri[0] in ['Temperature', 'Humidity', 'Blood Pressure']:
            sensor_type = uri[0]
            
            # Query to retrieve sensor data based on sensor_type and date range, ordered by timestamp
            query = """
            SELECT sensor_id, sensor_type, device_id, last_reading, last_reading_timestamp, thingspeak_field_it 
            FROM sensors
            WHERE sensor_type = ? AND last_reading_timestamp BETWEEN ? AND ?
            ORDER BY last_reading_timestamp ASC
            """
            cursor.execute(query, (sensor_type, start_date, end_date))
            rows = cursor.fetchall()

            # Prepare the data in the required format
            chart_data = [{
                "series": ["Systolic", "Diastolic"],  # Two separate series for systolic and diastolic
                "data": [[], []],  # Two lists for storing x and y pairs for both systolic and diastolic
                "labels": ["Systolic", "Diastolic"]
            }]

            for row in rows:
                last_reading = row[3]
                
                # For blood pressure: convert the "systolic/diastolic" string to separate values
                if sensor_type == 'Blood Pressure' and '/' in last_reading:
                    try:
                        systolic, diastolic = map(float, last_reading.split('/'))  # Convert both to float
                        
                        # Append the systolic value to the first series (index 0)
                        chart_data[0]["data"][0].append({
                            "x": row[4],  # last_reading_timestamp as string
                            "y": systolic  # systolic value
                        })
                        
                        # Append the diastolic value to the second series (index 1)
                        chart_data[0]["data"][1].append({
                            "x": row[4],  # last_reading_timestamp as string
                            "y": diastolic  # diastolic value
                        })
                    except ValueError:
                        continue  # Skip if the blood pressure value is not valid
                
                # For other sensor types, add a single value to the first series
                elif sensor_type != 'Blood Pressure' and last_reading is not None:
                    chart_data[0]["data"][0].append({
                        "x": row[4],  # last_reading_timestamp as string
                        "y": float(last_reading)  # other sensor value as a float
                    })

            conn.close()
            return json.dumps(chart_data)
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
