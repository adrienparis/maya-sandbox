#client.py
import socket

my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = "localhost" # "127.0.1.1"
port = 8000

my_socket.connect((host, port))

my_socket.send("hello".encode())