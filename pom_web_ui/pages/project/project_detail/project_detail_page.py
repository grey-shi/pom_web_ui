# 项目详情页面  分布图、采样图、细胞图功能等
from time import sleep
from common import all_path
from common.base_page import BasePage
from common.logger import Log
from common.widgets.base_toast import BaseToast
from common.widgets.button import Button
from common.widgets.input import Input
from common.yaml_util import YamlUtil
from pages.enums.page_id import PageId
from pages.registry.auto_register_page import register_page


@register_page(PageId.PROJECT_DETAIL)
class ProjectDetailPage(BasePage):

    def __init__(self, driver):
        super().__init__(driver)  # 初始化父类属性

        self.bt = Button(driver)

    def switch_report_editor(self):
        self.bt.click_button('填写报告')

