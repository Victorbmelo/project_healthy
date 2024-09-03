import os
import sqlite3

SCRIPT_PATH = os.path.abspath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
DB_FILENAME = 'ProjectHealth.db'
SCHEMA_FILENAME = 'sql_generate.sql'

DB_PATH = os.path.join(SCRIPT_DIR, DB_FILENAME)
SCHEMA_PATH = os.path.join(SCRIPT_DIR, SCHEMA_FILENAME)


class DatabaseHandler:
    def __init__(self, db_file=DB_PATH, schema_file=SCHEMA_PATH):
        """
        Initializes the database connection and schema file.

        :param str db_file: Name of the database file.
        :param str schema_file: Name of the file containing the SQL schema for table creation.
        """
        self.db_file = db_file
        self.schema_file = schema_file
        self.conn = None
        self.cursor = None

    def connect(self):
        """
        Connects to the database and creates a cursor.
        """
        try:
            if self.conn is None:
                self.conn = sqlite3.connect(self.db_file)
                self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise

    def close(self):
        """
        Closes the connection to the database.
        """
        if self.conn:
            try:
                self.conn.close()
            except sqlite3.Error as e:
                print(f"Error closing the database connection: {e}")

    def execute_script(self, script_file):
        """
        Executes an SQL script from a file.

        :param str script_file: Name of the file containing the SQL script.
        """
        try:
            with open(script_file, 'r') as file:
                script = file.read()
            self.cursor.executescript(script)
            self.conn.commit()
        except FileNotFoundError:
            print(f"SQL script file not found: {script_file}")
            raise FileNotFoundError(f"SQL script file not found: {script_file}")
        except sqlite3.Error as e:
            print(f"Error executing SQL script: {e}")
            self.conn.rollback()  # Rollback in case of error

    def create_tables(self):
        """
        Creates tables using the specified SQL schema file.
        """
        self.execute_script(self.schema_file)

    def insert_data(self, table_name, **kwargs):
        """
        Inserts data into a specific table.

        :param str table_name: Name of the table where data will be inserted.
        :param kwargs: Data to be inserted, where keys are column names and values are the data.
        """
        try:
            columns = ', '.join(kwargs.keys())
            placeholders = ', '.join('?' for _ in kwargs)
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(sql, tuple(kwargs.values()))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting data into table {table_name}: {e}")
            self.conn.rollback()  # Rollback in case of error

    def query_data(self, query, params=()):
        """
        Executes an SQL query and returns the results.

        :param query: SQL query to be executed.
        :param params: Parameters for the SQL query.
        :return: Query results.
        """
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error querying data: {e}")
            return []

    @staticmethod
    def get_connection():
        """
        Provides a context-managed way to get a database connection.

        :return: A DatabaseHandler instance with an active connection.
        """
        db_handler = DatabaseHandler()
        db_handler.connect()
        return db_handler

    def __enter__(self):
        """
        Enables context management (with statement) for the DatabaseHandler.
        """
        if self.conn is None:
            self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Closes the database connection when exiting the context.
        """
        self.close()

# Example usage
if __name__ == "__main__":
    import datetime
    now = datetime.datetime.now(datetime.timezone.utc)
    db = DatabaseHandler()

    try:
        db.connect()
        db.create_tables()

        # User
        # db.insert_data('Users', name='Joao', address='456 Via Dois', emergency_contact='555-5678-555')
        # Device
        # db.insert_data('Devices', mac_address='DD1B44113F', device_name='Arduino', device_type='Actuator Control',
        #                 location='Bedroom', status='Active', user_id=2)
        # Actuator
        # db.insert_data('Actuators', actuator_type='Lamp', device_id=3, status='Active')
        # Services
        # db.insesert_data('Services', name='body_temp_check', alias='Body Temperature Check', service_description='Monitors body temperatures', status='Active',
        #                 last_run_timestamp=now, protocol='MQTT')
        # Endpoint
        # db.insesert_data('Endpoints', service_id=1, entity_type='sensor', entity_id=1, endpoint='/1/body_temp_check/001B44113A/sensor/1')

        results = db.query_data('SELECT * FROM Users')
        for row in results:
            print(row)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Ensure that the connection is closed even if an error occurs
        db.close()
