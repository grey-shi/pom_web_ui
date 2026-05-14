import time
from selenium.common import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from common.logger import Log
from common.base_page import BasePage


class Input(BasePage):
    """ 带输入框 下拉框选择类 (填写报告的下拉框)"""

    def __init__(self, driver):
        super().__init__(driver)
        self.input_locator = ["//label[contains(text(), '{label}')]/ancestor::div[2]//input",
                              "//label[contains(text(), '{label}')]/ancestor::div[2]//textarea",
                              "//span[contains(text(), '{label}')]/ancestor::div[1]//input",
                              "//div[contains(text(), '{label}')]//input",
                              "//input[contains(@placeholder, '{label}')]"]
        self.input_el = None
        self.label = None

    def _wait_any_input_present(self, label: str, timeout=3):
        """
        在短 timeout 内，等待任意一个输入框候选进入 DOM
        作为页面已渲染按钮区域的信号
        """
        by_list = []
        for xpath in self.input_locator:
            xpath1 = xpath.replace("{label}", str(label))
            by_list.append(self._parse_locator(['By.XPATH', xpath1]))

        def _cond(driver):
            for by in by_list:
                if driver.find_elements(*by):
                    return True
            return False
        try:
            WebDriverWait(self.driver, timeout).until(_cond)
            Log.info(f"success 一个输入框: {label} 候选进入 DOM")
        except TimeoutException:
            Log.error(f"timeout DOM不存在输入框：{label} 元素")
            raise TimeoutException(f"timeout DOM不存在输入框：{label} 元素")

    def _find_inputs(self, label: str) -> list[WebElement]:
        """
        返回所有匹配的按钮候选元素
        不判断可见性、不判断可点击
        """
        inputs = []
        for xpath in self.input_locator:
            xpath1 = xpath.replace("{label}", str(label))
            locator = ['By.XPATH', xpath1]
            els = self.find_elements(locator)  # 立刻查
            inputs.extend(els)

        if not inputs:
            Log.warning(f'未找到任何按钮候选: {label}')
        else:
            Log.info(f'找到 {len(inputs)} 个按钮候选: {label}')
        return inputs

    def _wait_any_visible_from_elements(self, inputs):
        for ipt in inputs:
            if ipt.is_displayed():  # 输入框不需要判断是否可点击
                self.input_el = ipt
                Log.info(f"输入框可见：{ipt}")
                return
        Log.warning(f"输入框不可见：{inputs}")

    def input_text(self, label: str, value: str):
        self._wait_any_input_present(label)
        bts = self._find_inputs(label)
        self._wait_any_visible_from_elements(bts)
        if not self.input_el:
            Log.error(f"输入框：{label} 元素未找到！")
            raise Exception(f"输入框：{label} 元素未找到！")
        self.input(self.input_el, value, label)

    def get_input_attr_value(self, label, value='value') -> str:
        """
        获取指定下拉框当前选中的值
        :return: 当前选中值
        """
        self._wait_any_input_present(label)
        bts = self._find_inputs(label)
        self._wait_any_visible_from_elements(bts)
        if not self.input_el:
            Log.error(f"输入框：{self.input_el} 元素未找到！")
            raise Exception(f"输入框：{self.input_el} 元素未找到！")
        value = self.get_attr(self.input_el, value)
        Log.info(f"输入框 {label} 显示：{value}")
        return value

    def get_input_placeholder(self, label) -> str:
        """
        获取指定下拉框当前选中的值
        :return: 当前选中值
        """
        if not self.input_el:
            Log.error(f"输入框：{self.input_el} 元素未找到！")
            raise Exception(f"输入框：{self.input_el} 元素未找到！")
        placeholder = self.get_attr(self.input_el, 'placeholder')
        Log.info(f"输入框 {label} 显示：{placeholder}")
        return placeholder
