import socket


'''端口扫描 扫描封装到类单线程版本'''

class Myportscan:
    def __init__(self, ip='', port='', timeout=2):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        socket.setdefaulttimeout(timeout)

    def get_port_isalive(self, ip, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.connect((ip, int(port)))
            # result = '[+] {0}:{1} open'.format(ip, port)
            # print(result)
            # return ('1', ip, port)
            # return result
            return True
        except Exception as e:
            # result = '[-] {0}:{1} close'.format(ip, port)
            # print(result)
            # return ('0', ip, port)
            # return result
            return False
        finally:
            server.close()

    # 获取banner，主要是为开放的端口进行获取开放的端口的banner
    def get_port_banner(self, ip, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.connect((ip, int(port)))
            banner = server.recv(1024).decode()
            return banner
        except Exception as e:
            return None  # 空没有获取到banner
        finally:
            server.close()

    # 探开放+获取banner，先探活，然后获取banner
    def port_alive_and_banner_scan(self, ip, port):
        if self.get_port_isalive(ip, port) is True:
            port_banner = self.get_port_banner(ip, port)
            result = '[+] {0}:{1} open {2}'.format(ip, port, port_banner)
            return result
        elif self.get_port_isalive(ip, port) is False:
            result = '[-] {0}:{1} close'.format(ip, port)
            return result

    # 探端口，只探活
    def port_alive_scan(self, ip, port):
        if self.get_port_isalive(ip, port) is True:
            result = '[+] {0}:{1} open'.format(ip, port)
            return result
        elif self.get_port_isalive(ip, port) is False:
            result = '[-] {0}:{1} close'.format(ip, port)
            return result




def get_ip_status(ip, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server.settimeout(3)
    try:
        server.connect((ip, int(port)))
        print(server.recv(1024))
        print(server)
        # print(server.recv(1024).decode())
        print('[+] {0}:{1} open'.format(ip, port))
    except Exception as err:
        # print(err)
        print('[-] {0}:{1} close'.format(ip, port))
    finally:
        server.close()


if __name__ == '__main__':
    host = '192.168.148.128'
    socket.setdefaulttimeout(1)
    # for port in range(20, 100):
    for port in [6002, 6003, 6004, 6005]:
        get_ip_status(host, port)