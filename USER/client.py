import socket
import threading
from callServer import *

class Client:
    def __init__(self, host, tcp_port, udp_listen_port, udp_speak_port):
        self.username = self.change_username()
        self.host = host

        self.tcp_port = tcp_port
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.connect((self.host, self.tcp_port))

        self.udp_call_port = udp_speak_port
        self.udp_call_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_call_sock.bind((self.host, self.udp_call_port))

        self.call_server = CallServer(self.host, udp_listen_port, self.udp_call_port)
        threaded_server = threading.Thread(target=self.call_server.start)
        threaded_server.start()

        self.is_logged = False

    def change_username(self):
        username = input("Digite seu nome de usuario: ")
        return username

    def start(self):
        self.tcp_send(f'login {self.username} {self.call_server.port}')
        thread_receive_message = threading.Thread(target=self.tcp_receive)
        thread_receive_message.start()

    def tcp_send(self, msg):
        self.tcp_sock.send(msg.encode())
        
    def tcp_receive(self):
        while True:
            msg = self.tcp_sock.recv(1024).decode()
            print(msg)
            msg_list = msg.split()
            
            commands = {
                'resposta_login': self.login,
                'resposta_consulta': self.invite,
                'resposta_convite': self.call,

            }
            commands[msg_list[0]](msg_list)
                        
    def login(self, msg_list):
        action = msg_list[1]
        if action == 'usuario_logado_com_sucesso':
            self.is_logged = True
            print("Usuario logado")
        elif action == 'usuario_existente':
            print("Usuario ja existe")
            self.username = self.change_username()
            self.tcp_send(f'login {self.username} {self.udp_listen_port}')

    def get_user_information(self):
        username = input("Digite o nome do usuario que deseja chamar: ")
        self.tcp_send(f"consulta {username}")        

    def close(self):
        self.tcp_send('logout')
        self.tcp_sock.close()
        self.call_server.close()
        self.udp_call_sock.close()
        self.is_logged = False
        
    def invite(self, msg_list):
        action = msg_list[1]
        if action == 'usuario_ineexistente':
            print("Usuario nao encontrado")
        else:
            username = msg_list[2]
            ip = msg_list[3]
            port = msg_list[4]
            self.udp_send(f"convite {self.username} {self.host} {self.udp_call_port}", ip, port)
            print(f"Convite enviado para {username}")
            

    def call(self, msg_list):
        action = msg_list[1]
        if action == "ocupado":
            print("Usuario ocupado")
            self.call_server.in_call = False
        elif action == "disponivel":
            ip = msg_list[2]
            port = msg_list[3]
            self.start_call(ip, port)


    def start_call(self, ip, port):
        self.call_server.in_call = True
        thread_speak = threading.Thread(target=self.speak, args=(ip, port))
        thread_speak.start()  
        thread_listen = threading.Thread(target=self.listen)
        thread_listen.start()
     
        
    def listen(self):
        while True:
            msg = self.udp_call_sock.recv(1024).decode()
            print(msg)
    
    def speak(self, ip, port):
        while True:
            msg = input()
            self.udp_send(msg, ip, port)
    
    def udp_send(self, msg, ip, port):
        self.udp_call_sock.sendto(msg.encode(), (ip, port))


    def menu(self):
        print("1 - Chamar usuario")
        print("2 - Sair")
        option = int(input("Digite a opcao desejada: "))
        if option == 1:
            self.call_server.in_call = True
            self.get_user_information()
        elif option == 2:
            self.close()
        else:
            print("Opcao invalida")

if __name__ == '__main__':
    udp_listen = int(input("Digite a porta UDP para receber mensagens: "))
    udp_speak = int(input("Digite a porta UDP para enviar mensagens: "))
    client = Client('localhost', 5000, udp_listen, udp_speak)
    client.start()

    while not client.is_logged:
        pass

    while client.is_logged:
        while client.call_server.in_call:
            pass
        thread_menu = threading.Thread(target=client.menu)
        thread_menu.start()
        thread_menu.join()




    
        
