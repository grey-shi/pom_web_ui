import time
from common.base_page import DriverFactory
from common.widgets.base_toast import BaseToast
from navigation.navigator import Navigator

from pages.registry.page_registry import PageRegistry


class TestDoctorPage(object):
    def test1(self):
        driver = DriverFactory.get_driver()
        driver.maximize_window()

        toast = BaseToast(driver)  # 悬浮提示通用类

        navigator = Navigator(driver)
        registry = PageRegistry(driver)

        page_id = navigator.goto_login()  # 进入页面，获取页面ID
        registry.get(page_id)  # 获取登录类的实例对象

        registry.LoginPage.login()

        # 进入医生管理
        p_id = navigator.goto_doctor_manage()
        registry.get(p_id)

        registry.DoctorManagePage.open_add_dialog()
        time.sleep(0.2)


