import json
import pytz
import cherrypy
import datetime
from src.database.sqliteHandler import Database

db = Database()
timestamp_now = datetime.datetime.now().astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S%z")

class StepCount(object):
    exposed = True

    def PUT(self, *path, **queries):
        try:
            data = json.loads(cherrypy.request.body.read())
            mac = data['mac']
            steps = data['steps']
            timestamp = data['timestamp']

            db.connect()
            # Insert info in 'Steps' table
            db.insert_data(mac, steps, timestamp)
            db.close()

            return json.dumps({'message': 'Dados salvos com sucesso.'})
        except Exception as e:
            return json.dumps({
                'message': str(e),
                'timestamp': timestamp_now
            })
