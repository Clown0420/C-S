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
server_list = []

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
        global server_list


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
                lock.acquire()
                try:
                    cli = client_dict[str(msg[1])][1]
                    cli.send(data.encode('utf8'))
                except Exception:
                    err = '用户(id:{})不在线'.format(str(msg[1]))
                    client_dict[str(msg[0])][1].send(err.encode('utf8'))
                finally:
                    lock.release()

    def is_online(self):
        i = len(server_list)
        while True:
            if i != len(server_list):
                infor = '当前在线用户:{}'.format(str(server_list))
                self.notice(client_dict.values(), infor)
                i = len(server_list)


    def notice(self,clientlist,msg):
        lock.acquire()
        for i in clientlist:
            i[1].send(msg.encode('utf8'))
        lock.release()




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
        self.stop = False
        global msg_queue
        global client_dict
        global id
        global server_list
        data = self.clientsocket.recv(1024)
        if data.decode('utf-8') == ('No id'):
            id += 1
            self.clientsocket.send(str(id).encode('utf8'))
            self.username = self.clientsocket.recv(1024).decode('utf-8')
            lock.acquire()
            client_dict[self.username] = [self.address, self.clientsocket]
            lock.release()
        else:
            self.username = data.decode('utf-8')
            lock.acquire()
            client_dict[self.username] = [self.address, self.clientsocket]
            lock.release()
        server_list.append(self.username)



    def run(self):
        print('{}is online !'.format(self.username))
        while True:
            if not self.stop:
                data = self.clientsocket.recv(1024)
                if data.decode('utf-8') != ',logout':
                    msg = self.username + ',' + data.decode('utf-8')
                    self.append(msg)
                else:
                    self.stop = True
            else:
                lock.acquire()
                self.clientsocket.send('logout success'.encode('utf-8'))
                server_list.remove(self.username)
                del client_dict[self.username]
                lock.release()
                break




    def append(self, data):
        lock.acquire()
        msg_queue.put(data.split(','))
        lock.release()


def main():
    server = Server(9999)
    t1 = threading.Thread(target=server.run)
    t2 = threading.Thread(target=server._recv)
    t3 = threading.Thread(target=server.is_online)
    t1.start()
    t2.start()
    t3.start()


if __name__ == '__main__':
    main()