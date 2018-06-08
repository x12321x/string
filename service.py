#!/usr/bin/env python
# -*- coding:utf-8 -*-
#   
#   Author  :   XueYining
#   Date    :   2018/6/6
#   Desc    :   非阻塞 server

# 采用 fork 的方式实现非阻塞 Server主要原理：
# 当 socket 接受到(accept)一个请求,就 fork 出一个子进程去处理这个请求。
# 然后父进程继续接受请求。
# 从而实现并发的处理请求,不需要处理上一个请求才能接受、处理下一个请求。

import errno
import os
import signal
import socket

# 设置server端IP地址及端口号
SERVER_ADDRESS = (HOST, PORT) = '192.168.92.8', 6666
# 设置请求队列大小
REQUEST_QUEUE_SIZE = 1024

'''===========================此部分为处理僵尸进程==========================='''

'''僵尸进程:一个进程使用fork创建子进程,如果子进程退出,而父进程并没有调用wait或waitpid
获取子进程的状态信息,那么子进程的进程描述符仍然保存在系统中。这种进程称之为僵尸进程。
(系统所能使用的进程号是有限制的,如果大量的产生僵死进程,将因为没有可用的进程号而导致系统
不能产生新的进程。则会抛出OSError: [Errno 35] Resource temporarily unavailable异常)'''

# 多个子进程并发开始，同时结束会并发发出结束信号，父进程的signal一瞬间接受过多的信号，
# 导致有的信号丢失，这种情况还是会有僵尸进程遗留

#信号处理函数
def grim_reaper(signum, frame):
    while True:
        try:
            pid, status = os.waitpid(
                -1,          # pid=-1时，等待任何一个子进程的退出
                 os.WNOHANG  # 如果没有子进程退出，则不阻塞waitpid()调用
            )
        except OSError:
            return

        # 子进程关闭需告诉其父进程
        if pid == 0:  # no more zombies
            return


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
        
        # 如果传输来的字符为exit或者为空，断开连接
        if data == 'exit' or not data:
            print '{0} connection close'.format(client_address)
            
            # 发送TCP数据，告诉client断开连接client_connection.send('Connection closed!')
            break
        
        # 发送TCP数据，给每一个传来的字符串一个响应
        client_connection.send('Hello, {0}'.format(data))

'''===========================此部分为server主要内容==========================='''

def serve_forever():
    
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

    #解决僵尸进程：编写一个SIGCHLD信号处理程序来调用wait/waitpid来等待子进程返回
    signal.signal(signal.SIGCHLD, grim_reaper)

    while True:
        try:
            # 接受TCP连接并返回（conn,address）
            # conn是新的套接字对象，可以用来接收和发送数据。
            # address是连接客户端的地址。
            client_connection, client_address = listen_socket.accept()
        
        except IOError as e:
            code, msg = e.args
            # 重新 'accept' 如果它被阻断
            if code == errno.EINTR:
                continue
            else:
                raise

        # 采用 fork 的方式实现非阻塞 Server,主要原理就是当 socket 接受到(accept)一个请求,
        # 就 fork 出一个子进程去处理这个请求。然后父进程继续接受请求。从而实现并发的处理请求,
        # 不需要处理上一个请求才能接受、处理下一个请求。

        pid = os.fork()
        if pid == 0:  # 子进程
            # 停止接受请求
            listen_socket.close()  
            # 调用响应请求
            handle_request(client_connection, client_address)
            #关闭套接字
            client_connection.close()
            os._exit(0)
        else:  # 父进程
            #关闭套接字
            client_connection.close()  

if __name__ == '__main__':
    serve_forever()
