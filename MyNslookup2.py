# coding=gbk
import subprocess
import csv

"""
python批量处理多DNS多域名的nslookup解析实现
https://www.jb51.net/article/189617.htm
多个域名，每个域名指定一个dns从excel读取数据，详细看文章
重点是使用Popen命令执行数据出结果

"""


def get_nslookup(domain, dns):
    res = subprocess.Popen("nslookup {0} {1}".format(domain, dns), stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE).communicate()[0]
    response = res.decode("gbk")
    res_list = response.split("s:")
    row_nslookup = [domain, dns]
    row_ip = res_list[2].split()[:-1]
    row_nslookup.extend(row_ip)
    return row_nslookup


if __name__ == "__main__":
    file_domain = r'data\domain.csv'  # 输入文件
    file_nslookup = r'data\nslookup.csv'  # 输出文件
    with open(file_domain, 'r', newline='', encoding='gbk') as rf:
        domain_csv = csv.DictReader(rf, dialect=csv.excel)
        domain_list = [row['domain'] for row in domain_csv]

    with open(file_domain, 'r', newline='', encoding='gbk') as rf:
        domain_csv = csv.DictReader(rf, dialect=csv.excel)
        dns_list = []
        for row in domain_csv:
            print(row['DNS'])
            if row['DNS'] != '':  # 通常DNS数量少于需要监测的域名数量，做去空处理
                dns_list.append(row['DNS'])

    with open(file_nslookup, 'w+', newline='', encoding='gbk') as wf:
        nslookup_csv = csv.writer(wf, dialect=csv.excel)
        header = ['domain', 'DNS', 'nslookup_res...']
        nslookup_csv.writerow(header)
        for domain in domain_list:
            for dns in dns_list:
                print('解析中：域名：{0}___DNS：{1}'.format(domain, dns))
                row_nslookup = get_nslookup(domain, dns)
                nslookup_csv.writerow(row_nslookup)

print('执行完毕')