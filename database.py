import sqlite3
import hashlib

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS blogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            complexity TEXT NOT NULL,
            interests TEXT NOT NULL,
            output TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO users (username, email, password)
        VALUES (?, ?, ?)
    ''', (username, email, hash_password(password)))
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = get_db_connection()
    user = conn.execute('''
        SELECT * FROM users WHERE username = ? AND password = ?
    ''', (username, hash_password(password))).fetchone()
    conn.close()
    return user

def user_exists(username):
    conn = get_db_connection()
    user = conn.execute('''
        SELECT * FROM users WHERE username = ?
    ''', (username,)).fetchone()
    conn.close()
    return user is not None

def get_all_users():
    conn = get_db_connection()
    users = conn.execute('SELECT id, username, email FROM users').fetchall()
    conn.close()
    return users

def print_all_users():
    users = get_all_users()
    for user in users:
        print(f"ID: {user['id']}, Username: {user['username']}, Email: {user['email']}")

if __name__ == "__main__":
    create_tables()
    print_all_users()
