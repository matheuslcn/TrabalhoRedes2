import socket
import threading
import pyaudio
import pickle

from tkinter import messagebox

FRAMES_PER_BUFFER = 1024*2
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

class Client:
    def __init__(self, host, tcp_port, udp_port, call_port):
        self.username = self.change_username()
        self.host = host

        self.tcp_port = tcp_port
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.connect((self.host, self.tcp_port))

        self.udp_port = udp_port
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.bind((self.host, self.udp_port))

        self.call_port = call_port

        self.py_audio = pyaudio.PyAudio()

        self.is_logged = False
        self.in_call = False

    def change_username(self):
        username = input("Digite seu nome de usuario: ")
        return username

    def start(self):
        self.tcp_send(f'login {self.username} {self.udp_port}')
        thread_receive_message = threading.Thread(target=self.tcp_receive)
        thread_receive_message.daemon = True
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
            self.tcp_send(f'login {self.username} {self.udp_port}')

    def get_user_information(self):
        username = input("Digite o nome do usuario que deseja chamar: ")
        self.tcp_send(f"consulta {username}")        

    def close(self):
        self.tcp_send('logout')
        self.tcp_sock.close()
        self.is_logged = False
        
    def invite(self, msg_list):
        username = msg_list[1]
        if username == 'usuario_inexistente':
            print("Usuario nao encontrado")
        else:
            ip = msg_list[2]
            port = int(msg_list[3])
            self.udp_send(f"convite {self.username} {self.call_port}", ip, port)
            print(f"Convite enviado para {username}")     
        
    def listen(self, sock):
        stream = self.py_audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True,
                        frames_per_buffer=FRAMES_PER_BUFFER)
        while self.in_call:
            try:
                audio, _ = sock.recvfrom(1024 * 8)
                p_audio = pickle.loads(audio)
                if p_audio == b'fim_chamada':
                    self.in_call = False
                    break
                stream.write(p_audio)
            except:
                pass
        
    def speak(self, sock, ip, port):
        stream = self.py_audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=FRAMES_PER_BUFFER)
        while self.in_call:
            audio = stream.read(FRAMES_PER_BUFFER)
            p_audio = pickle.dumps(audio)
            if not self.in_call:
                break
            sock.sendto(p_audio, (ip, port))

    def end_call_popup(self, sock, ip, port):
        messagebox.showinfo(f"Fim da chamada do {self.username}", "Deseja finalizar a chamada?")
        self.in_call = False
        sock.sendto(b'fim_chamada', (ip, port))

    def end_call(self, *_):
        self.in_call = False

    def udp_send(self, msg, ip, port):
        self.udp_sock.sendto(msg.encode(), (ip, port))

    def udp_receive(self):
        msg, (ip, port) = self.udp_sock.recvfrom(1024*8)
        print(msg)
        msg_list = msg.decode().split()
        commands = {
        'convite': self.receive_invite,
        'resposta_convite': self.call,
        'mensagem_invalida': lambda *_: None,
        }
        commands.get(msg_list[0], self.udp_message_error)(msg_list, (ip, port))
        

    def receive_invite(self, msg_list, ip_port):
        ip, port = ip_port
        port = int(port)
        username = msg_list[1]
        call_port = int(msg_list[2])
        if self.in_call:
            self.udp_send(f'resposta_convite ocupado', ip, port)
            return
        option = messagebox.askyesno(f"Ligação para {self.username}", f"Voce deseja atender a ligação de {username}?")
        if option:
            self.in_call = True
            self.start_call(ip, call_port)
            ans = "disponivel"
        else:
            ans = "recusou"
        self.udp_send(f"resposta_convite {ans} {self.call_port}", ip, port)

    def call(self, msg_list, ip_port):
        ip, _ = ip_port
        status = msg_list[1]
        call_port = int(msg_list[2])
        if status == "ocupado" or status == "recusou":
            print(f"Usuario {status}")
            self.in_call = False
        elif status == "disponivel":
            self.start_call(ip, call_port)

    def tcp_message_error(self, *_):
        self.tcp_send("mensagem_invalida")

    def udp_message_error(self, *_):
        self.udp_send("mensagem_invalida")


    def start_call(self, ip, port):
        self.in_call = True
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.call_port))
        thread_speak = threading.Thread(target=self.speak, args=(sock, ip, port))
        thread_speak.start()
        thread_listen = threading.Thread(target=self.listen, args=(sock,))
        thread_listen.start()
        thread_end_call = threading.Thread(target=self.end_call_popup, args=(sock, ip, port))
        thread_end_call.start()
        
    def menu(self):
        print("1 - Chamar usuario")
        print("2 - Sair")
        print("Digite a opcao desejada: ")
        while not self.in_call:
            option = input('')
            if option == '1':
                if not self.in_call:
                    self.in_call = True
                    self.get_user_information()
                else:
                    print("Voce ja esta em uma chamada")
            elif option == '2':
                self.close()
            else:
                print("Opcao invalida")
        

if __name__ == '__main__':
    udp_listen = int(input("Digite a porta UDP para receber mensagens: "))
    call_port = int(input("Digite a porta UDP para receber chamadas: "))
    client = Client('localhost', 5000, udp_listen, call_port)
    client.start()

    while not client.is_logged:
        pass

    while client.is_logged:
        while client.in_call:
            pass
        
        t_menu = threading.Thread(target=client.menu)
        t_menu.daemon = True
        t_menu.start()
        t_receive_invite = threading.Thread(target=client.udp_receive)
        t_receive_invite.daemon = True
        t_receive_invite.start()

        while not client.in_call:
            pass