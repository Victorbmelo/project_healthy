import json
import cherrypy

from src.database.sqlite_handler import DatabaseHandler


class APIHandler:
    def __init__(self):
        self.db = DatabaseHandler()
        self.db.connect()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def patient(self, id=None):
        if cherrypy.request.method == 'GET':
            if id:
                query = "SELECT * FROM Paciente WHERE id = ?"
                result = self.db.query_data(query, (id,))
                return result[0] if result else {}
            else:
                return self.db.query_data("SELECT * FROM Paciente")
        elif cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            query = "INSERT INTO Paciente (name, age, address) VALUES (?, ?, ?)"
            self.db.execute_query(query, (data['name'], data['age'], data['address']))
            return {"status": "success"}
        elif cherrypy.request.method == 'PUT' and id:
            data = cherrypy.request.json
            query = "UPDATE Paciente SET name = ?, age = ?, address = ? WHERE id = ?"
            self.db.execute_query(query, (data['name'], data['age'], data['address'], id))
            return {"status": "success"}
        elif cherrypy.request.method == 'DELETE' and id:
            query = "DELETE FROM Paciente WHERE id = ?"
            self.db.execute_query(query, (id,))
            return {"status": "success"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def device(self, id=None):
        if cherrypy.request.method == 'GET':
            if id:
                query = "SELECT * FROM Device WHERE id = ?"
                result = self.db.query_data(query, (id,))
                return result[0] if result else {}
            else:
                return self.db.query_data("SELECT * FROM Device")
        elif cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            query = "INSERT INTO Device (mac_address, device_name, device_type, location, status) VALUES (?, ?, ?, ?, ?)"
            self.db.execute_query(query, (data['mac_address'], data['device_name'], data['device_type'], data['location'], data['status']))
            return {"status": "success"}
        elif cherrypy.request.method == 'PUT' and id:
            data = cherrypy.request.json
            query = "UPDATE Device SET mac_address = ?, device_name = ?, device_type = ?, location = ?, status = ? WHERE id = ?"
            self.db.execute_query(query, (data['mac_address'], data['device_name'], data['device_type'], data['location'], data['status'], id))
            return {"status": "success"}
        elif cherrypy.request.method == 'DELETE' and id:
            query = "DELETE FROM Device WHERE id = ?"
            self.db.execute_query(query, (id,))
            return {"status": "success"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def entity(self, id=None):
        if cherrypy.request.method == 'GET':
            if id:
                query = "SELECT * FROM Entity WHERE id = ?"
                result = self.db.query_data(query, (id,))
                return result[0] if result else {}
            else:
                return self.db.query_data("SELECT * FROM Entity")
        elif cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            query = "INSERT INTO Entity (type, description) VALUES (?, ?)"
            self.db.execute_query(query, (data['type'], data['description']))
            return {"status": "success"}
        elif cherrypy.request.method == 'PUT' and id:
            data = cherrypy.request.json
            query = "UPDATE Entity SET type = ?, description = ? WHERE id = ?"
            self.db.execute_query(query, (data['type'], data['description'], id))
            return {"status": "success"}
        elif cherrypy.request.method == 'DELETE' and id:
            query = "DELETE FROM Entity WHERE id = ?"
            self.db.execute_query(query, (id,))
            return {"status": "success"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def login(self):
        if cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            query = "SELECT * FROM Login WHERE username = ? AND password = ?"
            result = self.db.query_data(query, (data['username'], data['password']))
            return {"status": "success", "user": result[0]} if result else {"status": "failure"}

    def __del__(self):
        self.db.close()


if __name__ == '__main__':
    cherrypy.quickstart(APIHandler(), '/', {'/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}})
