# -*- coding:utf-8 -*-
import os
import socket 
import sys


def showProgress(percent, size=25):
    """
    显示传输进度
    """

    global filename, mode
    size /= 100
    percent = int(percent)

    if mode == 1:
        print('\r 正在发送 "{}" ... {}% [{}{}] '.format(
            filename, percent, "#"*int((percent*size)), " "*int(((100*size)-percent*size))), end="")
    else:
        print('\r 正在接收 "{}" ... {}% [{}{}] '.format(
            filename, percent, "#"*int((percent*size)), " "*int(((100*size)-percent*size))), end="")

while True:
    
    filename = None
    filename_size = 20
    ip = '127.0.0.1'
    hostname = 'summerdesktop'
    port = 9997

    # 与客户端建立连接以传输 mode 和 path
    host = socket.gethostname() 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind ((host, int(port)))
    except:
        print("连接失败！错误 : " + str(sys.exc_info()))
        sys.exit()


    server_socket.listen(5)
    print("主机名 : " + host)
    print('监听端口中 ...')
    print('*'*40)


# Connect to a client
    client_socket, address = server_socket.accept()
    ip, port = str(address[0]), str(address[1])
    print(" 已连接到 " + ip + ":" + port)

    # Get username and password
    mode = client_socket.recv(1024).decode()
    mode = int(mode)
    if mode == 3: # listdir
        client_socket.send((os.listdir('upload')).encode())
    else:
        client_socket.send(('ACK : 接收到模式！').encode())
    print(" 已从 "+ip+":"+port+" 接收到模式")
    path = client_socket.recv(1024).decode()
    client_socket.send(('ACK : 接收到路径！').encode())
    print(" 已从 "+ip+":"+port+"接收到路径")

    # Close client socket
    client_socket.close()
    print(ip + ":" + port + " 连接关闭！")
    print('*'*40)

    ip = '127.0.0.1'
    port = 9999
    from fileTransfer import FileTransfer
    if mode == 2:
        fileTransfer = FileTransfer(filename=path, mode=FileTransfer.SEND)
        print(" 等待连接 ...")
    else:
        print(" 连接中 ...")
        fileTransfer = FileTransfer(path=path, mode=FileTransfer.RECEIVE)
    try:
        info = fileTransfer.connect((ip, port))
    except:
        input(" 尝试连接失败")
        quit()


    # 如果用户正在发送文件，则将通知他需要等待客户的确认。
    # 确认后，将发送文件。

    if mode == 2:
        print(" 等待 host 确定： {} ...".format(info[0]))
        filename = os.path.split(path)[-1]

        # 检查文件名大小是否大于限制大小。 如果是这样，它将减少
        if len(filename.split(".")[0]) > filename_size:
            filename = filename.split(
                ".")[0][0:filename_size]+"."+filename.split(".")[-1]

        try:
            fileTransfer.transfer(showProgress)
            print("")
            print("\n 文件传输成功。\n\n")
        except:
            print("\n 连接断开。\n\n")
        finally:
            fileTransfer.close()


    # 如果用户要下载文件，则将显示文件信息以供用户确认一切正常。
    # 确认后，将接收文件

    else:

        # 获取所用文件的大小
        size = int(float(info[1]))
        size = FileTransfer.getFormattedSize(size)

        filename = info[0]

        # 检查文件名大小是否大于限制大小。 如果超出限制截掉末尾
        if len(filename.split(".")[0]) > filename_size:
            filename = filename.split(
                ".")[0][0:filename_size]+"."+filename.split(".")[-1]

        print(
            '\n 您确定要下载 "%s" [%.2f %s] 吗? (Y/N)' % (filename, size[0], size[1]))

        # 等待用户响应
        confirmation = None

        while not confirmation:
            confirmation = input("\n 您的选择: ").lower()

            if confirmation == "y":
                confirmation = 1
            elif confirmation == "n":
                confirmation = 2
            else:
                confirmation = None

        # 如果用户不接受该文件，则关闭连接和程序
        if confirmation == 2:
            fileTransfer.close()

        else:
            # 初始化传输
            try:
                fileTransfer.transfer(showProgress)
                print("")
                print("\n 传输结束。\n\n")
            except:
                print("")
                input("\n 传输过程出错。。。\n\n")
            finally:
                fileTransfer.close()
