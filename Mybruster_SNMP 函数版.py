#!/usr/local/bin/ python
# -*- coding: utf-8 -*-

__author__ = 'yangxiaodi'
# https://www.cnblogs.com/yangxiaodi/p/5660431.html

from pysnmp.entity.rfc3413.oneliner import cmdgen


def read_file(filepath):
    f = open(filepath).readlines()
    return f


def snmp_connect(ip, key):
    crack = 0
    try:
        errorIndication, errorStatus, errorIndex, varBinds = \
            cmdgen.CommandGenerator().getCmd(
                cmdgen.CommunityData('my-agent', key, 0),
                cmdgen.UdpTransportTarget((ip, 161)),
                (1, 3, 6, 1, 2, 1, 1, 1, 0)
            )
        if varBinds:
            crack = 1
    except:
        pass
    return crack


def snmp_l():
    try:
        host = read_file('host.txt')
        for ip in host:
            ip = ip.replace('\n', '')
            passd = read_file('pass.txt')
            for pwd in passd:
                pwd = pwd.replace('\n', '')
                flag = snmp_connect(ip, key=pwd)
                if flag == 1:
                    print("%s snmp  has weaken password!!-----%s\r\n" % (ip, pwd))
                    break
                else:
                    print("test %s snmp's scan fail" % (ip))
    except Exception as e:
        pass


if __name__ == '__main__':
    snmp_l()
