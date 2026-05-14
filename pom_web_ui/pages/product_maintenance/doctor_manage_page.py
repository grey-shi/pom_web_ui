import json
import time
from time import sleep
from common import all_path
from common.api_util import APIUtil
from common.base_page import BasePage
from common.logger import Log
from common.widgets.base_pagination import Pagination
from common.widgets.button import Button
from common.widgets.input import Input
from common.widgets.navbar import NavBar
from common.yaml_util import YamlUtil
from selenium.webdriver.common.by import By

from pages.enums.page_id import PageId
from pages.registry.auto_register_page import register_page


@register_page(PageId.DOCTOR_MANAGE)
class DoctorManagePage(BasePage):

    def __init__(self, driver):
        super().__init__(driver)  # 初始化父类属性
        self.navbar = NavBar(driver)
        self.button = Button(driver)
        self.input = Input(driver)
        self.pagination = Pagination(driver)

        self.add_label = '新增医生'

    def open_add_dialog(self):
        self.button.click_button(self.add_label)

