import socket
import threading
import os
import sys

class AquaClient:
    def __init__(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_host = input("Enter the server IP address: ")
        self.server_port = int(input("Enter the server port: "))
        self.nickname = input("Enter your nickname: ")

    def connect(self):
        try:
            self.client_socket.connect((self.server_host, self.server_port))
        except ConnectionRefusedError:
            print("Connection refused. The server is not available.")
            sys.exit(1)

        self.send_message(self.nickname)

        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

        self.send_user_messages()

    def send_message(self, message):
        self.client_socket.send(message.encode())

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if message:
                    print(message)
            except ConnectionResetError:
                print("Disconnected from the server.")
                break

        self.client_socket.close()
        sys.exit(0)

    def send_user_messages(self):
        try:
            while True:
                message = input()
                if message == "/quit":
                    self.send_message(message)
                    break
                self.send_message(message)
        except (KeyboardInterrupt, EOFError):
            self.send_message("/quit")

        self.client_socket.close()

client = AquaClient()
client.connect()
