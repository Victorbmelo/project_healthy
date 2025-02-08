-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Admins Table
CREATE TABLE IF NOT EXISTS Admins (
  admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

-- Patients Table
CREATE TABLE IF NOT EXISTS Patients (
  patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  address TEXT,
  emergency_contact TEXT,
  passport_code TEXT UNIQUE NOT NULL,
  admin_id INTEGER NOT NULL,
  FOREIGN KEY (admin_id) REFERENCES Admins(admin_id)
);

-- Devices Table
CREATE TABLE IF NOT EXISTS Devices (
  device_id INTEGER PRIMARY KEY AUTOINCREMENT,
  mac_address TEXT UNIQUE NOT NULL,
  device_name TEXT NOT NULL,
  device_type TEXT NOT NULL,
  location TEXT,
  is_active BOOLEAN DEFAULT 0,
  patient_id INTEGER NOT NULL,
  admin_id INTEGER NOT NULL,
  thingspeak_channel_id TEXT,
  thingspeak_channel_key TEXT,
  FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
  FOREIGN KEY (admin_id) REFERENCES Admins(admin_id)
);

-- DeviceEntities Table
CREATE TABLE IF NOT EXISTS DeviceEntities (
  entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
  entity_type TEXT CHECK(entity_type IN ('sensor', 'actuator')) NOT NULL,
  entity_name TEXT NOT NULL,
  device_id INTEGER NOT NULL,
  is_active BOOLEAN DEFAULT 0,
  last_reading TEXT,
  last_reading_timestamp DATETIME,
  service_id INTEGER,
  thingspeak_field_id INTEGER,
  FOREIGN KEY (device_id) REFERENCES Devices(device_id),
  FOREIGN KEY (service_id) REFERENCES Services(service_id),
  CONSTRAINT unique_entity_name_per_device UNIQUE (device_id, entity_name)
);

-- Services Table
CREATE TABLE IF NOT EXISTS Services (
  service_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  alias TEXT,
  service_description TEXT,
  is_active BOOLEAN DEFAULT 0,
  last_run_timestamp DATETIME,
  protocol TEXT
);

-- Endpoints Table
CREATE TABLE IF NOT EXISTS Endpoints (
  endpoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
  service_id INTEGER NOT NULL,
  entity_id INTEGER NOT NULL,
  endpoint TEXT NOT NULL,
  FOREIGN KEY (service_id) REFERENCES Services(service_id),
  FOREIGN KEY (entity_id) REFERENCES DeviceEntities(entity_id),
  UNIQUE (service_id, entity_id)  -- Ensure one record per service-entity combination
);

-- EntityConfigurations Table
CREATE TABLE IF NOT EXISTS EntityConfigurations (
  config_id INTEGER PRIMARY KEY AUTOINCREMENT,
  entity_id INTEGER NOT NULL,
  config_key TEXT NOT NULL,
  config_value TEXT NOT NULL,
  FOREIGN KEY (entity_id) REFERENCES DeviceEntities(entity_id),
  FOREIGN KEY (config_key) REFERENCES ConfigKeys(config_key)
);

-- TelegramBot Table
CREATE TABLE IF NOT EXISTS TelegramBot (
  bot_id INTEGER PRIMARY KEY AUTOINCREMENT,
  bot_token TEXT NOT NULL,
  chat_id TEXT NOT NULL,
  patient_id INTEGER NOT NULL,
  last_message TEXT,
  last_message_timestamp DATETIME,
  has_history_access BOOLEAN DEFAULT 0,
  FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
);

-- Schedules Table
CREATE TABLE IF NOT EXISTS Schedules (
  schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
  entity_id INTEGER NOT NULL,
  day_of_week TEXT CHECK(day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')) NOT NULL,
  start_time TIME NOT NULL,
  end_time TIME,
  action TEXT CHECK(action IN ('ON', 'OFF')) NOT NULL,
  repeat BOOLEAN DEFAULT 0,
  FOREIGN KEY (entity_id) REFERENCES DeviceEntities(entity_id)
);

-- ConfigKeys Table
CREATE TABLE IF NOT EXISTS ConfigKeys (
  config_key TEXT PRIMARY KEY,
  description TEXT NOT NULL,
  value_type TEXT CHECK(value_type IN ('numeric', 'boolean', 'string', 'json')) NOT NULL,
  apply_to TEXT CHECK(apply_to IN ('sensor', 'actuator')) NOT NULL
);


-- Indexes
CREATE INDEX IF NOT EXISTS idx_admins_email ON Admins (email);

CREATE INDEX IF NOT EXISTS idx_patients_admin_id ON Patients (admin_id);
CREATE INDEX IF NOT EXISTS idx_patients_passport_code ON Patients (passport_code);

CREATE INDEX IF NOT EXISTS idx_devices_mac_address ON Devices (mac_address);
CREATE INDEX IF NOT EXISTS idx_devices_patient_id ON Devices (patient_id);
CREATE INDEX IF NOT EXISTS idx_devices_admin_id ON Devices (admin_id);

CREATE INDEX IF NOT EXISTS idx_deviceentities_device_id ON DeviceEntities (device_id);
CREATE INDEX IF NOT EXISTS idx_deviceentities_service_id ON DeviceEntities (service_id);
CREATE INDEX IF NOT EXISTS idx_deviceentities_entity_type ON DeviceEntities (entity_type);

CREATE INDEX IF NOT EXISTS idx_services_name ON Services (name);
CREATE INDEX IF NOT EXISTS idx_services_is_active ON Services (is_active);

CREATE INDEX IF NOT EXISTS idx_endpoints_service_id ON Endpoints (service_id);
CREATE INDEX IF NOT EXISTS idx_endpoints_entity_id ON Endpoints (entity_id);

CREATE INDEX IF NOT EXISTS idx_entityconfig_entity_id ON EntityConfigurations (entity_id);
CREATE INDEX IF NOT EXISTS idx_entityconfig_config_key ON EntityConfigurations (config_key);

CREATE INDEX IF NOT EXISTS idx_telegrambot_patient_id ON TelegramBot (patient_id);
CREATE INDEX IF NOT EXISTS idx_telegrambot_chat_id ON TelegramBot (chat_id);

CREATE INDEX IF NOT EXISTS idx_schedules_entity_id ON Schedules (entity_id);
CREATE INDEX IF NOT EXISTS idx_schedules_day_of_week ON Schedules (day_of_week);
CREATE INDEX IF NOT EXISTS idx_schedules_action ON Schedules (action);

CREATE INDEX IF NOT EXISTS idx_configkeys_apply_to ON ConfigKeys (apply_to);
