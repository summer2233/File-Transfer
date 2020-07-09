# This is the server code
import csv
import socket 
import sys
import traceback

# filename of csv file-name
filename = 'login_credentials.csv'
data = {}
host = socket.gethostname() 

# Function to validate authentication
def validate_login(username, password):
    if (data.get(username)) is None:
        return '0'
    elif (data[username] == password):
        return '1'
    else:
        return '0'


# Read CSV file
def file_read():
    with open(filename,'r') as login_file:
        reader = csv.reader(login_file)
        for row in reader:
            if row[0] != 'Username':
                data[row[0]] = row[1]


def login():
    file_read()
    global host
    # Create socket and bind
    port = 9998#input('Enter Port : ')
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind ((host, int(port)))
    except:
        print("Bind Failed! Error : " + str(sys.exc_info()))
        sys.exit()
    
    
    server_socket.listen(5)
    print("主机名 : " + host)
    print('监听端口中 ...')
    print('*'*40)

    while True:
        # Connect to a client
        client_socket, address = server_socket.accept()
        ip, port = str(address[0]), str(address[1])
        print(" 已连接到 " + ip + ":" + port)

        # Get username and password
        username = client_socket.recv(1024).decode()
        client_socket.send(('ACK : 接收到用户名！').encode())
        print(" 已从 "+ip+":"+port+" 接收到用户名")
        password = client_socket.recv(1024).decode()
        client_socket.send(('ACK : 接收到密码！').encode())
        print(" 已从 "+ip+":"+port+" 接收到密码")

        # Validate authentication
        if validate_login(username, password) == '1':
            client_socket.send(('1').encode())
        else:
            client_socket.send(('0').encode())

        # Close client socket
        client_socket.close()
        print(ip + ":" + port + " 连接关闭！")
        print('*'*40)

# Run the main function
login()

