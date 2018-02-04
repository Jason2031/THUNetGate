# -*- coding: utf-8 -*-
import hashlib
import requests
import json
import sys
import inspect


class Wox(object):
    """
    Wox python plugin base
    """

    def __init__(self):
        rpc_request = json.loads(sys.argv[1])
        self.proxy = rpc_request.get("proxy", {})
        request_method_name = rpc_request.get("method")
        request_parameters = rpc_request.get("parameters")
        methods = inspect.getmembers(self, predicate=inspect.ismethod)

        request_method = dict(methods)[request_method_name]
        results = request_method(*request_parameters)
        if request_method_name == "query":
            print(json.dumps({"result": results}))

    def query(self, query):
        """
        sub class need to override this method
        """
        return []

    def debug(self, msg):
        """
        alert msg
        """
        print("DEBUG:{}".format(msg))
        sys.exit()


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
        return msg

    def logout(self):
        logout_data = {
            'action': 'logout'
        }
        msg = self.check()
        msg = self.post(logout_data) + ('\n' + msg if msg is not False else '')
        return msg

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


class THUNetGate_Wox():
    def query(self, query):
        results = []
        net_gate = THUNetGate()
        if query == 'o':
            msg = net_gate.logout().split('\n')
            results.append({
                "Title": msg[0],
                "SubTitle": msg[1] if len(msg) == 2 else '',
                "IcoPath": "Images/app.png",
                "ContextData": "ctxData"
            })
        elif query == 'c':
            usage = net_gate.check()
            results.append({
                "Title": 'Traffic usage',
                "SubTitle": usage if usage is not False else 'You are not online.',
                "IcoPath": "Images/app.png",
                "ContextData": "ctxData"
            })
        elif query == 'i':
            with open('account.json') as acc:
                account = json.loads(acc.read())
                msg = net_gate.login(account['username'], account['password']).split('\n')
                results.append({
                    "Title": msg[0],
                    "SubTitle": msg[1],
                    "IcoPath": "Images/app.png",
                    "ContextData": "ctxData"
                })
        else:
            results.append({
                "Title": 'Login',
                "SubTitle": 'thunet i',
                "IcoPath": "Images/app.png",
                "ContextData": "ctxData"
            })
            results.append({
                "Title": 'Logout',
                "SubTitle": 'thunet o',
                "IcoPath": "Images/app.png",
                "ContextData": "ctxData"
            })
            results.append({
                "Title": 'Check traffic usage',
                "SubTitle": 'thunet c',
                "IcoPath": "Images/app.png",
                "ContextData": "ctxData"
            })
        return results


if __name__ == "__main__":
    THUNetGate_Wox()
