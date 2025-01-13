class Sender:
    def __init__(self,socket,cmds):
        self.socket = socket
        self.cmds - cmds
    
    def send_data(self,cmd,args):
        msg = cmd + "\u0000"

        for arg in args:
            msg += arg + "\u0003"
        
        msg.pop(len(msg)-1)
        self.socket.send(msg.encode("utf-8"))