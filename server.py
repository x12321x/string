#!/usr/bin/env python
# -*- coding:utf-8 -*-
#   
#   Author  :   XueYining
#   Date    :   2018/6/6

import socket
import threading
import time
import sys

# 设置server端IP地址及端口号
SERVER_ADDRESS = (HOST, PORT) = '192.168.92.8', 6666
# 设置请求队列大小
REQUEST_QUEUE_SIZE = 5

'''===========================此部分为响应client request==========================='''

def handle_request(client_connection, client_address):

    print 'Accept new connection from {0}'.format(client_address)
    
    '''*****************此部分为响应client request*****************'''
    
    # 通过发送TCP数据，告诉client已成功连接到server
    client_connection.send('Hi, Welcome to the server!')

    
    '''******************此部分为实现字符串传输******************'''

    while True:
        # 接受TCP套接字的数据，数据以字符串形式返回
        data = client_connection.recv(1024)
        
        print '{0} client send string is {1}'.format(client_address, data)
        
        # 模拟阻塞事件
        time.sleep(10) 
    
        # 如果传输来的字符为exit或者为空，断开连接
        if data == 'exit' or not data:
            print '{0} connection close'.format(client_address)
            
            # 发送TCP数据，告诉client断开连接
            client_connection.send('Connection closed!')
            break

        # 发送TCP数据，给每一个传来的字符串一个响应
        client_connection.send('Hello, {0}'.format(data))


'''===========================此部分为server主要内容==========================='''

def server():

    '''**************此部分为创建套接字并连接到远端**************'''
    
    # 先正常执行try中的socket，若出错则执行except中的指令
    
    try:
        # 定义socket类型，创建套接字
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # 防止socket server重启后端口被占用
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # 绑定需要监听的Ip和端口号
        listen_socket.bind(SERVER_ADDRESS)
        
        # 开始监听TCP传入连接。
        listen_socket.listen(REQUEST_QUEUE_SIZE)
    
    except socket.error as msg:
        print msg
        sys.exit(1)


    '''*****************此部分为等待client响应*****************'''
    
    print 'Waiting connection...'


    '''******************此部分为实现字符串传输******************'''

    while True:
        # 接受TCP连接并返回（conn,address）
        # conn是新的套接字对象，可以用来接收和发送数据。
        # address是连接客户端的地址。
        client_connection, client_address = listen_socket.accept()
        
        #调用响应request函数
        handle_request(client_connection, client_address)
        
        #关闭套接字
        client_connection.close()  

if __name__ == '__main__':
    server()
