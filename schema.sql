DROP TABLE IF EXISTS work_items;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS portfolios;

CREATE TABLE portfolios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artist_name TEXT NOT NULL,
    headline TEXT,
    biography TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios (id) ON DELETE CASCADE
);

CREATE TABLE work_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    media_type TEXT CHECK(media_type IN ('image', 'video', 'audio', 'link')),
    media_url TEXT,
    is_featured INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE SET NULL
);

-- Seed initial sample artist portfolio
INSERT INTO portfolios (artist_name, headline, biography) 
VALUES (
    'Alex Morgan', 
    'Multidisciplinary Visual Artist & Designer', 
    'Exploring modern digital aesthetics through generative art, photography, and interactive design.'
);