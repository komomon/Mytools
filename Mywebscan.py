import requests
import argparse
from queue import Queue
import threading
import random
import csv
import datetime, os
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

'''
全类多线程 web banner信息扫描
'''


class My_web_banner_scan:
    def __init__(self, queue=None, url_file=None, csvfile=None, timeout=2, saveheadbody=False):
        self.timeout = timeout
        self.queue = queue
        self.url_file = url_file  # 没用到
        self.csvfile = csvfile
        self.saveheadbody = saveheadbody
        self.initialize_outputfile()

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

    # http/https请求获取banner
    def get_web_banner(self, url):
        # 网站的头部Head信息，Title标题信息，Body内容信息，并保持文件里面（支持http / https）
        header = {'User-Agent': self.random_useragent()}
        # print(header)
        # request = requests.session()
        # requests.exceptions.ReadTimeout  # 下载文件超时,4秒
        # requests.exceptions.ConnectTimeout  # 连接超时,2秒
        res = requests.get(url, headers=header, timeout=2)
        res.encoding = "utf-8"
        status_code = str(res.status_code)
        html = res.text
        soup = BeautifulSoup(html, "lxml")
        # print(type(soup.head.title.string))
        try:
            title = str(soup.head.title.string)
            timeout = 0
        except AttributeError as e:
            print(url, "request timeout,Can set --timeout")
            title = ""
            timeout = 1
        # for k, v in res.headers.items():
        #     print(k, ': ', v)
        # return True
        if self.saveheadbody is False:
            # result = {"URL": url, "status_code": status_code, "title": title, "headers": "", "body": ""}
            result = [url, status_code, title, timeout, "", ""]
        else:
            headers = res.headers
            result = [url, status_code, title, timeout, headers, html]
        return result

    # 获取数据传入管道
    def get_url_from_file(self, url_file):
        with open(url_file, 'r', encoding='utf-8') as f:
            for line in f:
                self.queue.put(line.strip())

    def initialize_outputfile(self):
        # 如果csvfile是一个文件对象，它应该用newline =''打开。
        with open(self.csvfile, 'w', newline='')as f:
            header = ['URL', 'status_code', 'title', 'timeout', 'headers', 'body']
            # newline的作用是防止每次插入都有空行
            writer = csv.writer(f)
            writer.writerow(header)

    def write_file(self, data):
        # 如果csvfile是一个文件对象，它应该用newline =''打开。
        with open(self.csvfile, 'a+', newline='')as f:
            # fieldnames = {'URL', 'status_code', 'title', 'timeout', 'headers', 'body'}
            # newline的作用是防止每次插入都有空行
            writer = csv.writer(f)
            writer.writerow(data)

    def web_banner(self):
        while not self.queue.empty():
            url = self.queue.get()
            # bot = self.web_banner_scan()
            result = self.get_web_banner(url)
            # print(result)
            if self.csvfile is not None:
                self.write_file(result)
            else:
                print(result)


if __name__ == '__main__':
    usage = """
    GET url status code,title,body And write csv file.

    """
    parser = argparse.ArgumentParser(usage=usage, description="")
    parser.add_argument("-f", "--file", type=str, default=None, dest="file", help="URL file")
    parser.add_argument("-hb", "--headbody", default=False, action="store_true", dest="saveheadbody",
                        help="Store header and body")
    parser.add_argument("-o", "--output", type=str, default=datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.csv',
                        dest="outputfile",
                        help="Result to csv")
    # parser.add_argument("-u", "--url", type=str, default=None, dest="url", help="URL")
    parser.add_argument("-t", "--thread", type=int, default=50, dest="threads", help="Threads")
    parser.add_argument("--timeout", type=int, default=2, dest="timeout", help="Request timeout")
    args = parser.parse_args()
    Thread_maxnum = args.threads
    timeout = 2
    thread_list = []
    URL_QUEUE = Queue()
    # URL_QUEUE.put("https://www.baidu.com")
    # URL_QUEUE.put("https://www.taobao.com")
    # URL_QUEUE.put("https://www.taobao.com")
    # URL_QUEUE.put("https://www.taobao.com")
    # URL_QUEUE.put("https://www.taobao.com")
    if args.timeout != 0 and args.timeout > 0:
        timeout = args.timeout
    else:
        print("--timeout Setting error.")
        exit(1)
    web_banner_bot = My_web_banner_scan(queue=URL_QUEUE, url_file=args.file, csvfile=args.outputfile, timeout=timeout,
                                        saveheadbody=args.saveheadbody)
    web_banner_bot.get_url_from_file(args.file)
    for i in range(Thread_maxnum):
        thread = threading.Thread(target=web_banner_bot.web_banner)
        thread.start()
        thread_list.append(thread)
    for thread in thread_list:
        thread.join()

    print("[+] Output save in", os.getcwd() + args.outputfile)
