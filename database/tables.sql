--products
CREATE TABLE IF NOT EXISTS products(
    name VARCHAR(50) UNIQUE,
    price REAL NOT NULL,
    photo_id TEXT,
    description VARCHAR(255),
    tags VARCHAR(100)
);

--users
CREATE TABLE IF NOT EXISTS users(
    chat_id BIGINT NOT NULL,
    username TEXT,
    is_admin BOOLEAN DEFAULT FALSE,
    balance REAL DEFUALT 0.0,
    PRIMARY KEY (chat_id)
);

--carts
CREATE TABLE IF NOT EXISTS carts(
    chat_id BIGINT REFERENCES users(chat_id) ON DELETE CASCADE,
    name VARCHAR(50) REFERENCES products(name) ON DELETE CASCADE,
    PRIMARY KEY(chat_id, name)
);

--indexes
CREATE INDEX IF NOT EXISTS index_name ON products (name);
CREATE INDEX IF NOT EXISTS index_name ON carts (name);