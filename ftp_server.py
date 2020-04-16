"""
ftp 文件服务
多线程并发和套接字练习
"""

from socket import *
from threading import Thread
import sys,os
import time

# 全局变量
HOST = "0.0.0.0"
PORT = 8888
ADDR = (HOST,PORT)
FTP = "/home/tarena/File/"  # 代表文件库

# 处理客户端各种请求
class FTPServer(Thread):
    def __init__(self,connfd):
        super().__init__()
        self.connfd = connfd

    def do_list(self):
        # 判断文件库是否为空
        file_list = os.listdir(FTP)
        if not file_list:
            self.connfd.send(b"NO")
            return
        else:
            self.connfd.send(b"YES")
            time.sleep(0.1)
            # 发送文件列表
            data = "\n".join(file_list)
            self.connfd.send(data.encode())

    # 下载功能 给客户端发文件
    def do_get(self,filename):
        try:
            f = open(FTP+filename,'rb')
        except:
            # 文件不存在
            self.connfd.send(b"NO")
            return
        else:
            self.connfd.send(b"YES")
            time.sleep(0.1)
            # 发送文件
            while True:
                data = f.read(1024)
                if not data:
                    time.sleep(0.1)
                    self.connfd.send(b"##")
                    break
                self.connfd.send(data)
            f.close()

    # 上传文件 接收客户端发送来的文件
    def do_put(self,filename):
        if os.path.exists(FTP+filename):
            self.connfd.send(b"NO")
            return
        else:
            self.connfd.send(b"YES")
            # 接收文件
            # 接收文件
            f = open(FTP+filename, 'wb')
            while True:
                data = self.connfd.recv(1024)
                # 文件接收完毕
                if data == b"##":
                    break
                f.write(data)
            f.close()


    def run(self):
        while True:
            data = self.connfd.recv(1024).decode() # 接收客户端请求
            # 根据请求类型分情况讨论
            if not data or data == 'E':
                return # 函数结束即线程退出
            elif data == "L":
                self.do_list()
            elif data[0] == 'G':
                # "G filename"
                filename = data.split(' ')[-1]
                self.do_get(filename)
            elif data[0] == 'P':
                # "P filename"
                filename = data.split(' ')[-1]
                self.do_put(filename)


# 网络并发结构搭建
def main():
    # 创建套接字
    sock = socket()
    sock.bind(ADDR)
    sock.listen(3)

    print("Listen the port 8888")
    # 循环链接客户端
    while True:
        try:
            connfd,addr = sock.accept()
            print("客户端地址:",addr)
        except:
            sys.exit("服务退出")

        # 创建新的线程,处理客户端请求 (通过自定义线程类)
        t = FTPServer(connfd)
        t.setDaemon(True)  # 主服务退出,其他服务也随之退出
        t.start()  # 运行run


if __name__ == '__main__':
    main()