import hashlib
import sys
import requests
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
        request = requests.get('{}do_login.php'.format(self.main_url), params=data)
        f = request.content
        return f.decode('utf-8')

    def login(self, username='', password=''):
        login_data = {
            'action': 'login',
            'username': username,
            'password': '{MD5_HEX}' + self.get_encrypted_pw(password),
            'ac_id': '1'
        }
        msg = self.post(login_data)
        traffic = self.check()
        msg += '\n' + (traffic if traffic is not False else 'Login failed...')
        print(msg)

    def logout(self):
        logout_data = {
            'action': 'logout'
        }
        msg = self.check()
        msg = self.post(logout_data) + ('\n' + msg if msg is not False else '')
        print(msg)

    @staticmethod
    def check():
        request = requests.get('http://net.tsinghua.edu.cn/rad_user_info.php')
        f = request.content
        result = f.decode('utf-8')
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
