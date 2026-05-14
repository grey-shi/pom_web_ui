# ⭐ 左侧菜单栏基类
from selenium.webdriver.support.wait import WebDriverWait
from common.base_page import BasePage
from common.logger import Log


class SideBar(BasePage):
    """
    左侧菜单栏基类
    负责：
    - 菜单点击
    - 菜单展开状态判断
    - 按路径打开多级菜单

    设计原则：
    - 使用 aria-expanded 判断真实展开状态
    - 避免重复点击导致菜单收起
    - 上层只关心“打开到哪里”，不关心点击细节
    """

    # 菜单按钮（可点击的文本节点）
    MENU_BUTTON = ['By.XPATH', "//span[contains(text(), '{label}')]"]
    # 菜单容器（通常带有 aria-expanded）
    MENU_CONTAINER = ['By.XPATH', "//span[contains(text(), '{label}')]/ancestor::div[1]"]

    def __init__(self, driver):
        super().__init__(driver)

    def _menu_locator(self, label):
        """
        获取菜单按钮定位
        :param label: 菜单文本
        """
        return ['By.XPATH', self.MENU_BUTTON[1].replace('{label}', label)]

    def _menu_container(self, label):
        """
        获取菜单容器定位（用于判断展开状态）
        :param label: 菜单文本
        """
        return ['By.XPATH', self.MENU_CONTAINER[1].replace('{label}', label)]

    def _click_menu(self, label):
        """
        点击菜单（不关心是否展开）
        :param label: 菜单文本
        """
        self.click(self._menu_locator(label), label)

    def _open_leaf_menu(self, label):
        """
        点击叶子菜单（最终菜单）
        通常会触发页面跳转或内容区刷新
        """
        self._click_menu(label)

    def _get_expand_state(self, label):
        """
        返回菜单展开状态
        :return:
            True  -> 已展开
            False -> 可展开但未展开
            None  -> 不可展开（叶子菜单）
        """
        try:
            value = self.get_attr(self._menu_container(label), 'aria-expanded', label)
            return value == 'true'
        except Exception:
            Log.error(f'error 无法获取到属性：{label} -> aria-expanded')
            return None

    def _expand_menu(self, label, timeout=10):
        """
        保证菜单处于 “展开” 状态
        - 如果菜单不可展开，直接跳过
        - 如果已展开，不重复点击
        """
        state = self._get_expand_state(label)
        # 叶子菜单，直接跳过
        if state is None:
            return

        # 已展开，不重复点击
        if state is True:
            return

        # 可展开但未展开
        self._click_menu(label)
        WebDriverWait(self.driver, timeout).until(
            lambda driver: self._get_expand_state(label) is True,
            message=f"侧边栏菜单未展开: {label}"
        )

    # ======================= 外部主要调用函数 =========================

    def open_path(self, menus: tuple):
        """
        按菜单路径依次打开
        示例：
            open_path("账号管理", "医生管理")

        行为说明：
        - 中间层级：保证展开
        - 最后一层：直接点击
        """
        for menu in menus[:-1]:
            self._expand_menu(menu)  # 展开侧边栏，如点击账号管理
            Log.info(f"打开菜单路径: {' > '.join(menus)}")
        self._open_leaf_menu(menus[-1])  # 进入界面，如 医生管理
        Log.info(f'进入【{menus[-1]}】界面')
