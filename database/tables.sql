CREATE TABLE IF NOT EXISTS products(
    name VARCHAR(50) UNIQUE,
    price REAL NOT NULL,
    photo_id TEXT,
    description VARCHAR(255),
    tags VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS users(
    chat_id BIGINT NOT NULL,
    username TEXT,
    is_admin BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (chat_id)
);

CREATE TABLE IF NOT EXISTS carts(
    chat_id BIGINT REFERENCES users(chat_id),
    name VARCHAR(50) UNIQUE REFERENCES products(name),
    PRIMARY KEY(chat_id, name)
);

CREATE INDEX IF NOT EXISTS index_tags ON products (tags);