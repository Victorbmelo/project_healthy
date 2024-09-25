CREATE TABLE IF NOT EXISTS Users (
  user_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  address TEXT,
  emergency_contact TEXT,
  passport_code TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Services (
  service_id INTEGER PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  alias TEXT,
  service_description TEXT,
  status TEXT DEFAULT 'inactive',
  last_run_timestamp DATETIME,
  protocol TEXT
);

CREATE TABLE IF NOT EXISTS Devices (
  device_id INTEGER PRIMARY KEY,
  mac_address TEXT UNIQUE NOT NULL,
  device_name TEXT,
  device_type TEXT,
  location TEXT,
  status TEXT DEFAULT 'offline',
  user_id INTEGER NOT NULL,
  thingspeak_channel_key TEXT,
  FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE IF NOT EXISTS Sensors (
  sensor_id INTEGER PRIMARY KEY,
  sensor_type TEXT NOT NULL,
  sensor_name TEXT NOT NULL,
  device_id INTEGER NOT NULL,
  service_id INTEGER,
  last_reading TEXT,
  last_reading_timestamp DATETIME,
  thingspeak_field_id INTEGER,
  FOREIGN KEY (device_id) REFERENCES Devices(device_id),
  FOREIGN KEY (service_id) REFERENCES Services(service_id),
  CONSTRAINT unique_sensor_name_per_device UNIQUE (device_id, name)
);

CREATE TABLE IF NOT EXISTS Actuators (
  actuator_id INTEGER PRIMARY KEY,
  actuator_type TEXT NOT NULL,
  actuator_name TEXT NOT NULL,
  device_id INTEGER NOT NULL,
  service_id INTEGER,
  status TEXT DEFAULT 'off',
  thingspeak_field_id INTEGER,
  FOREIGN KEY (device_id) REFERENCES Devices(device_id),
  FOREIGN KEY (service_id) REFERENCES Services(service_id),
  CONSTRAINT unique_actuator_name_per_device UNIQUE (device_id, name)
);

CREATE TABLE IF NOT EXISTS Endpoints (
  endpoint_id INTEGER PRIMARY KEY,
  service_id INTEGER NOT NULL,
  entity_type TEXT NOT NULL,
  entity_id INTEGER NOT NULL,
  endpoint TEXT NOT NULL,
  FOREIGN KEY (service_id) REFERENCES Services(service_id)
);

CREATE TABLE IF NOT EXISTS Configurations (
  config_id INTEGER PRIMARY KEY,
  entity_id INTEGER NOT NULL,
  config_key TEXT NOT NULL,
  config_value TEXT
);

CREATE TABLE IF NOT EXISTS TelegramBot (
  bot_id INTEGER PRIMARY KEY,
  bot_token TEXT NOT NULL,
  chat_id TEXT NOT NULL,
  user_id INTEGER NOT NULL,
  last_message TEXT,
  last_message_timestamp DATETIME,
  has_history_access BOOLEAN DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_devices_mac_address ON Devices (mac_address);
CREATE INDEX IF NOT EXISTS idx_devices_user_id ON Devices (user_id);
CREATE INDEX IF NOT EXISTS idx_sensors_device_id ON Sensors (device_id);
CREATE INDEX IF NOT EXISTS idx_sensors_service_id ON Sensors (service_id);
CREATE INDEX IF NOT EXISTS idx_actuators_device_id ON Actuators (device_id);
CREATE INDEX IF NOT EXISTS idx_actuators_service_id ON Actuators (service_id);
CREATE INDEX IF NOT EXISTS idx_endpoints_service_id ON Endpoints (service_id);
CREATE INDEX IF NOT EXISTS idx_endpoints_entity_type ON Endpoints (entity_type);
CREATE INDEX IF NOT EXISTS idx_endpoints_entity_id ON Endpoints (entity_id);
CREATE INDEX IF NOT EXISTS idx_telegrambot_user_id ON TelegramBot (user_id);
CREATE INDEX IF NOT EXISTS idx_configurations_entity_id ON Configurations (entity_id);

PRAGMA foreign_keys = ON;
