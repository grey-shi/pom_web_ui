# ⭐ 表单输入基类
from common import all_path
from common.base_page import BasePage
from common.widgets.button import Button
from common.widgets.date_picker import DatePicker
from common.widgets.select import Select
from common.widgets.input import Input
from common.yaml_util import YamlUtil


class BaseForm(BasePage):
    """ 读取列表型数据 + 行/列/单元格的定位与操作 """
    locator_json = YamlUtil.read_yaml(f"{all_path.WIDGETS}\\base_form.yaml")

    def __init__(self, driver):
        super().__init__(driver)
        self.input = Input(driver)
        self.select = Select(driver)
        self.date = DatePicker(driver)
        self.button = Button(driver)

    def input(self, label: str, value: str):
        ...

    def select(self, label: str, value: str):
        """ 通过标签 选择下拉框"""
        self.select.select(label, value)

    def set_date(self, label: str, date: str):
        ...

    def checkbox(self, label: str, checked=True):
        ...

    def submit(self):
        ...

    def reset(self):
        ...

    def get_value(self, label: str):
        ...