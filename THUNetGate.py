import hashlib
import sys
import urllib.parse
import urllib.request
import json


class THUNetGate:
    def __init__(self):
        pass

    main_url = 'http://net.tsinghua.edu.cn/'

    @staticmethod
    def get_encrypted_pw(unencrypted_pw):
        md5 = hashlib.md5()
        md5.update(unencrypted_pw.encode('utf-8'))
        return md5.hexdigest()

    def post(self, data):
        post_data = urllib.parse.urlencode(data).encode('utf-8')
        request = urllib.request.Request('{}do_login.php'.format(self.main_url), post_data)
        f = urllib.request.urlopen(request)
        return f.read().decode('utf-8')

    def login(self, username='', password=''):
        login_data = {
            'action': 'login',
            'username': username,
            'password': '{MD5_HEX}' + self.get_encrypted_pw(password),
            'ac_id': '1'
        }
        print(self.post(login_data))
        msg = self.check()
        print(msg if msg is not False else 'Login failed...')

    def logout(self):
        logout_data = {
            'action': 'logout'
        }
        msg = self.check()
        print(self.post(logout_data))
        if msg is not False:
            print(msg)

    @staticmethod
    def check():
        request = urllib.request.Request('http://net.tsinghua.edu.cn/rad_user_info.php')
        f = urllib.request.urlopen(request)
        result = f.read().decode('utf-8')
        if result == '':
            return False
        traffic = int(result.split(',')[6])
        if traffic >= 1000000000:
            traffic /= 1000000000.0
            return 'Traffic usage: {}G'.format(round(traffic, 5))
        else:
            traffic /= 1000000.0
            return 'Traffic usage: {}M'.format(round(traffic, 5))


def usage():
    print('''
    Usage: 
    login: python THUNetGate.py i
    logout: python THUNetGate.py o
    check traffic usage: python THUNetGate.py c
    ''')


if __name__ == '__main__':
    net_gate = THUNetGate()
    if len(sys.argv) == 2:
        if sys.argv[1] == 'o':
            net_gate.logout()
        elif sys.argv[1] == 'c':
            usage = net_gate.check()
            print(usage if usage is not False else 'You are not online.')
        elif sys.argv[1] == 'i':
            with open('account.json') as acc:
                account = json.loads(acc.read())
                net_gate.login(account['username'], account['password'])
    else:
        usage()
