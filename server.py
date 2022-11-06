import socket
import threading

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.users_list = {}

    def create_connection(self):
        self.sock.listen()
        while True:
            print("Esperando conexao...")
            conn, ip = self.sock.accept()
            print('GOT CONNECTION FROM:', ip)
            thread = threading.Thread(target=self.threaded_client, args=(conn,))
            thread.start()

    def threaded_client(self, conn):
        self.add_user(conn)

    def add_user(self, conn):
        conn.send('Digite seu nome de usuario: '.encode())
        username = conn.recv(1024).decode()
        while username in self.users_list:
            conn.send('Nome de usuario ja existente, digite outro: '.encode())
            username = conn.recv(1024).decode()
        port = self.get_port(conn)
        self.users_list[username] = (conn.getpeername()[0], port)

        print(self.users_list)
    
    def get_port (self, conn):
        conn.send('Digite a porta que deseja usar: '.encode())
        port = conn.recv(1024).decode()
        return port
        
    
    def close(self):
        self.sock.close()

if __name__ == '__main__':
    server = Server('localhost', 5000)
    server.create_connection()
    server.close()
        