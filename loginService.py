import cherrypy
import json
import sqlite3

class LoginAPI:
    exposed = True

    #post Request
    def POST(self, *uri, **params):
        # Parse the request body (JSON format)
        raw_body = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        try:
            login_data = json.loads(raw_body)
            username = login_data.get('username')
            password = login_data.get('password')
        except (json.JSONDecodeError, KeyError):
            cherrypy.response.status = 400  # Bad Request
            return json.dumps({"status": "error", "message": "Invalid JSON format or missing credentials"})

        # Check if username and password are provided
        if not username or not password:
            cherrypy.response.status = 400  # Bad Request
            return json.dumps({"status": "error", "message": "Username and password are required"})

        # Connect to the SQLite database
        conn = sqlite3.connect('users.db')  # Replace with your actual database path
        cursor = conn.cursor()

        # Query to check if the user exists with the provided username and password
        query = "SELECT id_user, email FROM users WHERE username = ? AND password = ?"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            # Login successful
            response = {
                "status": "success",
                "message": "Login successful",
                "id_user": user[0],
                "email": user[1]
            }
        else:
            # Login failed
            cherrypy.response.status = 401  # Unauthorized
            response = {
                "status": "error",
                "message": "Invalid username or password"
            }

        conn.close()
        return json.dumps(response)


if __name__ == "__main__":
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }
    # Mounting the application
    cherrypy.tree.mount(LoginAPI(), '/login', conf)

    # Server configuration
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})  # Listening on all available network interfaces
    cherrypy.config.update({'server.socket_port': 8080})  # Set the port number

    # Start CherryPy engine
    cherrypy.engine.start()
    cherrypy.engine.block()
