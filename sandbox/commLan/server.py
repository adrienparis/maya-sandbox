#server.py
import socket

my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

PORT = 8000
ADDRESS = "0.0.0.0"
my_socket.bind((ADDRESS, PORT))

my_socket.listen()
client, client_address = my_socket.accept()

result = client.recv(1024)
print(result.decode())