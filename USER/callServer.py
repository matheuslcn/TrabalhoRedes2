import socket

class CallServer:
    def __init__(self, host, port, call_port):
        self.host = host
        self.port = port
        self.call_port = call_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.in_call = False

    def start(self):
        while True:
            msg, (ip, port) = self.sock.recvfrom(1024)
            print(msg)
            msg_list = msg.split()
            commands = {
                "convite": self.invite,
            }
            commands[msg_list[0]](msg_list, ip, port)

    def invite(self, _, ip, port):
        if self.in_call:
            response = "resposta_convite ocupado"
        else:
            response = f"resposta_convite disponivel {self.host} {self.call_port}"
        self.udp_send(response, ip, port)

    def udp_send(self, msg, ip, port):
        self.sock.sendto(msg.encode(), (ip, port))
    
    def close(self):
        self.sock.close()