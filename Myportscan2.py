import socket
import threading
from queue import Queue
import time
import argparse

# import argparse
'''

端口探测全类封装版，管道+探测

2021.7.27
实现多IP、IP段(10-20)，C段 端口扫描+banner扫描
经过不断测试，发现一个问题
通过socket 发送包，如果认为目标,不响应则认为端口是关闭的，
但是有些端口是开放的，但是端口会回应你内容，
所以，如果不设置超时 通过s.recv(1024)会一直无响应，程序中断不了，一直在那卡着

2021.8.1
添加-f参数从文件读取多IP机制

默认不打印关闭端口信息

'''


class Myportscan:
    def __init__(self, ips=None, ipfile=None, ports=None, queue=None, timeout=2):
        self.ips = ips
        self.ipfile = ipfile
        self.ports = ports
        self.queue = queue
        self.timeout = timeout
        socket.setdefaulttimeout(timeout)

    def get_port(self):
        # 80 - 100, 3380 - 3390
        port_list = []
        port_segments = self.ports.split(',')
        for port_segment in port_segments:
            if '-' in port_segment:
                start, end = port_segment.split('-')
                for i in range(int(start), int(end) + 1):
                    port_list.append(i)
            else:
                port_list.append(port_segment)

        return port_list

    def get_ip(self):
        # 10.10.10.10/24  10.10.10.10-20 10.10.10.10 10.10.10.11
        ip_section_list = []
        ip_list = []
        if self.ips is not None:
            ip_section_list.append(self.ips)
        elif self.ipfile is not None:
            with open(self.ipfile, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip() != '':
                        ip_section_list.append(line.strip())
        for ips in ip_section_list:
            if '/24' in ips:
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
            elif ',' in ips:
                iplist = ips.split(',')
                ip_list.extend(iplist)
            else:
                ip_list.append(ips)
        return ip_list

    def queue_put(self):
        ip_list = self.get_ip()
        port_list = self.get_port()
        for ip in ip_list:
            for port in port_list:
                self.queue.put((ip, port))

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

    # 探端口，只探活
    def port_alive_scanner(self):
        while not self.queue.empty():
            ip, port = self.queue.get()
            port_isalive = self.get_a_port_isalive(ip, port)
            if port_isalive is True:
                scan_result = '[+] {0}:{1} open'.format(ip, port)
                print(scan_result)
                return scan_result
            elif port_isalive is False:
                # scan_result = '[-] {0}:{1} close'.format(ip, port)
                # print(scan_result)
                # return scan_result
                pass

    # 探活+获取banner，先探活，然后获取banner
    def port_alive_and_banner_scanner(self):
        while not self.queue.empty():
            ip, port = self.queue.get()
            port_isalive = self.get_a_port_isalive(ip, port)
            if port_isalive is True:
                port_banner = self.get_a_port_banner(ip, port)
                scan_result = '[+] {0}:{1} open {2}'.format(ip, port, port_banner)
                print(scan_result)
                return scan_result
            elif port_isalive is False:
                # scan_result = '[-] {0}:{1} close'.format(ip, port)
                # print(scan_result)
                # return scan_result
                pass


if __name__ == '__main__':
    title = '''
        python3 portscan.py -H 192.168.148.128/24 -p 10-90
        python3 portscan.py -H 192.168.148.128/24 -p 10-90 -s
        python3 portscan.py -H 192.168.148.128/24 -p 10-90 -a
        python3 portscan.py -H 192.168.148.128/24 -p 10-90 -t 100
        python3 portscan.py -H 10.10.10.10,10.10.10.11 -p 10-90
        python3 portscan.py -f ip.txt -p 10-90 -a
    '''
    parser = argparse.ArgumentParser(usage=title, description="Multithread Portscan,the defalut threads is 50.")
    parser.add_argument("-f", "--file", default=None, type=str, dest="ipfile", help="IP file to scan")
    parser.add_argument("-H", "--host", type=str, dest="hosts", required=True, help="Hosts to scan")
    parser.add_argument("-p", "--port", type=str, dest="ports", help="ports to scan")
    parser.add_argument("-s", "--simple", default=True, type=bool, dest="simple_scan", help="alive scan")
    parser.add_argument("-a", "-all", default=False, type=bool, dest="all_scan", help="banner scan")
    parser.add_argument("-t", "--thread", default=50, type=int, dest="threads", help="threads")
    parser.add_argument("--timeout", default=2, type=int, dest="timeout", help="timeout")
    args = parser.parse_args()
    Thread_maxnum = args.threads
    ipfile = args.ipfile
    ips = args.hosts
    ports = args.ports
    timeout = 2
    if args.timeout != 0 and args.timeout > 0:
        timeout = args.timeout
    else:
        print("--timeout Setting error.")
        exit(1)

    IP_PORT_QUEUE = Queue()
    Portscanner = Myportscan(ips, ports, IP_PORT_QUEUE, timeout)
    threads = []
    start_time = time.time()
    # 读取数据，存入管道
    Portscanner.queue_put()
    if args.simple_scan is True:
        for i in range(Thread_maxnum):
            thread = threading.Thread(target=Portscanner.port_alive_scanner)
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
    elif args.all_scan is True:
        for i in range(Thread_maxnum):
            thread = threading.Thread(target=Portscanner.port_alive_and_banner_scanner)
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
