import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import socket
import json
import time

from database_manager import DatabaseManager
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class ServerGUI:
    def __init__(self, host='127.0.0.1', port=5555):
        self.root = tk.Tk()
        self.root.title("Chat Server Control Panel")
        self.root.geometry("800x600")
        self.host = host
        self.port = port
        
        self.setup_encryption()
        self.setup_gui()
        self.server_running = False
        self.clients = {}  # {user_id: (connection, username, current_room)}
        self.db = DatabaseManager()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_encryption(self):
        # Generate encryption key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'static_salt',  # In production, use a proper salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(b"static_key"))
        self.cipher_suite = Fernet(key)

    def setup_gui(self):
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Server control section
        control_frame = ttk.LabelFrame(main_container, text="Server Control", padding="10")
        control_frame.pack(fill=tk.X, pady=5)
        
        # Status and controls
        self.status_label = ttk.Label(control_frame, text="Server Status: Stopped")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.start_button = ttk.Button(control_frame, text="Start Server", command=self.start_server)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Server", command=self.stop_server, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Statistics section
        stats_frame = ttk.LabelFrame(main_container, text="Server Statistics", padding="10")
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.connected_users_label = ttk.Label(stats_frame, text="Connected Users: 0")
        self.connected_users_label.pack(side=tk.LEFT, padx=5)
        
        self.active_rooms_label = ttk.Label(stats_frame, text="Active Rooms: 0")
        self.active_rooms_label.pack(side=tk.LEFT, padx=5)
        
        # Log section
        log_frame = ttk.LabelFrame(main_container, text="Server Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=20)
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
        # Connected users section
        users_frame = ttk.LabelFrame(main_container, text="Connected Users", padding="10")
        users_frame.pack(fill=tk.X, pady=5)
        
        self.users_listbox = tk.Listbox(users_frame, height=5)
        self.users_listbox.pack(fill=tk.X)

    def log_message(self, message):
        self.log_area.insert(tk.END, f"[{time.time()}] {message}\n")
        self.log_area.see(tk.END)

    def start_server(self):
        if not self.server_running:
            try:
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.bind((self.host, self.port))
                self.server_socket.listen()
                
                self.server_running = True
                self.status_label.config(text="Server Status: Running")
                self.start_button.config(state='disabled')
                self.stop_button.config(state='normal')
                
                self.log_message(f"Server started on {self.host}:{self.port}")
                
                # Start listening for connections in a separate thread
                self.server_thread = threading.Thread(target=self.accept_connections)
                self.server_thread.daemon = True
                self.server_thread.start()
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not start server: {e}")

    def stop_server(self):
        if self.server_running:
            try:
                # Notify all clients
                self.broadcast_system_message("Server is shutting down...")
                
                # Close all client connections
                for user_id in list(self.clients.keys()):
                    self.remove_client(user_id)
                
                self.server_socket.close()
                self.server_running = False
                self.status_label.config(text="Server Status: Stopped")
                self.start_button.config(state='normal')
                self.stop_button.config(state='disabled')
                
                self.log_message("Server stopped")
                self.update_statistics()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error stopping server: {e}")

    def accept_connections(self):
        while self.server_running:
            try:
                conn, addr = self.server_socket.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.daemon = True
                thread.start()
                self.log_message(f"New connection from {addr}")
            except:
                break

    def handle_client(self, conn, addr):
        try:
            while True:
                encrypted_data = conn.recv(1024)
                if not encrypted_data:
                    break
                    
                data = json.loads(self.cipher_suite.decrypt(encrypted_data).decode())
                command = data.get('command')
                
                if command == 'register':
                    self.handle_registration(conn, data)
                elif command == 'login':
                    self.handle_login(conn, data)
                elif command == 'message':
                    self.handle_message(conn, data)
                elif command == 'private_message':
                    self.handle_private_message(conn, data)
                elif command == 'disconnect':
                    break
                    
        except Exception as e:
            self.log_message(f"Error handling client: {e}")
        finally:
            conn.close()

    def handle_registration(self, conn, data):
        success = self.db.create_user(data['username'], data['password'], data['email'])
        response = {
            'status': 'success' if success else 'error',
            'message': 'Registration successful' if success else 'Username or email already exists'
        }
        self.send_encrypted(conn, response)
        if success:
            self.log_message(f"New user registered: {data['username']}")

    def handle_login(self, conn, data):
        user_id = self.db.verify_user(data['username'], data['password'])
        if user_id:
            self.clients[user_id] = (conn, data['username'], None)
            response = {
                'status': 'success',
                'user_id': user_id,
                'rooms': self.db.get_user_rooms(user_id)
            }
            self.log_message(f"User logged in: {data['username']}")
            self.update_statistics()
        else:
            response = {
                'status': 'error',
                'message': 'Invalid credentials'
            }
        self.send_encrypted(conn, response)

    def send_encrypted(self, conn, data):
        encrypted_data = self.cipher_suite.encrypt(json.dumps(data).encode())
        conn.send(encrypted_data)

    def broadcast_system_message(self, message):
        for user_id, (conn, _, _) in self.clients.items():
            try:
                self.send_encrypted(conn, {
                    'command': 'system',
                    'message': message
                })
            except:
                pass

    def update_statistics(self):
        self.connected_users_label.config(text=f"Connected Users: {len(self.clients)}")
        active_rooms = len(set(room for _, _, room in self.clients.values() if room))
        self.active_rooms_label.config(text=f"Active Rooms: {active_rooms}")
        
        # Update users listbox
        self.users_listbox.delete(0, tk.END)
        for _, username, room in self.clients.values():
            self.users_listbox.insert(tk.END, f"{username} ({room if room else 'lobby'})")

    def remove_client(self, user_id):
        if user_id in self.clients:
            self.clients[user_id][0].close()
            del self.clients[user_id]
            self.update_statistics()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to shut down the server?"):
            self.stop_server()
            self.root.destroy()

    def start(self):
        self.root.mainloop()

if __name__ == "__main__":
    server = ServerGUI()
    server.start()