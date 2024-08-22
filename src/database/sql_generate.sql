CREATE TABLE IF NOT EXISTS Users (
  id INTEGER PRIMARY KEY,
  name TEXT,
  address TEXT,
  emergency_contact TEXT
);

CREATE TABLE IF NOT EXISTS Devices (
  id INTEGER PRIMARY KEY,
  mac_address TEXT UNIQUE,
  device_name TEXT,
  device_type TEXT,
  location TEXT,
  status TEXT,
  user_id INTEGER,
  FOREIGN KEY (user_id) REFERENCES Users(id)
);

CREATE TABLE IF NOT EXISTS Sensors (
  sensor_id INTEGER PRIMARY KEY,
  sensor_type TEXT,
  device_id INTEGER,
  last_reading TEXT,
  last_reading_timestamp DATETIME,
  FOREIGN KEY (device_id) REFERENCES Devices(id)
);

CREATE TABLE IF NOT EXISTS Actuators (
  actuator_id INTEGER PRIMARY KEY,
  actuator_type TEXT,
  device_id INTEGER,
  status TEXT,
  FOREIGN KEY (device_id) REFERENCES Devices(id)
);

CREATE TABLE IF NOT EXISTS Endpoints (
  endpoint_id INTEGER PRIMARY KEY,
  service_id INTEGER,
  entity_type TEXT,
  entity_id INTEGER,
  endpoint TEXT,
  FOREIGN KEY (service_id) REFERENCES Services(service_id)
);

CREATE TABLE IF NOT EXISTS Commands (
  command_id INTEGER PRIMARY KEY,
  actuator_id INTEGER,
  command TEXT,
  timestamp DATETIME,
  FOREIGN KEY (actuator_id) REFERENCES Actuators(actuator_id)
);

CREATE TABLE IF NOT EXISTS Alerts (
  alert_id INTEGER PRIMARY KEY,
  user_id INTEGER,
  message TEXT,
  timestamp DATETIME,
  FOREIGN KEY (user_id) REFERENCES Users(id)
);

CREATE TABLE IF NOT EXISTS Configurations (
  config_id INTEGER PRIMARY KEY,
  device_id INTEGER,
  config_key TEXT,
  config_value TEXT,
  FOREIGN KEY (device_id) REFERENCES Devices(id)
);

CREATE TABLE IF NOT EXISTS Services (
  service_id INTEGER PRIMARY KEY,
  name TEXT UNIQUE,
  alias TEXT,
  service_description TEXT,
  status TEXT,
  last_run_timestamp DATETIME,
  protocol TEXT
);

-- index
CREATE INDEX IF NOT EXISTS Devices_index_0 ON Devices (mac_address);
CREATE INDEX IF NOT EXISTS Devices_index_1 ON Devices (user_id);
CREATE INDEX IF NOT EXISTS Sensors_index_2 ON Sensors (device_id);
CREATE INDEX IF NOT EXISTS Actuators_index_3 ON Actuators (device_id);
CREATE INDEX IF NOT EXISTS Endpoints_index_4 ON Endpoints (service_id);
CREATE INDEX IF NOT EXISTS Endpoints_index_5 ON Endpoints (entity_type);
CREATE INDEX IF NOT EXISTS Endpoints_index_6 ON Endpoints (entity_id);
CREATE INDEX IF NOT EXISTS Commands_index_7 ON Commands (actuator_id);
CREATE INDEX IF NOT EXISTS Alerts_index_8 ON Alerts (user_id);
CREATE INDEX IF NOT EXISTS Configurations_index_9 ON Configurations (device_id);
CREATE UNIQUE INDEX IF NOT EXISTS Services_index_10 ON Services (name);

PRAGMA foreign_keys = ON;
