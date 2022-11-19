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
            msg_list = msg.decode().split()
            commands = {
                "convite": self.invite,
                "resposta_convite": self.ans_invite,
                'mensagem_invalida': lambda *_: None,
            }
            commands.get(msg_list[0], self.message_error)(msg_list, ip, port)

    def invite(self, username, ip, port):
        if self.in_call:
            self.udp_send("resposta_convite ocupado", ip, port)
            
        else:
            self.ask_call(username, ip, port)

    def ans_invite(self, msg_list, ip, port):
        status = msg_list[1]
        ip_ = msg_list[2]
        port_ = int(msg_list[3])
        if status == "recusou":
            print("Convite recusado")
        elif status == "disponivel":
            print("Convite aceito")
            status += f" {ip} {port}"
            self.in_call = True
        self.udp_send(f"resposta_convite {status}", ip_, port_)
        

        

    def ask_call(self, msg_list, ip, port):
        username = msg_list[1]
        self.udp_send(f"convite {username} {ip} {port}", self.host, self.call_port)

    def udp_send(self, msg, ip, port):
        self.sock.sendto(msg.encode(), (ip, port))

    def message_error(self, *_):
        print("mensagem_invalida")
    
    def close(self):
        self.sock.close()