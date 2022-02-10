import dns.resolver
import sys

"""
Nslookup程序（获取A记录，CNAME，MX，TXT，DNS，MX等信息）
完成但是有些记录不太行
"""


class pynslookup:
    def __init__(self, domain='', type=''):
        self.domain = domain
        self.type = type

    def bytetostring(self, bv):
        sv = bv.decode()
        return sv

    def getSPFKey(self, domain):
        spf = 'spf' + "." + domain
        return spf

    def getSPFValue(self, domain):
        try:
            answersSPF = dns.resolver.resolve(self.getSPFKey(domain), 'TXT')
            for rdata in answersSPF:
                for txt_string in rdata.strings:
                    txt_string = self.bytetostring(txt_string)
                    return txt_string
        except dns.resolver.NoAnswer:
            # print('NO TXT Record')
            return 'None'

    def getTvalue(self, domain):
        try:
            answersTXT = dns.resolver.resolve(domain, 'TXT')
            for tdata in answersTXT:
                for txt_string in tdata.strings:
                    txt_string = self.bytetostring(txt_string)
                    return txt_string
        except dns.resolver.NoAnswer:
            # print('NO TXT Record')
            return 'None'

    def getMXvalue(self, domain):
        try:
            resultMX = dns.resolver.resolve(domain, 'MX')
            for exdata in resultMX:
                res = exdata.to_text()
                av = res.split(' ')
                return av[1]
        except dns.resolver.NoAnswer:
            # print('NO MX Record')
            return 'None'

    def getCNAMEvalue(self, domain):
        try:
            result = dns.resolver.resolve(domain, 'CNAME')
            # print('result ', result)
            for ip in result:
                return ip.to_text()
        except dns.resolver.NoAnswer:
            # print('NO CNAME Record')
            return 'None'

    def getAvalue(self, domain):
        try:
            resultA = dns.resolver.resolve(domain, 'A')
            for ip in resultA:
                return ip.to_text()
        except dns.resolver.NoAnswer:
            # print('NO A Record')
            return 'None'

    def result(self, domain, type=''):
        nslookup_result = {}
        if type == '':
            nslookup_result['domain'] = domain
            nslookup_result['A'] = self.getAvalue(domain)
            nslookup_result['CNAME'] = self.getCNAMEvalue(domain)
            nslookup_result['MX'] = self.getMXvalue(domain)
            nslookup_result['TXT'] = self.getTvalue(domain)
            # print(nslookup_result)
            return nslookup_result
        elif type == 'A':
            nslookup_result['domain'] = domain
            nslookup_result['A'] = self.getAvalue(domain)
            # print(nslookup_result)
            return nslookup_result
        elif type == 'CNAME':
            nslookup_result['domain'] = domain
            nslookup_result['CNAME'] = self.getAvalue(domain)
            # print(nslookup_result)
            return nslookup_result
        elif type == 'MX':
            nslookup_result['domain'] = domain
            nslookup_result['MX'] = self.getAvalue(domain)
            # print(nslookup_result)
            return nslookup_result
        elif type == 'TXT':
            nslookup_result['domain'] = domain
            nslookup_result['TXT'] = self.getAvalue(domain)
            # print(nslookup_result)
            return nslookup_result
        else:
            print('type is error!')
            exit(1)


if __name__ == '__main__':
    title = '''
            Nslookup by Python
            Get the record, CNAME, MX, TXT, DNS, MX and other information
        Usage: 
            python3 pynslookup.py www.baidu.com
        '''
    params = sys.argv
    if sys.argv[1] == '-h':
        print(title)
    else:
        domain = sys.argv[1]
        result = pynslookup()
        res = result.result(domain)
        for k, v in res.items():
            print(k, ': ', v)
# result.result('bilibili.com')
# for k,v in result:
#     print(k,': ',v)


#
# re = getCNAMEvalue('www.baidu.com')
# print(re)
# re = getAvalue('www.baidu.com')
# print(re)

# file_r = "wang.txt"
# file_w = "res.json"
#
# with open(file_r, 'r') as file_object_r:
#     lines = file_object_r.readlines()
#     for line in lines:
#         line = line.strip('\n')
#         mx = getMXvalue(line)
#         ip = getAvalue(getMXvalue(line))
#         txt = getTvalue(line)
#         spf = getSPFValue(line)
#         res = mx + "#" + ip + "#" + txt + "#" + spf
#         with open(file_w, 'a') as file_object_w:
#             file_object_w.write(res + '\n')
