-- =============================================
-- Migration v8: Agent (bot) accounts
-- Run: mysql -u root -p social_app < backend/migrate_v8.sql
-- Then create the bots: python seed_agents.py
-- =============================================

USE social_app;

-- is_agent: 1 = autonomous AI bot account (World Simulation, Core 2d)
-- personality: the character description that drives the bot's posts/comments
ALTER TABLE users
    ADD COLUMN is_agent TINYINT(1) NOT NULL DEFAULT 0,
    ADD COLUMN personality TEXT NULL;
