CREATE TABLE `performance_test`
(
  `id`               BIGINT AUTO_INCREMENT PRIMARY KEY,
  `ts`               DATETIME DEFAULT CURRENT_TIMESTAMP,
  `provider`         VARCHAR(64) NOT NULL,
  `ip`               VARCHAR(64)  NULL,
  `target_status`    INT NULL,
  `exception_status` INT NULL,
  `response_time`    FLOAT NULL
);
