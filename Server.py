# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: JYZ

import socket
import threading
from queue import Queue

lock = threading.Lock()
msg_queue = Queue()
client_dict = dict()
id = 0


class Server():
    def __init__(self, port):
        self.port = port
        self.host = '127.0.0.1'
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((self.host, self.port))
        self.serversocket.listen(5)
        print("ServerSocket Started !")
        global id
        global client_dict
        global msg_queue


    def run(self):
        while True:
            clientsocket, address = self.serversocket.accept()
            try:

                thread = Client(clientsocket, address)
                thread.start()

            except socket.timeout:
                print("Client Connection Timeout !")


    def _recv(self):
        while True:
            if not msg_queue.empty():
                msg = self.get_msg(msg_queue)
                data = '>>>>>来自id:{}的消息:{}'.format(str(msg[0]), str(msg[2]))
                client_dict[str(msg[1])].send(data.encode('utf8'))


    def get_msg(self, _queue):
        lock.acquire()
        _msg = _queue.get()
        lock.release()
        return _msg


class Client(threading.Thread):
    def __init__(self, clientsocket, address):
        super(Client, self).__init__()
        self.clientsocket = clientsocket
        self.username = None
        self.address = address
        global msg_queue
        global client_dict
        global id
        data = self.clientsocket.recv(1024)
        if data == 'No id':
            msg = '你的id是:{}'.format(str(id))
            id += 1
            self.clientsocket.send(msg.encode('utf8'))
            self.username = self.clientsocket.recv(1024)
            client_dict[self.username] = [self.address, self.clientsocket]
        else:
            self.username = str(data)


    def run(self):
        while True:
            data = self.clientsocket.recv(1024)
            msg = self.username + ',' + data
            self.append(msg)


    def append(self, data):
        lock.acquire()
        msg_queue.put(data.split(','))
        lock.release()


def main():
    server = Server(9999)
    t1 = threading.Thread(target=server.run())
    t2 = threading.Thread(target=server._recv())
    t1.start()
    t2.start()


if __name__ == '__main__':
    main()