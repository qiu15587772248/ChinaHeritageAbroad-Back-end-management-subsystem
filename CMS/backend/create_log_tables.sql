-- 创建操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
  id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  admin_id INT(11) NOT NULL,
  admin_username VARCHAR(50) NOT NULL,
  operation_type VARCHAR(50) NOT NULL,
  operation_content TEXT,
  operation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  ip_address VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 为表添加索引以提高查询性能
CREATE INDEX idx_operation_admin ON operation_logs(admin_id); 