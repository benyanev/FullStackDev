-- =============================================
-- Migration v9: Video posts (optional feature — Video Integration)
-- Run (from the backend folder):
--   Get-Content migrate_v9.sql -Raw | & "C:\Program Files\MySQL\MySQL Server 9.6\bin\mysql.exe" -u root -p
-- =============================================

USE social_app;

-- Relative path to an uploaded video in static/uploads/videos/ ('' = none).
-- A post has either an image_url or a video_url, not both.
ALTER TABLE posts ADD COLUMN video_url VARCHAR(500) NOT NULL DEFAULT '';
