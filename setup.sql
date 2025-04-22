
CREATE TABLE IF NOT EXISTS t_rule (
    ruleId INT,
    ruleName TEXT,
    conditionIds VARCHAR(50),
    actionIds VARCHAR(50),
    dayofweeks VARCHAR(50),
    starttime TIME,
    endtime TIME,
    userId INT,
    sceneid INT
);
LOAD DATA LOCAL INFILE "Data/experiment rules/t_rule.txt" INTO TABLE t_rule IGNORE 3 ROWS;

CREATE TABLE IF NOT EXISTS t_condition (
    conditionId INT,
    deviceId INT,
    attribute VARCHAR(255),
    compareType INT,
    standardValue INT
);
LOAD DATA LOCAL INFILE "Data/experiment rules/t_condition.txt" INTO TABLE t_condition IGNORE 3 ROWS;

CREATE TABLE IF NOT EXISTS t_action (
    actionId INT,
    deviceId INT,
    attribute VARCHAR(255),
    newValue INT
);
LOAD DATA LOCAL INFILE "Data/experiment rules/t_action.txt" INTO TABLE t_action IGNORE 3 ROWS;

CREATE TABLE IF NOT EXISTS t_entity (
  deviceid INT,
  attribute VARCHAR(255),
  compareType INT,
  newvalue INT,
  influence INT
);
LOAD DATA LOCAL INFILE "Data/experiment rules/t_entity.txt" INTO TABLE t_entity IGNORE 3 ROWS;

CREATE TABLE IF NOT EXISTS t_spec (
  device1id	INT,
  attribute1 VARCHAR(255),
  newValue1 INT,
  device2id INT,
  attribute2 VARCHAR(255),
  newValue2	INT,
  together INT
);
LOAD DATA LOCAL INFILE "Data/experiment rules/t_spec.txt" INTO TABLE t_spec IGNORE 3 ROWS;
