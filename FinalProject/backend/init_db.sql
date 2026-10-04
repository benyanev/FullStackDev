-- =============================================
-- SocialApp — Database Initialization (complete, current schema)
--
-- Creates a NEW database with everything from migrations v2–v9 already
-- included.  Used automatically by Docker (mounted into the MySQL
-- container's /docker-entrypoint-initdb.d/) and for fresh local setups:
--     mysql -u root -p < backend/init_db.sql
--
-- An EXISTING database should instead be upgraded with the
-- migrate_vX.sql files it hasn't run yet.
-- =============================================

CREATE DATABASE IF NOT EXISTS social_app
    CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE social_app;

-- Users: accounts (humans + AI agents), bcrypt password hashes, roles
CREATE TABLE IF NOT EXISTS users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    bio             TEXT,
    profile_picture VARCHAR(500) DEFAULT '',
    role            ENUM('user', 'admin') NOT NULL DEFAULT 'user',  -- admin = moderator
    is_banned       TINYINT(1) NOT NULL DEFAULT 0,
    is_agent        TINYINT(1) NOT NULL DEFAULT 0,                 -- 1 = AI bot account
    personality     TEXT                                           -- drives a bot's content
);

-- Posts: rich-text body (Tiptap HTML) + optional image OR video
CREATE TABLE IF NOT EXISTS posts (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    author_id  INT NOT NULL,
    title      VARCHAR(255) NOT NULL,
    body       TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    image_url  VARCHAR(500) DEFAULT '',
    video_url  VARCHAR(500) NOT NULL DEFAULT '',
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_posts_author (author_id)
);

-- Sessions: server-side login sessions (UUID in an HttpOnly cookie)
CREATE TABLE IF NOT EXISTS sessions (
    id         CHAR(36) PRIMARY KEY,
    user_id    INT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_sessions_user (user_id),
    INDEX idx_sessions_expires (expires_at)
);

-- Follows: who follows whom (junction table)
CREATE TABLE IF NOT EXISTS follows (
    follower_id  INT NOT NULL,
    following_id INT NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower_id, following_id),
    FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (following_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_follows_follower (follower_id),
    INDEX idx_follows_following (following_id)
);

-- Likes: one like per user per post (junction table)
CREATE TABLE IF NOT EXISTS likes (
    user_id    INT NOT NULL,
    post_id    INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

-- Comments: flat, with optional nesting via parent_id
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

-- Password resets: one-time tokens emailed to the user (1 hour expiry)
CREATE TABLE IF NOT EXISTS password_resets (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    token      CHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    used       TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_resets_user (user_id)
);

-- Reports: users flag posts for moderator review (one per user per post)
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
