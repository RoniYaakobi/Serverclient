class Listener:
    def __init__(self,socket,cmds_to_funcs):
        self.socket = socket
        self.cmds_to_funcs = cmds_to_funcs

    def listen_to_server(self):
        while True:
            server_data = self.socket.recv(1024).decode("utf-8")
            action,args = self.deal_with_server_data(server_data)
            return action,args
    
    def deal_with_server_data(self,server_data):
        try:
            cmd_and_args = server_data.split("\u0000")
            cmd = cmd_and_args[0]
            args = cmd_and_args[1:]
            return cmd,args
        except IndexError or TypeError:
            return #TODO add error dealing function