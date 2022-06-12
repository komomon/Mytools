import argparse
import datetime
import socket
import ssl
import threading
from queue import Queue
import os
import OpenSSL.crypto as crypto
import re


class Handle_Data:
    def __init__(self, queue=None, file=None, outputfile=None):
        self.queue = queue
        self.file = file
        self.outputfile = outputfile

    def producer(self):
        with open(self.file, 'r') as f:
            for line in f.readlines():
                ll = line.strip()
                if ll is not None:
                    self.queue.put(ll)

    def handle_data(self, line, outputfile=None):

        ipstr = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}:?\d{0,5}\b', line)
        if len(ipstr) != 0:
            if ":" in line:
                ip, port = ipstr[0].split(":", 1)
            else:
                ip = ipstr[0]
                port = 443
            try:
                dst = (ip, int(port))
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect(dst)

                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(s, server_hostname=dst[0])

                # get certificate
                cert_bin = s.getpeercert(True)
                x509 = crypto.load_certificate(crypto.FILETYPE_ASN1, cert_bin)
                msg = "IP    : " + str(ip) + " || Cert name: " + x509.get_subject().CN + ""

            except socket.error:
                msg = "IP    : " + str(ip) + " || No cert"
        else:
            msg = "Domain: " + line + " || No cert"
        print(msg)
        if outputfile is not None:
            with open(outputfile, "a", encoding="utf-8") as g:
                g.write(msg + "\n")

    def start(self):
        while not self.queue.empty():
            # while True:
            line = self.queue.get()
            self.handle_data(line, self.outputfile)


def iter_count(file_name):
    from itertools import (takewhile, repeat)
    buffer = 1024 * 1024
    with open(file_name) as f:
        buf_gen = takewhile(lambda x: x, (f.read(buffer) for _ in repeat(None)))
        return sum(buf.count('\n') for buf in buf_gen)


if __name__ == '__main__':
    logo = """
    
 ██▓ ██▓███        ▓█████▄  ▒█████   ███▄ ▄███▓ ▄▄▄       ██▓ ███▄    █ 
▓██▒▓██░  ██▒      ▒██▀ ██▌▒██▒  ██▒▓██▒▀█▀ ██▒▒████▄    ▓██▒ ██ ▀█   █ 
▒██▒▓██░ ██▓▒      ░██   █▌▒██░  ██▒▓██    ▓██░▒██  ▀█▄  ▒██▒▓██  ▀█ ██▒
░██░▒██▄█▓▒ ▒      ░▓█▄   ▌▒██   ██░▒██    ▒██ ░██▄▄▄▄██ ░██░▓██▒  ▐▌██▒
░██░▒██▒ ░  ░      ░▒████▓ ░ ████▓▒░▒██▒   ░██▒ ▓█   ▓██▒░██░▒██░   ▓██░
░▓  ▒▓▒░ ░  ░       ▒▒▓  ▒ ░ ▒░▒░▒░ ░ ▒░   ░  ░ ▒▒   ▓▒█░░▓  ░ ▒░   ▒ ▒ 
 ▒ ░░▒ ░            ░ ▒  ▒   ░ ▒ ▒░ ░  ░      ░  ▒   ▒▒ ░ ▒ ░░ ░░   ░ ▒░
 ▒ ░░░              ░ ░  ░ ░ ░ ░ ▒  ░      ░     ░   ▒    ▒ ░   ░   ░ ░ 
 ░                    ░        ░ ░         ░         ░  ░ ░           ░ 
                    ░                                       By Komomon                               
"""

    print(logo)
    ttime = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    usage = """
            python3 {0} -f file.txt
        """.format(os.path.basename(__file__))
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument("-f", "--file", default=None, dest="file", help="the url file")
    parser.add_argument("-o", "--output", default=ttime + "_result.txt", dest="output", help="the result file")
    parser.add_argument("-t", "--thread", type=int, default=10, dest="threads", help="Threads num, defalut 10")
    args = parser.parse_args()
    file = args.file
    outputfile = args.output
    Thread_maxnum = args.threads
    print("[+] {0} starting...".format(ttime))

    if file != None:
        lines = iter_count(file)
        if lines < Thread_maxnum:
            Thread_maxnum = lines
        URL_QUEUE = Queue()
        thread_list = []
        Object = Handle_Data(queue=URL_QUEUE, file=file, outputfile=outputfile)

        print("[+] Threads num:", Thread_maxnum)
        thread = threading.Thread(target=Object.producer)
        thread_list.append(thread)
        # thread.start()
        for i in range(Thread_maxnum):
            thread = threading.Thread(target=Object.start)
            thread_list.append(thread)
        for thread in thread_list:
            thread.start()
        for thread in thread_list:
            thread.join()
    else:
        print("Please use -h see usage!")
        exit(1)
    ttime = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    print("[+] result: {0}".format(outputfile))
    print("[+] {0} finished!".format(ttime))
