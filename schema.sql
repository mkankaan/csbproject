CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    password_hash TEXT
);

CREATE TABLE rooms (
    id INTEGER PRIMARY KEY,
    name TEXT,
    owner INTEGER REFERENCES users
);

CREATE TABLE members (
    user_id INTEGER REFERENCES users,
    room_id INTEGER REFERENCES rooms,
    joined INTEGER DEFAULT 0
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    room_id INTEGER REFERENCES rooms,
    content TEXT,
    time TEXT
);
