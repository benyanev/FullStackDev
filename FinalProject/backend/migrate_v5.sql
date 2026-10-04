-- =============================================
-- Migration v5: Likes & Comments tables
-- Run: mysql -u root -p social_app < backend/migrate_v5.sql
-- =============================================

USE social_app;

-- Likes: junction table — one like per user per post
CREATE TABLE IF NOT EXISTS likes (
    user_id    INT NOT NULL,
    post_id    INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

-- Comments: flat with optional nesting via parent_id
CREATE TABLE IF NOT EXISTS comments (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    post_id    INT NOT NULL,
    author_id  INT NOT NULL,
    parent_id  INT DEFAULT NULL,
    body       TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id)   REFERENCES posts(id)    ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES comments(id) ON DELETE CASCADE,
    INDEX idx_comments_post (post_id)
);
