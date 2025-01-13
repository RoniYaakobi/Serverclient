import sqlite3
from datetime import datetime
import bcrypt
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_name='chat_database.db'):
        self.db_name = db_name
        self.init_database()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        try:
            yield conn
        finally:
            conn.close()

    def init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create rooms table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_id INTEGER,
                    user_id INTEGER,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (room_id) REFERENCES rooms (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Create room_members table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS room_members (
                    room_id INTEGER,
                    user_id INTEGER,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (room_id) REFERENCES rooms (id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    PRIMARY KEY (room_id, user_id)
                )
            ''')
            
            conn.commit()

    def create_user(self, username, password, email):
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    'INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
                    (username, password_hash.decode(), email)
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def verify_user(self, username, password):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            
            if result and bcrypt.checkpw(password.encode(), result[1].encode()):
                return result[0]  # Return user_id
            return None

    def create_room(self, name, description=""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO rooms (name, description) VALUES (?, ?)',
                (name, description)
            )
            conn.commit()
            return cursor.lastrowid

    def add_user_to_room(self, user_id, room_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    'INSERT INTO room_members (room_id, user_id) VALUES (?, ?)',
                    (room_id, user_id)
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def get_user_rooms(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.id, r.name, r.description
                FROM rooms r
                JOIN room_members rm ON r.id = rm.room_id
                WHERE rm.user_id = ?
            ''', (user_id,))
            return cursor.fetchall()

    def save_message(self, room_id, user_id, content):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO messages (room_id, user_id, content) VALUES (?, ?, ?)',
                (room_id, user_id, content)
            )
            conn.commit()
            return cursor.lastrowid

    def get_room_messages(self, room_id, limit=50):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT m.id, m.content, m.created_at, u.username
                FROM messages m
                JOIN users u ON m.user_id = u.id
                WHERE m.room_id = ?
                ORDER BY m.created_at DESC
                LIMIT ?
            ''', (room_id, limit))
            return cursor.fetchall()

    def get_username(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None