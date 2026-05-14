import requests
from common.logger import Log


class APIUtil(object):
    def __init__(self):
        self.session = requests.session()
        self.token = None

    # 统一请求封装
    def send_all_request(self, **kwargs):
        res = self.session.request(**kwargs)
        Log.info(f'\n请求返回结果：{res.text}')
        return res

    def send_api(self, method, url, headers, json_data):
        """ 接口发送 """
        res = self.send_all_request(method=method, url=url, headers=headers, json=json_data)
        res_json = res.json()
        return res_json

    def login(self):
        method = 'post'
        url = 'http://192.168.31.201/api/user/login'
        headers = {'content-type': 'application/json'}
        json_data = {
            'name': 'root',
            'pwd': '3ddb996582bfdbaa7d8c9470ce5ccc52312cc9d661c0bf7a06eb92802d9bbe5d'
        }
        res = self.send_all_request(method=method, url=url, headers=headers, json=json_data)
        res_json = res.json()
        Log.info(res_json)
        self.token = res_json['result']['token']
        assert self.token

    def get_doctor_list(self):
        Log.info(self.token)
        method = 'post'
        url = 'http://192.168.31.201/api/user/get_user_list'
        headers = {
            'content-type': 'application/json',
            'authorization': f'{self.token}'
        }
        json_data = {
            "is_ignore_admin": True,
            "user_name": "",
            "start": 0,
            "get_num": 1000
        }
        res = self.send_all_request(method=method, url=url, headers=headers, json=json_data)
        res_json = res.json()
        assert res_json
        return res_json

