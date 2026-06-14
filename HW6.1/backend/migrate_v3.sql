-- =============================================
-- SocialApp — Migration v3: Add profile fields
-- Run via MySQL Workbench or CLI
-- =============================================

USE social_app;

-- Add bio and profile_picture columns to existing users table
ALTER TABLE users ADD COLUMN bio TEXT, ADD COLUMN profile_picture VARCHAR(500) DEFAULT '';
