-- =============================================
-- Migration v6: Password reset tokens table
-- Run: mysql -u root -p social_app < backend/migrate_v6.sql
-- =============================================

USE social_app;

CREATE TABLE IF NOT EXISTS password_resets (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    token      CHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    used       TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_resets_token (token),
    INDEX idx_resets_user (user_id)
);
