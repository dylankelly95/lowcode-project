CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique auto-incrementing ID for each artist account
    email TEXT NOT NULL, -- Required email address for the artist
    full_name TEXT NOT NULL, -- Required display or legal name of the artist
    username TEXT NOT NULL UNIQUE -- Required public handle; no two users can share a username
);

CREATE TABLE roles (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique auto-incrementing ID for each creative role
    role_name TEXT NOT NULL UNIQUE CHECK (role_name IN (
        'Musician',
        'Vocalist',
        'Visual Artist',
        'Graphic Designer',
        'Sound Designer',
        'Music Producer',
        'Audio Engineer',
        'Foley Artist'
    )) -- Required, unique role name restricted to the 8 approved creative disciplines
);

CREATE TABLE user_roles (
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE, -- Required link to users; deletes assignment if user is deleted
    role_id INTEGER NOT NULL REFERENCES roles(role_id) ON DELETE CASCADE, -- Required link to roles; deletes assignment if role is deleted
    PRIMARY KEY (user_id, role_id) -- Prevents assigning the exact same role to the same user twice
);

CREATE TABLE portfolios (
    portfolio_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique auto-incrementing ID for each portfolio
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE, -- Required 1-to-1 link to users; deletes portfolio if user is deleted
    title TEXT NOT NULL, -- Required title for the artist's portfolio
    bio TEXT NOT NULL, -- Required biography text for the portfolio
    theme TEXT -- Optional visual theme name (can be left blank/NULL)
);

CREATE TABLE projects (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique auto-incrementing ID for each project
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(portfolio_id) ON DELETE RESTRICT, -- Required link to portfolios; blocks portfolio deletion if projects still exist
    title TEXT NOT NULL, -- Required title of the creative project
    description TEXT NOT NULL, -- Required summary or description of the project
    category_medium TEXT NOT NULL, -- Required category or creative medium for the project
    release_date TEXT -- Optional release date stored as YYYY-MM-DD text
);

CREATE TABLE media (
    media_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique auto-incrementing ID for each media file
    project_id INTEGER NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE, -- Required link to projects; deletes media records automatically when parent project is deleted
    file_name TEXT NOT NULL, -- Required original or display file name
    file_type TEXT NOT NULL CHECK (file_type IN ('image', 'audio', 'video')), -- Required media type restricted to image, audio, or video
    file_url TEXT NOT NULL -- Required storage URL pointing to the media asset
);