import socket
import threading

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))

    def create_connection(self):
        self.sock.listen()
        while True:
            print("Esperando conexao...")
            conn, ip = self.sock.accept()
            print('GOT CONNECTION FROM:', ip)
            thread = threading.Thread(target=self.threaded_client, args=(conn,))
            thread.start()

    def threaded_client(self, conn):
        pass


    def close(self):
        self.conn.close()
        self.sock.close()

if __name__ == '__main__':
    server = Server('localhost', 1234)
    while True:
        data = server.receive()
        print(data)
        server.send(data)
        