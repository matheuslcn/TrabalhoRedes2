import socket
import multiprocessing

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def send(self, data):
        self.sock.send(data.encode())

    def receive(self):
        data = self.sock.recv(1024).decode()
        return data

    def close(self):
        self.sock.close()

if __name__ == '__main__':
    client = Client('localhost', 1234)
    while True:
        data = input('Enter data: ')
        client.send(data)
        print(client.receive())
