-- =============================================
-- SocialApp — Migration v4: Add image_url to posts
-- Run via MySQL Workbench or CLI
-- =============================================

USE social_app;

-- Add image_url column to existing posts table
ALTER TABLE posts ADD COLUMN image_url VARCHAR(500) DEFAULT '';
