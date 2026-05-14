from common.widgets.base_dialog import BaseDialog


class CommonDialog(BaseDialog):

    def __init__(self, driver):
        super().__init__(driver)

    def confirm(self):
        return self.click_with_log("确 定")

    def cancel(self):
        return self.click_with_log("取 消")