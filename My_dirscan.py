import requests
import argparse
from queue import Queue
import threading
import random
import csv
import datetime, os
from bs4 import BeautifulSoup
import sys
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

'''
全类多线程 dirscan 信息扫描
还是按照原来的思路，扫描封装到类，多线程外挂类似Mywebscan Myportscan
注意threading.Thread(target)target 不能有括号，否则会线程卡死
'''

include_status = "200, 301, 302"
exclude_status = "500, 502"


class My_dirscan:
    def __init__(self, site=None, queue=None, dict_file=None, outfile=None, include_status=None, timeout=2, ):
        self.site = site
        self.timeout = timeout
        self.queue = queue
        self.dict_file = dict_file
        self.outfile = outfile
        self.include_status = include_status
        # 获取字典初始化的时候执行一次就够了，然后往gueue中送数据
        self.get_dict_from_file(self.dict_file)

    # 生成随机UA
    def random_useragent(self):
        USER_AGENTS = [
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
        ]
        return random.choice(USER_AGENTS)

    # 进行扫描获取状态码
    def get_status_code(self, url=None):
        # 支持http / https
        header = {'User-Agent': self.random_useragent()}
        try:
            # print(url)
            res = requests.get(url, headers=header, timeout=2)
            res.encoding = "utf-8"
            status_code = str(res.status_code)
            # print(self.include_status)
            # print(type(status_code))
            if status_code in self.include_status:
                # sys.stdout.write('\r' + '[+]%s\t\t\n' % url)
                result = url + '\t\t' + status_code
                print("[+]" + result)
                if self.outfile is not None:
                    self.write_file(result)
            else:
                pass
        except Exception:
            pass

    # 获取数据传入管道
    def get_dict_from_file(self, dict_file):
        with open(dict_file, 'r') as f:
            for line in f:
                self.queue.put(self.site + '/' + line.strip())

    def write_file(self, data):
        # 如果csvfile是一个文件对象，它应该用newline =''打开。
        # with open(self.csvfile, 'a+', newline='')as f:
        #     # fieldnames = {'URL', 'status_code', 'title', 'timeout', 'headers', 'body'}
        #     # newline的作用是防止每次插入都有空行
        #     writer = csv.writer(f)
        #     writer.writerow(data)
        # f = open(datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.txt', 'a+')
        f = open(Outfile, 'a+')
        f.write(data + '\n')
        f.close()
        # print('xieru')
        # # 保存到本地文件，以HTML的格式
        # result = open('result.html', 'a+')
        # result.write('<a href="' + url + '" rel="external nofollow" target="_blank">' + url + '</a>')
        # result.write('\r\n</br>')
        # result.close()

    def start(self):
        while not self.queue.empty():
            url = self.queue.get()
            # print(url)
            # bot = self.web_banner_scan()
            self.get_status_code(url)
            # result = self.get_status_code(url)


if __name__ == '__main__':
    usage = """
    Dir scanner.
    """
    parser = argparse.ArgumentParser(usage=usage, description="")
    parser.add_argument("-f", "--file", type=str, default=None, dest="file", help="Dict file")
    # parser.add_argument("-hb", "--headbody", default=False, action="store_true", dest="saveheadbody",
    #                     help="Store header and body")
    parser.add_argument("-o", "--output", type=str, default=None,
                        dest="outputfile", help="Result to txt")
    parser.add_argument("-u", "--url", type=str, default=None, dest="url", help="URL")
    parser.add_argument("-s", "--status-code", type=str, default=include_status, dest="include_status",
                        help="Include status")
    parser.add_argument("-t", "--thread", type=int, default=50, dest="threads", help="Threads")
    parser.add_argument("--timeout", type=int, default=2, dest="timeout", help="Request timeout")
    args = parser.parse_args()

    Site = args.url
    Thread_maxnum = args.threads
    Timeout = args.timeout
    Dict_file = args.file
    Outfile = args.outputfile
    Include_status = args.include_status.split(',')  # 返回list

    URL_QUEUE = Queue()
    thread_list = []
    if args.timeout != 0 and args.timeout > 0:
        timeout = args.timeout
    else:
        print("--timeout Setting error.")
        exit(1)
    dir_scanner_bot = My_dirscan(site=Site, queue=URL_QUEUE, dict_file=Dict_file, outfile=Outfile,
                                 include_status=Include_status, timeout=Timeout)
    # web_banner_bot.get_url_from_file(args.file)
    # dir_scanner_bot.get_dict_from_file(Dict_file)
    print(Thread_maxnum)
    for i in range(Thread_maxnum):
        # 注意target参数没有(),有()会线程卡死，应该是根据名称去起线程执行函数
        thread = threading.Thread(target=dir_scanner_bot.start)
        thread_list.append(thread)
    #     print(thread_list)
    # print(thread_list)
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()

    if Outfile is not None:
        print("[+] Output save in", os.getcwd() + "\\" + Outfile)
