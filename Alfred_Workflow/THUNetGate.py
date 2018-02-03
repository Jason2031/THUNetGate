import hashlib
import sys
import urllib
import json
from workflow import Workflow


class THUNetGate:
    main_url = 'http://net.tsinghua.edu.cn/'

    def __init__(self, workflow):
        self.workflow = workflow

    @staticmethod
    def get_encrypted_pw(unencrypted_pw):
        md5 = hashlib.md5()
        md5.update(unencrypted_pw.encode('utf-8'))
        return md5.hexdigest()

    def post(self, data):
        post_data = urllib.urlencode(data)
        f = urllib.urlopen('{}do_login.php'.format(self.main_url), post_data)
        return f.read().decode('utf-8')

    def login(self, username='', password=''):
        login_data = {
            'action': 'login',
            'username': username,
            'password': '{MD5_HEX}' + self.get_encrypted_pw(password),
            'ac_id': '1'
        }
        self.workflow.add_item(title=self.post(login_data))
        msg = self.check()
        self.workflow.add_item(title=msg if msg is not False else 'Login failed...')
        self.workflow.send_feedback()

    def logout(self):
        logout_data = {
            'action': 'logout'
        }
        msg = self.check()
        self.workflow.add_item(title=self.post(logout_data))
        if msg is not False:
            self.workflow.add_item(title=msg)
        self.workflow.send_feedback()

    def check_traffic(self):
        msg = self.check()
        self.workflow.add_item(title=msg if msg is not False else 'You are not online.')
        self.workflow.send_feedback()

    @staticmethod
    def check():
        f = urllib.urlopen('http://net.tsinghua.edu.cn/rad_user_info.php')
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


def main(workflow):
    net_gate = THUNetGate(workflow)
    if sys.argv[1] == 'o':
        net_gate.logout()
    elif sys.argv[1] == 'c':
        net_gate.check_traffic()
    elif sys.argv[1] == 'i':
        with open('account.json') as f:
            account = json.loads(f.read())
            net_gate.login(account['username'], account['password'])


if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
