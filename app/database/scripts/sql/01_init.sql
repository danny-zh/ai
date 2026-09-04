CREATE DATABASE IF NOT EXISTS habitdb
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE habitdb;

CREATE TABLE IF NOT EXISTS `user` (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(254) NOT NULL,
    password VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT uq_user_username UNIQUE (username),
    CONSTRAINT uq_user_email UNIQUE (email)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS habit (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(32) NOT NULL,
    description TEXT NULL,
    id_user BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT uq_habit_id_user UNIQUE (id, id_user),
    CONSTRAINT fk_habit_user
        FOREIGN KEY (id_user) REFERENCES `user` (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS habit_log (
    id_habit BIGINT UNSIGNED NOT NULL,
    id_user BIGINT UNSIGNED NOT NULL,
    habit_duration INT UNSIGNED NOT NULL DEFAULT 60,
    log_date DATE NOT NULL,
    PRIMARY KEY (id_habit, log_date),
    KEY idx_habit_log_id_user (id_user),
    CONSTRAINT chk_habit_log_duration CHECK (habit_duration >= 0),
    CONSTRAINT fk_habit_log_habit_owner
        FOREIGN KEY (id_habit, id_user) REFERENCES habit (id, id_user)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_habit_log_user
        FOREIGN KEY (id_user) REFERENCES `user` (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB;