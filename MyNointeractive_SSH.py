import argparse
import datetime
import paramiko
import platform
import re

ip = "192.168.148.128"
port = "22"
username = "root"
password = "981129"
SSH_CON_TIMEOUT = 10


def Nointeractive_SSH(ip, port, username, password, SSH_CON_TIMEOUT=5):
    ssh = paramiko.SSHClient()
    try:
        print('[-] try login ssh {}@{}:{} .....'.format(username, ip, port))
        # 创建一个ssh的白名单 paramiko.AutoAddPolicy()
        # #加载创建的白名单
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # compress 启用压缩
        ssh.connect(ip, port=port, username=username, password=password, compress=True, timeout=SSH_CON_TIMEOUT)
        print('[+] Login successfully')
        print('[+] username: ', username, ' ,password: ', password)
        while True:
            print()
            cmd = input("shell>")
            if cmd == "exit":
                exit(0)
            else:
                stdin, stdout, stderr = ssh.exec_command(cmd)  # stdin为输入，stdout为正确输出，stderr为错误输出，同时只有一个变量有值。
                printdata(stdout.read().decode('utf-8'))
    except Exception as e:
        print("Error:", e)
        ssh.close()


def printdata(data):
    if platform.system() == "Windows":
        dataa = re.sub(r'\x1b\[.*?m', '', data, flags=re.M)
        print(dataa, end='')
    elif platform.system() == "Linux":
        print(data, end='')


if __name__ == '__main__':
    usage = """
        Non Interactive SSH connection
        Input exit to quit.
    """
    parser = argparse.ArgumentParser(usage=usage, description="des")
    parser.add_argument("-H", "--host", type=str, dest="host", required=True, help="Hosts to scan")
    parser.add_argument("--port", type=int, dest="port", default=22, help="ports to scan")
    parser.add_argument("-t", "--timeout", type=int, default=10, dest="timeout", help="Request timeout")
    parser.add_argument("-u", "--user", type=str, required=True, dest="username", help="Username")
    parser.add_argument("-p", "--pass", type=str, required=True, dest="password", help="Password")
    args = parser.parse_args()

    host = args.host
    port = args.port
    username = args.username
    password = args.password
    SSH_CON_TIMEOUT = args.timeout
    Nointeractive_SSH(host, port, username, password, SSH_CON_TIMEOUT)
