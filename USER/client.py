import socket
import threading

class Client:
    def __init__(self, host, tcp_port, udp_listen, udp_speak):
        self.username = self.change_username()
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
        self.is_logged = False


    def send_to_server(self, msg):
        self.tcp_sock.send(msg.encode())
        
    def receive_from_server(self):
        while True:
            msg = self.tcp_sock.recv(1024).decode()
            print(msg)
            msg_list = msg.split()
            response = ''
            """
            # para refatoracao
            commands = {
                'SUCCESSFUL_LOGIN': self.login,
                'USER_ALREADY_EXISTS': self.user_already_exists,
                'CALL': self.call,
                'LOGOUT': self.logout,
                'OCCUPIED': self.occupied,
                'AVAILABLE': self.available,
                'USER_NOT_FOUND': self.user_not_found,
            }
            """


            if msg_list[0] == 'CALL':
                if self.in_call:
                    response = 'OCCUPIED'
                else:
                    response = 'AVAILABLE'
                    self.start_call(msg_list[1], msg_list[2])
                self.send_to_server(response)
            elif msg_list[0] == 'OCCUPIED':
                print("Usuario ocupado")
                self.in_call = False
            elif msg_list[0] == 'AVAILABLE':
                print("Usuario disponivel")
                self.start_call(msg_list[1], msg_list[2])
            elif msg_list[0] == 'USER_ALREADY_EXISTS':
                print("Usuario ja existe")
                self.username = self.change_username()
                self.send_to_server(f'LOGIN {self.username} {self.udp_listen_port}')
            elif msg_list[0] == 'SUCCESSFUL_LOGIN':
                print("Usuario criado")
                self.is_logged = True
            elif msg_list[0] == 'INVALID_COMMAND':
                print("Comando invalido")
            elif msg_list[0] == 'USER_NOT_FOUND':
                print("Usuario nao encontrado")
                
            
            

            
        

    def close(self):
        self.tcp_sock.close()
        self.udp_listen_port.close()
        self.udp_speak_port.close()
        self.is_logged = False
        

    def call(self):
        username = input("Digite o nome do usuario que deseja chamar: ")
        self.send_to_server(f"CALL {username}")

    def start_call(self, ip, port):
        self.in_call = True
        thread_speak = threading.Thread(target=self.speak, args=(ip, port))
        thread_speak.start()  
        thread_listen = threading.Thread(target=self.listen)
        thread_listen.start()
     
        
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
    
    def change_username(self):
        username = input("Digite seu nome de usuario: ")
        return username

    def menu(self):
        print("1 - Chamar usuario")
        print("2 - Sair")
        option = int(input("Digite a opcao desejada: "))
        if option == 1:
            self.call()
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
        while client.in_call:
            pass
        thread_menu = threading.Thread(target=client.menu)
        thread_menu.start()
        thread_menu.join()




    
        
