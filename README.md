# Configuration & Setup

To properly configure the project and set up your backend environment, you need to create two essential files in your root directory: `.env` and `config.py`.

### 1. Environment Variables (`.env`)
The `.env` file acts as a secure storage for your private credentials and sensitive data. Create this file in the root directory and define the variables exactly in this format:

TOKEN="your_bot_token_here"
DB_PASS="your_postgres_password_here"
ADMIN_ID="your_telegram_id_here"

*Make sure never to commit this file to GitHub or any version control system to keep your secrets safe.*

### 2. Configuration Module (`config.py`)
The `config.py` file serves as the configuration module that reads these environment variables using the built-in `os` library and prepares them for your application logic. 

Inside `config.py`, paste the following code:

```python
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Sensitive data pulled dynamically from the hidden environment file
BOT_TOKEN = os.getenv("TOKEN")
DB_PASS = os.getenv("DB_PASS")

# Explicitly cast into an integer to ensure that administrative filters evaluate correctly
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Pre-configured parameters to match your local PostgreSQL infrastructure layout
DB_USER = "bot_user"
DB_NAME = "shop_bot"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"

The bot itself, too [link](https://t.me/shoppere_bot)