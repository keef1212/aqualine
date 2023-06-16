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

        self.send_message(f"{self.nickname}")

        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

        while True:
            message = input()
            if message == "/quit":
                self.send_message(message)
                break
            self.send_message(message)

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
                sys.exit(1)


client = AquaClient()
client.connect()
