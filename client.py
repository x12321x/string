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

def client():

    '''**************此部分为创建套接字并连接到远端**************'''
    
    # 先正常执行try中的socket，若出错则执行except中的指令
    try:
        # 定义socket类型，创建套接字
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 连接到远端的套接字
        s.connect(('192.168.92.8', 6666))
    except socket.error as msg:
        print msg
        sys.exit(1)


    '''*****************此部分为等待server响应*****************'''
    
    print 'Client is Waiting response...'   
    # 接受TCP套接字的数据，数据以字符串形式返回
    print s.recv(1024)


    '''******************此部分为实现文件传输******************'''
    while True:
        data = raw_input('please input string: ')
        # 发送TCP数据。将data中的数据发送到连接的套接字。
        s.send(data)
        
        print 'Client is Waiting response...'
        
        # 接受TCP套接字的数据，数据以字符串形式返回
        print s.recv(1024)
        
        # 如果data为exit，则不再传输文件，终止循环
        if data == 'exit':
            break
    
if __name__ == '__main__':
    client()
