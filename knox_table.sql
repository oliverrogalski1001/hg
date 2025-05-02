-- create copy of rules for knox algorithm with only sceneId 3 and 0 indexed
CREATE TABLE knox_rule AS SELECT * FROM t_rule WHERE sceneId = 3;
ALTER TABLE knox_rule AUTO_INCREMENT = 0;
ALTER TABLE knox_rule ADD id INT PRIMARY KEY AUTO_INCREMENT;
ALTER TABLE knox_rule ADD id_zero INT;
UPDATE knox_rule SET id_zero = id - 1;
