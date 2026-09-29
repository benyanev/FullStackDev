-- =============================================
-- Migration v7: Admin roles, bans, and post reports
-- Run: mysql -u root -p social_app < backend/migrate_v7.sql
-- =============================================

USE social_app;

-- Role: 'admin' users can open the Admin Dashboard (moderators)
-- is_banned: banned users cannot log in
ALTER TABLE users
    ADD COLUMN role ENUM('user', 'admin') NOT NULL DEFAULT 'user',
    ADD COLUMN is_banned TINYINT(1) NOT NULL DEFAULT 0;

-- Reports: a user flags a post for moderator review.
-- One report per user per post (UNIQUE). Deleting the post deletes its reports.
CREATE TABLE IF NOT EXISTS reports (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    reporter_id INT NOT NULL,
    post_id     INT NOT NULL,
    reason      VARCHAR(500) NOT NULL,
    status      ENUM('pending', 'resolved', 'dismissed') NOT NULL DEFAULT 'pending',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id)     REFERENCES posts(id) ON DELETE CASCADE,
    UNIQUE KEY uq_reports_reporter_post (reporter_id, post_id),
    INDEX idx_reports_status (status)
);

-- Make the first moderator (replace with your own email):
-- UPDATE users SET role = 'admin' WHERE email = 'you@example.com';
