import datetime
import re
import time
from selenium.common import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait

from common.logger import Log
from common.base_page import BasePage


class DatePicker(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

        # 时间控件的定位
        self.date_picker_type_location = {
            "calendar": "//label[contains(text(),'{label}')]/ancestor::div[1]/following-sibling::div[1]//input[contains(@class, 'calendar')]",
            "custom_start_end_picker": "//label[contains(text(),'{label}')]/ancestor::div[1]/following-sibling::div[1]//input[contains(@date-range, 'start')]",
            "custom_end_picker": "//label[contains(text(),'{label}')]/ancestor::div[1]/following-sibling::div[1]//input[contains(@date-range, 'end')]",
            "datetime-local": "//label[contains(text(),'{label}')]/ancestor::div[1]/following-sibling::div[1]//input[@type='datetime-local']"
        }
        self.date_picker_location = {
            "calendar": {
                "selected_data": "//label[contains(text(),'{label}')]/ancestor::div[1]/following-sibling::div[1]//span",
                "prev_year": "//div[contains(@class, 'calendar-header')]//a[contains(@title, '上一年')]",
                "prev_month": "//div[contains(@class, 'calendar-header')]//a[contains(@title, '上个月')]",
                "year_select": {
                    "year_select_btn": "//div[contains(@class, 'calendar-header')]//a[contains(@title, '选择年份')]",
                    "year_select_by_num": "//tabel/tbody//td/a[contains(text(), '{year}')]",
                    "prev_year": "//div/a[contains(@title, '上一年代')]",
                    "last_year": "//div/a[contains(@title, '下一年代')]"
                },
                "month_select": "//div[contains(@class, 'calendar-header')]//a[contains(@title, '选择月份')]",
                "next_year": "//div[contains(@class, 'calendar-header')]//a[contains(@title, '下一年')]",
                "next_month": "//div[contains(@class, 'calendar-header')]//a[contains(@title, '下个月')]",
                "day": "//tbody[contains(@class, 'calendar-tbody')]//tr/td[not(contains(@class, 'month'))]/div[text()='{day}']",
                "today": "//span/a[contains(text(), '今天')]"
            },
            "custom_start_end_picker": {
                "selected_data": "//label[contains(text(),'{label}')]/ancestor::div[1]/following-sibling::div[1]//input[@date-range='start']",
                "prev_year": "//div[contains(@class, 'picker-panels')]/div[1]//button[contains(@aria-label, '上一年')]",
                "prev_month": "//div[contains(@class, 'picker-panels')]/div[1]//button[contains(@aria-label, '上个月')]",
                "next_year": "//div[contains(@class, 'picker-panels')]/div[2]//button[contains(@aria-label, '下一年')]",
                "next_month": "//div[contains(@class, 'picker-panels')]/div[2]//button[contains(@aria-label, '下个月')]",
                "day": "//div[contains(@class, 'picker-panels')]/div[1]//tr/td[contains(@class, 'picker-cell-in-view')]/div[text()='{day}']",
                "today": "//div/ul/li[text()='当天')]",
                "this_month": "//div/ul/li[text()='本月')]",
                "this_week": "//div/ul/li[text()='本周')]"
            }
        }
        # 初始化
        self.date_picker_type = None
        self.date_picker_el = None
        self.label = None
        self.year_gap = None
        self.month_gap = None
        self.day = None

    def select_date(self, label: str, value: str, value_end: str = None):
        """ 选择日期控件中的日期或时间 """
        self._wait_any_date_picker_present(label)
        bts = self._find_date_pickers(label)
        self._wait_any_clickable_from_elements(bts)
        selected_date = self.get_selected_date()
        if selected_date:
            year, month, day = self._parse_date(selected_date)
            start_value = f"{year}-{month}-{day}"
        else:
            current_date = datetime.datetime.now()
            start_value = current_date.strftime("%Y-%m-%d")
        self._get_date_gap(start_value, value)  # 获取 年、月差值 与 day
        self._open()
        self._choose(value, value_end)

    def _wait_any_date_picker_present(self, label: str, timeout=3):
        """
        在短 timeout 内，等待任意一个输入框候选进入 DOM
        作为页面已渲染按钮区域的信号
        """
        by_list = []
        for xpath in self.date_picker_type_location.values():
            xpath1 = xpath.replace("{label}", str(label))
            by_list.append(self._parse_locator(['By.XPATH', xpath1]))

        def _cond(driver):
            for by in by_list:
                if driver.find_elements(*by):
                    return True
            return False
        try:
            WebDriverWait(self.driver, timeout).until(_cond)
            self.label = label
            Log.info(f"success 一个 时间控件 : {label} 候选进入 DOM")
        except TimeoutException:
            Log.error(f"timeout DOM不存在 时间控件：{label} 元素")
            raise TimeoutException(f"timeout DOM不存在 时间控件 ：{label} 元素")

    def _find_date_pickers(self, label: str) -> dict:
        """
        返回所有匹配的按钮候选元素
        不判断可见性、不判断可点击
        """
        pickers = {}
        for key, xpath in self.date_picker_type_location.items():
            xpath1 = xpath.replace("{label}", str(label))
            locator = ['By.XPATH', xpath1]
            els = self.find_elements(locator)  # 立刻查
            pickers[key] = els
        if not pickers:
            Log.warning(f'未找到任何 时间控件 按钮候选: {label}')
        else:
            Log.info(f'找到 {len(pickers)} 个 时间控件 按钮候选: {label}')
        return pickers

    def _wait_any_clickable_from_elements(self, pickers: dict):
        for key, pickers in pickers.items():
            for picker in pickers:
                if picker.is_displayed() and picker.is_enabled():  # 输入框不需要判断是否可点击
                    self.date_picker_el = picker
                    self.date_picker_type = key
                    Log.info(f"时间控件 可点击：{picker}")
                    return
        Log.warning(f"时间控件 不可点击：{pickers}")

    def _open(self):
        """ 展开时间控件 """
        if not self.date_picker_el:
            Log.error(f"[_open] 日期控件元素未找到！")
            raise Exception(f"[_open] 日期控件元素未找到！")
        self.click(self.date_picker_el)
        Log.info(f"[_open] 下拉框展开：{self.label}")

    @staticmethod
    def _parse_date(date_value: str):
        """解析日期字符串，并返回年、月、日"""
        pattern = r'(\d{4}).*?(\d{2}).*?(\d{2})'
        match = re.match(pattern, date_value)
        if match:
            return int(match.group(1)), int(match.group(2)), int(match.group(3))
        else:
            raise ValueError(f"日期格式错误{date_value}，正确格式为：YYYY-MM-DD, 例如：2022-12-01")

    def _get_date_gap(self, start_date: str, end_date: str):
        """计算开始日期与结束日期的差值"""
        start_year, start_month, start_day = self._parse_date(start_date)
        end_year, end_month, end_day = self._parse_date(end_date)

        # 计算年、月差值
        self.year_gap = end_year - start_year
        self.month_gap = end_month - start_month
        self.day = end_day  # 以结尾

    def _choose_year(self, year_gap):
        next_year_locator = ['By.XPATH', self.date_picker_location.get(self.date_picker_type, '').get('next_year', '')]
        prev_year_locator = ['By.XPATH', self.date_picker_location.get(self.date_picker_type, '').get('prev_year', '')]

        # 根据年差值进行点击操作
        for _ in range(abs(year_gap)):
            if year_gap > 0:
                self.click(next_year_locator)
            else:
                self.click(prev_year_locator)
            Log.info(f"选择年份，年差值：{year_gap}")

    def _choose_month(self, month_gap):
        prev_month_locator = ['By.XPATH', self.date_picker_location.get(self.date_picker_type, '').get('prev_month', '')]
        next_month_locator = ['By.XPATH', self.date_picker_location.get(self.date_picker_type, '').get('next_month', '')]

        # 根据月差值进行点击操作
        for _ in range(abs(month_gap)):
            if month_gap > 0:
                self.click(next_month_locator)
            else:
                self.click(prev_month_locator)
            Log.info(f"选择月份，月差值：{month_gap}")

    def _choose_day(self, day):
        day_xpath = self.date_picker_location.get(self.date_picker_type, '').get('day', '').replace(f"{{day}}", str(day))
        day_locator = ['By.XPATH', day_xpath]  # 不能使用元组 ，使用元组定位不到
        self.click(day_locator)
        Log.info(f"选择日期：{day}")

    def _choose(self, date_value: str, date_value_end: str = None):
        """选择日期，支持开始时间和结束时间"""
        if not self.date_picker_el:
            Log.error(f"日期控件元素未找到: {self.label}")
            raise Exception(f"日期控件元素未找到: {self.label}")

        def _choose_date():
            # 选择开始日期
            self._choose_year(self.year_gap)
            self._choose_month(self.month_gap)
            self._choose_day(self.day)

        _choose_date()  # 选择年月日

        # 如果是日期范围，选择结束日期
        if date_value_end:
            self._get_date_gap(date_value, date_value_end)  # 获取 年、月差值 与 day
            _choose_date()  # 选择年月日

        self.wait_invisibility(['By.XPATH', self.date_picker_location.get(self.date_picker_type, '')
                               .get('prev_year', '').replace(f'{{label}}', self.label)])
        Log.info(f"等待日期控件消失: {self.label}")

    def get_selected_date(self) -> str:
        """ 获取当前选中的时间 """
        try:
            selected_date_xpath = (self.date_picker_location.get(self.date_picker_type, '')
                                   .get('selected_data', '').replace(f"{{label}}", self.label))
            selected_date_locator = ['By.XPATH', selected_date_xpath]
            text = self.get_attr(selected_date_locator, 'value')
            if text.isdigit():  # 可能获取到时间 是一个时间戳， 转化为 正确的时间格式
                timestamp = int(text) / 1000  # 毫秒转换为秒
                date = datetime.datetime.fromtimestamp(timestamp)  # 根据本地时区转换时间
                text = date.strftime('%Y-%m-%d')
            Log.info(f'[get_selected_date] 获取时间控件： {self.label} 的时间为：{text}')
            return text
        except Exception as e:
            Log.error(f"[get_selected_date] 获取时间控件 '{self.label}' 的选中时间失败: {e}")
            raise EnvironmentError(f"[get_selected_date] 获取时间控件 '{self.label}' 的选中时间失败: {e}")
