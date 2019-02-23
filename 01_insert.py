import pymysql

#数据库连接
db = pymysql.connect('localhost','root','123456',
                     'dict',charset='utf8')
#游标对象
cursor = db.cursor()
ins = 'insert into words(word,interpret) values(%s,%s)'

i = 1
#打开文件，分行读取并插入数据库
with open('dict.txt','r') as f:
    while True:
        oneLine = f.readline()
        if not oneLine:
            break
        word = oneLine.split()[0]
        interpret = ' '.join(oneLine.split()[1:])
        #插入数据库
        cursor.execute(ins,[word,interpret])
        # 提交到数据库执行
        db.commit()
        print("第%d条存入成功" % i)
        i += 1

cursor.close()
db.close()
