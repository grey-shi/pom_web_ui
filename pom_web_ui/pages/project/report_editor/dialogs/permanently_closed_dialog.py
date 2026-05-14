from common.logger import Log
from common.widgets.base_dialog import BaseDialog


class PermanentlyClosedDialog(BaseDialog):

    def __init__(self, driver):
        super().__init__(driver)

    def permanently_closed(self):
        return self.click_with_log("永久关闭", "永久关闭")
