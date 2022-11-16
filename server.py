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
            conn, (ip, port) = self.sock.accept()
            print('GOT CONNECTION FROM:', (ip, port))
            thread = threading.Thread(target=self.threaded_client, args=(conn, ip))
            thread.start()

    def threaded_client(self, conn, ip):
        while True:
            try:
                self.receive_message(conn)
            except:
                self.remove_user(ip)
                break
        print('Conexao encerrada')
        print(self.users_list)

    def add_user(self, conn, ip):
        msg = conn.recv(1024).decode()
        msg_list = msg.split()
        while msg_list[0] in self.users_list:
            conn.send('EXISTING_USER'.encode())
            username = conn.recv(1024).decode()
        port = self.get_port(conn)
        self.users_list[username] = (ip, port)

        print(self.users_list)
    
    def remove_user(self, ip):
        for username in self.users_list:
            if self.users_list[username][0] == ip:
                del self.users_list[username]
                break
                
      
    def receive_message(self, conn):
        msg = conn.recv(1024).decode()
        msg_list = msg.split()
        if msg_list[0] == 'LOGOUT':
            conn.close()
        elif msg_list[0] == 'LOGIN':
            self.add_user(conn, msg_list[1], msg_list[2])

        print(msg)
        conn.send('Mensagem recebida'.encode())

    def close(self):
        self.sock.close()

if __name__ == '__main__':
    server = Server('localhost', 5000)
    server.create_connection()
        