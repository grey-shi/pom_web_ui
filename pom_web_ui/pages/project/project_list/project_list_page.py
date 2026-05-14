from common.base_page import BasePage
from common.logger import Log
from common.widgets.base_dialog import BaseDialog
from common.widgets.base_table import BaseTable
from common.widgets.base_toast import BaseToast
from common.widgets.button import Button
from common.widgets.input import Input
from pages.enums.page_id import PageId
from pages.enums.project_tab import ProjectTab
from pages.enums.page_id import PageId
from pages.registry.auto_register_page import register_page


@register_page(PageId.PROJECT_LIST)
class ProjectListPage(BasePage):

    def __init__(self, driver):
        super().__init__(driver)
        self.btn_open = '打开'
        self.btn_remove = '移除'
        self.btn_preview_report = '预览报告'
        self.btn_release = '发布'

        self.base_dialog = BaseDialog(driver)  # 弹窗提示通用类
        self.base_toast = BaseToast(driver)  # 弹窗提示通用类
        self.table = BaseTable(driver)

        self.ipt = Input(driver)
        self.bt = Button(driver)

    # =================== 切换标签 ===================

    def goto_tab_all(self):
        self.bt.click_button(ProjectTab.ALL.value)
        return ProjectTab.ALL

    def goto_tab_my(self):
        self.bt.click_button(ProjectTab.MY_TODO.value)
        return ProjectTab.MY_TODO

    def goto_tab_recycle(self):
        self.bt.click_button(ProjectTab.RECYCLE.value)
        return ProjectTab.RECYCLE

    # =================== 获取 列表行 元素 ===================

    def get_bone_first_row(self):
        return self.table.find_row_by_conditions(项目类型='骨髓', 项目状态='待查看')

    def get_blood_first_row(self):
        return self.table.find_row_by_conditions(项目类型='外周血', 项目状态='待查看')

    def get_brain_first_row(self):
        return self.table.find_row_by_conditions(项目类型='脑脊液', 项目状态='待查看')

    # =================== 执行动作 ===================
    def open(self, el):
        self.table.click_in_cell(el, 操作='打开')

    def remove(self, el):
        self.table.click_in_cell(el, 操作='移除')

    def preview_report(self, el):
        self.table.click_in_cell(el, 操作='移除')

    def release(self, el):
        self.table.click_in_cell(el, 发布='发布')
    # =================== 结果判断 ===================
    #  =================== UI 控制  ===================
