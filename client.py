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


    def send(self, msg):
        self.sock.send(msg.encode())
        
    def receive(self):
        return self.sock.recv(1024).decode()

    def close(self):
        self.sock.close()

    def call(self):
        thread_listen = threading.Thread(target=self.listen_call)
        thread_listen.start()
        thread_listen = threading.Thread(target=self.speak_call)
        thread_listen.start()

        
    def listen_call(self):
        while True:
            msg = self.udp_listen_sock.recv(1024).decode()
            print(msg)
    
    def speak_call(self):
        while True:
            msg = input()
            self.udp_speak_sock.send(msg.encode())



if __name__ == '__main__':
    client = Client('localhost', 5000)
    while True:
        msg = client.receive()
        print(msg)
        msg = input()
        client.send(msg)

    
        
