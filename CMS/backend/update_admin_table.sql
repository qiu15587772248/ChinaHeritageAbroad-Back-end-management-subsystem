-- 修改管理员表的列名，将userid改为id
ALTER TABLE admin_users CHANGE COLUMN userid id INT(11) NOT NULL AUTO_INCREMENT; 