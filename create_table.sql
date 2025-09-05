-- SQLite version
CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    datetime DATETIME NOT NULL,
    user VARCHAR(255) NOT NULL,
    fullfill BOOLEAN NOT NULL DEFAULT FALSE,
    process_time INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- MySQL version
-- CREATE TABLE IF NOT EXISTS chats (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     session VARCHAR(255) NOT NULL,
--     question TEXT NOT NULL,
--     answer TEXT NOT NULL,
--     datetime DATETIME NOT NULL,
--     user VARCHAR(255) NOT NULL,
--     fullfill BOOLEAN NOT NULL DEFAULT FALSE,
--     process_time INT DEFAULT 0,
--     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--     updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
-- );

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_chats_session ON chats(session);
CREATE INDEX IF NOT EXISTS idx_chats_user ON chats(user);
CREATE INDEX IF NOT EXISTS idx_chats_datetime ON chats(datetime);
CREATE INDEX IF NOT EXISTS idx_chats_fullfill ON chats(fullfill);