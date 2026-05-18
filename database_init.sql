-- =============================================
-- 员工信息审核系统 MySQL 数据库初始化脚本
-- 账号: root, 密码: root, 服务名: MySQL60
-- =============================================

-- 1. 创建数据库
CREATE DATABASE IF NOT EXISTS online_check DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. 使用数据库
USE online_check;

-- 3. 创建用户表
CREATE TABLE IF NOT EXISTS `user` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(50) NOT NULL,
    `password` VARCHAR(100) NOT NULL,
    `name` VARCHAR(50) NOT NULL,
    `department` VARCHAR(50) NOT NULL,
    `position` VARCHAR(50) NOT NULL,
    `entry_date` DATE NOT NULL,
    `work_years` INT DEFAULT 0,
    `seniority_salary` DECIMAL(10, 2) DEFAULT 0.00,
    `role` VARCHAR(20) DEFAULT 'user',
    `status` VARCHAR(20) DEFAULT 'pending',
    `reject_reason` VARCHAR(500) DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. 创建日志表
CREATE TABLE IF NOT EXISTS `log` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `user_id` INT NOT NULL,
    `action` VARCHAR(200) NOT NULL,
    `operator` VARCHAR(50) NOT NULL,
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    CONSTRAINT `fk_log_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. 插入默认管理员账号
INSERT INTO `user` (`username`, `password`, `name`, `department`, `position`, `entry_date`, `work_years`, `seniority_salary`, `role`, `status`)
VALUES ('admin', 'admin', '系统管理员', '管理部', '管理员', '2020-01-01', 4, 800.00, 'admin', 'approved')
ON DUPLICATE KEY UPDATE `username` = `username`;

-- 6. 插入默认普通员工账号
INSERT INTO `user` (`username`, `password`, `name`, `department`, `position`, `entry_date`, `work_years`, `seniority_salary`, `role`, `status`)
VALUES ('user01', '123456', '张三', '技术部', '工程师', '2022-06-15', 2, 400.00, 'user', 'pending')
ON DUPLICATE KEY UPDATE `username` = `username`;

-- 7. 查看创建结果
SELECT '数据库初始化完成！' AS message;
SELECT * FROM `user`;