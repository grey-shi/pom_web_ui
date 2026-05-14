from selenium.common import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from common.logger import Log
from common.base_page import BasePage


class Button(BasePage):
    """ 带输入框 下拉框选择类 (填写报告的下拉框)"""

    def __init__(self, driver):
        super().__init__(driver)
        self.button_locator = [
            "//button[contains(normalize-space(text()), '{label}')]",  # 去除空格 (版本不兼容，可能无效)
            "//div[contains(normalize-space(text()), '{label}')]",
            "//span[contains(normalize-space(text()), '{label}')]",
            "//span[contains(@aria-label, '{label}')]",
            "//a[contains(normalize-space(text()), '{label}')]",
            "//i[contains(normalize-space(text()), '{label}')]",
        ]
        self.button_el = None

    def _wait_any_button_present(self, label: str, timeout=3):
        """
        在短 timeout 内，等待任意一个按钮候选进入 DOM
        作为页面已渲染按钮区域的信号
        """
        by_list = []
        for xpath in self.button_locator:
            xpath1 = xpath.replace("{label}", str(label))
            by_list.append(self._parse_locator(['By.XPATH', xpath1]))

        def _cond(driver):
            for by in by_list:
                if driver.find_elements(*by):
                    return True
            return False

        try:
            WebDriverWait(self.driver, timeout).until(_cond)
            Log.info(f"success 一个按钮: {label} 候选进入 DOM")
        except TimeoutException:
            Log.error(f"timeout DOM不存在按钮：{label} 元素")
            raise TimeoutException(f"timeout DOM不存在按钮：{label} 元素")

    def _find_buttons(self, label: str, container) -> list[WebElement]:
        """
        返回所有匹配的按钮候选元素
        不判断可见性、不判断可点击
        """
        buttons = []
        for xpath in self.button_locator:
            xpath1 = xpath.replace("{label}", str(label))
            locator = ['By.XPATH', xpath1]
            try:
                # 立刻查
                els = self.find_in_all(locator, container, label) if container else self.find_elements(locator, label)
                buttons.extend(els)  # 把“另一个可迭代对象里的元素，一个一个地加进来”
            except:
                continue

        if not buttons:
            Log.warning(f'未找到任何按钮候选: {label}')
        else:
            Log.info(f'找到 {len(buttons)} 个按钮候选: {label}')
        return buttons

    def _wait_any_clickable_from_elements(self, buttons):
        for bt in buttons:
            if bt.is_displayed() and bt.is_enabled():
                self.button_el = bt
                Log.info(f"按钮可点击：{bt}")
                return
        Log.warning(f"按钮不可点击：{buttons}")

    def click_button(self, label, container=None):
        self._wait_any_button_present(label)
        bts = self._find_buttons(label, container)
        self._wait_any_clickable_from_elements(bts)
        if not self.button_el:
            Log.error(f"按钮元素: {label} 未找到！")
            raise Exception(f"按钮元素: {label} 未找到！")
        self.click(self.button_el, label)
