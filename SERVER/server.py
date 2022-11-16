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

    def add_user(self, conn, username, port):
        if username in self.users_list:
            conn.send('EXISTING_USER'.encode())
            return
        self.users_list[username] = (conn, port)
        self.send_message(conn, 'SUCCESSFUL_LOGIN')
        print(self.users_list)    

    def remove_user(self, ip):
        for username in self.users_list:
            user_ip = self.users_list[username][0].getpeername()[0]
            if user_ip == ip:
                del self.users_list[username]
                break
                
    def send_message(self, conn, msg):
        conn.send(msg.encode())

    def receive_message(self, conn):
        msg = conn.recv(1024).decode()
        print(msg)
        msg_list = msg.split()
        commands = {
            'LOGIN': self.add_user,
            'CALL': self.call,
            'LOGOUT': self.logout,
            'OCCUPIED': self.occupied,
            'AVAILABLE': self.available
        }
        commands.get(msg_list[0], self.message_error)(conn, msg_list)

    def call(self, conn, msg_list):
        username = msg_list[1]
        if username in self.users_list:
            user_conn = self.users_list[username][0]
            user_port = self.users_list[username][1]
            user_ip = user_conn.getpeername()[0]
            self.send_message(user_conn, f'CALL {user_ip} {user_port}')
        else:
            self.send_message(conn, 'USER_NOT_FOUND')

    def logout(self, conn, _):
        ip = conn.getpeername()[0]
        self.remove_user(ip)

    def occupied(self, conn, _):
        self.send_message(conn, 'OCCUPIED')

    def available(self, conn, _):
        self.send_message(conn, 'AVAILABLE')

    def message_error(self, conn, _):
        self.send_message(conn, 'INVALID_COMMAND')

    def close(self):
        self.sock.close()

if __name__ == '__main__':
    server = Server('localhost', 5000)
    server.create_connection()
        