import cherrypy
import json
import sqlite3

class LampAction:
    exposed = True
    def GET(self, *uri, **params):
        # Database connection
        conn = sqlite3.connect('lamp_schedule.db')  # Replace with your actual database path
        cursor = conn.cursor()

        if uri and uri[0] == 'lamps':
            # Query to retrieve distinct id_Lamp values for dropdown
            cursor.execute("SELECT DISTINCT id_Lamp FROM schedule")
            lamps = cursor.fetchall()
        
            # Prepare the data in the format required by the dropdown
            options = []
            for row in lamps:
                # Format each lamp as { "Lamp X": X }
                id_lamp = row[0]
                options.append({ f"Lamp {id_lamp}": id_lamp })
            # Close the database connection
            conn.close()
        
            return json.dumps(options)
    
        else:
            # Query to retrieve all data from the 'schedule' table
            cursor.execute("SELECT id, id_Lamp, time, weekdays, action FROM schedule")
            rows = cursor.fetchall()
        
        # Prepare the data as a list of dictionaries
        data = []
        for row in rows:
            print("row ")
            print(row)
            data.append({
                "id": row[0],
                "id_Lamp": row[1],
                "time": row[2],
                "weekdays": row[3],
                "action": row[4]  # Convert state to boolean if stored as integer
            })
            
            # Close the database connection
        conn.close()
            
        return json.dumps(data)
    

    def PUT(self, *uri, **params):
        # Database connection
        conn = sqlite3.connect('lamp_schedule.db')  # Replace with your actual database path
        reqString = cherrypy.request.body.read().decode()  # Read request body and decode from binary to string
        
        print("ReqString")
        print(reqString)
        reqDict = json.loads(reqString)  # Convert JSON string to dictionary
        print(reqDict)  # Print the received data for debugging

        cursor = conn.cursor()
        
        # Extract values from request
        time = reqDict['time']
        weekdays = ','.join(reqDict.get('weekdays', []))  # Default to empty list if 'weekdays' is not provided
        id_Lamp= reqDict['id_Lamp']
        #weekdays =reqDict['weekdays']
        #action = reqDict['action']

        # Check if record already exists
        print("weekdays")
        print(weekdays)
        check_query = """SELECT COUNT(*) FROM schedule WHERE time = ? AND weekdays = ? AND id_Lamp = ? """
        cursor.execute(check_query, (time,weekdays, id_Lamp))
        record_exists = cursor.fetchone()[0] > 0
        
        if record_exists:
            # Record exists, return a message
            cherrypy.response.status = 409  # Conflict status code
            #return json.dumps({"status": "exists", "message": "Record already exists"})
            conn.close()
            return "Record already exists"
        else:
            # Insert the record
            print("There is not this record ")
            insert_query = """INSERT INTO schedule(id_Lamp,time, weekdays, action) VALUES (?,?, ?, ?)"""
            cursor.execute(insert_query, (reqDict['id_Lamp'],reqDict['time'], ','.join(reqDict['weekdays']), reqDict['action']))

            conn.commit()
            
            # Return a success response
            cherrypy.response.status = 200
            #return json.dumps({"status": "success", "message": "Data inserted successfully"})
            conn.close()
    
            return  "Data inserted successfully"
    
    def DELETE(self, *uri, **params):
        # Extract the 'id' from query parameters
        record_id = params.get('id')

        if not record_id:
            cherrypy.response.status = 400  # Bad Request
            return json.dumps({"status": "error", "message": "ID is required for DELETE"})

        try:
            record_id = int(record_id)
        except ValueError:
            cherrypy.response.status = 400
            return json.dumps({"status": "error", "message": "Invalid ID format"})

        # Database connection
        conn = sqlite3.connect('lamp_schedule.db')
        cursor = conn.cursor()

        # Check if the record exists
        check_query = "SELECT COUNT(*) FROM schedule WHERE id = ?"
        cursor.execute(check_query, (record_id,))
        exists = cursor.fetchone()[0] > 0

        if not exists:
            conn.close()
            cherrypy.response.status = 404  # Not Found
            return json.dumps({"status": "error", "message": f"Record with id {record_id} not found"})

        # Perform the delete operation
        delete_query = "DELETE FROM schedule WHERE id = ?"
        cursor.execute(delete_query, (record_id,))
        conn.commit()

        # Close the database connection
        conn.close()

        # Return a success response
        cherrypy.response.status = 200
        return json.dumps({"status": "success", "message": f"Record with id {record_id} successfully deleted"})
    
    
        

    
        
    

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
