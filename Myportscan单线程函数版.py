#!/usr/bin/python3
# -*- coding: utf-8 -*-
import socket
import queue

Thread_maxnum = 50


# 获取端口开放情况
def portScanner(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        # print(s.recv(1024))
        print('[+] %d open' % port)
        s.close()
    except:
        print('[-] %d close' % port)


# 获取端口banner
def get_a_port_banner(ip, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.connect((ip, int(port)))
        banner = server.recv(1024).decode()
        return banner
    except Exception as e:
        return None  # 空没有获取到banner
    finally:
        server.close()


def main():
    # setdefaulttimeout(1)
    for p in [6002, 6003]:
        portScanner('192.168.148.128', p)


if __name__ == '__main__':
    main()
