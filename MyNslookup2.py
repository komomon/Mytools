# coding=gbk
import subprocess
import csv

"""
python���������DNS��������nslookup����ʵ��
https://www.jb51.net/article/189617.htm
���������ÿ������ָ��һ��dns��excel��ȡ���ݣ���ϸ������
�ص���ʹ��Popen����ִ�����ݳ����

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
    file_domain = r'data\domain.csv'  # �����ļ�
    file_nslookup = r'data\nslookup.csv'  # ����ļ�
    with open(file_domain, 'r', newline='', encoding='gbk') as rf:
        domain_csv = csv.DictReader(rf, dialect=csv.excel)
        domain_list = [row['domain'] for row in domain_csv]

    with open(file_domain, 'r', newline='', encoding='gbk') as rf:
        domain_csv = csv.DictReader(rf, dialect=csv.excel)
        dns_list = []
        for row in domain_csv:
            print(row['DNS'])
            if row['DNS'] != '':  # ͨ��DNS����������Ҫ����������������ȥ�մ���
                dns_list.append(row['DNS'])

    with open(file_nslookup, 'w+', newline='', encoding='gbk') as wf:
        nslookup_csv = csv.writer(wf, dialect=csv.excel)
        header = ['domain', 'DNS', 'nslookup_res...']
        nslookup_csv.writerow(header)
        for domain in domain_list:
            for dns in dns_list:
                print('�����У�������{0}___DNS��{1}'.format(domain, dns))
                row_nslookup = get_nslookup(domain, dns)
                nslookup_csv.writerow(row_nslookup)

print('ִ�����')