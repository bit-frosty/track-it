import sqlite3
import os

DATABASE_FILE = 'frostbytectf.db'

def add_asset(name, location, user_id):
    """Add a new asset to the database with logging."""
    with connect_db() as conn:
        conn.execute(
            'INSERT INTO assets (name, location, user_id) VALUES (?, ?, ?)', 
            (name, location, user_id)
        )
        log_event("DATABASE", f"Asset '{name}' added for user {user_id}")
        conn.commit()

def add_user(username, password):
    """Add a user with a hashed password."""
    password_hash = hash_password(password)
    with connect_db() as conn:
        conn.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)', 
            (username, password_hash)
        )
        log_event("DATABASE", f"User '{username}' added with hashed password")
        conn.commit()


def connect_db():
    """Connect to the SQLite database with logging."""
    log_event("DATABASE", "Connecting to the database")
    return sqlite3.connect(DATABASE_FILE)

def init_db():
    """Initialize the database with the required schema."""
    if not os.path.exists(DATABASE_FILE):
        with connect_db() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS assets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            conn.commit()


def add_location_history(asset_id, location):
    """Track location history of an asset."""
    with connect_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS location_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER NOT NULL,
                location TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (asset_id) REFERENCES assets (id)
            )
        ''')
        conn.execute('INSERT INTO location_history (asset_id, location) VALUES (?, ?)', (asset_id, location))
        conn.commit()


def update_asset_location(name, new_location):
    """Update the location of an asset."""
    with connect_db() as conn:
        cursor = conn.execute('UPDATE assets SET location = ? WHERE name = ?', (new_location, name))
        conn.commit()
        return cursor.rowcount > 0
