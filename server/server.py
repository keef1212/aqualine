import socket
import threading
import os

os.system('cls' if os.name == 'nt' else 'clear')

class AquaServer:
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

        threading.Thread(target=self.handle_server_input).start()

        while True:
            client_socket, client_address = self.server_socket.accept()
            self.client_sockets.append(client_socket)
            self.client_addresses.append(client_address)
            threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()

    def handle_client(self, client_socket, client_address):
        nickname = self.receive_message(client_socket)

        if self.is_username_taken(nickname):
            self.send_message("Username is already in use. Please choose a different username.", client_socket)
            client_socket.close()
            return

        self.nicknames[client_socket] = nickname

        print(f"New connection from {client_address[0]}:{client_address[1]} (Username: {nickname})")
        self.broadcast_message(f"{nickname} has joined the chat!")

        try:
            while True:
                message = self.receive_message(client_socket)
                if not message:
                    break
                elif message.startswith("/private"):
                    self.send_private_message(message, sender_socket=client_socket)
                elif message == "/users":
                    self.send_connected_users(client_socket)
                elif message == "/quit":
                    os._exit()
                elif message == "/help":
                    self.send_message("Available commands: /users, /private", client_socket)
                else:
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

    def send_message(self, message, client_socket):
        client_socket.send(message.encode())

    def broadcast_message(self, message, sender_socket=None, sender_nickname=None):
        for client_socket in self.client_sockets:
            if sender_nickname and client_socket == sender_socket:
                self.send_message(message, client_socket)
            elif sender_nickname:
                self.send_message(f"{sender_nickname}: {message}", client_socket)
            else:
                try:
                    self.send_message(message, client_socket)
                except OSError:
                    print("Error sending message to a client.")


    def send_private_message(self, message, sender_socket):
        try:
            _, recipient, content = message.split(" ", 2)
            recipient_socket = None
            for client_socket, nickname in self.nicknames.items():
                if nickname == recipient:
                    recipient_socket = client_socket
                    break
            if recipient_socket:
                self.send_message(f"[Private] {self.nicknames[sender_socket]}: {content}", recipient_socket)
                self.send_message(f"[Private] To {self.nicknames[recipient_socket]}: {content}", sender_socket)
            else:
                self.send_message(f"User '{recipient}' not found.", sender_socket)
        except ValueError:
            self.send_message("Invalid private message format.", sender_socket)

    def send_connected_users(self, client_socket):
        connected_users = ", ".join(self.nicknames.values())
        self.send_message(f"Connected Users: {connected_users}", client_socket)

    def is_username_taken(self, nickname):
        return nickname in self.nicknames.values()

    def handle_server_input(self):
        while True:
            command = input()
            if command == "/quit":
                self.broadcast_message("Server closed.")
                os._exit(0)
            elif command == "/restart":
                self.broadcast_message("Server is restarting.")
                print("Note: the server wont restart on its own, you have to reopen the server file.")
                print("This should only be used if you want to alert people that your restarting and not closing.")
                os._exit(0)
            elif command.startswith("/servermsg"):
                server_message = command.split(" ", 1)[1]
                print(f"Server: {server_message}")
                self.broadcast_message(f"Server: {server_message}")
            else:
                print("Unknown command!")

server = AquaServer()
server.start()
