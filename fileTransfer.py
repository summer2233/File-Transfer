# -*- coding:utf-8 -*-
from os.path import exists, getsize, normpath, split
import socket
import io


class ActiveConnectionException(Exception):
    def __str__(self):
        return "Once you have made the connection, you will not be able to create a new connection or make changes to the file name or transfer mode until the connection is terminated."


class IncompleteTransferError(Exception):
    def __str__(self):
        return "The transfer was not completed successfully."


class NoConnectionException(Exception):
    def __str__(self):
        return "You must first start a connection."


class FileTransfer(object):
    __CLIENT = 0
    __HOST = 1
    __OK = "OK+"
    __END = "{;[???END???];}"

    CLIENT = __CLIENT
    HOST = __HOST
    OK = __OK
    END = __END

    MODE = None
    PATH = None
    FILENAME = None

    __connected = False
    __stop = False
    __running = False

    def __init__(self, filename=None, path=None, mode=CLIENT):
        """
        在调用“ connect”和“ transfer”方法之前，必须使用参数“ filename”和“ path”。
        如果传输类型为UPLOAD，则必须在参数“ filename”中传递文件路径。
        如果传输类型为DOWNLOAD，则必须传递目录以将文件保存在“ path”参数中。
        “模式”参数必须为FileTransfer.CLIENT或FileTransfer.HOST。
        """

        self.changeMode(mode)
        self.changeFileName(filename)
        self.changePath(path)
        self.__socket = socket.socket()

    def changeFileName(self, filename):
        """
        更改文件名的方法。
        """
        if self.__connected:
            raise ActiveConnectionException

        if not filename or exists(filename):
            self.__filename = filename
            self.FILENAME = self.__filename
        else:
            raise FileNotFoundError

    def changeMode(self, mode):
        """
        更改传输模式的方法。
        """
        if self.__connected:
            raise ActiveConnectionException

        if mode in [self.__CLIENT, self.__HOST]:
            self.__mode = mode
            self.MODE = self.__mode
        else:
            raise ValueError(
                "The mode parameter must be FileTransfer.CLIENT or FileTransfer.HOST")

    def changePath(self, path):
        """
        更改目录以保存下载文件的方法。
        """
        if self.__connected:
            raise ActiveConnectionException

        if not path or exists(path):
            self.__path = path
            self.PATH = self.__path
        else:
            raise FileNotFoundError

    def close(self):
        """
        终止连接的方法
        """
        self.__stop = True
        self.__socket.close()
        self.__running = False
        self.__connected = False

    def connect(self, address, family=socket.AF_INET, type_=socket.SOCK_STREAM):
        """
        连接方法。
        “address”参数必须为
        包含IP和端口号的字符串。
        如果连接类型为CLIENT，则名称为
        文件及其大小（以字节为单位）。
        示例：[“ hello world.txt”，“ 987”]。
        如果连接类型为HOST，则将返回客户端地址。
        """

        if self.__connected:
            raise ActiveConnectionException

        self.__socket = socket.socket(family, type_)

        if self.__mode == self.CLIENT:

            # 检查是否存在用于保存要下载文件的目录
            if not self.__path:
                raise TypeError(
                    "You must define a directory to save the file to.")

            # 连接到服务器
            self.__socket.connect(address)
            self.__connected = True

            # 接收文件的名称和大小（以字节为单位），格式为 b'filename?size'
            transferInfo = self.__socket.recv(1024).decode().split("?")
            self.__filename = transferInfo[0]
            self.__size = int(float(transferInfo[1]))

            # 返回包含文件名称和大小的字符串
            return transferInfo

        elif self.__mode == self.HOST:

            # 检查是否定义了要发送的文件
            if not self.__filename:
                raise TypeError("You must set a file name to upload.")

            # 创建服务器
            self.__socket.bind(address)
            self.__socket.listen(1)

            # 获取客户端连接和数据
            newSocket, clientInfo = self.__socket.accept()
            self.__connected = True

            # 关闭旧的连接，套接字成为与用户的连接
            self.__socket.close()
            self.__socket = newSocket

            # 获取要发送的文件的大小
            self.__size = getsize(self.__filename)

            # 以b'filename?Size'格式向客户端发送文件名和大小（以字节为单位）
            transferInfo = "%s?%f" % (split(self.__filename)[-1], self.__size)
            self.__socket.send(transferInfo.encode())

            return clientInfo

    @staticmethod
    def getFormattedSize(bytes_):
        """
        获取格式化字节大小的静态方法。
        """
        types = ["Bytes", "KB", "MB", "GB", "TB"]
        index = 0

        while bytes_ > 1024 and index < len(types)-1:
            bytes_ /= 1024
            index += 1
        return bytes_, types[index]

    def transfer(self, progressFunction=None):
        """
        开始文件传输的方法。
        progressFunction参数（可选）必须是包含以下内容的函数需要一个参数以百分比形式接收转移进度。
        """

        if self.__running:
            return

        if not self.__connected:
            raise NoConnectionException

        self.__running = True
        self.__stop = False

        if self.__mode == self.CLIENT:

            # 此变量将存储接收到的字节数
            received = 0

            # 创建文件和bufferedWriter以保存下载的文件数据
            file = io.FileIO(normpath(self.__path+"/"+self.__filename), 'wb')
            bufferedWriter = io.BufferedWriter(file, self.__size)

            # 发送确认您已准备好接收数据的确认
            self.__socket.send(self.__OK.encode())

            while not self.__stop:
                try:
                    data = self.__socket.recv(1024)
                    if not data:
                        break
                except:
                    break

                # 如果数据通知传输结束，则退出while块
                if data == self.__END.encode():
                    break

                # 将数据写入缓冲区
                bufferedWriter.write(data)

                # 求和收到的字节数
                received += len(data)

                # 将转移进度按百分比发送给角色
                if progressFunction:
                    progressFunction(100/self.__size*received)

            # 关闭缓冲区和文件
            bufferedWriter.flush()
            bufferedWriter.close()
            self.__running = False

            # 通知传输已成功完成。
            if data == self.__END.encode():
                return self.__OK
            else:
                raise IncompleteTransferError

        elif self.__mode == self.HOST:

            # 此变量将存储发送的字节数
            sent = 0

            # 创建一个文件和bufferReader以从文件中读取要发送的数据
            file = io.FileIO(self.__filename, 'rb')
            bufferedReader = io.BufferedReader(file)
            confirmation = None

            # 等待确认以开始发送数据
            while confirmation != self.__OK and not self.__stop:
                try:
                    confirmation = self.__socket.recv(1024).decode()
                    if not confirmation:
                        break
                except:
                    break

            # 检查是否有客户确认
            if confirmation != self.__OK and not self.__stop:
                raise IncompleteTransferError
            elif self.__stop:
                return

            # 开始发送文件数据
            for data in bufferedReader.readlines():
                if self.__stop:
                    break
                try:
                    self.__socket.send(data)
                except:
                    raise IncompleteTransferError

                # 对发送的字节数求和
                sent += len(data)

                # 将转移进度按百分比发送给角色
                if progressFunction:
                    progressFunction(100/self.__size*sent)

            # 通知已发送文件中的所有数据。
            self.__socket.send(self.__END.encode())

            # 关闭缓冲区和文件
            bufferedReader.close()
            self.__running = False

            # 通知传输已成功完成
            return self.__OK
