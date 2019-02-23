'''
项目：电子词典
模块：socket pymysql
'''

import socket,pymysql
import os,sys
from multiprocessing import Process

#处理注册函数
def doRegister(client,db,username,password):
    #判断user表中是否有此用户
    cursor = db.cursor()
    sel = 'select password from user where username=%s'
    #根据要注册的用户名判断查询结果是否为空
    cursor.execute(sel,[username])
    #r结果为元组
    r = cursor.fetchall()
    if r:
        client.send('EXISTS'.encode())
        return
    else:
        #用户不存在，可以注册
        ins = 'insert into user(username,password) values(%s,%s)'
        try:
            cursor.execute(ins,[username,password])
            db.commit()
            client.send(b'OK')
        except Exception as e:
            db.rollback()
            client.send(b'FAIL')

#处理登录函数
def doLogin(client,db,username,password):
    sel = 'select password from user where username=%s'
    cursor = db.cursor()
    cursor.execute(sel,[username])
    r = cursor.fetchall()
    #如果没有查到结果，表示用户名输入错误
    if not r:
        client.send(b'NAMEERROR')
    elif r[0][0] == password:
        client.send(b'OK')
    else:
        client.send(b'PASSWORDERROR')
    doRequest_second(client,db,username)

#查询单词函数
def doQuery(client,db,word,username):
    sel = 'select interpret from words where word=%s'
    cursor = db.cursor()
    try:
        cursor.execute(sel,[word])
    except Exception:
        print("查询错误")

    r = cursor.fetchall()
    if not r:
        client.send('词典中没有该单词'.encode())
    else:
        client.send(r[0][0].encode())
        selh = 'select word from history where username=%s'
        cursor.execute(selh,[username])
        if (word,) not in cursor.fetchall():
            ins = 'insert into history(username,word,time) values(%s,%s,now())'
            try:
                cursor.execute(ins,[username,word])
                db.commit()
            except Exception as e:
                db.rollback()
                print(e)

#查询历史记录
def doHistory(client,db,username):
    sel = 'select word from history where username=%s'
    cursor = db.cursor()
    try:
        cursor.execute(sel,[username])
    except Exception:
        print("查询失败")

    r = cursor.fetchall()
    if not r:
        client.send('当前没有历史记录'.encode())
        cursor.close()
        return
    s = ''
    for i in r:
        for j in i:
            s += j + ' '
    client.send(s.encode())
    cursor.close()

# 二级登录页面请求
def doRequest_second(client, db, username):
    while True:
        message = client.recv(1024).decode()
        if message == 'Break':
            continue
        msgList = message.split()
        if msgList[0] == 'Q':
            doQuery(client, db, msgList[1],username)
        elif msgList[0] == 'H':
            doHistory(client,db,username)


#处理客户端请求函数
def doRequest(client,db,addr):
    while True:
        message = client.recv(1024).decode()
        msgList = message.split()
        if msgList[0] == 'E':
            print("客户端",addr,'退出')
            sys.exit(0)
        elif msgList[0] == 'R':
            doRegister(client,db,msgList[1],msgList[2])
        elif msgList[0] == 'L':
            doLogin(client,db,msgList[1],msgList[2])

#搭建网络
def main():
    ADDRESS = ('0.0.0.0', 8888)
    #创建数据库连接对象
    db = pymysql.connect('localhost','root','123456','dict',charset='utf8')
    #创建TCP套接字
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server.bind(ADDRESS)
    server.listen(5)
    print("等待客户端连接......")
    while True:
        try:
            client,addr = server.accept()
            print('客户端',addr,'已连接')
        except KeyboardInterrupt:
            sys.exit('服务器已退出')
        except Exception as e:
            print(e)
            continue

        #创建进程,子进程和客户端交互，父进程等待其他客户端连接
        pid = os.fork()
        if pid == 0:
            doRequest(client,db,addr)
        else:
            continue


if __name__ == '__main__':
    main()