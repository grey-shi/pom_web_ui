# navigation/navigator.py
from common import all_path
from common.widgets.navbar import NavBar
from common.widgets.sidebar import SideBar
from common.yaml_util import YamlUtil

from navigation.enums.top_module import EnumTopModule
from navigation.enums.product_sidebar import EnumProductSidebar
from navigation.enums.user_menu import EnumUserMenu

from pages.enums.page_id import PageId


class Navigator:
    """
    Navigator（导航器）
    - 只负责路径
    - 返回 PageId，而不 new Page
    """

    def __init__(self, driver):
        self.driver = driver
        self.navbar = NavBar(driver)
        self.sidebar = SideBar(driver)

    def enter_top_module(self, module: EnumTopModule):
        """ 根据模块定义的 enter_type 进入模块
        :param module 枚举
        """
        if module.enter_type == "hover_click":
            self.navbar.enter_settings(module.name)

        elif module.enter_type == "click":
            self.navbar.enter_tab(module.name)

        else:
            raise ValueError(f"未知的模块进入方式: {module.enter_type}")

    # =================  模块入口 ========================

    def goto_module_product_maintenance(self):
        """ 进入系统维护模块 """
        self.enter_top_module(EnumTopModule.PRODUCT_MAINTENANCE)  # 传入枚举

    def goto_module_digital_reading(self):
        """ 进入数字阅片模块 """
        self.enter_top_module(EnumTopModule.DIGITAL_READING)  # 传入枚举
        return PageId.PROJECT_LIST

    def goto_module_graphic_report(self):
        """ 进入图文报告模块 """
        self.enter_top_module(EnumTopModule.GRAPHIC_REPORT)  # 传入枚举
        return PageId.PROJECT_LIST

    def goto_module_report_management(self):
        """ 进入图文报告模块 """
        self.enter_top_module(EnumTopModule.REPORT_MANAGEMENT)  # 传入枚举
        return PageId.PROJECT_LIST

    # =================  系统维护模块中的页面 ========================

    def goto_doctor_manage(self):
        """进入医生管理页"""
        self.goto_module_product_maintenance()
        self.sidebar.open_path(EnumProductSidebar.DOCTOR_MANAGE.value)  # .value 才是元组("账号维护", "医生管理")
        return PageId.DOCTOR_MANAGE

    def goto_role_manage(self):
        """进入角色管理页"""
        self.goto_module_product_maintenance()
        self.sidebar.open_path(EnumProductSidebar.ROLE_MANAGE.value)  # 传入枚举值
        return PageId.ROLE_MANAGE  # 如果 PageId 中有角色管理

    # =================  菜单页面 ========================
    def update_password(self):
        self.navbar.enter_tab(EnumUserMenu.UPDATE_PASSWORD.value)  # 传入枚举值
        return PageId.RESET_PASSWORD  # 对应的 PageId

    def signature(self):
        self.navbar.enter_tab(EnumUserMenu.SIGNATURE.value)  # 传入枚举值
        return PageId.SIGNATURE

    def language(self):
        self.navbar.enter_tab(EnumUserMenu.LANGUAGE.value)
        return PageId.LANGUAGE

    # =================  项目的页面 ========================
    def goto_project_list(self):
        """ 进入列表管理页
        :return 返回页面枚举
        """
        return PageId.PROJECT_LIST

    def goto_project_detail(self):
        """ 进入项目详情页
        :return 返回页面枚举
        """
        return PageId.PROJECT_DETAIL

    def goto_report_editor(self):
        """ 进入报告编辑页
        :return 返回页面枚举
        """
        return PageId.REPORT_EDITOR

    # =================  系统入口 ========================
    def goto_login(self):
        """进入登录页（系统入口）
        :return 返回页面枚举
        """
        return PageId.LOGIN

