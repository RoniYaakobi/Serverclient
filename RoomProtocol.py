import socket
import select

from clock import Clock
from AccountProtocol import User
from shortcuts import Shortcut

"""
TODO ADD auth_manager,room manager,message, processor, and socket_manager classes and objects
"""


class Room:
    """
    This class creates room objects, which are effectively like discord channels.
    They store the chat messages, and the users connected to the room.
    Each server has at least on room. For now I haven't implemented the ability to add rooms, but it is not hard.
    """
    
    def __init__(self,name,chat_file = None, messages = []):
        Shortcut.print_initializing(f"Initializing room {name} ({Clock.get_date_time()})",clock= False)
        
        self.name = name

        if chat_file:
            self.chat_file = chat_file
        else:
            self.chat_file = f"room{self.name}.txt"
        
        try:
            with open(self.chat_file,"r") as chat:
                self.messages = chat.readlines()
                Shortcut.print_success(f"Got room {name} old messages successfully")

        except FileNotFoundError:
            self.messages = messages
            history = "an empty history" if messages else "the inputed history"
            Shortcut.print_warning(f"Could not access {self.chat_file} for the old chat messages. Initializing chat with {history}.")

        self.connected_users = []
        
        self.time_created = Clock.get_date_time()
        Shortcut.print_success(f"Created room {name} at time ({self.time_created}).",clock = Shortcut.INACTIVE)

    def join_room(self,user,in_no_room):
        # Adds a user to the room after making sure they are in no room
        Shortcut.print_initializing(f"Trying to add {user.account.username} to room {self.name}.")
        if not user in in_no_room:
            Shortcut.print_error(f"Error: could not connect user {user.account.username} to room {self.name}. User not connected to server, or already connected to another room. ({Clock.get_date_time()})")
            return in_no_room
        
        self.connected_users.append(user)
        in_no_room.remove(user)

        user.account.join_room(self.name)

        Shortcut.print_success(f"User {user.account.username} joined room {self.name}.")
        

        return in_no_room

    def leave_room(self,user):
        # Removes a user from the room
        Shortcut.print_initializing(f"Trying to remove {user.account.username} from room {self.name}.")
        if user in self.connected_users:
            self.connected_users.remove(user)
            user.account.leave_room()
        
            Shortcut.print_success(f"User {user.account.username} left room {self.name}.")
        else:
            Shortcut.print_warning(f"User {user.account.username} was not in the room!")
        
        return user

    def add_message(self,message,user):
        # This triggers when the user sends message TODO make this smarter, get more data and get it safer
        username = user.account.username
        datetime = Clock.get_date_time()
        
        message = f"{username} : {message} ({datetime})\n"
        self.messages.append(message)

        with open(self.chat_file,"a") as chat:
            chat.write(message)
    
    def update_socket(self,socket):
        # update a socket with the room's data
        big_msg = ""
        for msg in self.messages:
            big_msg += msg
        
        socket.send(big_msg.encode("utf-8"))




class Server:
    # This class creates server objects. It is the central control center for the server.
    def __init__(self,max_msg_length,server_port,server_ip, Accounts = {}, rooms = [Room("A")]):
        Shortcut.print_initializing("Initializing server.")

        self.server_port = server_port
        self.server_ip = server_ip

        self.max_msg_length = max_msg_length

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((server_ip,server_port))

        self.socket.listen()

        self.rooms = rooms
        self.amount_of_rooms = len(rooms)
        self.accounts = Accounts

        self.all_sockets = []
        self.signed_out_clients = []
        self.signed_in_clients = []
        self.in_no_room = []
        self.socket_to_room = {}
        self.socket_to_user = {}

        Shortcut.print_success("Listening for clients")
    
    def run(self):
        """
        Running the server loops over all the clients connected or trying to connect and does the following:
        If the client is trying to connect, the server authenticates the client's account.
        If the client is already connected, the server updates it with the most recent updates for the room they are in
        after checking what messages the client inputted. TODO Make the client update immediatly after the server recives a message
        and not after sending a message their selves.
        """

        while True:
            try:
                read_list, write_list, error_list = select.select([self.socket] + self.all_sockets, [], [])
                for current_socket in read_list:
                    if current_socket is self.socket:
                        self.deal_with_new_connection(current_socket)
                    elif current_socket in self.socket_to_room.keys():
                        still_active = self.get_new_data(current_socket)

                        if not still_active:
                            continue
                        self.send_new_data(current_socket)
            except Exception as e:
                Shortcut.print_warning(f"Exception occured: {e}")

    def deal_with_new_connection(self,socket):
        """
        This deals with the connection from a new client. It creates a user for them, and tries to sign them in
        to the account they requested and then move them to the room they want . TODO implement respose for wrong password
        """
        authenticated,new_user = self.generate_user(socket)
        
        if authenticated:
            if self.amount_of_rooms > 1:
                pass #TODO add functionality for multiple rooms
            else:
                room = self.rooms[0]
            self.add_user_to_room(room,new_user)
    
    def generate_user(self,socket):
        # creates a user and attempt to connect them to an account.
        connection,client_adress = socket.accept()
        self.signed_out_clients.append(connection)

        new_user = User(connection,client_adress,self.max_msg_length)
        username,password = new_user.get_sign_in_info()

        authenticated,self.accounts = new_user.sign_in(username,password,self.accounts)
        
        self.socket_to_user[new_user.socket] = new_user
        self.all_sockets.append(new_user.socket)
        
        if authenticated:
            self.in_no_room.append(new_user)
            self.accounts[new_user.account.username] = new_user.account

        return authenticated, new_user


    def add_user_to_room(self,room,new_user):
        self.in_no_room = room.join_room(new_user,self.in_no_room)
        
        # TODO change these to a dictionary for user:in_room/not_in_room
        self.signed_in_clients.append(new_user.socket) 
        if new_user.socket in self.signed_out_clients:
            self.signed_out_clients.remove(new_user.socket)
        
        self.socket_to_room[new_user.socket] = room
        self.send_new_data(new_user.socket)



    def get_new_data(self,socket):
        # If user sent data, catagorize it, and deal with it
        data = socket.recv(self.max_msg_length).decode("utf-8")
        user = self.socket_to_user[socket]
        room = self.socket_to_room[socket]

        
        if data == "Exit": 
            return self.disconnect_user(room,user,socket) # return if the user is still here (is not)
        else:
            room.add_message(data,user)
            return Shortcut.ACTIVE # return if th user is still here (is in this case)
    
    def disconnect_user(self,room,user,socket):
        """
        remove the user from the client lists,
        and remove the user from the account (freeing the account for future sign ins.)
        """
        Shortcut.print_success(f"Connection with {user.ip} closed.")
        user.account.signed_out()
        self.clear_socket_from_system(socket)


        room.leave_room(user)
        
        if user:
            del user
        
        socket.close()
        return Shortcut.INACTIVE 

    def clear_socket_from_system(self,socket):
        socket_storage_lists = [self.signed_in_clients,
                            self.signed_out_clients,
                            self.in_no_room,
                            self.all_sockets]
        
        socket_storage_dictionaries = [self.socket_to_room,self.socket_to_user]

        for socket_storage in socket_storage_lists:
            if socket_storage and socket in socket_storage:
                socket_storage.remove(socket)
        
        for socket_storage in socket_storage_dictionaries:
            if socket in socket_storage.keys():
                del socket_storage[socket]


    def send_new_data(self,socket):
        # update the user's socket with new information.
        room = self.socket_to_room[socket]
        room.update_socket(socket)
