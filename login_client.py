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
        print('连接服务器成功！\n')
        print(welcome_msg)
    except:
        print("连接服务器出错！")
        sys.exit()

    username = input(' 请输入用户名: ')
    client_socket.send(username.encode())
    print(client_socket.recv(1024).decode())
    password = input(' 请输入密码 : ')
    client_socket.send(password.encode())
    print(client_socket.recv(1024).decode())

    validate_bit = client_socket.recv(1024).decode()
    if validate_bit == '0':
        print('用户名不存在或密码错误！')
        return False
        client_socket.close()
    else:
        print('登录成功！')
        return True
