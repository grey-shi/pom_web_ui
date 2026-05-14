# ⭐ 表格基类
import time
from appium.webdriver import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from common import all_path
from common.base_page import BasePage
from common.logger import Log
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from common.yaml_util import YamlUtil


class BaseTable(BasePage):
    """ 读取列表型数据 + 行/列/单元格的定位与操作 """

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        # Table 是「必须」在父元素里查找的，Dialog 不是
        self.table_body = ['By.XPATH', "//div[contains(@class, 'custom-ant-table-body')]/table"]  # table表位置
        self.table_header = ['By.XPATH', "//div[contains(@class, 'custom-ant-table-header')]/table"]  # 标题表位置

        # 行内单元格（⚠️ 注意 .//）
        self.table_header_text = ['By.XPATH', ".//thead/tr/th"]  # 表的标题（全部）
        self.table_body_rows = ['By.XPATH', ".//tbody/tr"]  # 表的行 （全部）
        self.table_body_row_attr = ['By.XPATH', ".//td"]  # 行的信息

        # 不在 td 的 text属性
        self.table_txt = ['By.XPATH', ".//div|.//span|.//a|.//button"]  # 不在 td 的 text属性
        self.loading = ['By.XPATH', ".//div[contains(@class, 'custom-ant-spin-nested-loading')]"]  # 加载控件

    def _get_table_body(self) -> WebElement:
        """ 获取 body表"""
        table_body = self.wait_any_visible(self.table_body)
        return table_body

    def _get_table_header(self) -> WebElement:
        """ 获取标题表"""
        table_header = self.wait_element_present(self.table_header)
        return table_header

    def _resolve_readable_value(self, el: WebElement):
        """
        从任意元素中提取“可读值”
        返回：
            - ""           无值
            - str          单值
            - list[str]    多值
        """
        if el is None:
            return ""

        # 直接取 element.text
        text = self.get_text(el).strip()
        if text:
            return text

        # 取常见可读子元素
        sub_elements = self.find_in_all(self.table_txt, el)

        values = []
        for sub in sub_elements:
            t = sub.text.strip()
            if t:
                values.append(t)
        if not values:
            return ""

        if len(values) == 1:
            return values[0]

        return values

    def _operation_location(self, el: WebElement, operation: str) -> WebElement:
        """
        从任意元素中提取“可读值”
        :return WebElement
        """
        # 直接取 element.text
        text = self.get_text(el).strip()
        if text == operation:
            return el

        # 取常见可读子元素
        sub_elements = self.find_in_all(self.table_txt, el)
        for sub in sub_elements:
            t = sub.text.strip()
            if t == operation:
                return sub
        raise ValueError(f'【_operation_location】 元素下无操作：{operation}')

    def wait_table_loading(self, rows=0, timeout=10) -> bool:
        """ 等待表格可用(加载元素判断)
        param: rows 等待至少存在多少行加载完成 (默认等待 表格行 > 0)
        return: bool
        """
        try:
            # 等待 loading 可见
            self.wait_any_visible(self.loading, timeout=timeout)
            # 等待 loading 消失
            self.wait_invisibility(self.loading, timeout=timeout)
            # 行数判断（强烈推荐）
            WebDriverWait(self.driver, timeout).until(
                lambda d: len(self._get_rows()) > rows
            )
            Log.info(f"[wait_table_loading]  success 表格加载 > 0 行")
            return True
        except TimeoutException:
            Log.info(f"[wait_table_loading]  timeout 表格加载超时")
            return False

    """ 获取所有的行 """
    def _get_rows(self) -> list:
        """ 获取所有行元素"""
        table_body = self._get_table_body()
        els = self.find_in_all(self.table_body_rows, table_body)
        return els

    """ 获取列标题 """
    def _get_headers_text(self, retries=3, delay=1) -> list:
        """ 获取列标题
        param: retries  最多尝试次数
        param: delay 每次失败后的等待间隔
        return: list
        """
        for _ in range(retries):   # _ 表示 变量不重要、不会被使用
            try:
                table_header = self._get_table_header()
                els = self.find_in_all(self.table_header_text, table_header)
                headers = [self.get_attr(el, 'title').strip() for el in els]
                return headers
            except StaleElementReferenceException:
                Log.warning("获取列标题失败, retrying…")
                time.sleep(delay)  # 延迟后重试
        raise StaleElementReferenceException(f"[_get_headers_text] 无法获取到列标题 fail ")

    # -----------------------------------
    # 【表格级操作】
    # -----------------------------------
    """ 获取所有行的某列的所有值"""
    def get_all_col_value(self, col_name: str, unique=False) -> list:
        """ 通过表格列表项 查找指定列表项的所有值
        :param col_name 列名
        :param unique 列是否去重（默认不去重）
        :return list  如申请单号列表
        """
        headers = self._get_headers_text()
        rows = self._get_rows()
        if col_name not in headers:
            raise ValueError(f"列名 {col_name} 不存在")
        col_idx = headers.index(col_name)  # 查找标题所在的索引
        all_col_value = []
        for row in rows:
            tds = self.find_in_all(self.table_body_row_attr, row)
            el = tds[col_idx]
            text = self._resolve_readable_value(el)
            all_col_value.append(text)
        Log.info(f"[get_all_col_value]  {col_name}: -> {all_col_value}")
        return list(set(all_col_value)) if unique else all_col_value

    # -----------------------------------
    # 【查找行】
    # -----------------------------------
    """ 多条件查找 唯一 行元素 """
    def find_row_by_conditions(self, **conditions) -> WebElement:
        """
        多条件查找行索引
        示例： find_rows(项目状态='进行中', 项目类型='检测')
        :return int 符合条件行索引（找到的第一行）
        """
        headers = self._get_headers_text()
        rows = self._get_rows()

        # 检验字段合法性
        for col_name in conditions.keys():
            if col_name not in headers:
                raise ValueError(f"列名 {col_name} 不存在")

        for idx, row in enumerate(rows):
            tds = self.find_in_all(self.table_body_row_attr, row)
            match = True

            for col_name, expected in conditions.items():
                col_idx = headers.index(col_name)
                a = len(tds)
                Log.info(f'{col_idx}, ......{a}')
                cell_text = self._resolve_readable_value(tds[col_idx]).strip()

                if cell_text != expected:
                    match = False
                    break
            if match:
                Log.info(f"[find_rows] conditions={conditions} -> idxs={idx}")
                return row

        raise LookupError(f"未找到符合条件的行: {conditions}")

    """ 多条件查找 行元素  列表"""
    def find_rows(self, **conditions) -> list:
        """
        多条件查找行索引
        示例： find_rows(项目状态='进行中', 项目类型='检测')
        :return list 符合条件的所有行索引
        """
        headers = self._get_headers_text()
        rows = self._get_rows()

        # 检验字段合法性
        for col_name in conditions.keys():
            if col_name not in headers:
                raise ValueError(f"列名 {col_name} 不存在")

        result_rows = []
        result_idxs = []

        for idx, row in enumerate(rows):
            tds = self.find_in_all(self.table_body_row_attr, row)
            match = True

            for col_name, expected in conditions.items():
                col_idx = headers.index(col_name)
                a = len(tds)
                Log.info(f'{col_idx}, ......{a}')
                cell_text = self._resolve_readable_value(tds[col_idx]).strip()

                if cell_text != expected:
                    match = False
                    break
            if match:
                result_rows.append(row)
                result_idxs.append(idx)
        Log.info(f"[find_rows] conditions={conditions} -> idxs={result_idxs}")
        return result_rows

    # -----------------------------------
    # 以下为【行的操作】
    # -----------------------------------
    """ 行（元素）+ 列（名）得到 指定 cell"""
    def get_cell(self, row: WebElement, col_name: str) -> WebElement:
        """ 通过行， 列（列标题）查找 指定的元素"""
        headers = self._get_headers_text()
        if col_name not in headers:
            raise ValueError(f"列名 {col_name} 不存在")
        col_idx = headers.index(col_name)  # 查找标题所在的索引
        tds = self.find_in_all(self.table_body_row_attr, row)
        return tds[col_idx]

    """ 行（元素）+ 列（名）得到 指定 cell, cell -> 值"""
    def get_cell_value(self, row: WebElement, col_name: str):
        """
        获取单元格的“可读值”
        - 纯文本 → str
        - 多元素 → list[str]
        """
        cell = self.get_cell(row, col_name)
        value = self._resolve_readable_value(cell)
        return value

    """ 获取行的所有列标题数据 """
    def get_row_data(self, row: WebElement) -> dict:
        """ 通过行索引，获取该行所有字段数据"""
        headers = self._get_headers_text()
        tds = self.find_in_all(self.table_body_row_attr, row)
        row_data = {}
        for col_idx, header in enumerate(headers):
            # 防止这一行里 td 数量 < 表头数量 时 索引越界
            if col_idx >= len(tds):
                row_data[header] = None
                continue
            row_data[header] = self._resolve_readable_value(tds[col_idx])

        Log.info(f"[get_row_data] row -> {row_data}")
        return row_data

    def click_in_cell(self, row: WebElement, **conditions):
        """
        在单元格内部执行 点击 操作
        :param **conditions 操作='打开'  or 操作='预览报告'
        """
        for col_name, value in conditions.items():
            cell = self.get_cell(row, col_name)
            el = self._operation_location(cell, value)
            # 确保单元格可见后点击
            self.scroll_to_element(el)
            el = self.click(el)
            return el
