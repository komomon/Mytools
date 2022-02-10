import threading
import subprocess
import time
import os
import sys
from queue import Queue

'''
多线程ping 缺少文件参数和线程数量控制参数
'''
# 定义工作线程
Thread_maxnum = 50


# 定义一个执行 ping 的函数
def ping_ip(IP_QUEUE):
    while not IP_QUEUE.empty():
        ip = IP_QUEUE.get()
        if os.name == 'nt':
            res = subprocess.call('ping -n 2 -w 5 %s' % ip, stdout=subprocess.PIPE)  # linux 系统将 '-n' 替换成 '-c'
        else:
            res = subprocess.call('ping -c 2 -w 5 %s' % ip, stdout=subprocess.PIPE)  # linux 系统将 '-n' 替换成 '-c'

        # 打印运行结果
        # print(ip, "Found" if res == 0 else "Not found")
        if res == 0:
            print(ip, 'is Alive.')


if __name__ == '__main__':
    title = '''
        Multithread ping,the defalut threads is 50.
    Usage: 
        python3 ping.py 10.10.10.10
        python3 ping.py 10.10.10.10 10.10.10.11
        python3 ping.py 10.10.10.10-20
        python3 ping.py 10.10.10.10/24
    '''
    IP_QUEUE = Queue()
    ips = sys.argv
    if sys.argv[1] == '-h':
        print(title)
    if len(sys.argv) == 2:
        ips = sys.argv[1]
        if '/' in ips:
            # 192.168.1.1/24
            ip_csection = ips.rsplit('.', 1)[0]
            # 将需要 ping 的 ip 加入队列
            for i in range(1, 255):
                IP_QUEUE.put(ip_csection + '.' + str(i))
        elif '-' in ips:
            # 192.168.1.2-10
            start_ip = ips.rsplit('-', 1)
            ip_csection, start = start_ip[0].rsplit('.', 1)
            end = int(start_ip[1]) + 1
            for i in range(int(start), end):
                IP_QUEUE.put(ip_csection + '.' + str(i))
        else:
            IP_QUEUE.put(ips)
    else:
        ips = sys.argv
        for ip in ips:
            IP_QUEUE.put(ip)
    threads = []
    start_time = time.time()
    for i in range(Thread_maxnum):
        thread = threading.Thread(target=ping_ip, args=(IP_QUEUE,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print('程序运行耗时：%s' % (time.time() - start_time))
