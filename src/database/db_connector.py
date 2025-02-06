import cherrypy
import os
import sqlite3

SCRIPT_PATH = os.path.abspath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
DB_FILENAME = 'ProjectHealth.db'
SCHEMA_FILENAME = 'sql_generate.sql'

DB_PATH = os.path.join(SCRIPT_DIR, DB_FILENAME)
SCHEMA_PATH = os.path.join(SCRIPT_DIR, SCHEMA_FILENAME)

STATUS_SUCCESS = {"status": "success"}
STATUS_ERROR = {"status": "error", "message": "Invalid request method or missing ID"}


class DatabaseHandler:
    def __init__(self, db_file=DB_PATH, schema_file=SCHEMA_PATH):
        self.db_file = db_file
        self.schema_file = schema_file
        self.conn = None
        self.cursor = None

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            self.cursor = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()

    def execute_script(self, script_file):
        with open(script_file, 'r') as file:
            script = file.read()
        self.cursor.executescript(script)
        self.conn.commit()

    def create_tables(self):
        self.execute_script(self.schema_file)

    def query_data(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def execute_query(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()

    def insert_data(self, table_name, **kwargs):
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join('?' for _ in kwargs)
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(sql, tuple(kwargs.values()))
        self.conn.commit()


class APIHandler:
    def __init__(self):
        self.db = DatabaseHandler()
        self.db.connect()

    def apply_filters(self, base_query, params):
        filters = []
        values = []
        for key, value in params.items():
            filters.append(f"{key} = ?")
            values.append(value)
        if filters:
            base_query += " WHERE " + " AND ".join(filters)
        return base_query, values

    def handle_get_request(self, table_name, id, params):
        base_query = f"SELECT * FROM {table_name}"
        try:
            if id:
                base_query += f" WHERE {table_name[:-1]}_id = ?"
                result = self.db.query_data(base_query, (id,))
            else:
                query, values = self.apply_filters(base_query, params)
                print("query", query)
                print("values", values)
                result = self.db.query_data(query, values)
            return [dict(row) for row in result]

        except sqlite3.OperationalError as e:
            # Check if the error is due to a missing column (you can refine this further)
            cherrypy.log(f"Error: {str(e)}")
            # Return a Bad Request response with the error message
            cherrypy.response.status = 400
            return {"status": "error", "message": f"Bad Request: Column not found or query error({e})"}


    def handle_post_request(self, table_name, data, fields):
        columns = ", ".join(fields)
        placeholders = ", ".join(["?"] * len(fields))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.db.execute_query(query, tuple(data[field] for field in fields))
        return STATUS_SUCCESS

    def handle_put_request(self, table_name, id, data, fields):
        set_clause = ", ".join([f"{field} = ?" for field in fields])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {table_name[:-1]}_id = ?"
        self.db.execute_query(query, tuple(data[field] for field in fields) + (id,))
        return STATUS_SUCCESS

    def handle_delete_request(self, table_name, id):
        query = f"DELETE FROM {table_name} WHERE {table_name[:-1]}_id = ?"
        self.db.execute_query(query, (id,))
        return STATUS_SUCCESS

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def patient(self, *uri, **params):
        method = cherrypy.request.method
        params = cherrypy.request.params
        data = cherrypy.request.json if method in ['POST', 'PUT'] else None
        id = params.get('patient_id')

        if method == 'GET':
            return self.handle_get_request("Patients", id, params)
        elif method == 'POST':
            return self.handle_post_request("Patients", data, ["name", "address", "emergency_contact", "passport_code", "admin_id"])
        elif method == 'PUT' and id:
            return self.handle_put_request("Patients", id, data, ["name", "address", "emergency_contact", "passport_code", "admin_id"])
        elif method == 'DELETE' and id:
            return self.handle_delete_request("Patients", id)

        return STATUS_ERROR

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def device(self, *uri, **params):
        method = cherrypy.request.method
        params = cherrypy.request.params
        data = cherrypy.request.json if method in ['POST', 'PUT'] else None
        id = params.get('device_id')

        if method == 'GET':
            return self.handle_get_request("Devices", id, params)
        elif method == 'POST':
            return self.handle_post_request("Devices", data, ["mac_address", "device_name", "device_type", "location", "is_active", "patient_id", "admin_id", "thingspeak_channel_key"])
        elif method == 'PUT' and id:
            return self.handle_put_request("Devices", id, data, ["mac_address", "device_name", "device_type", "location", "is_active", "patient_id", "admin_id", "thingspeak_channel_key"])
        elif method == 'DELETE' and id:
            return self.handle_delete_request("Devices", id)

        return STATUS_ERROR

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def entity(self, *uri, **params):
        method = cherrypy.request.method
        params = cherrypy.request.params
        data = cherrypy.request.json if method in ['POST', 'PUT'] else None
        id = params.get('entity_id')

        if method == 'GET':
            return self.handle_get_request("DeviceEntities", id, params)
        elif method == 'POST':
            return self.handle_post_request("DeviceEntities", data, ["entity_type", "entity_name", "device_id", "is_active", "last_reading", "last_reading_timestamp", "service_id", "thingspeak_field_id"])
        elif method == 'PUT' and id:
            return self.handle_put_request("DeviceEntities", id, data, ["entity_type", "entity_name", "device_id", "is_active", "last_reading", "last_reading_timestamp", "service_id", "thingspeak_field_id"])
        elif method == 'DELETE' and id:
            return self.handle_delete_request("DeviceEntities", id)

        return STATUS_ERROR

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def telegrambot(self, *uri, **params):
        method = cherrypy.request.method
        params = cherrypy.request.params
        data = cherrypy.request.json if method in ['POST', 'PUT'] else None
        bot_id = params.get('bot_id')

        if method == 'GET':
            return self.handle_get_request("TelegramBot", bot_id, params)
        elif method == 'POST':
            required_fields = ['bot_token', 'chat_id', 'patient_id']
            return self.handle_post_request("TelegramBot", data, required_fields)
        elif method == 'PUT' and bot_id:
            return self.handle_put_request("TelegramBot", bot_id, data, data.keys())
        elif method == 'DELETE' and bot_id:
            return self.handle_delete_request("TelegramBot", bot_id)

        return STATUS_ERROR

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def endpoints(self, *uri, **params):
        method = cherrypy.request.method
        params = cherrypy.request.params
        data = cherrypy.request.json if method in ['POST', 'PUT'] else None
        endpoint_id = params.get('endpoint_id')

        if method == 'GET':
            return self.handle_get_request("Endpoints", endpoint_id, params)
        elif method == 'POST':
            required_fields = ['service_id', 'entity_id', 'endpoint']
            return self.handle_post_request("Endpoints", data, required_fields)
        elif method == 'PUT' and endpoint_id:
            return self.handle_put_request("Endpoints", endpoint_id, data, data.keys())
        elif method == 'DELETE' and endpoint_id:
            return self.handle_delete_request("Endpoints", endpoint_id)

        return STATUS_ERROR

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def login(self, *uri, **params):
        if cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            query = "SELECT * FROM Login WHERE username = ? AND password = ?"
            result = self.db.query_data(query, (data['username'], data['password']))
            return {"status": "success", "user": result[0]} if result else {"status": "failure"}

    def __del__(self):
        self.db.close()


if __name__ == "__main__":
    cherrypy.quickstart(APIHandler(), '/', {
        '/': {
            'tools.sessions.on': True,
            'tools.json_in.force': False,
        }
    })
