# -*- coding:utf-8 -*-
from fileTransfer import FileTransfer
from getFreeSpace import getFreeSpaceMb
import os
import socket 
import sys

from login_client import login

if login():
    def showProgress(percent, size=25):
        """
        显示传输进度
        """

        global filename, mode
        size /= 100
        percent = int(percent)

        if mode == 1:
            print('\r 正在上传 "{}" ... {}% [{}{}] '.format(
                filename, percent, "#"*int((percent*size)), " "*int(((100*size)-percent*size))), end="")
        else:
            print('\r 正在下载 "{}" ... {}% [{}{}] '.format(
                filename, percent, "#"*int((percent*size)), " "*int(((100*size)-percent*size))), end="")
    

    filename = 'None'
    filename_size = 20
    ip = '127.0.0.1'
    hostname = 'summerdesktop'#input('Enter hostname: ')
    mode = 2
    port = 9997
    

    # 与服务端建立连接，传输 mode 和 path
    welcome_msg = ('-'*20) + 'WELCOME!' + ('-'*20)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((hostname, int(port)))
        print('连接成功！\n')
        print(welcome_msg)
    except:
        print("连接错误！")
        sys.exit()


    while not mode in ['1', '2']:    
        mode = input('请选择 \n 1)上传\n 2)下载\n 3)列出远程的文件 : ')
        if mode == '3':
            client_socket.send(mode.encode())
            dirlist = client_socket.recv(1024).decode()
            print('远程文件列表如下：')
            print(dirlist)
    client_socket.send(mode.encode())
    mode = int(mode)
    # dirlist = client_socket.recv(1024).decode()
        
    if mode == 1:
        localPath = input(' 请输入本地文件的路径及文件名: ')
        path = input(' 请输入要上传到的远程路径 (默认为 upload): ')
        if not path: 
            path = os.getcwd() + '\\upload'
    elif mode == 2:
        path = input(' 请输入远程文件的路径及文件名: ')
        localPath = input(' 请输入要下载到的本地路径 (默认为 download): ')
        if not localPath:
            localPath = os.getcwd() + '\\download'
    
    # 将相对路径转换为绝对路径
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    if not os.path.isabs(localPath):
        path = os.path.abspath(localPath)


    client_socket.send(path.encode())
    # print(client_socket.recv(1024).decode())


    ip = '127.0.0.1'
    port = 9999
    # 启动文件传输服务

    if mode == 1: # 上传到服务端
        fileTransfer = FileTransfer(filename=localPath, mode=FileTransfer.SEND)
        print(" 等待连接 ...")
    else: # 下载到本地
        print(" 连接中 ...")
        fileTransfer = FileTransfer(path=localPath, mode=FileTransfer.RECEIVE)
    try:
        info = fileTransfer.connect((ip, port))
    except:
        input(" 尝试连接失败")
        quit()
        pass

    # 如果用户正在发送文件，则将通知他需要等待客户的确认。
    # 确认后，将发送文件。

    if mode == 1:
        print(" 等待 host 确定： {} ...".format(info[0]))
        filename = os.path.split(localPath)[-1]

        # 检查文件名大小是否大于限制大小。 如果是这样，它将减少
        if len(filename.split(".")[0]) > filename_size:
            filename = filename.split(
                ".")[0][0:filename_size]+"."+filename.split(".")[-1]

        try:
            freespace = getFreeSpaceMb('C:\\')
            print('\n磁盘剩余空间: ', str(freespace), 'MB, 可以传输\n')
            fileTransfer.transfer(showProgress)
            print("")
            input("\n 文件传输成功。\n\n")
        except:
            input("\n 连接断开。\n\n")
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
                freespace = getFreeSpaceMb('C:\\')
                print('磁盘剩余容量: ', str(freespace)[:5], 'GB, 空间充足, 开始传输。')
                fileTransfer.transfer(showProgress)
                print("")
                input("\n 传输结束，请按任意键退出。\n\n")
            except:
                print("")
                input("\n 传输过程出错。。。\n\n")
            finally:
                fileTransfer.close()
