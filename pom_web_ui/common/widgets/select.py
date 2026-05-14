import time
from selenium.common import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from common.logger import Log
from common.base_page import BasePage


class Select(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        self.select_type_location = {
            "rendered_select": "//label[contains(text(),'{label}')]/ancestor::div[1]/following-sibling::div[1]//div[contains(@class, 'rendered')]",
            "selector_select": "//label[contains(text(),'{label}')]/ancestor::div[1]/following-sibling::div[1]//div[contains(@class, 'selector')]"
        }
        self.select_location = {
            "selector_select": {
                "select": "//label[contains(text(),'{label}')]/ancestor::div[1]/following-sibling::div[1]//div[contains(@class, 'selector')]",
                "selected": "//label[contains(text(),'{label}')]/ancestor::div[1]/following-sibling::div[1]//div[contains(@class, 'selector')]//span[contains(@class, 'selection-item')]",
                "ipt_select": "",
                "menu": "//div[contains(@class, 'ant-select-dropdown') and not (contains(@style, 'none'))]//div[contains(@class, 'item-option-content')]",
                "menu_sel": "//div[contains(@class, 'ant-select-dropdown') and not (contains(@style, 'none'))]//div[@title='{value}']"
            },
            "rendered_select": {
                "select": "//label[contains(text(),'{label}')]/ancestor::div[1]/following-sibling::div[1]//div[contains(@class, 'rendered')]",
                "selected": "//label[contains(text(),'{label}')]/ancestor::div[1]/following-sibling::div[1]//div[contains(@class, 'rendered')]//div[contains(@class, 'selected-value')]",
                "ipt_select": "//div[not(contains(@style,'display: none'))]/input[@class='ant-select-search__field']",
                "menu": "//div[contains(@class, 'ant-select-dropdown ant-select-dropdown--single') and not (contains(@style, 'none'))]//ul[@role='listbox']/li",
                "menu_sel": "//div[contains(@class, 'ant-select-dropdown ant-select-dropdown--single') and not (contains(@style, 'none'))]//ul[@role='listbox']/li[@title='{value}']"
            }
        }
        # 设置当前下拉框类型
        self.select_type = None  # 默认类型为 None
        self.select_el = None  # 初始化 self.select_el 为 None
        self.label = None

    def _wait_any_select_present(self, label: str, timeout=3):
        """
        在短 timeout 内，等待任意一个输入框候选进入 DOM
        作为页面已渲染按钮区域的信号
        """
        by_list = []
        for xpath in self.select_type_location.values():
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

    def _find_selects(self, label: str) -> dict:
        """
        返回所有匹配的按钮候选元素
        不判断可见性、不判断可点击
        """
        selects = {}
        for key, xpath in self.select_type_location.items():
            xpath1 = xpath.replace("{label}", str(label))
            locator = ['By.XPATH', xpath1]
            els = self.find_elements(locator)  # 立刻查
            selects[key] = els
        if not selects:
            Log.warning(f'未找到任何按钮候选: {label}')
        else:
            Log.info(f'找到 {len(selects)} 个按钮候选: {label}')
        return selects

    def _wait_any_clickable_from_elements(self, selects: dict):
        for key, selects in selects.items():
            for select in selects:
                if select.is_displayed() and select.is_enabled():  # 输入框不需要判断是否可点击
                    self.select_el = select
                    self.select_type = key
                    Log.info(f"下拉框可点击：{select}")
                    return
        Log.warning(f"下拉框不可点击：{selects}")

    def _open(self):
        """ 展开下拉框 """
        if not self.select_el:
            Log.error(f"[_open] 下拉框元素未找到！")
            raise Exception(f"[_open] 下拉框元素未找到！")
        self.click(self.select_el)
        Log.info(f"[_open] 下拉框展开：{self.label}")

    def _choose(self, value: str):
        """ 下拉框选择 """
        xpath_1 = self.select_location.get(self.select_type, '').get('menu_sel', '').replace(f"{{value}}", str(value))
        locator_1 = ['By.XPATH', xpath_1]  # 不能使用元组 ，使用元组定位不到
        self.click(locator_1)
        self.wait_invisibility(locator_1)
        Log.info(f"[_choose] 下拉框选择：{value}, 并等待下拉框消失")

    def select(self, label: str, value: str):
        """ 通过标签选择下拉框选项
        :param label: 要选择的下拉框内容
        :param value: 要选择的下拉框内容 """
        self._wait_any_select_present(label)
        bts = self._find_selects(label)
        self._wait_any_clickable_from_elements(bts)
        self._open()
        self._choose(value)

    def get_selected_text(self, label) -> str:
        """
        获取指定下拉框当前选中的值
        :return: 当前选中值
        """
        self._wait_any_select_present(label)
        bts = self._find_selects(label)
        self._wait_any_clickable_from_elements(bts)
        try:
            # 定位下拉框输入框或显示文本区域
            locator = ['By.XPATH',
                       self.select_location.get(self.select_type, '').get('selected', '').replace("{label}", label)]
            text = self.get_text(locator)
            Log.info(f'获取标签： {label} 的文本为：{text}; locator: {locator}')
            return text
        except Exception as e:
            Log.error(f"获取下拉框 '{label}' 的选中值失败: {e}")
            return ''

    def get_all_options(self, label) -> list:
        self._wait_any_select_present(label)
        bts = self._find_selects(label)
        self._wait_any_clickable_from_elements(bts)
        self._open()
        els = self.wait_all_visible(["By.XPATH", self.select_location.get(self.select_type, '').get('menu', '')], label)
        options = []
        for el in els:
            text = self.get_text(el, label)
            options.append(text)
        Log.info(f"下拉框:{label} 所有选项为: {options}")
        return options
