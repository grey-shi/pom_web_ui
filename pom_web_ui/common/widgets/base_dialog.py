from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from common.base_page import BasePage
from common.logger import Log
from selenium.common.exceptions import TimeoutException
from common.widgets.button import Button


class BaseDialog(BasePage):
    """通用弹窗基类：用于 ElementUI / AntD / 统一弹窗结构"""

    # 公共定位信息（类级只读，不会污染实例）
    def __init__(self, driver):
        super().__init__(driver)

        # 定义弹窗定位信息
        self.all_dialog_locator = [
            "//div[@role='dialog']/ancestor::div[1]"  # Custom dialog
        ]

        self.button = Button(driver)
        self.title = None  # 弹窗的标题
        self.dialogs_info = []
        self.dialog_top = ''

    def _wait_any_dialog_present(self, timeout=3):
        """
        在 timeout 内，等待任意一个按钮候选进入 DOM
        作为页面已渲染按钮区域的信号
        """
        by_list = []
        for xpath in self.all_dialog_locator:
            by_list.append(self._parse_locator(['By.XPATH', xpath]))

        def _cond(driver):
            for by in by_list:
                if driver.find_elements(*by):
                    return True
            return False

        try:
            WebDriverWait(self.driver, timeout).until(_cond)
            Log.info(f"success 一个 弹窗 候选进入 DOM")
        except TimeoutException:
            Log.error(f"timeout DOM不存在 弹窗 元素")
            raise TimeoutException(f"timeout DOM不存在 弹窗 元素")

    def _find_dialogs(self) -> list[WebElement]:
        """
        返回所有匹配的按钮候选元素
        不判断可见性、不判断可点击
        """
        dialogs = []
        for xpath in self.all_dialog_locator:
            locator = ['By.XPATH', xpath]
            els = self.find_elements(locator)  # 立刻查
            dialogs.extend(els)

        if not dialogs:
            Log.warning(f'未找到任何 弹窗 候选')
        else:
            Log.info(f'找到 {len(dialogs)} 个 弹窗 候选')
        return dialogs

    def _get_visible_dialogs_z_index(self):
        """ 获取可见弹窗的 z_index, 并更具z_index将弹窗 从最上层到最底层排序 """
        self._wait_any_dialog_present()
        dialogs = self._find_dialogs()
        dialogs_info = []  # 初始化弹窗
        try:
            for dl in dialogs:
                if dl.is_displayed():
                    z = dl.value_of_css_property("z-index")  # value_of_css_property才能拿到真实渲染后的值（包括继承和计算结果）
                    z = int(z) if z.isdigit() else 0
                    dialogs_info.append((dl, z))  # [(dl, 1000), (dl, 2000)]
                    # 按照 z-index 排序，最大值为最上层弹窗
                    # 根据列表中元组的第2个数值进行排序 从大到小  [(el, 2000), (el, 1000)]
                    dialogs_info.sort(key=lambda x: x[1], reverse=True)
                    self.dialogs_info = dialogs_info
                    a = len(self.dialogs_info)
                    Log.info(f"[_get_visible_dialogs_z_index] 获取到弹窗数量：{a}, 弹窗：{self.dialogs_info}")
                    return
        except:
            Log.error(f'获取可见弹窗的 z_index 失败')

    def get_top_dialog(self):
        """ 获取最上层的弹窗 """
        self._get_visible_dialogs_z_index()
        if not self.dialogs_info:
            Log.error("[get_top_dialog] 没有弹窗可用！")
            return None
        # 返回最上层弹窗
        self.dialog_top = self.dialogs_info[0][0]
        return self.dialogs_info[0][0]

    def _get_second_dialog(self):
        """ 获取第二层的弹窗 """
        self._get_visible_dialogs_z_index()
        if len(self.dialogs_info) > 1:
            return self.dialogs_info[1][0]
        return None

    def wait_dialog_invisibility(self, el, timeout=10):
        """ 等待弹窗消失 """
        try:
            self.wait_invisibility(el, timeout)
            Log.info(f"[wait_dialog_invisibility] 弹窗已消失")
        except TimeoutException:
            Log.error(f"[wait_dialog_invisibility] 弹窗消失超时")
            raise TimeoutException(f"[wait_dialog_invisibility] 弹窗消失超时")

    def click_multiple_button(self, button_text):
        """ 在最上层弹窗中点击按钮 """
        top_dialog = self.get_top_dialog()
        if not top_dialog:
            Log.warning("[click_button] 当前无弹窗")
            return None

        try:
            self.button.click_button(button_text, top_dialog)
            Log.info(f"[click_button] 点击按钮：{button_text}")
            return True
        except:
            Log.warning(f"[click_button] 最顶层弹窗未找到按钮: {button_text}")
            return False

    def click_with_log(self, button_text, dialog_name=None):
        """ 在最顶层弹窗中点击指定按钮，并根据结果统一输出日志。
        该方法允许“弹窗不存在”的情况，适用于非强制弹窗场景。
        使用场景：
        - 同步 / 确认 / 关闭 等“可能出现、也可能不出现”的弹窗
        - 用例中不希望因弹窗缺失而中断流程
        :param button_text: 按钮显示文本，用于实际点击定位
        :param dialog_name: 弹窗或按钮的业务名称（用于日志展示），
                            为空时默认使用 button_text
        :return: True / False / None，表示点击结果 """
        result = self.click_multiple_button(button_text)
        name = dialog_name or button_text

        if result is True:
            Log.info(f"点击 [{name}] 按钮成功")
        elif result is False:
            Log.error(f"弹窗存在，但按钮 [{name}] 不存在")
        else:
            Log.info(f"当前无 [{name}] 弹窗，跳过")
        return result
