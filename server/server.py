import socket
import threading
import os
import sys

os.system('cls' if os.name == 'nt' else 'clear')

class ChatServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_host = '127.0.0.1'
        self.server_port = 8000
        self.client_sockets = []
        self.client_addresses = []
        self.nicknames = {}
        self.motd = self.load_motd()  # Load the MOTD from file

    def load_motd(self):
        try:
            with open("motd.txt", "r") as file:
                return file.read()
        except FileNotFoundError:
            return "If you see this, your motd file is missing."

    def start(self):
        self.server_socket.bind((self.server_host, self.server_port))
        self.server_socket.listen(5)
        print("Server started. Listening for connections...")

        threading.Thread(target=self.handle_server_input).start()  # Start a separate thread to handle server input

        while True:
            client_socket, client_address = self.server_socket.accept()
            self.client_sockets.append(client_socket)
            self.client_addresses.append(client_address)
            threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()

    def handle_client(self, client_socket, client_address):
        nickname = self.receive_message(client_socket)
        self.nicknames[client_socket] = nickname

        print(f"New connection from {client_address[0]}:{client_address[1]} (Username: {nickname})")
        self.broadcast_message(f"{nickname} has joined the chat!")

        try:
            while True:
                message = self.receive_message(client_socket)
                if not message:
                    break
                self.broadcast_message(message, sender_socket=client_socket, sender_nickname=nickname)
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

    def send_message(self, client_socket, message):
        client_socket.send(message.encode())

    def broadcast_message(self, message, sender_socket=None, sender_nickname=None):
        for client_socket in self.client_sockets:
            if sender_nickname and client_socket == sender_socket:
                self.send_message(client_socket, message)
            elif sender_nickname:
                self.send_message(client_socket, f"{sender_nickname}: {message}")
            else:
                self.send_message(client_socket, message)

    def handle_server_input(self):
        while True:
            command = input("Server Command: ")
            if command == "/quit":
                self.broadcast_message("Server closed.")
                os._exit(0)
            elif command.startswith("/servermsg"):
                server_message = command.split(" ", 1)[1]  # Extract the server message
                print(f"Server: {server_message}")
                self.broadcast_message(f"Server: {server_message}")
            else:
                print("Unknown command!")

server = ChatServer()
server.start()
