# This is the client code
import socket
import sys


def login():
    ip = 'summerdesktop'  # input('Enter hostname of server : ')
    port = 9998  # input('Enter Port : ')
    welcome_msg = ('-'*20) + 'WELCOME!' + ('-'*20)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((ip, int(port)))
        print('Connection Successful!\n')
        print(welcome_msg)
    except:
        print("Connection Error!")
        sys.exit()

    username = input('Enter Username : ')
    client_socket.send(username.encode())
    print(client_socket.recv(1024).decode())
    password = input('Enter Password : ')
    client_socket.send(password.encode())
    print(client_socket.recv(1024).decode())

    validate_bit = client_socket.recv(1024).decode()
    if validate_bit == '0':
        print('Invalid Username/Password!')
        return False
        client_socket.close()
    else:
        print('Authentication Successful!')
        return True
