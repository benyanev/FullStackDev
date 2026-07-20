-- =============================================
-- SocialApp — Database Initialization
-- Run: mysql -u root -p < backend/init_db.sql
-- =============================================

CREATE DATABASE IF NOT EXISTS social_app;
USE social_app;

-- Users table: stores registered user profiles with hashed passwords
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    bio TEXT,
    profile_picture VARCHAR(500) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Posts table: stores user-created posts
CREATE TABLE IF NOT EXISTS posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    author_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    image_url VARCHAR(500) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
    -- Index defined inside table:
    INDEX idx_posts_author (author_id)
);

-- Sessions table: stores active user sessions (UUID-based)
CREATE TABLE IF NOT EXISTS sessions (
    id         CHAR(36) PRIMARY KEY,
    user_id    INT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    -- Indexes defined inside table:
    INDEX idx_sessions_user (user_id),
    INDEX idx_sessions_expires (expires_at)
);

-- Follows table: stores follower/following relationships between users
CREATE TABLE IF NOT EXISTS follows (
    follower_id  INT NOT NULL,
    following_id INT NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower_id, following_id),
    FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (following_id) REFERENCES users(id) ON DELETE CASCADE,
    -- Indexes defined inside table:
    INDEX idx_follows_follower (follower_id),
    INDEX idx_follows_following (following_id)
);
