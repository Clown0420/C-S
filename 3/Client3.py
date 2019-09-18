# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: JYZ

import socket
import os
import threading

threadlist = []

class Client():
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = '127.0.0.1'
        self.port = 9999
        self.stop = False
        self.socket.connect((self.host, self.port))
        if not os.path.isfile('key.txt'):
            self.socket.send('No id'.encode('utf-8'))
            _recv = self.socket.recv(1024)
            f = open('key.txt', 'w')
            f.writelines(_recv.decode('utf-8'))
            f.close()
            print('你的id为:{}'.format(_recv.decode('utf-8')))
            self.socket.send(_recv)
        else:
            f = open('key.txt', 'r')
            line = f.read()
            self.socket.send(str(line).encode('utf-8'))



    def _send(self):
        while True:
            if not self.stop:
                target = input(">>>>>>to").strip()
                line = input(">>>>>>say:").strip()
                msg = target + ',' + line
                self.socket.send(msg.encode('utf-8'))
            else:
                break


    def _recv(self):
        while True:
            if not self.stop:
                data = self.socket.recv(1024)
                if data.decode('utf-8') != 'logout success':
                    print('>>>>{}\n'.format(data.decode('utf-8')))
                else:
                    self.stop = True
            else:
                break


def stop ():
    global threadlist
    for i in threadlist:
        i.join()


def main():
    global threadlist
    client = Client()
    t1 = threading.Thread(target=client._send)
    t2 = threading.Thread(target=client._recv)
    threadlist.append(t1)
    threadlist.append(t2)
    for i in threadlist:
        i.start()


if __name__ == '__main__':
    main()
    stop()
