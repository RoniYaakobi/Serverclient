from RoomProtocol import Server

MAX_MSG_LENGTH = 1024 
SERVER_PORT = 8000 
SERVER_IP = "0.0.0.0"


server = Server(MAX_MSG_LENGTH,SERVER_PORT,SERVER_IP)

server.run()