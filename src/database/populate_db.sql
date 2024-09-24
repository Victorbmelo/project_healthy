-- Users
INSERT INTO Users (user_id, name, address, emergency_contact, passport_code)
VALUES (1, 'Pedro Loa', '123 Via Um', '555-1234-555', 'P12345678');

INSERT INTO Users (user_id, name, address, emergency_contact, passport_code)
VALUES (2, 'Joao Town', '456 Via Dois', '555-5678-555', 'P23456789');

-- Services
INSERT INTO Services (service_id, name, alias, service_description, status, last_run_timestamp, protocol)
VALUES
(1, 'body_temp_check', 'Body Temperature Check', 'Monitors body temperatures', 'Active', '2024-08-22 21:28:49.076691', 'MQTT'),
(2, 'air_conditioning', 'Air Conditioning Control', 'Controls air conditioning system', 'Inactive', NULL, 'MQTT'),
(3, 'blood_pressure', 'Blood Pressure Monitoring', 'Monitors blood pressure levels', 'Inactive', NULL, 'MQTT'),
(4, 'body_temperature', 'Body Temperature Monitoring', 'Monitors body temperature', 'Inactive', NULL, 'MQTT'),
(5, 'telegram_bot', 'Telegram Bot Notifications', 'Sends notifications via Telegram', 'Active', '2024-08-22 21:28:49.076691', 'Telegram'),
(6, 'thingspeak', 'ThingSpeak Integration', 'Sends data to ThingSpeak', 'Active', '2024-08-22 21:28:49.076691', 'HTTP');

-- Devices
INSERT INTO Devices (device_id, mac_address, device_name, device_type, location, status, user_id, thingspeak_channel_key)
VALUES
(1, '001B44113A', 'RPi 4', 'Server', 'Living Room', 'Active', 1, NULL),
(2, 'FF1B44113A', 'RPi Zero', 'Weareable', 'User', 'Active', 2, NULL),
(3, 'DD1B44113F', 'Arduino', 'Actuator Control', 'Bedroom', 'Active', 2, NULL);

-- Sensors
INSERT INTO Sensors (sensor_id, sensor_type, device_id, service_id, last_reading, last_reading_timestamp, thingspeak_field_id)
VALUES
(1, 'Temperature', 1, 1, '22.5', '2024-09-08 19:02:14.163875+00:00', NULL),
(2, 'Humidity', 1, NULL, '45', '2024-09-08 19:02:14.163875+00:00', NULL),
(3, 'Blood Pressure', 2, 3, '120/80', '2024-09-08 19:02:14.163875+00:00', NULL);

-- Actuators
INSERT INTO Actuators (actuator_id, actuator_type, device_id, service_id, status, thingspeak_field_id)
VALUES
(1, 'Lamp', 3, NULL, 'Active', NULL);

-- Endpoints
INSERT INTO Endpoints (endpoint_id, service_id, entity_type, entity_id, endpoint)
VALUES
(1, 1, 'sensor', 1, '/1/body_temp_check/001B44113A/sensor/1');
