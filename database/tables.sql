CREATE TABLE IF NOT EXISTS products(
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
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
    product_id INTEGER REFERENCES products(id),
    PRIMARY KEY(chat_id, product_id)
);
