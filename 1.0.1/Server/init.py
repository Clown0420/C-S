#!/usr/bin/python3.6
# -*- coding: UTF-8 -*-
# Author: icanfly

import socket
import threading
from queue import Queue
from conf import *
import time
import signal
import os

# 在线用户列表
user_list = []
# 用户对应的信息
client_list = dict()
# 消息队列
msg_list = Queue()
lock = threading.Lock()
flag = False


def minitor():
    global msg_list, says
    global client_list
    global flag
    while True:
        if not msg_list.empty():
            msg = get_msg(msg_list)
            first_id = str(msg[0])
            second_id = str(msg[1])
            if second_id == '':
                client_list[first_id][1].send('服务器提示： 缺少发送的对象！！！'.encode('utf8'))
            else:
                ip = str(client_list[msg[0]][0])
                says = str(msg[2])
                if says == '':
                    client_list[first_id][1].send('服务器提示： 缺少发送的信息！！！'.encode('utf8'))
                else:
                    data = '>>>>>> 来自 id:{}(ip:{})的消息: {}'.format(first_id, ip, says)
                    lock.acquire()
                    try:
                        cli = client_list[str(msg[1])][1]
                        cli.send(data.encode('utf8'))
                    except Exception:
                        err = '用户(id:{})不在线'.format(str(msg[1]))
                        client_list[str(msg[0])][1].send(err.encode('utf8'))
                    finally:
                        lock.release()


def get_msg(_queue):
    lock.acquire()
    _msg = _queue.get()
    lock.release()
    return _msg


class Server(threading.Thread):
    def __init__(self):
        super(Server, self).__init__()
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((host, port))
        self.serversocket.listen(max_connections)
        print("ServerSocket Started !")
        global id, user_list, client_list, msg_list, flag

    def run(self):
        while True:
            clientsocket, address = self.serversocket.accept()
            try:
                thread = Client(clientsocket, address)
                thread.start()
            except socket.timeout:
                print("Client Connection Timeout !")


class Client(threading.Thread):
    def __init__(self, clientsocket, address):
        super(Client, self).__init__()
        self.clientsocket = clientsocket
        self.username = None
        self.address = address
        self.stop = False
        global user_list
        global client_list
        global msg_list
        global flag
        f = open('db.txt','r')
        id = int(f.read())
        f.close()
        data = self.clientsocket.recv(1024)
        # 分发id
        if data.decode('utf-8') == ('Noid'):
            self.clientsocket.send(str(id).encode('utf8'))
            self.username = str(id)
            lock.acquire()
            client_list[self.username] = [self.address, self.clientsocket]
            lock.release()
            f= open('db.txt','w')
            f.write(str(int(id)+1))
            f.close()
        else:
            self.username = data.decode('utf-8')
            lock.acquire()
            client_list[self.username] = [self.address, self.clientsocket]
            lock.release()
        user_list.append(self.username)

    def run(self):
        while True:
            data = self.clientsocket.recv(1024)
            if data.decode('utf-8') != ',users':
                if data.decode('utf-8') != 'logout':
                    msg = self.username + ',' + data.decode('utf-8')
                    if msg != '{},'.format(self.username):
                        self.append(msg)
                    else:
                        print('客户端id:{}异常关闭'.format(self.username))
                        self.clientsocket.close()
                        user_list.remove(self.username)
                        del client_list[self.username]
                        break
                # 退出请求
                else:
                    msg = 'logout success'
                    self.clientsocket.send(msg.encode('utf-8'))
                    user_list.remove(self.username)
                    del client_list[self.username]
                    self.clientsocket.close()
                    break
            # 获取所有在线用户
            else:
                msg = '在线用户： ' + '(' + str(user_list).replace('[', '').replace(']', '') + ')'
                self.clientsocket.send(msg.encode('utf-8'))

    def append(self, msg):
        global msg_list
        lock.acquire()
        msg_list.put(msg.split(','))
        lock.release()


def main():
    S = Server()
    t1 = threading.Thread(target=S.run)
    t2 = threading.Thread(target=minitor)
    t1.start()
    t2.start()


def quit(signum, frame):
    print('Stopping...')
    time.sleep(1)
    os._exit(0)


if __name__ == '__main__':
    main()
    signal.signal(signal.SIGINT, quit)
