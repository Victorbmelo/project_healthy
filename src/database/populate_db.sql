-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Admins
INSERT INTO Admins (admin_id, name, email, password)
VALUES
(1, 'Admin One', 'admin1@example.com', 'securepassword1'),
(2, 'Admin Two', 'admin2@example.com', 'securepassword2');

-- Patients
INSERT INTO Patients (patient_id, name, address, emergency_contact, passport_code, admin_id)
VALUES
(1, 'Pedro Loa', '123 Via Um', '555-1234-555', 'P12345678', 1),
(2, 'Joao Town', '456 Via Dois', '555-5678-555', 'P23456789', 2);

-- Services
INSERT INTO Services (service_id, name, alias, service_description, is_active, last_run_timestamp, protocol)
VALUES
(1, 'body_temp_check', 'Body Temperature Check', 'Monitors body temperatures', true, '2024-08-22 21:28:49.076691', 'MQTT'),
(2, 'air_conditioning', 'Air Conditioning Control', 'Controls air conditioning system', false, NULL, 'MQTT'),
(3, 'blood_pressure', 'Blood Pressure Monitoring', 'Monitors blood pressure levels', false, NULL, 'MQTT'),
(4, 'telegram_bot', 'Telegram Bot Notifications', 'Sends notifications via Telegram', true, '2024-08-22 21:28:49.076691', 'Telegram'),
(5, 'thingspeak', 'ThingSpeak Integration', 'Sends data to ThingSpeak', true, '2024-08-22 21:28:49.076691', 'HTTP'),
(6, 'action', 'Actuators', 'Execute an Action', true, '2024-08-22 21:28:49.076691', 'MQTT');


-- Devices
INSERT INTO Devices (device_id, mac_address, device_name, device_type, location, is_active, patient_id, admin_id, thingspeak_channel_key)
VALUES
(1, '001B44113A', 'RPi 4', 'Server', 'Living Room', true, 1, 1, NULL),
(2, 'FF1B44113A', 'RPi Zero', 'Wearable', 'User', true, 2, 2, NULL),
(3, 'DD1B44113F', 'Arduino', 'Actuator Control', 'Bedroom', true, 2, 2, NULL);

-- DeviceEntities
INSERT INTO DeviceEntities (entity_id, entity_type, entity_name, device_id, is_active, last_reading, last_reading_timestamp, service_id, thingspeak_field_id)
VALUES
(1, 'sensor', 'Temperature Sensor', 1, true, '22.5', '2024-09-08 19:02:14.163875+00:00', 1, NULL),
(2, 'sensor', 'Humidity Sensor', 1, true, '45', '2024-09-08 19:02:14.163875+00:00', 2, NULL),
(3, 'sensor', 'Blood Pressure Sensor', 2, true, '120/80', '2024-09-08 19:02:14.163875+00:00', 3, NULL),
(4, 'actuator', 'Bedroom Lamp', 3, true, NULL, NULL, NULL, NULL),
(5, 'sensor', 'Temperature Sensor2', 3, true, NULL, NULL, 1, NULL),
(6, 'sensor', 'Blood Pressure2', 1, true, NULL, NULL, 3, NULL);

-- Endpoints
INSERT INTO Endpoints (endpoint_id, service_id, entity_id, endpoint)
VALUES
(1, 1, 1, '/1/body_temp_check/001B44113A/1'),
(2, 3, 3, '/2/blood_pressure/FF1B44113A/3');

-- ConfigKeys
INSERT INTO ConfigKeys (config_key, description, value_type, apply_to)
VALUES
('max_limit', 'Defines the maximum reading limit for the sensor.', 'numeric', 'sensor'),
('unit', 'Defines the measurement unit of the sensor (Celsius or Fahrenheit).', 'string', 'sensor'),
('initial_state', 'Defines the initial state of the actuator (on or off).', 'boolean', 'actuator'),
('operation_mode', 'Defines the operation mode of the actuator (automatic or manual).', 'string', 'actuator'),
('sampling_rate', 'Defines the rate at which the sensor takes readings, in seconds.', 'numeric', 'sensor'),
('schedule', 'Schedule configuration for the actuator (e.g., turning on/off at specific times).', 'json', 'actuator');

-- EntityConfigurations
INSERT INTO EntityConfigurations (config_id, entity_id, config_key, config_value)
VALUES
(1, 1, 'sampling_rate', '60s'),
(2, 3, 'unit', 'mmHg');

-- TelegramBot
INSERT INTO TelegramBot (bot_id, bot_token, chat_id, patient_id, last_message, last_message_timestamp, has_history_access)
VALUES
(1, '12345:ABCDEF123456', '987654321', 1, NULL, NULL, true),
(2, '67890:ZYXWV987654', '123456789', 2, NULL, NULL, false);

-- Schedules
INSERT INTO Schedules (entity_id, day_of_week, start_time, end_time, repeat, action)
VALUES
(4, 'Wednesday', '12:00', NULL, 0, 'ON'),
(4, 'Wednesday', '17:00', NULL, 0, 'OFF'),
(4, 'Friday', '07:00', '07:01', 1, 'ON'),
(4, 'Saturday', '07:00', '07:01', 1, 'OFF'),
(4, 'Monday', '08:00', '12:00', 1, 'ON'),
(4, 'Monday', '12:00', '12:01', 1, 'OFF');
