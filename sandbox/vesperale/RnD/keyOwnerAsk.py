# coding: utf-8
import ctypes
import time
 
def get_display_name():
    GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
    NameDisplay = 3
 
    size = ctypes.pointer(ctypes.c_ulong(0))
    GetUserNameEx(NameDisplay, None, size)
 
    nameBuffer = ctypes.create_unicode_buffer(size.contents.value)
    GetUserNameEx(NameDisplay, nameBuffer, size)
    return nameBuffer.value

import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', 8377))

keyOwnerIp = ""

while True:
        sock.listen(5)
        client, address = sock.accept()
        print("{} connected".format( address ))

        response = client.recv(255)
        if response != "":
                print(response)
                keyOwnerIp = address[0]
                break
port = 8376

time.sleep(10)
print(get_display_name(), (keyOwnerIp, port))
time.sleep(1)

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((keyOwnerIp, port))
print("Connection on {}".format(port))

socket.send(bytes(get_display_name(), "utf-8"))


print ("Close")
client.close()
sock.close()