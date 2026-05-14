from common.base_page import BasePage
from common.logger import Log
from common.widgets.base_dialog import BaseDialog
from common.widgets.base_toast import BaseToast
from common.widgets.button import Button
from common.widgets.input import Input
from common.widgets.navbar import NavBar


class ResetPassword(BasePage):

    def __init__(self, driver):
        super().__init__(driver)
        self.nav_bar = NavBar(driver)
        self.window_label = '修改密码'
        self.old_pwd_label = '旧密码'
        self.new_pwd_label = '新密码'
        self.confirm_pwd_label = '确认密码'
        self.btn_confirm = '确 认'
        self.btn_close = '关闭'
        self.btn_cancel = '取 消'

        self.success_tip = '密码修改成功'
        self.tip_locator = ['By.XPATH',
                            "//form//label[contains(text(), '{label}')]/ancestor::div[2]//div[contains(@class, 'explain-error')]"]

        self.img = ['By.XPATH',
                            "//form//label[contains(text(), '{label}')]/ancestor::div[2]//img"]

        self.base_dialog = BaseDialog(driver)  # 弹窗提示通用类
        self.base_toast = BaseToast(driver)  # 弹窗提示通用类

        self.ipt = Input(driver)
        self.bt = Button(driver)

    # =================== 动作 ===================
    def reset_password(self, old, new, confirm):
        """ 重设密码
        :param 旧密码
        :param 新密码
        :param 确认密码
        """
        self.input_old_pwd(old)
        self.input_new_pwd(new)
        self.input_confirm_pwd(confirm)
        self.confirm()

    def reset_and_submit(self, old, new, confirm):
        self.reset_password(old, new, confirm)

    def enter_reset_password(self):
        self.nav_bar.enter(self.window_label)

    def confirm(self):
        self.base_dialog.click_multiple_button('确 认')

    def cancel(self):
        self.base_dialog.click_multiple_button('取 消')

    def close(self):
        self.base_dialog.click_multiple_button('关闭')

    def input_old_pwd(self, old):
        self.ipt.input_text(self.old_pwd_label, old)

    def input_new_pwd(self, new):
        self.ipt.input_text(self.new_pwd_label, new)

    def input_confirm_pwd(self, confirm):
        self.ipt.input_text(self.confirm_pwd_label, confirm)

    # =================== 结果判断 ===================

    def get_error_tip(self, label):
        tip = []
        locator = ["By.XPATH", self.tip_locator[1].replace(f'{{label}}', label)]
        els = self.find_elements(locator, label)
        if els:
            for el in els:
                error_tip = self.get_text(el, label)
                Log.info(f'获取到错误提示：{error_tip}')
                tip.append(error_tip)
            return tip
        else:
            Log.warning(f'未找到获取到错误提示')
            return tip

    def get_old_error_tip(self):
        return self.get_error_tip(self.old_pwd_label)

    def get_new_error_tip(self):
        return self.get_error_tip(self.new_pwd_label)

    def get_confirm_error_tip(self):
        return self.get_error_tip(self.confirm_pwd_label)

    def is_reset_success(self):
        return self.base_toast.wait_toast_appear(self.success_tip)

    def is_coded_message(self, label):
        tip = self.ipt.get_input_attr_value(label, 'type')
        if tip == 'password':
            return True
        elif tip == 'text':
            return False
        else:
            Log.error('属性：{type}错误')
            raise

    def old_pwd_is_coded_message(self):
        return self.is_coded_message(self.old_pwd_label)

    def new_pwd_is_coded_message(self):
        return self.is_coded_message(self.new_pwd_label)

    def confirm_pwd_is_coded_message(self):
        return self.is_coded_message(self.confirm_pwd_label)

    #  =================== UI 控制  ===================
    def show_or_hidden_pwd(self, label):
        """ 根据标签点击 显示/隐藏密码按钮"""
        locator = ["By.XPATH", self.img[1].replace(f'{{label}}', label)]
        self.click(locator)

    def show_or_hidden_old_pwd(self):
        self.show_or_hidden_pwd(self.old_pwd_label)

    def show_or_hidden_new_pwd(self):
        self.show_or_hidden_pwd(self.new_pwd_label)

    def show_or_hidden_confirm_pwd(self):
        self.show_or_hidden_pwd(self.confirm_pwd_label)


