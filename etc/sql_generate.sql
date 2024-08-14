CREATE TABLE `Users` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255),
  `address` varchar(255),
  `emergency_contact` varchar(255)
);

CREATE TABLE `Devices` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `mac_address` varchar(255) UNIQUE,
  `device_name` varchar(255),
  `device_type` varchar(255),
  `location` varchar(255),
  `status` varchar(255),
  `user_id` int
);

CREATE TABLE `Sensors` (
  `sensor_id` int PRIMARY KEY AUTO_INCREMENT,
  `sensor_type` varchar(255),
  `device_id` int,
  `last_reading` varchar(255),
  `last_reading_timestamp` datetime
);

CREATE TABLE `Actuators` (
  `actuator_id` int PRIMARY KEY AUTO_INCREMENT,
  `actuator_type` varchar(255),
  `device_id` int,
  `status` varchar(255)
);

CREATE TABLE `Endpoints` (
  `endpoint_id` int PRIMARY KEY AUTO_INCREMENT,
  `service_id` int,
  `entity_type` varchar(255),
  `entity_id` int,
  `endpoint` varchar(255)
);

CREATE TABLE `Commands` (
  `command_id` int PRIMARY KEY AUTO_INCREMENT,
  `actuator_id` int,
  `command` varchar(255),
  `timestamp` datetime
);

CREATE TABLE `Alerts` (
  `alert_id` int PRIMARY KEY AUTO_INCREMENT,
  `user_id` int,
  `message` varchar(255),
  `timestamp` datetime
);

CREATE TABLE `Configurations` (
  `config_id` int PRIMARY KEY AUTO_INCREMENT,
  `device_id` int,
  `config_key` varchar(255),
  `config_value` varchar(255)
);

CREATE TABLE `Services` (
  `service_id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255) UNIQUE,
  `alias` varchar(255),
  `service_description` varchar(255),
  `status` varchar(255),
  `last_run_timestamp` datetime,
  `protocol` varchar(255)
);

CREATE INDEX `Devices_index_0` ON `Devices` (`mac_address`);

CREATE INDEX `Devices_index_1` ON `Devices` (`user_id`);

CREATE INDEX `Sensors_index_2` ON `Sensors` (`device_id`);

CREATE INDEX `Actuators_index_3` ON `Actuators` (`device_id`);

CREATE INDEX `Endpoints_index_4` ON `Endpoints` (`service_id`);

CREATE INDEX `Endpoints_index_5` ON `Endpoints` (`entity_type`);

CREATE INDEX `Endpoints_index_6` ON `Endpoints` (`entity_id`);

CREATE INDEX `Commands_index_7` ON `Commands` (`actuator_id`);

CREATE INDEX `Alerts_index_8` ON `Alerts` (`user_id`);

CREATE INDEX `Configurations_index_9` ON `Configurations` (`device_id`);

CREATE UNIQUE INDEX `Services_index_10` ON `Services` (`name`);

ALTER TABLE `Users` ADD FOREIGN KEY (`id`) REFERENCES `Devices` (`user_id`);

ALTER TABLE `Devices` ADD FOREIGN KEY (`id`) REFERENCES `Sensors` (`device_id`);

ALTER TABLE `Devices` ADD FOREIGN KEY (`id`) REFERENCES `Actuators` (`device_id`);

ALTER TABLE `Actuators` ADD FOREIGN KEY (`actuator_id`) REFERENCES `Commands` (`actuator_id`);

ALTER TABLE `Users` ADD FOREIGN KEY (`id`) REFERENCES `Alerts` (`user_id`);

ALTER TABLE `Devices` ADD FOREIGN KEY (`id`) REFERENCES `Configurations` (`device_id`);

ALTER TABLE `Services` ADD FOREIGN KEY (`service_id`) REFERENCES `Endpoints` (`service_id`);
