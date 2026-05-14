import time
from selenium.common import TimeoutException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from typing import Tuple, Any
from common.logger import Log

# 建立一个映射字典
BY_MAP = {
    "By.ID": By.ID,
    "By.XPATH": By.XPATH,
    "By.NAME": By.NAME,
    "By.CLASS_NAME": By.CLASS_NAME,
    "By.CSS_SELECTOR": By.CSS_SELECTOR,
    "By.LINK_TEXT": By.LINK_TEXT,
    "By.PARTIAL_LINK_TEXT": By.PARTIAL_LINK_TEXT,
    "By.TAG_NAME": By.TAG_NAME
}


class BasePage(object):

    def __init__(self, driver=None):
        self.driver = driver

    # ---------------- Browser ----------------
    def max_window(self):
        """ 窗口最大化 """
        self.driver.maximize_window()
        Log.info('success 窗口最大化')

    def get(self, url):
        """ 跳转至指定的 url 界面 """
        self.driver.get(url)
        Log.info(f'success 调整界面:{url}')

    def quit(self):
        """ 关闭浏览器 """
        self.driver.quit()
        Log.info('success 关闭浏览器')

    @staticmethod
    def _parse_locator(locator) -> tuple[Any, ...] or WebElement:
        """
        将 ['By.XPATH', 'xxx'] 转为 (By.XPATH, 'xxx')
        """
        if isinstance(locator, tuple) and len(locator) == 2:
            return locator

        if isinstance(locator, list) and len(locator) == 2:
            key = locator[0]
            value = locator[1]
            if key not in BY_MAP:
                raise ValueError(f"定位方式 '{key}' 不在 BY_MAP 中，请检查你的 YAML 或 key 是否写错")
            tuple_locator = tuple([BY_MAP[key], value])
            return tuple_locator

        raise TypeError(f"错误的 locator 格式: {locator}, 应为 ['By.XPATH', 'xxx'] 或 (By.XPATH, 'xxx')")

    # ---------------- Common Find ----------------

    def find_element(self, locator: list or tuple, msg='') -> WebElement:
        """不等待， 找到直接返回，找不到 NoSuchElementException异常"""
        by = self._parse_locator(locator)
        try:
            el = self.driver.find_element(*by)
            return el
        except NoSuchElementException:
            Log.error(f"元素:{msg} 未找到： {locator}")
            raise NoSuchElementException(f"元素:{msg} 未找到： {locator}")

    def find_elements(self, locator: list or tuple, msg='') -> list:
        """ 不等待，找不到返回 []"""
        by = self._parse_locator(locator)
        els = self.driver.find_elements(*by)
        return els

    # ---------------- Wait ----------------

    def wait_element_present(self, locator: list | tuple | WebElement, msg='', timeout=10) -> WebElement:
        """ timeout 内必须出现 1 个，否则抛 TimeoutException"""
        if isinstance(locator, WebElement):
            return locator
        try:
            by = self._parse_locator(locator)
            el = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(by)
            )  # timeout 内必须找到，否则报异常
            Log.info(f'success 元素{msg}： {locator} 已存在')
            return el
        except TimeoutException: # raise 抛出的类型是TimeoutException, 如果不是，不能被调用的函数中的try，可能直接raise
            Log.error(f"timeout 元素{msg}： {locator} 查找超时")
            raise TimeoutException(f"timeout 元素{msg}： {locator} 查找超时")

    def wait_elements_present(self, locator: list | tuple | WebElement, msg='', timeout=10) -> list:
        """ timeout 内至少出现 1 个，返回当前全部已存在的元素;
        否则抛 TimeoutException"""
        try:
            by = self._parse_locator(locator)
            els = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located(by)
            )  # timeout 内你必须至少出现 1 个，否则报异常
            Log.info(f'success 已查找所有元素{msg}： {locator}')
            return els
        except TimeoutException:
            Log.error(f"timeout 查找所有元素超时{msg}: {locator}")
            raise TimeoutException(f"timeout 查找所有元素超时{msg}: {locator}")

    # 等待可见
    def wait_first_visible(self, locator: list | tuple | WebElement, msg='', timeout=10) -> WebElement:
        """ timeout 内 找到 1 个匹配 locator 的元素
        这个元素必须是可见的（可在找到后等待可见），否则抛 TimeoutException
        """
        try:
            if isinstance(locator, WebElement):
                el = WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of(locator)
                )
                Log.info(f"success 元素:{msg} 已可见: {locator}")
                return el
            by = self._parse_locator(locator)
            el = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(by)
            )
            Log.info(f"success 元素:{msg} 已可见: {locator}")
            return el
        except TimeoutException:
            Log.warning(f"timeout 元素:{msg} 不可见: {locator}")
            raise TimeoutException(f"timeout 元素:{msg} 不可见: {locator}")

    def wait_any_visible(self, locator: list | tuple, msg='', timeout=10) -> WebElement:
        """ timeout 内 至少存在 1 个匹配 locator 的元素，且【当前匹配到的所有元素】至少一个是可见的，
        返回可见的元素
        """
        by = self._parse_locator(locator)

        def _cond(driver):
            try:
                els = driver.find_elements(*by)
                for el in els:
                    if el.is_displayed():
                        return el
            except StaleElementReferenceException:
                Log.error(f'el 元素: {msg} 失效： {locator}')
                return False
            return False
        # until()本身就可以传入回环函数，在函数内部调用，until(_cond())的until函数的参数就是结果了不是回环函数了
        try:
            element = WebDriverWait(self.driver, timeout).until(_cond)
            Log.info(f"success 已找到任意一个可见元素：{msg}: {locator}")
            return element
        except TimeoutException:
            Log.error(f"timeout 未找到任意一个可见元素：{msg}: {locator}")
            raise TimeoutException(f"timeout 未找到任意一个可见元素：{msg}: {locator}")

    def wait_all_visible(self, locator: list | tuple, msg='', timeout=10) -> list:
        """ timeout 内 至少存在 1 个匹配 locator 的元素，且【当前匹配到的所有元素】均为可见状态，
        任一元素不可见，或始终为空列表，则抛 TimeoutException；
        适合：表头、固定按钮组、一次性渲染完成的控件
        不适合：列表懒加载、表格逐行渲染、动态 append DOM、loading 过程中元素逐步出现
        """
        try:
            by = self._parse_locator(locator)
            elements = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_all_elements_located(by)
            )
            Log.info(f"success 个数：{len(elements)}元素: {msg} 可见: {locator}")
            return elements
        except TimeoutException:
            Log.warning(f"timeout 元素: {msg} 不可见: {locator}")
            raise TimeoutException(f"timeout 元素: {msg} 不可见: {locator}")

    # ------------------------------------------------------
    # 查找 子元素
    # ------------------------------------------------------
    def find_in(self, locator: list | tuple, parent: WebElement, msg='') -> WebElement:
        """
        在指定父节点中查找元素（用于弹窗、悬浮提示等）
        :param locator 元素位置
        :param parent 父结点元素  不是位置
        :msg parent 父结点元素  不是位置
        """
        text = msg or locator
        try:
            by = self._parse_locator(locator)
            el = parent.find_element(*by)
            Log.info(f'success 在父元素已找到子元素：{text}')
            return el
        except TimeoutException:
            Log.error(f"timeout 在父元素查找子元素超时: {text}")
            raise

    def find_in_all(self, locator, parent: WebElement, msg='') -> list:
        """
        在指定父节点中查找元素（用于弹窗、悬浮提示等）
        :param locator 元素位置
        :param parent 父结点元素  不是位置
        :param msg
        """
        text = msg or locator
        try:
            by = self._parse_locator(locator)
            els = parent.find_elements(*by)  # //td huo  全局查找  .//td  只找当前节点的直接子 td
            Log.info(f'success 在父元素 已经找到 所有子元素： {text}')
            return els
        except TimeoutException:
            Log.error(f"timeout 查找子元素超时: {text}")
            raise

    def wait_any_child_visible(self, parent: WebElement, locator, timeout=10) -> WebElement:
        by = self._parse_locator(locator)

        def _cond(driver):
            try:
                els = parent.find_elements(*by)
                for el in els:
                    if el.is_displayed():
                        return el
            except StaleElementReferenceException:
                Log.error(f'parent 元素失效: {parent}')
                return False
            return False
        element = WebDriverWait(self.driver, timeout).until(_cond)
        return element

    def wait_all_child_visible(self, parent: WebElement, locator, msg='', timeout=10) -> list:
        by = self._parse_locator(locator)

        def _cond(driver):
            try:
                els = parent.find_elements(*by)
                if els and all(el.is_displayed() for el in els):
                    return els
            except StaleElementReferenceException:
                Log.error(f'parent 元素失效: {parent}')
                return False
            return False

        try:
            elements = WebDriverWait(self.driver, timeout).until(_cond)
            a = len(elements)
            Log.info(f"success 已找到元素:{msg}, 个数：{a}个,  {locator}")
            return elements
        except TimeoutException:
            Log.error(f"timeout 等待所有元素：{msg}, 可见超时：{locator}")
            raise TimeoutException(f"timeout 等待所有元素：{msg}, 可见超时：{locator}")

    # 等待元素可点击
    def wait_first_clickable(self, locator: list | tuple | WebElement, msg='', timeout=10) -> WebElement:
        """ 严格等待：
        - locator 只应命中一个逻辑元素
        - 等待 DOM 顺序中的第一个元素可点击
        """
        try:
            if isinstance(locator, WebElement):
                by = locator
            else:
                by = self._parse_locator(locator)
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(by)
            )
            Log.info(f"success 元素: {msg} 可点击: {locator}")
            return element
        except Exception as e:
            Log.warning(f"timeout: {timeout} 元素: {msg} 不可点击: {locator}")
            raise e

    def wait_any_clickable(self, locator: list | tuple | WebElement, msg='', timeout=10) -> WebElement:
        """ 在 timeout 内，等待任意一个匹配 locator 的元素：
        - 可见
        - enabled
        返回第一个满足条件的元素
        """
        by = self._parse_locator(locator)

        def _cond(driver):
            els = driver.find_elements(*by)
            for el in els:
                try:
                    if el.is_displayed() and el.is_enabled():
                        return el
                except StaleElementReferenceException:
                    continue
            return False
        try:
            element = WebDriverWait(self.driver, timeout).until(_cond)
            Log.info(f"success 已找到任意一个可见元素：{msg}: {locator}")
            return element
        except TimeoutException:
            Log.error(f"timeout 未找到任意一个可见元素：{msg}: {locator}")
            raise TimeoutException(f"timeout 未找到任意一个可见元素：{msg}: {locator}")

    # 等待消失
    def wait_invisibility(self, locator: list | tuple | WebElement, msg='', timeout=10, check_interval=0.3) -> WebElement:
        """ 在 timeout 轮询查询 元素是否不可见， 等到元素不可见 """
        try:
            if isinstance(locator, WebElement):
                by = locator
                el = WebDriverWait(self.driver, timeout, poll_frequency=check_interval).until(
                    EC.invisibility_of_element(by)
                )  # 兼容 Selenium 历史版本  invisibility_of_element_located部分可以传入 元素
                Log.info(f"success 元素:{msg} 已消失：{locator}")
                return el

            else:
                by = self._parse_locator(locator)
            el = WebDriverWait(self.driver, timeout, poll_frequency=check_interval).until(
                EC.invisibility_of_element_located(by)
            )
            Log.info(f"success 元素:{msg} 已消失：{locator}")
            return el
        except TimeoutException:
            Log.error(f"timeout 元素:{msg} 未消失: {locator}")
            raise TimeoutException(f"timeout 元素:{msg} 未消失: {locator}")

    def wait_until_not_presence(self, locator: list | tuple, timeout=10):
        by = self._parse_locator(locator)
        Log.info(f"等待元素变化：{by}")
        return WebDriverWait(self.driver, timeout).until_not(
            EC.presence_of_element_located(by)
        )

    def wait_for_element_stale(self, locator: list | tuple | WebElement, timeout=10):
        """ 等待元素被移除或失效 """
        try:
            if isinstance(locator, WebElement):
                by = locator
            else:
                by = self._parse_locator(locator)
            WebDriverWait(self.driver, timeout).until(
                EC.staleness_of(by)  # 等待元素被移除或失效
            )
            Log.info(f"元素 {locator} 已失效")
        except TimeoutException:
            Log.error(f"元素 {locator} timeout 未失效")

    # ---------------- Actions ----------------

    #  点击
    def click(self, locator: list or WebElement, msg=None) -> WebElement:
        """ 点击元素（统一入口）
        - 支持 locator / WebElement
        - 默认等待元素可点击
        - 普通 click 失败时，自动降级 JS click
        """
        text = msg or locator
        try:
            el = self.wait_first_clickable(locator, msg)
        except Exception as e:
            # 直接抛出异常，避免使用强制点击
            Log.error(f"failed 点击失败：{text}, 错误信息：{e}")
            raise Exception(f"元素不可点击，已抛出异常：{text}, 错误：{e}")
        try:
            el.click()
            Log.info(f"success 点击：{text}")
        except:
            Log.warning(f"执行强制点击：{text}")
            self.driver.execute_script("arguments[0].click();", el)
        return el

    # 输入（自动 clear）
    def input(self, locator: list or WebElement, value, msg=None):
        """输入（自动 clear）"""
        try:
            el = self.wait_first_visible(locator, msg)
            el.clear()
            el.send_keys(value)
            Log.info(f"success 输入：{msg}: -> {value}\n{locator}")
        except TimeoutException:
            Log.error(f"timeout 输入：{msg}: -> {value}\n{locator}")
            raise

    def input_dropdown(self, locator: list or WebElement, value, msg=''):
        """输入（不自动 clear）"""
        try:
            el = self.wait_element_present(locator)
            Log.info(f"success 输入：{msg}: -> {value}\n{locator}")
            el.send_keys(value)
        except TimeoutException:
            Log.error(f"timeout 输入：{msg}: -> {value}\n{locator}")
            raise

    # 上传
    def upload(self, locator: list or WebElement, file_path, msg=''):
        """上传文件专用：不能 clear，只能 send_keys"""
        try:
            el = self.wait_element_present(locator)
            el.send_keys(file_path)
            Log.info(f"success 上传文件: {msg} → {file_path}")
        except TimeoutException:
            Log.error(f"timeout 上传文件: {msg} → {file_path}")
            raise

    # 清空
    def clear(self, locator: list or WebElement, msg=''):
        try:
            el = self.wait_any_visible(locator)
            el.clear()
            Log.info(f"success 清空{msg}：{locator}")
        except TimeoutException:
            Log.error(f"timeout 清空{msg} → {locator}")
            raise

    # 获取属性
    def get_attr(self, locator: list or WebElement, attr, msg=''):
        """ 获取指定属性
        param: locator  坐标或元素
        param: attr  获取的属性
        """
        try:
            el = self.wait_element_present(locator)
            v = el.get_attribute(attr)
            Log.info(f"success 获取属性：{msg} | {attr} -> {v}")
            return v
        except TimeoutException:
            Log.error(f"timeout 获取属性：{msg} | {attr}")
            raise

    def get_text(self, locator: list or WebElement, msg=''):
        """ 获取文本属性
        param: locator  坐标或元素
        """
        if isinstance(locator, WebElement):
            el = locator
        else:
            el = self.wait_element_present(locator)
        try:
            v = el.text
            Log.info(f"success 获取 text 属性：{msg} | text -> {v}")
            return v
        except TimeoutException:
            Log.error(f"timeout 获取 text 属性：{msg} | text")
            raise

    def scroll_to_element(self, el: WebElement):
        """
        滚动到指定列的可视区域
        """
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", el)
            Log.info(f"success 滚动到指定列的可视区域")
        except TimeoutException:
            Log.error(f"timeout 滚动到指定列的可视区域")

    # ---------------- Window / iframe ----------------

    def switch_iframe(self, element):
        """建议直接传入 WebElement，可靠性更高"""
        self.driver.switch_to.frame(element)
        Log.info(f"success 切入 iframe")

    def switch_default(self):
        self.driver.switch_to.default_content()
        Log.info("success 切回主文档")

    def switch_window(self, index=-1):
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[index])
        Log.info(f"success 切换窗口：{index}")

    # ---------------- Screenshot ----------------

    def screenshot(self, name=''):
        file = f"screenshot/{name}_{int(time.time())}.png"
        self.driver.save_screenshot(file)
        Log.info(f"success 已截图：{file}")
        return file


class DriverFactory:
    @staticmethod
    def get_driver(browser='chrome'):
        """ 选择浏览器驱动 """
        if "chrome" == browser.lower():
            return webdriver.Chrome()
        elif "edge" == browser.lower():
            return webdriver.Edge()
        elif "firefox" == browser.lower():
            return webdriver.Firefox()
        else:
            raise ValueError("不支持的浏览器")
