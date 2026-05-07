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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Posts table: stores user-created posts
CREATE TABLE IF NOT EXISTS posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    author_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index for faster lookups by author
CREATE INDEX idx_posts_author ON posts(author_id);
