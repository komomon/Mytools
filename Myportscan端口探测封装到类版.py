import socket
import threading
from queue import Queue
import sys
import time
import argparse

# import argparse
'''
经过不断测试，发现一个问题
通过socket 发送包，如果认为目标,不响应则认为端口是关闭的，
但是有些端口是开放的，但是端口会回应你内容，
所以，如果不设置超时 通过s.recv(1024)会一直无响应，程序中断不了，一直在那卡着

单端口探测封装到类版

'''


class Myportscan:
    def __init__(self, ip='', port='', timeout=2):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        socket.setdefaulttimeout(timeout)

    def get_a_port_isalive(self, ip, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.connect((ip, int(port)))
            # result = '[+] {0}:{1} open'.format(ip, port)
            # print(result)
            # return ('1', ip, port)
            # return result
            return True
        except Exception as e:
            # result = '[-] {0}:{1} close'.format(ip, port)
            # print(result)
            # return ('0', ip, port)
            # return result
            return False
        finally:
            server.close()

    # 获取banner，主要是为开放的端口进行获取开放的端口的banner
    def get_a_port_banner(self, ip, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.connect((ip, int(port)))
            banner = server.recv(1024).decode()
            return banner
        except Exception as e:
            return None  # 空没有获取到banner
        finally:
            server.close()

    # 探开放+获取banner，先探活，然后获取banner
    def port_alive_and_banner_scan(self, ip, port):
        if self.get_a_port_isalive(ip, port) is True:
            port_banner = self.get_a_port_banner(ip, port)
            result = '[+] {0}:{1} open {2}'.format(ip, port, port_banner)
            return result
        elif self.get_a_port_isalive(ip, port) is False:
            result = '[-] {0}:{1} close'.format(ip, port)
            return result

    # 探端口，只探活
    def port_alive_scan(self, ip, port):
        if self.get_a_port_isalive(ip, port) is True:
            result = '[+] {0}:{1} open'.format(ip, port)
            return result
        elif self.get_a_port_isalive(ip, port) is False:
            result = '[-] {0}:{1} close'.format(ip, port)
            return result


def get_port(ports):
    # 80 - 100, 3380 - 3390
    port_list = []
    port_segments = ports.split(',')
    for port_segment in port_segments:
        if '-' in port_segment:
            start, end = port_segment.split('-')
            for i in range(int(start), int(end) + 1):
                port_list.append(i)
        else:
            port_list.append(port_segment)

    return port_list


def get_ip(ips):
    # 10.10.10.10/24  10.10.10.10-20 10.10.10.10 10.10.10.11
    ip_list = []
    if '/' in ips:
        # 192.168.1.1/24
        ip_csection = ips.rsplit('.', 1)[0]
        # 将需要 ping 的 ip 加入队列
        for i in range(1, 256):
            ip_list.append(i)
    elif '-' in ips:
        # 192.168.1.2-10
        start_ip = ips.rsplit('-', 1)
        ip_csection, start = start_ip[0].rsplit('.', 1)
        end = int(start_ip[1]) + 1
        for i in range(int(start), end):
            ip_list.append(i)
    else:
        ip_list.append(ips)
    return ip_list


def alive_scanner(queue, timeout=2):
    while not queue.empty():
        ip, port = queue.get()
        scanner = Myportscan(timeout)
        scan_result = scanner.port_alive_scan(ip, port)
        print(scan_result)


def alive_and_banner_scanner(queue, timeout):
    while not queue.empty():
        ip, port = queue.get()
        scanner = Myportscan(timeout)
        scan_result = scanner.port_alive_and_banner_scan(ip, port)
        print(scan_result)


if __name__ == '__main__':
    title = '''
        Multithread ping,the defalut threads is 50.
    Usage: 
        python3 portscan.py -p 80,81 10.10.10.10
        python3 portscan.py -p 80-100,3380-3390 10.10.10.10 10.10.10.11
        python3 portscan.py -p 1-65535 10.10.10.10-20
        python3 portscan.py -p 80,90-100 10.10.10.10/24
    '''

    parser = argparse.ArgumentParser(usage="it's usage tip.", description=title)
    parser.add_argument("-H", type=str, dest="hosts", required=True, help="Hosts to scan")
    parser.add_argument("-p", type=str, dest="ports", help="ports to scan")
    parser.add_argument("-s", "--simple", default=True, type=bool, dest="simple_scan", help="alive scan")
    parser.add_argument("-a", "-all", default=False, type=bool, dest="all_scan", help="banner scan")
    parser.add_argument("-t", "--thread", default=50, type=int, dest="threads", help="threads")
    parser.add_argument("--timeout", default=2, type=int, dest="timeout", help="timeout")
    args = parser.parse_args()
    Thread_maxnum = args.threads
    ip_list = get_ip(args.hosts)
    port_list = get_port(args.ports)
    timeout = 2
    if args.timeout != 0 and args.timeout > 0:
        timeout = args.timeout
    else:
        print("--timeout Setting error.")
        exit(1)

    IP_PORT_QUEUE = Queue()

    for i in ip_list:
        for j in port_list:
            IP_PORT_QUEUE.put((i, j))
    threads = []
    start_time = time.time()

    if args.simple_scan is True:
        # print(2)
        for i in range(Thread_maxnum):
            # print(1)
            thread = threading.Thread(target=alive_scanner, args=(IP_PORT_QUEUE, timeout,))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
    elif args.all_scan is True:
        for i in range(Thread_maxnum):
            thread = threading.Thread(target=alive_and_banner_scanner(), args=(IP_PORT_QUEUE, timeout))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
