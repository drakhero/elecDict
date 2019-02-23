import socket
import os,sys
import string
import getpass
from hashlib import sha1


#注册函数
def doRegister(client):
    #所有的特殊字符
    allChars = string.punctuation + string.whitespace
    while True:
        username = input("\033[31m请输入用户名:\033[0m")
        flag = 0
        for u in username:
            if u in allChars:
                print("用户名不能有特殊字符~~~")
                flag = 1
                break

        if flag == 1:
            continue
        #隐藏密码输入
        password1 = getpass.getpass("请输入密码:")
        password2 = getpass.getpass("请再次输入密码:")
        #判断两次密码是否一致
        if password1 == password2:
            #创建sha1加密对象
            s = sha1()
            s.update(password1.encode())
            password = s.hexdigest()
        else:
            print("两次密码不一致")
            continue

        #向服务端发送用户信息
        message = 'R %s %s' % (username,password)
        client.send(message.encode())
        #等待服务器反馈
        data = client.recv(1024).decode()
        if data == 'OK':
            print('注册成功')
        elif data == 'EXISTS':
            print("该用户已存在")
        else:
            print("注册失败")

        return

#查词函数
def doQuery(client):
    while True:
        word = input("请输入您要查找的单词:")
        if word == '##':
            client.send('Break'.encode())
            break
        message = 'Q ' + word
        client.send(message.encode())
        data = client.recv(2048)
        print(data.decode())


#查询历史记录函数
def doHistory(client):
    message = 'H'
    client.send(message.encode())
    data = client.recv(1024)
    print(data.decode())

#二级子界面函数
def doTwoLogin(client):
    while True:
        prompt = '''
        \033[32m==========二级子界面==========
        ---1.查词　2.历史记录　3.注销---
        请选择(1/2/3):\033[0m
        '''
        cmd = input(prompt)
        if cmd not in ['1','2','3']:
            print("请做出正确的选择")
            continue
        elif cmd == '1':
            #查词函数
            doQuery(client)
        elif cmd == '2':
            #查询历史记录函数
            doHistory(client)
        else:
            break

#登录函数
def doLogin(client):
    username = input('请输入用户名:')
    password = getpass.getpass("请输入密码:")
    #给密码加密
    s = sha1()
    s.update(password.encode())
    password = s.hexdigest()
    #包装消息并发送给服务端
    message = 'L %s %s' % (username,password)
    client.send(message.encode())
    #接收服务端反馈结果
    data = client.recv(1024).decode()
    if data == 'OK':
        print('登录成功')
        doTwoLogin(client)
    elif data == 'NAMEERROR':
        print("用户名错误")
    else:
        print('密码错误')

def doExit(client):
    client.send(b'E')
    sys.exit(0)

#创建网络连接
def main():
    #获取命令行参数
    if len(sys.argv) < 3:
        print('参数错误')
        return
    ADDRESS = (sys.argv[1],int(sys.argv[2]))
    client = socket.socket()
    try:
        #连接服务器
        client.connect(ADDRESS)
    except Exception as e:
        print(e)
        return

    #客户端连接成功，进入一级界面
    while True:
        prompt = '''
        **********一级界面**********
        ---1.注册　2.登录　3.退出 ---
        请选择(1/2/3):
        '''
        cmd = input(prompt)
        if cmd.isdigit() and cmd in ['1','2','3']:
            if cmd == '1':
                #注册函数
                doRegister(client)
            elif cmd == '2':
                #登录函数
                doLogin(client)
            else:
                #退出函数
                doExit(client)
        else:
            print("输入有误,请输入(1/2/3)!")

if __name__ == '__main__':
    main()