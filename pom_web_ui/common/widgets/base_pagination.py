# ⭐ 分页控件
from common import all_path
from common.base_page import BasePage
from common.logger import Log
from common.yaml_util import YamlUtil


class Pagination(BasePage):
    """
    页码控制类，处理分页相关的操作
    """
    locator_json = YamlUtil.read_yaml(f"{all_path.WIDGETS}\\base_pagination.yaml")

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

        # 分页组件定位器
        self.counts = ['By.XPATH', "//ul/li[contains(@title, '上一页')]/preceding-sibling::li[1]"]
        self.btn_previous_page = ['By.XPATH', "//ul/li[contains(@title, '上一页')]/button"]  # 上一页按钮
        self.appoint_page = ['By.XPATH', "//ul/li[@title={a}]/a"]  # '1'
        self.btn_next_page = ['By.XPATH', "//ul/li[contains(@title, '下一页')]/button"]  # 下一页按钮

        self.btn_current_page = ['By.XPATH',
                           "//ul/li[contains(@title, '下一页')]/ancestor::ul[1]/li[contains(@class, 'active')]/a"]   # 当前页码

        self.listbox_item = ['By.XPATH',
                       "//ul/li[contains(@title, '下一页')]/following-sibling::li[1]//span[@class='custom-ant-select-selection-item']"]
        self.listbox_select = ['By.XPATH',
                         "//div[contains(@class, 'custom-ant-select-dropdown') and not (contains(@pointer-events, 'none'))]//div[@role='option' and @title='{title}']"]

    def next_page(self):
        """翻到下一页"""
        disabled = self.get_attr(self.btn_next_page, 'aria-disabled')
        if not disabled:
            self.click(self.btn_next_page)
            Log.info("翻到下一页")

    def prev_page(self):
        """翻到上一页"""
        disabled = self.get_attr(self.btn_previous_page, 'aria-disabled')
        if not disabled:
            self.click(self.btn_previous_page)
            Log.info("翻到下一页")

    def get_current_page_number(self) -> int:
        """
        获取当前页码
        :return: 当前页码
        """
        el = self.find_element(self.btn_current_page)
        a = self.get_text(el)
        Log.info(f'[get_current_page_number] 当前页码为：{a}')
        return int(a)  # 或者用任何适合你的方法来获取页码

    def get_total_items(self) -> int:
        """
        获取总项数
        :return: 总项数
        """
        total_text = self.get_text(self.counts)
        total_items = int(total_text.split(' ')[1])  # 假设文本格式为 "共 349 项"
        return total_items

    def get_total_pages(self) -> int:
        """
        获取总页数
        :return: 总页数
        """
        total_items = self.get_total_items()
        items_per_page = self.get_items_per_page()  # 每页显示的条数
        return (total_items + items_per_page - 1) // items_per_page  # 向上取整

    def get_items_per_page(self) -> int:
        """
        获取每页显示的条数
        :return: 每页显示的条数
        """
        text = self.get_text(self.listbox_item)  # 假设此元素可以获取显示条数
        return int(text.split(' ')[0])  # 假设文本格式为 "50 条/页"
