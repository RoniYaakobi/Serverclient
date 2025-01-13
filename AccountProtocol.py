from shortcuts import Shortcut
from clock import Clock

# An object that stores all the shortcuts used in all the modules

class Account:
    """
    This class is meant to generate account objects for the user objects.
    Account objects have two main purposes: to sign in and out of your username,
    and to store your information. Accounts are saved into a database while users are not.
    Accounts currently have attributes for username and password, are they currently active,
    and what room they are in. They also store the current socket and ip connected to them,
    once someone connects to them.
    """
    def __init__(self,username,password,active = Shortcut.INACTIVE, room = None, is_silent = False):
        
        self.username = username
        self.password = password

        self.active = active

        self.room = room

        if not is_silent:
            Shortcut.print_success(f"New account {username} created.")
    
    def authenticate(self,password):
        # Did user enter the right password for this account?

        return self.check_password(password) and not self.active
    
    def check_password(self,password):
        return password == self.password
    
    def signed_in(self,socket,ip):
        # Store who is connected to this account.

        self.active_socket = socket
        self.active_ip = ip

        self.active = Shortcut.ACTIVE
    
    def signed_out(self):
        # Forget who was connected to this account.
        
        self.active_socket = None
        self.active_ip = None

        self.active = Shortcut.INACTIVE
    
    def join_room(self,room):
        self.room = room
    
    def leave_room(self):
        self.room = None

class User:
    """
    This is a client class. This stores the socket and ip of the client,
    along with the account that the user logged on to.
    """
    def __init__(self,socket,ip,max_msg_length):
        Shortcut.print_initializing(f"Initializing user for {ip}")

        self.socket = socket
        self.ip = ip

        self.max_msg_length = max_msg_length
    
    def get_sign_in_info(self):
        #This method asks the user to input their username and password, in order to try to sign them in.

        sign_in_request = "sign in"
        self.socket.send(sign_in_request.encode("utf-8"))
        
        sign_in_info = self.socket.recv(self.max_msg_length).decode()
        username,password = sign_in_info.split(":")
        
        return username,password
    
    def sign_in(self,username,password,accounts):
        """
        This method checks if username already has an account. If it does, it checks the password, to see 
        if the right password has been entered. Otherwise, it creates a new account for the user.
        """
        
        Shortcut.print_initializing(f"User at {self.ip} attempted to connect to account {username} with password {password}")

        if does_account_exist(username,accounts): # Is there a username like the username entered?
            account_to_connect = accounts[username]
            can_connect = account_to_connect.authenticate(password)
            if can_connect:
               return self.connect_to_account(account_to_connect,username),accounts          
            else:
                return self.could_not_connect(account_to_connect,username,password),accounts
        else:
            return self.register(username,password,accounts)
        
    def register(self,username,password,accounts):
        #Register a new account for the user in case there isn't an account on their username.
        
        Shortcut.print_initializing(f"No account found. Creating a new account for User at {self.ip} : Username: {username} with password: {password}")
        self.account =  Account(username,password, active = Shortcut.ACTIVE)
        accounts[username] = self.account

        msg = f"Welcome, {username}!"
        self.socket.send(msg.encode("utf-8"))

        return Shortcut.ACTIVE,accounts
    
    def connect_to_account(self,account,username):
        # Connect the user to an existing account 
        self.account = account
        self.account.signed_in(self.socket,self.ip)

        msg = f"Welcome back, {username}!"
        self.socket.send(msg.encode("utf-8"))

        Shortcut.print_success(f"User at {self.ip} successfully connected to account {username}.")
        return Shortcut.ACTIVE
    
    def could_not_connect(self,account,username,password):
        # Check why user could not connect to the account, and send the reason to the client and server
        
        has_right_password = account.check_password(password)
        reason =  f"User {username} already connected!" if has_right_password else "Wrong password."
        
        msg = f"Error: could not connect to account {username}. Reason: " + reason
        
        self.socket.send(msg.encode("utf-8"))

        Shortcut.print_warning(f"User at {self.ip} was blocked from connecting to user {username} with password {password}. Reason: {reason}")
        return Shortcut.INACTIVE
    
    
def does_account_exist(username,accounts):
    # Check if the account for username exists
    return username in accounts.keys()
        
        