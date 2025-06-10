-- 创建移动端用户表
CREATE TABLE IF NOT EXISTS mobile_users (
  userid INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  email VARCHAR(100),
  password VARCHAR(255) NOT NULL,
  avatar LONGBLOB,
  registration_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_login DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 为表添加索引以提高查询性能
CREATE INDEX idx_mobile_username ON mobile_users(username); 