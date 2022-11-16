import socket
import threading

class Client:
    def __init__(self, username, host, tcp_port, udp_listen, udp_speak):
        self.username = username
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
        while True:
            msg = self.tcp_sock.recv(1024).decode()
            msg_list = msg.split()
            response = ''
            if msg_list[0] == 'CALL':
                if self.in_call:
                    response = 'OCCUPIED'
                else:
                    response = 'AVAILABLE'
                    self.start_call(msg_list[1], msg_list[2])
                self.send_to_server(response)
            elif msg_list[0] == 'OCCUPIED':
                print("Usuario ocupado")
            elif msg_list[0] == 'AVAILABLE':
                print("Usuario disponivel")
                self.start_call(msg_list[1], msg_list[2])

            
        

    def close(self):
        self.tcp_sock.close()
        self.udp_listen_port.close()
        self.udp_speak_port.close()
        

    def call(self):
        username = input("Digite o nome do usuario que deseja chamar: ")
        self.send_to_server(f"CALL {username}")

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
        self.send_to_server(f'LOGIN {self.username} {self.udp_listen_port}')
        thread_receive_message = threading.Thread(target=self.receive_from_server)
        thread_receive_message.start()


if __name__ == '__main__':
    udp_listen = int(input("Digite a porta UDP para receber mensagens: "))
    udp_speak = int(input("Digite a porta UDP para enviar mensagens: "))
    username = input("Digite seu nome de usuario: ")
    client = Client('localhost', username, 5000, udp_listen, udp_speak)
    client.start()
    while True:
        print("1 - Fazer chamada")
        print("2 - Sair")
        option = input()
        if option == '1':
            client.call()
        elif option == '2':
            client.send_to_server('LOGOUT')
            client.close()
            break
        else:
            print("Opcao invalida")



    
        
