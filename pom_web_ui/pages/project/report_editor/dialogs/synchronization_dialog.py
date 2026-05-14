from common.logger import Log
from common.widgets.base_dialog import BaseDialog


class SynchronizationDialog(BaseDialog):

    def __init__(self, driver):
        super().__init__(driver)

    def synchronization(self):
        return self.click_with_log("同 步", "同步")
