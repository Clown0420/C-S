# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: JYZ

import socket
import os
import threading
import time
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
            target = input(">>>>>>to").strip()
            line = input(">>>>>>say:").strip()
            msg = target + ',' + line
            self.socket.send(msg.encode('utf-8'))


    def to_stop(self):
        global threadlist
        while True:
            if not self.stop:
                time.sleep(0.5)
            else:
                for i in threadlist:
                    i.join()

    def _recv(self):
        while True:
            data = self.socket.recv(1024)
            if data.decode('utf-8') != 'logout success':
                print('>>>>{}\n'.format(data.decode('utf-8')))
            else:
                self.stop = True



def main():
    global threadlist
    client = Client()
    t1 = threading.Thread(target=client._send)
    t2 = threading.Thread(target=client._recv)
    t3 = threading.Thread(target=client.to_stop)
    threadlist.append(t1)
    threadlist.append(t2)
    threadlist.append(t3)
    for i in threadlist:
        i.start()


if __name__ == '__main__':
    main()
