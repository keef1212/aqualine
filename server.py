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
        self.admins = {'admin_ip_address'}  # Set the IP address of the admin here

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
        self.broadcast_message(f"{nickname} has joined the chat!")
        if nickname == "badactor": # This is just an example, I recommend you use client_address instead of the nickname.
            print("WARNING: User above is listed as dangerous, be wary!")
        if client_address == self.admins:
            self.broadcast_message(f"Administrator", sender_socket=client_socket)
        self.broadcast_message(f"{nickname} has joined the chat!", sender_socket=client_socket)

        try:
            while True:
                message = self.receive_message(client_socket)
                if not message:
                    break
                if client_address[0] in self.admins:
                    self.process_admin_command(message, client_address[0])
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

    def broadcast_message(self, message, sender_socket=None, sender_nickname=None):
        for client_socket in self.client_sockets:
            if sender_nickname and client_socket == sender_socket:
                client_socket.send(message.encode())
            elif sender_nickname:
                client_socket.send(f"{sender_nickname}: {message}".encode())
            else:
                client_socket.send(message.encode())

    def process_admin_command(self, message, admin_ip):
        command_parts = message.strip().split()
        if len(command_parts) > 0:
            command = command_parts[0]
            if command == '/ban':
                if len(command_parts) > 1:
                    ip_to_ban = command_parts[1]
                    self.ban_ip(ip_to_ban)
                    print(f"Admin {admin_ip} banned IP: {ip_to_ban}")
            elif command == '/unban':
                if len(command_parts) > 1:
                    ip_to_unban = command_parts[1]
                    self.unban_ip(ip_to_unban)
                    print(f"Admin {admin_ip} unbanned IP: {ip_to_unban}")

    def ban_ip(self, ip_address):
        self.client_addresses = [addr for addr in self.client_addresses if addr[0] != ip_address]

    def unban_ip(self, ip_address):
        if ip_address not in [addr[0] for addr in self.client_addresses]:
            self.client_addresses.append((ip_address, 0))  # Add the IP back to the list

server = AquaServer()
server.start()
