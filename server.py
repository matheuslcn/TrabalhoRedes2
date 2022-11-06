import socket

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        self.conn, self.addr = self.sock.accept()

    def send(self, data):
        self.conn.send(data.encode())

    def receive(self):
        data = self.conn.recv(1024).decode()
        return data

    def close(self):
        self.conn.close()
        self.sock.close()

if __name__ == '__main__':
    server = Server('localhost', 1234)
    while True:
        data = server.receive()
        print(data)
        