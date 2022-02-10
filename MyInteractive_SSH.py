import argparse
import paramiko
import sys
import time
import platform
import re

# ip = "192.168.148.128"
# port = "22"
# username = "root"
# password = "981129"
# SSH_CON_TIMEOUT = 10  # SSH连接超时设置10s
RECV_BUFLEN = 32768  # SSH通道recv接收缓冲区大小
MAX_WAIT_OUTPUT = 32

'''
交互式SSH，可以使用cd more 但是vim好像不行
'''


def Interactive_SSH(ip, port, username, password, SSH_CON_TIMEOUT=10):
    ssh = paramiko.SSHClient()
    try:
        print('[-] try login ssh {}@{}:{} .....'.format(username, ip, port))
        # 创建一个ssh的白名单 paramiko.AutoAddPolicy() #目的是接受不在本地Known_host文件下的主机。
        # #加载创建的白名单
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # compress 启用压缩
        ssh.connect(ip, port=port, username=username, password=password, compress=True, timeout=SSH_CON_TIMEOUT)
        print('[+] Login successfully')
        print('[+] username:', username, ',password:', password)
        channel = ssh.invoke_shell()
        channel.settimeout(5)

        while True:
            cnt = 0
            while not channel.recv_ready():
                time.sleep(0.5)
                cnt += 1
                if cnt > MAX_WAIT_OUTPUT:
                    break
            result = channel.recv(RECV_BUFLEN)
            # print(result.decode().strip(), end='')
            printdata(result.decode())
            # sys.stdout.write(result.decode().strip())
            command = sys.stdin.readline()
            # print("cmd:", command)
            # print(1)
            channel.send(command)
    except Exception as e:
        print("Error:",e)
        ssh.close()


def printdata(data):
    if platform.system() == "Windows":
        dataa = re.sub(r'\x1b\[.*?m', '', data, flags=re.M)
        print(dataa, end='')
    elif platform.system() == "Linux":
        print(data, end='')


if __name__ == '__main__':
    usage = """
        Interactive SSH connection

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
    Interactive_SSH(host, port, username, password, SSH_CON_TIMEOUT)
