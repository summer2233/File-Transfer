# -*- coding:utf-8 -*-
from fileTransfer import FileTransfer
import os

try:
    import keyboard
except ModuleNotFoundError:
    keyboard = None

def showProgress(percent,size=25):
    """
    显示传输进度
    """

    global filename,mode
    size /= 100
    percent = int(percent)

    if mode == 1:
        print('\r Sending "{}" ... {}% [{}{}] '.format(filename,percent,"#"*int((percent*size))," "*int(((100*size)-percent*size))),end="")
    else:
        print('\r Downloading "{}" ... {}% [{}{}] '.format(filename,percent,"#"*int((percent*size))," "*int(((100*size)-percent*size))),end="")


filename = None
filename_size = 20
ip = None
mode = None
path = None
port = None 


# 询问用户上传还是下载

print("\n What do you want to do ?\n 1: Upload\n 2: Download")

if keyboard:
    while not mode:
        if keyboard.is_pressed("1"):
            mode = 1
        elif keyboard.is_pressed("2"):
            mode = 2
    keyboard.press("backspace")
else:
    while not mode:
        mode = input("\n Option: ")
        if mode in ("1","2"):
            mode = int(mode)
        else: mode = None

# 要求用户输入IP和端口号，并检查端口是否有效

ip = input("\n\n Enter the IP: ")

while not port:
    try:
        port = int(input("\n Enter the Port: "))
    except:
        input(" You entered an invalid value.")

# 要求用户输入文件夹或文件路径
while not path:

    # 如果用户要发送文件，将要求他们提供文件名。
    # 之后，将检查该文件是否存在。

    if mode == 1:
        input_ = input("\n Enter the file name to upload: ")

        if os.path.exists(input_):
            path = input_
        else:
            input(" Could not find this file.")

    # 如果用户要下载文件，将要求他们提供文件夹的路径，以便保存下载的文件。

    else:
        input_ = input("\n Enter a directory to save the file: ")

        if not input_:
            path = os.getcwd()
        else:
            if os.path.isdir(input_):
                path = input_
            else:
                input(" Could not find this directory.")

print("\n")

# 启动服务端或客户端

if mode == 1:
    fileTransfer = FileTransfer(filename=path,mode=FileTransfer.HOST)
    print(" Awaiting connection ...")
else:
    print(" Connecting ...")
    fileTransfer = FileTransfer(path=path,mode=FileTransfer.CLIENT)
try:
    info = fileTransfer.connect((ip,port))
except:
    input(" Failed to attempt to connect.")
    quit()


# 如果用户正在发送文件，则将通知他需要等待客户的确认。
# 确认后，将发送文件。

if mode == 1:
    print(" Awaiting confirmation of {} ...".format(info[0]))
    filename = os.path.split(path)[-1]

    # 检查文件名大小是否大于限制大小, 如果超出限制截掉末尾
    if len(filename.split(".")[0]) > filename_size:
        filename = filename.split(".")[0][0:filename_size]+"."+filename.split(".")[-1]

    try:
        fileTransfer.transfer(showProgress)
        print("")
        input("\n Transfer completed successfully.\n\n")
    except:
        input("\n Connection terminated.\n\n")
    finally:
        fileTransfer.close()


# 如果用户要下载文件，则将显示文件信息以供用户确认一切正常。
# 确认后，将接收文件

else:

    # 获取所用文件的大小
    size = int(float(info[1]))
    size = FileTransfer.getFormattedSize(size)

    filename = info[0]

    # 检查文件名大小是否大于限制大小, 如果超出限制截掉末尾
    if len(filename.split(".")[0]) > filename_size:
        filename = filename.split(".")[0][0:filename_size]+"."+filename.split(".")[-1]

    print('\n Do you want to download "%s" [%.2f %s] ? (Y/N)'%(filename,size[0],size[1]))

    # 等待用户响应
    confirmation = None

    if keyboard:
        while not confirmation:
            if keyboard.is_pressed("y") or keyboard.is_pressed("Y"):
                confirmation = 1
            if keyboard.is_pressed("n") or keyboard.is_pressed("N"):
                confirmation = 2
        keyboard.press("backspace")

    else:
        while not confirmation:
            confirmation = input("\n Your decision: ").lower()

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
            input("\n Transfer completed successfully.\n\n")
        except:
            print("")
            input("\n A failure occurred during the transfer.\n\n")
        finally:
            fileTransfer.close()



