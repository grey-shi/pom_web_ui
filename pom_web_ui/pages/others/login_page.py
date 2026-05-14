import json
from time import sleep
from common import all_path
from common.base_page import BasePage
from common.logger import Log
from common.widgets.base_toast import BaseToast
from common.widgets.button import Button
from common.widgets.input import Input
from common.yaml_util import YamlUtil

from pages.enums.page_id import PageId
from pages.registry.auto_register_page import register_page


@register_page(PageId.LOGIN)
class LoginPage(BasePage):
    env_json = YamlUtil.read_yaml(f"{all_path.CONFIG_DIR}\\env.yaml")
    default_user = env_json['default_user']
    default_username = default_user['username']
    default_password = default_user['password']
    login_url = 'http://' + env_json['ip']

    def __init__(self, driver):
        super().__init__(driver)  # 初始化父类属性

    def open_login_page(self):
        """ 打开登录页面 """
        self.driver.get(self.login_url)
        Log.info(f'打开登录页面url :{self.login_url}')

    def login(self, user=default_username, password=default_password):
        """ 模拟登录行为 """
        self.open_login_page()
        ip = Input(self.driver)
        bt = Button(self.driver)
        ip.input_text('用户名', user)
        ip.input_text('密码', password)
        bt.click_button('登 录')
        toast = BaseToast(self.driver)  # 悬浮提示通用类
        toast.wait_toast_and_disappear('登录成功')
