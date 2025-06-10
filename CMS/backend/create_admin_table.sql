-- 创建管理员用户表
CREATE TABLE IF NOT EXISTS admin_users (
  userid INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  email VARCHAR(100),
  password_hash VARCHAR(255) NOT NULL,
  status VARCHAR(20) DEFAULT 'active',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_login DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 为表添加索引以提高查询性能
CREATE INDEX idx_admin_username ON admin_users(username); 