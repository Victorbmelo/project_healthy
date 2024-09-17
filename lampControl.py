import cherrypy
import json
import sqlite3

class LampAction:
    exposed = True
    def GET(self):
        # Database connection
        conn = sqlite3.connect('D:/Documents/node/sqlite-tools-win-x64-3460100/lamp_schedule.db')  # Replace with your actual database path
        cursor = conn.cursor()
        
        # Query to retrieve all data from the 'schedules' table
        cursor.execute("SELECT id, time, weekday, state FROM schedules")
        rows = cursor.fetchall()
        
        # Prepare the data as a list of dictionaries
        data = []
        for row in rows:
            data.append({
                "id": row[0],
                "time": row[1],
                "weekdays": row[2],
                "state": row[3]  # Convert state to boolean if stored as integer
            })
        
        # Close the database connection
        conn.close()
        
       
        return json.dumps(data)

    

    def PUT(self, *uri, **params):
        # Database connection
        conn = sqlite3.connect('D:/Documents/node/sqlite-tools-win-x64-3460100/lamp_schedule.db')  # Replace with your actual database path
        reqString = cherrypy.request.body.read().decode()  # Read request body and decode from binary to string
        
        print("ReqString")
        print(reqString)
        reqDict = json.loads(reqString)  # Convert JSON string to dictionary
        print(reqDict)  # Print the received data for debugging

        cursor = conn.cursor()
        
        # Extract values from request
        time = reqDict['time']
        weekdays = ','.join(reqDict.get('weekdays', []))  # Default to empty list if 'weekdays' is not provided
        #weekdays =reqDict['weekdays']
        state = reqDict['state']

        # Check if record already exists
        print("weekdays")
        print(weekdays)
        check_query = """SELECT COUNT(*) FROM schedules WHERE time = ? AND weekday = ?"""
        cursor.execute(check_query, (time,weekdays))
        record_exists = cursor.fetchone()[0] > 0
        
        if record_exists:
            # Record exists, return a message
            cherrypy.response.status = 409  # Conflict status code
            #return json.dumps({"status": "exists", "message": "Record already exists"})
            return "Record already exists"
        else:
            # Insert the record
            print("There is not this record ")
            insert_query = """INSERT INTO schedules(time, weekday, state) VALUES (?, ?, ?)"""
            cursor.execute(insert_query, (reqDict['time'], ','.join(reqDict['weekdays']), reqDict['state']))

            conn.commit()
            
            # Return a success response
            cherrypy.response.status = 200
            #return json.dumps({"status": "success", "message": "Data inserted successfully"})
            return  "Data inserted successfully"
        conn.close()

if __name__ == "__main__":
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }
    # Mounting the application
    cherrypy.tree.mount(LampAction(), '/test', conf)

    # Server configuration
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})  # Listening on all available network interfaces
    cherrypy.config.update({'server.socket_port': 8080})  # Set the port number

    # Start CherryPy engine
    cherrypy.engine.start()
    cherrypy.engine.block()
