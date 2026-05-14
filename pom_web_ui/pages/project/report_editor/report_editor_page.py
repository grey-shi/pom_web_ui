from common.base_page import BasePage
from common.logger import Log
from common.widgets.base_dialog import BaseDialog
from common.widgets.button import Button
from common.widgets.date_picker import DatePicker
from common.widgets.input import Input
from common.widgets.select import Select
from common.widgets.base_toast import BaseToast

from pages.enums.page_id import PageId
from pages.project.report_editor.dialogs.common_dialog import CommonDialog
from pages.project.report_editor.dialogs.permanently_closed_dialog import PermanentlyClosedDialog
from pages.project.report_editor.dialogs.synchronization_dialog import SynchronizationDialog
from pages.registry.auto_register_page import register_page


@register_page(PageId.REPORT_EDITOR)
class ReportEditorPage(BasePage):

    # ===== 页面内私有 label 常量 =====
    _IPT_BONE_ANALYSIS = '髓象分析'
    _IPT_BLOOD_ANALYSIS = '血象分析'
    _IPT_OPINION = '诊断意见'
    _IPT_UPLOAD_PIC = '图片上传'

    _SEL_EXAMINING_DOCTOR = '检验医师'
    _SEL_REVIEWING_DOCTOR = '审核医师'

    _PICKER_REVIEWING_TIME = '审核时间'
    _PICKER_REPORTING_TIME = '报告时间'

    _BTN_SAVE = '保存'
    _BTN_SUBMIT = '提交'
    _BTN_HISTORICAL_REPORT = '历史报告'
    _BTN_PREVIEW = '预览'
    _BTN_RELEASE_REPORT = '发布报告'

    def __init__(self, driver):
        super().__init__(driver)
        self.dialog = BaseDialog(driver)
        self.toast = BaseToast(driver)
        self.drop_down = Select(driver)

        self.ipt = Input(driver)
        self.bt = Button(driver)
        self.sel = Select(driver)
        self.picker = DatePicker(driver)

    # ================= 输入框输入 =======================

    def input_bone_analysis(self, text: str):
        """ 输入髓象分析 """
        self.ipt.input_text(self._IPT_BONE_ANALYSIS, text)

    def input_blood_analysis(self, text: str):
        """ 输入血象分析 """
        self.ipt.input_text(self._IPT_BLOOD_ANALYSIS, text)

    def input_opinion(self, text: str):
        """ 输入意见 """
        self.ipt.input_text(self._IPT_OPINION, text)

    def upload_picture(self, path):
        """ 本地上传图片 """
        self.ipt.input_text(self._IPT_UPLOAD_PIC, path)

    # ================= 下拉框选择 =======================
    def select_examining_doctor(self, value: str):
        """ 选择检验医生 """
        self.sel.select(self._SEL_EXAMINING_DOCTOR, value)

    def select_reviewing_doctor(self, value: str):
        """ 选择审核医生 """
        self.sel.select(self._SEL_REVIEWING_DOCTOR, value)

    # ================= 时间控件选择 =======================
    def select_reviewing_time(self, date):
        """ 选择审核时间 """
        self.picker.select_date(self._PICKER_REVIEWING_TIME, date)

    def select_reporting_time(self, date):
        """ 选择报告时间 """
        self.sel.select(self._PICKER_REPORTING_TIME, date)

    # ================= 按钮点击 =======================

    def save_report(self):
        """ 保存报告 """
        self.bt.click_button(self._BTN_SAVE)

    def open_submit_dialog(self):
        """ 打开 提交报告 弹窗 """
        self.bt.click_button(self._BTN_SUBMIT)
        Log.info(f'点击提交报告，进入 [提交] 弹窗')
        return CommonDialog(self.driver)

    def open_permanently_closed_dialog(self):
        """ 打开 永久关闭 弹窗 """
        return PermanentlyClosedDialog(self.driver)

    def open_synchronization_dialog(self):
        """ 打开 同步 弹窗 """
        return SynchronizationDialog(self.driver)

    # ================= 悬浮提示 =======================
    def toast_submission_success(self):
        """ 等待 提交成功 提示出现并消失"""
        return self.toast.wait_toast_and_disappear('提交成功')
