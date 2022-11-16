import socket
import threading

class Client:
    def __init__(self, host, tcp_port, udp_listen, udp_speak):
        self.host = host
        self.tcp_port = tcp_port
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.connect((self.host, self.tcp_port))
        self.udp_listen_port = udp_listen
        self.udp_listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_listen_sock.bind((self.host, self.udp_listen_port))
        self.udp_speak_port = udp_speak
        self.udp_speak_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_speak_sock.connect((self.host, self.tcp_port))
        self.in_call = False


    def send_to_server(self, msg):
        self.tcp_sock.send(msg.encode())
        
    def receive_from_server(self):
        return self.tcp_sock.recv(1024).decode()

    def close(self):
        self.tcp_sock.close()
        self.udp_listen_port.close()
        self.udp_speak_port.close()
        

    def call(self):
        username = input("Digite o nome do usuario que deseja chamar: ")
        self.send_to_server(f"call {username}")
        msg = self.receive_from_server()
        msg = msg.split()
        if msg[0] == 'ok':
            ip = msg[1]
            port = msg[2]
            self.start_call(ip, port)
        elif msg[0] == 'ocupado':
            print("Usuario ocupado")
        elif msg[0] == 'nao_existe':
            print("Usuario nao existe")

    def start_call(self, ip, port):
        self.in_call = True
        thread_listen = threading.Thread(target=self.listen)
        thread_listen.start()
        thread_speak = threading.Thread(target=self.speak, args=(ip, port))
        thread_speak.start()       
        
    def listen(self):
        while True:
            msg = self.udp_listen_sock.recv(1024).decode()
            print(msg)
    
    def speak(self, ip, port):
        while True:
            msg = input()
            self.udp_speak_sock.sendto(msg.encode(), (ip, port))

    def start(self):
        username = input("Digite seu nome de usuario: ")
        self.send_to_server(f'login {username} {self.udp_listen_port}')
        



if __name__ == '__main__':
    client = Client('localhost', 5000)
    client.start()
    while True:
        print("1 - Fazer chamada")
        print("2 - Sair")
        option = input()
        if option == '1':
            client.call()
        elif option == '2':
            client.close()
            break
        else:
            print("Opcao invalida")



    
        
