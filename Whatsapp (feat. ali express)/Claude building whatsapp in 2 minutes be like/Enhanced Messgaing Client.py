import socket
import threading
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class MessagingClient:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.user_id = None
        self.username = None
        self.current_room = None
        self.rooms = []
        self.online_users = set()
        
        # Setup encryption
        self.setup_encryption()
        
        # Initialize GUI
        self.root = tk.Tk()
        self.root.title("Enterprise Messaging App")
        self.root.geometry("1000x700")
        self.setup_styles()
        self.show_login_register_choice()

    def setup_encryption(self):
        # Generate encryption key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'static_salt',  # In production, use a proper salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(b"static_key"))  # In production, use a proper key
        self.cipher_suite = Fernet(key)

    def setup_styles(self):
        # Configure styles
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('Room.TFrame', background='#e0e0e0')
        style.configure('Chat.TFrame', background='#ffffff')
        style.configure('TButton', padding=5)
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('Room.TLabel', font=('Helvetica', 10))
        
        # Custom styles for messages
        self.root.option_add('*TButton*background', '#007bff')
        self.root.option_add('*TButton*foreground', 'white')

    def show_login_register_choice(self):
        self.choice_frame = ttk.Frame(self.root, padding="20", style='TFrame')
        self.choice_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        ttk.Label(self.choice_frame, text="Welcome to Enterprise Messaging", 
                 font=('Helvetica', 16, 'bold')).pack(pady=20)
        
        ttk.Button(self.choice_frame, text="Login", 
                  command=self.show_login).pack(fill='x', pady=5)
        ttk.Button(self.choice_frame, text="Register", 
                  command=self.show_register).pack(fill='x', pady=5)

    def show_register(self):
        self.choice_frame.destroy()
        self.register_frame = ttk.Frame(self.root, padding="20", style='TFrame')
        self.register_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        ttk.Label(self.register_frame, text="Register", 
                 font=('Helvetica', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(self.register_frame, text="Username:").grid(row=1, column=0, pady=5)
        self.reg_username = ttk.Entry(self.register_frame)
        self.reg_username.grid(row=1, column=1, pady=5)
        
        ttk.Label(self.register_frame, text="Email:").grid(row=2, column=0, pady=5)
        self.reg_email = ttk.Entry(self.register_frame)
        self.reg_email.grid(row=2, column=1, pady=5)
        
        ttk.Label(self.register_frame, text="Password:").grid(row=3, column=0, pady=5)
        self.reg_password = ttk.Entry(self.register_frame, show="*")
        self.reg_password.grid(row=3, column=1, pady=5)
        
        ttk.Button(self.register_frame, text="Register", 
                  command=self.register).grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(self.register_frame, text="Back", 
                  command=self.back_to_choice).grid(row=5, column=0, columnspan=2)

    def show_login(self):
        self.choice_frame.destroy()
        self.login_frame = ttk.Frame(self.root, padding="20", style='TFrame')
        self.login_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        ttk.Label(self.login_frame, text="Login", 
                 font=('Helvetica', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(self.login_frame, text="Username:").grid(row=1, column=0, pady=5)
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(self.login_frame, text="Password:").grid(row=2, column=0, pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=2, column=1, pady=5)
        
        ttk.Button(self.login_frame, text="Login", 
                  command=self.login).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(self.login_frame, text="Back", 
                  command=self.back_to_choice).grid(row=4, column=0, columnspan=2)

    def back_to_choice(self):
        if hasattr(self, 'login_frame'):
            self.login_frame.destroy()
        if hasattr(self, 'register_frame'):
            self.register_frame.destroy()
        self.show_login_register_choice()

    def register(self):
        try:
            self.client_socket.connect((self.host, self.port))
            
            # Send registration data
            reg_data = {
                'command': 'register',
                'username': self.reg_username.get(),
                'password': self.reg_password.get(),
                'email': self.reg_email.get()
            }
            self.send_encrypted(reg_data)
            
            # Receive response
            response = self.receive_encrypted()
            
            if response['status'] == 'success':
                messagebox.showinfo("Success", "Registration successful! Please login.")
                self.show_login()
            else:
                messagebox.showerror("Registration Failed", response['message'])
                
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server: {e}")

    
    def login(self):
        try:
            # Connect to server if not already connected
            if not self.client_socket.fileno() > 0:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.host, self.port))
            
            # Get credentials from entry fields
            username = self.username_entry.get()
            password = self.password_entry.get()
            
            # Validate input
            if not username or not password:
                messagebox.showerror("Error", "Please enter both username and password")
                return
                
            # Prepare login data
            login_data = {
                'command': 'login',
                'username': username,
                'password': password
            }
            
            # Send encrypted login data
            self.send_encrypted(login_data)
            
            # Receive and process server response
            response = self.receive_encrypted()
            
            if response['status'] == 'success':
                self.user_id = response['user_id']
                self.username = username
                self.rooms = response.get('rooms', [])
                
                # Start receiving messages in a separate thread
                self.receive_thread = threading.Thread(target=self.receive_messages)
                self.receive_thread.daemon = True
                self.receive_thread.start()
                
                # Setup main chat GUI
                self.setup_chat_gui()
                
            else:
                messagebox.showerror("Login Failed", response.get('message', 'Invalid credentials'))
                
        except ConnectionRefusedError:
            messagebox.showerror("Connection Error", "Could not connect to server. Please ensure the server is running.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            # Reset socket on error
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    
    def setup_chat_gui(self):
        if hasattr(self, 'login_frame'):
            self.login_frame.destroy()
        
        # Main container
        self.main_container = ttk.Frame(self.root, style='TFrame')
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left sidebar
        self.left_sidebar = ttk.Frame(self.main_container, style='Room.TFrame', width=200)
        self.left_sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # User info
        ttk.Label(self.left_sidebar, text=f"Logged in as: {self.username}", 
                 style='Header.TLabel').pack(pady=5)
        
        # Rooms section
        ttk.Label(self.left_sidebar, text="Rooms", style='Header.TLabel').pack(pady=5)
        self.rooms_listbox = tk.Listbox(self.left_sidebar, width=25, bg='#ffffff')
        self.rooms_listbox.pack(fill=tk.X, padx=5, pady=5)
        self.rooms_listbox.bind('<<ListboxSelect>>', self.on_room_selected)
        
        # Online users section
        ttk.Label(self.left_sidebar, text="Online Users", style='Header.TLabel').pack(pady=5)
        self.users_listbox = tk.Listbox(self.left_sidebar, width=25, bg='#ffffff')
        self.users_listbox.pack(fill=tk.X, padx=5, pady=5)
        self.users_listbox.bind('<Double-Button-1>', self.start_private_chat)
        
        # Disconnect button
        ttk.Button(self.left_sidebar, text="Disconnect", 
                  command=self.disconnect).pack(pady=10, padx=5, fill=tk.X)
        
        # Chat area
        self.chat_frame = ttk.Frame(self.main_container, style='Chat.TFrame')
        self.chat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Room info
        self.room_info = ttk.Label(self.chat_frame, text="Select a room to start chatting", 
                                 style='Header.TLabel')
        self.room_info.pack(pady=5)
        
        # Chat display
        self.chat_area = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, 
                                                 bg='#ffffff', font=('Helvetica', 10))
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat_area.config(state='disabled')
        
        # Message input area
        self.input_frame = ttk.Frame(self.chat_frame, style='Chat.TFrame')
        self.input_frame.pack(fill=tk.X, pady=5)
        
        self.message_input = ttk.Entry(self.input_frame)
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.message_input.bind('<Return>', lambda e: self.send_message())
        
        ttk.Button(self.input_frame, text="Send", 
                  command=self.send_message).pack(side=tk.RIGHT, padx=5)
        
        # Update rooms list
        self.update_rooms_list()

    def disconnect(self):
        try:
            # Send disconnect message to server
            self.send_encrypted({'command': 'disconnect'})
            self.client_socket.close()
        except:
            pass
        finally:
            self.root.destroy()

    def start_private_chat(self, event):
        selection = self.users_listbox.curselection()
        if selection:
            target_user = self.users_listbox.get(selection[0])
            if target_user != self.username:
                self.open_private_chat(target_user)

    def open_private_chat(self, target_user):
        # Create new window for private chat
        chat_window = tk.Toplevel(self.root)
        chat_window.title(f"Chat with {target_user}")
        chat_window.geometry("400x500")
        
        # Chat display
        chat_display = scrolledtext.ScrolledText(chat_window, wrap=tk.WORD)
        chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        chat_display.config(state='disabled')
        
        # Message input
        input_frame = ttk.Frame(chat_window)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        message_input = ttk.Entry(input_frame)
        message_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def send_private_message():
            message = message_input.get().strip()
            if message:
                self.send_encrypted({
                    'command': 'private_message',
                    'target': target_user,
                    'message': message
                })
                message_input.delete(0, tk.END)
                # Display own message
                chat_display.config(state='normal')
                chat_display.insert(tk.END, f"You: {message}\n")
                chat_display.see(tk.END)
                chat_display.config(state='disabled')
        
        ttk.Button(input_frame, text="Send", 
                  command=send_private_message).pack(side=tk.RIGHT, padx=5)
        message_input.bind('<Return>', lambda e: send_private_message())

    def send_encrypted(self, data):
        encrypted_data = self.cipher_suite.encrypt(json.dumps(data).encode())
        self.client_socket.send(encrypted_data)

    def receive_encrypted(self):
        encrypted_data = self.client_socket.recv(1024)
        decrypted_data = self.cipher_suite.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())
    
    def receive_messages(self):
        """Background thread function to receive messages from server"""
        while True:
            try:
                # Receive and decrypt message from server
                response = self.receive_encrypted()
                
                if response.get('command') == 'message':
                    self.display_message(response['username'], response['message'], response['room'])
                elif response.get('command') == 'private_message':
                    self.handle_private_message(response)
                elif response.get('command') == 'system':
                    self.display_system_message(response['message'])
                elif response.get('command') == 'user_update':
                    self.update_online_users(response['users'])
                elif response.get('command') == 'room_update':
                    self.update_rooms_list()
                    
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    # ... (rest of the methods remain similar but use send_encrypted/receive_encrypted)

    def start(self):
        self.root.mainloop()

if __name__ == "__main__":
    client = MessagingClient()
    client.start()