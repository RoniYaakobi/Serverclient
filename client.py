import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
import time

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Chat Client")
        self.master.geometry("500x600")
        
        # Initializing socket
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "192.168.1.248"  # Change this to your server's IP
        self.port = 8000
        
        self.username = ""
        self.password = ""
        self.connected = False
        self.receive_thread = None
        self.running = True

        # Login Frame
        self.login_frame = tk.Frame(self.master)
        self.login_frame.pack(pady=20)
        
        tk.Label(self.login_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(self.login_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Chat Frame (hidden initially)
        self.chat_frame = tk.Frame(self.master)
        
        self.chat_display = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, state=tk.DISABLED, height=25, width=58)
        self.chat_display.pack(pady=10)
        
        self.message_entry = tk.Entry(self.chat_frame, width=40)
        self.message_entry.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.send_button = tk.Button(self.chat_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=10)
        
        self.exit_button = tk.Button(self.chat_frame, text="Exit", command=self.exit_chat)
        self.exit_button.pack(side=tk.LEFT, padx=10)

        # Bind window close event
        self.master.protocol("WM_DELETE_WINDOW", self.exit_chat)

    def update_chat_display(self, message):
        """Update the chat display with only the latest message."""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)  # Clear previous content
        self.chat_display.insert(tk.END, message)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.yview(tk.END)

    def login(self):
        """Handle user login."""
        self.username = self.username_entry.get().strip()
        self.password = self.password_entry.get().strip()

        if not self.username or not self.password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return

        try:
            self.my_socket.connect((self.host, self.port))
            auth = self.my_socket.recv(1024).decode("utf-8")
            if auth == "sign in":
                sign_in = f"{self.username}:{self.password}"
                self.my_socket.send(sign_in.encode("utf-8"))
                
                welcome_message = self.my_socket.recv(1024).decode("utf-8")
                self.show_chat(welcome_message)
                
                # Start receive thread after successful login
                self.receive_thread = threading.Thread(target=self.receive_messages)
                self.receive_thread.daemon = True
                self.receive_thread.start()
                
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to the server: {e}")

    def show_chat(self, welcome_message):
        """Switch to the chat frame and display the welcome message."""
        self.login_frame.pack_forget()
        self.chat_frame.pack(pady=20)
        self.master.after(0, self.update_chat_display, welcome_message)

    def receive_messages(self):
        """Continuously listen for messages from the server in a separate thread."""
        while self.running:
            try:
                # Set socket to non-blocking mode
                self.my_socket.setblocking(False)
                
                try:
                    data = self.my_socket.recv(1024).decode("utf-8")
                    if data:
                        # Schedule the GUI update to run in the main thread
                        self.master.after(0, self.update_chat_display, data)
                except BlockingIOError:
                    # No data available, continue the loop
                    pass
                except socket.error:
                    if self.running:  # Only show error if not deliberately closing
                        self.master.after(0, messagebox.showerror, "Error", "Lost connection to server")
                    break
                    
                # Small sleep to prevent CPU overuse
                time.sleep(0.1)
                
            except Exception as e:
                if self.running:  # Only show error if not deliberately closing
                    self.master.after(0, messagebox.showerror, "Error", f"Lost connection to server: {e}")
                break

    def send_message(self):
        """Send a message to the server."""
        msg = self.message_entry.get().strip()
        if msg:
            try:
                self.my_socket.send(msg.encode())
                self.message_entry.delete(0, tk.END)
                self.master.after(0, self.update_chat_display, f"You: {msg}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send message: {e}")

    def exit_chat(self):
        """Exit the chat and close the socket."""
        self.running = False  # Stop the receiving thread
        try:
            self.my_socket.send("Exit".encode("utf-8"))
            self.my_socket.close()
        except Exception:
            pass
        self.master.destroy()

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()