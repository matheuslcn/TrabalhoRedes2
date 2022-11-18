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
            self.receive_message(conn)
            username = self.get_username(conn)
            thread = threading.Thread(target=self.threaded_client, args=(conn, username))
            thread.start()

    def get_username(self, conn):
        for username in self.users_list:
            if self.users_list[username][0] == conn:
                return username
        return None

    def threaded_client(self, conn, username):
        while True:
            try:
                self.receive_message(conn)
            except:
                self.remove_user(username)
                break
        print('Conexao encerrada')
        print(self.users_list)  
                
    def send_message(self, conn, msg):
        conn.send(msg.encode())

    def receive_message(self, conn):
        msg = conn.recv(1024).decode()
        print(msg)
        msg_list = msg.split()
        commands = {
            'login': self.login,
            'consulta': self.get_user_information,
            'logout': self.logout,
        }
        print(msg_list)
        commands.get(msg_list[0], self.message_error)(conn, msg_list)

    def login(self, conn, msg_list):
        username = msg_list[1]
        ip = conn.getpeername()[0]
        port = msg_list[2]
        if username in self.users_list:
            self.send_message(conn, 'resposta_login usuario_existente')
            return
        print("login realizado")
        self.users_list[username] = (ip, port)
        self.send_message(conn, 'resposta_login usuario_logado_com_sucesso')
        print("Usuarios logados:")
        print(self.users_list)

    def get_user_information(self, conn, msg_list):
        username = msg_list[1]
        if username in self.users_list:
            user_ip = self.users_list[username][0]
            user_port = self.users_list[username][1]
            self.send_message(conn, f'resposta_consulta {username} {user_ip} {user_port}')
        else:
            self.send_message(conn, 'resposta_consulta usuario_inexistente')

    def logout(self, conn, msg_list):
        username = msg_list[1]
        self.remove_user(username)
        conn.close()

    def remove_user(self, username):
        self.users_list.pop(username)

    def message_error(self, conn, _):
        self.send_message(conn, 'comando_invalido')

    def close(self):
        self.sock.close()

if __name__ == '__main__':
    server = Server('localhost', 5000)
    server.create_connection()
        