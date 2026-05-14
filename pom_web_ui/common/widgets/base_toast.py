from selenium.webdriver.support.wait import WebDriverWait
from common import all_path
from common.base_page import BasePage
from common.logger import Log
from selenium.common.exceptions import TimeoutException
from common.yaml_util import YamlUtil


class BaseToast(BasePage):
    # 泛用悬浮提示外层定位（基于常见 UI 框架，如 element-ui）

    def __init__(self, driver):
        super().__init__(driver)
        self.ipt_toast_container = ['By.XPATH', "//div[contains(@class, 'ant-message')]"]
        self.ipt_toast_text = ['By.XPATH', "//span[contains(text(), '{a}')]"]

    def _text(self, text):
        xpath = self.ipt_toast_text[1].replace(f"{{a}}", str(text))
        locator = [self.ipt_toast_text[0], xpath]  # 不能使用元组 ，使用元组定位不到
        return locator

    def _has_toast_container(self):
        """ 是否存在 toast 外层容器 """
        try:
            self.wait_element_present(self.ipt_toast_container, timeout=2)
            return True
        except TimeoutException:
            return False

    def _has_toast_text(self, text):
        """ 是否存在指定文案的 toast """
        try:
            self.wait_any_visible(self._text(text), timeout=2)
            return True
        except TimeoutException:
            return False

    def wait_toast_appear(self, text):
        """
        等待悬浮提示出现

        :return:
            True  - 找到并显示指定 toast
            False - toast 容器存在，但未找到该文案
            None  - 当前页面不存在 toast 容器
        """
        if not self._has_toast_container():
            Log.info("当前页面无 toast 容器")
            return None

        if self._has_toast_text(text):
            Log.info(f"悬浮提示出现: {text}")
            return True

        Log.error(f"toast 存在，但未找到文案: {text}")
        return False

    def wait_toast_disappear(self, text):
        """
        等待悬浮提示消失

        :return:
            True  - toast 已消失
            False - toast 容器存在，但指定 toast 未消失
            None  - 页面无 toast 容器
        """
        if not self._has_toast_container():
            Log.info("当前页面无 toast 容器，视为已消失")
            return None

        try:
            self.wait_invisibility(self._text(text))
            Log.info(f"悬浮提示已消失: {text}")
            return True
        except TimeoutException:
            Log.error(f"等待悬浮提示消失失败: {text}")
            return False

    def wait_toast_and_disappear(self, text):
        """
        等待 toast 出现并消失
        :return True 为 出现并消失  False: 未出现或出现未消失
        """
        appear = self.wait_toast_appear(text)
        if appear is not True:
            return False
        disappear = self.wait_toast_disappear(text)
        if disappear is False:
            return False
        return True
