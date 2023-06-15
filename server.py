import socket
import threading
import os

os.system('cls' if os.name == 'nt' else 'clear')

class ChatServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_host = '127.0.0.1'
        self.server_port = 8000
        self.client_sockets = []
        self.client_addresses = []
        self.nicknames = {}

    def start(self):
        self.server_socket.bind((self.server_host, self.server_port))
        self.server_socket.listen(5)
        print("Server started. Listening for connections...")

        while True:
            client_socket, client_address = self.server_socket.accept()
            self.client_sockets.append(client_socket)
            self.client_addresses.append(client_address)
            threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()

    def handle_client(self, client_socket, client_address):
        nickname = self.receive_message(client_socket)
        self.nicknames[client_socket] = nickname

        print(f"New connection from {client_address[0]}:{client_address[1]} (Username: {nickname})")
        self.broadcast_message(f"{nickname} has joined the chat!", sender_socket=client_socket)

        try:
            while True:
                message = self.receive_message(client_socket)
                if not message:
                    break
                self.broadcast_message(f"{nickname}: {message}", sender_socket=client_socket)
        except ConnectionResetError:
            pass

        self.client_sockets.remove(client_socket)
        self.client_addresses.remove(client_address)
        self.nicknames.pop(client_socket)
        client_socket.close()
        print(f"Connection closed: {client_address[0]}:{client_address[1]} (Username: {nickname})")
        self.broadcast_message(f"{nickname} has left the chat.")

    def receive_message(self, client_socket):
        try:
            message = client_socket.recv(1024).decode()
            return message
        except ConnectionResetError:
            pass

    def broadcast_message(self, message, sender_socket=None):
        for client_socket in self.client_sockets:
            if client_socket != sender_socket:
                client_socket.send(message.encode())


server = ChatServer()
server.start()
