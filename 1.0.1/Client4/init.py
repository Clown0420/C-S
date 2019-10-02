#!/usr/bin/python3.6
# -*- coding: UTF-8 -*-
# Author: icanfly

import socket
import os, time
import threading
from conf import *
import signal


class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.flag = threading.Event()
        self.flag.set()
        self.socket.connect((self.host, self.port))
        # 检测是否注册
        if not os.path.isfile('key.txt'):
            self.socket.send('Noid'.encode('utf-8'))
            _recv = self.socket.recv(1024)
            self.username = _recv.decode('utf-8')
            file = open('key.txt', 'w')
            file.writelines(_recv.decode('utf-8'))
            file.close()
            print('自动注册成功，您的新id为:{}！'.format(_recv.decode('utf-8')))
        else:
            f = open('key.txt', 'r')
            line = f.read()
            self.socket.send(str(line).encode('utf-8'))
            self.username = str(line)
            print('id {}:登陆成功'.format(self.username))

    def _send(self):
        while True:
            target = input(">>>>> To: ").strip()
            line = input(">>>>>> Say: ").strip()
            if str(target) != str(self.username):
                if line != 'logout':
                    msg = target + ',' + line
                    self.socket.send(msg.encode('utf-8'))
                # 退出操作
                else:
                    msg = line
                    self.socket.send(msg.encode('utf-8'))
                    break
                # 错误提醒
            else:
                print('请不要给自己发送信息')

    def _recv(self):
        while self.flag.is_set():
            data = self.socket.recv(1024)
            if data.decode('utf-8') != 'logout success':
                print('>>>>{}\n'.format(data.decode('utf-8')))
            # 退出成功
            else:
                print('Logout Success, Closing Client... ')
                self.socket.close()
                break


def main():
    try:
        C = Client()
    except Exception:
        print('Connect is Refused !!!')
        return
    try:
        t1 = threading.Thread(target=C._send)
        t2 = threading.Thread(target=C._recv)
        t1.start()
        t2.start()
    except Exception:
        print('客户端异常退出!')
        return


def quit(signum, frame):
    print('Stopping...')
    time.sleep(1)
    os._exit(0)


if __name__ == '__main__':
    main()
    signal.signal(signal.SIGINT, quit)
