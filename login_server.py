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
    print("Hostname : " + host)
    print('Socket is now listening...')
    print('*'*40)

    while True:
        # Connect to a client
        client_socket, address = server_socket.accept()
        ip, port = str(address[0]), str(address[1])
        print("Connected with " + ip + ":" + port)

        # Get username and password
        username = client_socket.recv(1024).decode()
        client_socket.send(('ACK : Username received!').encode())
        print("Username received from "+ip+":"+port)
        password = client_socket.recv(1024).decode()
        client_socket.send(('ACK : Password received!').encode())
        print("Password received from "+ip+":"+port)

        # Validate authentication
        if validate_login(username, password) == '1':
            client_socket.send(('1').encode())
        else:
            client_socket.send(('0').encode())

        # Close client socket
        client_socket.close()
        print("Connection " + ip + ":" + port + " closed!")
        print('*'*40)

# Run the main function
login()

