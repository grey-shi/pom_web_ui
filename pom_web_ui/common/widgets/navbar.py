from selenium.webdriver import ActionChains
from common.base_page import BasePage
from common.widgets.button import Button


class NavBar(BasePage):
    """ 封装顶部导航栏（含下拉） """
    locator_sys_mgt = ['By.XPATH', "//div/img[contains(@alt, '用户名')]//following-sibling::div[1]"]

    def __init__(self, driver):
        super().__init__(driver)  # 初始化父类属性

    def expand(self):
        el = self.wait_any_visible(self.locator_sys_mgt)
        ActionChains(self.driver).move_to_element(el).perform()

    def enter_settings(self, label):
        self.expand()
        bt = Button(self.driver)
        bt.click_button(label)

    def enter_tab(self, label):
        bt = Button(self.driver)
        bt.click_button(label)
