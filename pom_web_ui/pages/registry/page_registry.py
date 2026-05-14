# pages/registry/page_registry.py
from common.logger import Log
from pages.enums.page_id import PageId
from pages.others.login_page import LoginPage

from pages.project.project_detail.project_detail_page import ProjectDetailPage
from pages.project.project_list.project_list_page import ProjectListPage
from pages.project.report_editor.report_editor_page import ReportEditorPage

from pages.product_maintenance.doctor_manage_page import DoctorManagePage

# ===== 各具体 Page 实现 =====
# PageRegistry 是唯一允许 import Page 的地方
# 其他任何模块（Navigator / Test / Component）都不应直接 import Page
from pages.registry.auto_register_page import get_registered_pages


class PageRegistry:
    """
    页面注册中心
    设计目的：
    1. 统一管理所有 Page 的创建与生命周期
    2. 保证 Page 实例的唯一性（同一 driver 下单例）
    3. 解耦 Navigator / Test 与具体 Page 实现

    核心原则：
    - Page 只能在这里被 new
    - 外部只能通过 PageId 获取 Page
    - 不允许在 Navigator / Test 中直接 import Page

    使用方式：
    >>> registry = PageRegistry(driver)
    >>> login_page = registry.get(PageId.LOGIN)
    >>> login_page.login() or registry.LoginPage.login() # IDE会自动提示
    """
    def __init__(self, driver):
        self.driver = driver
        self._pages = {}  # PageId -> Page 实例缓存
        self._page_classes = get_registered_pages()  # PageId -> Page 类

    def get(self, page_id: PageId):
        """获取 Page 实例（懒加载 + 缓存）"""
        if page_id not in self._page_classes:
            Log.error(f"未注册的 PageId: {page_id}")
            raise ValueError(f"未注册的 PageId: {page_id}")

        if page_id not in self._pages:
            # 根据 page_id 获取 页面 实例
            cls = self._page_classes[page_id]
            self._pages[page_id] = cls(self.driver)
        return self._pages[page_id]

    # ✅ 可选：提供属性访问，IDE 能提示
    @property
    def LoginPage(self) -> LoginPage:
        return self.get(PageId.LOGIN)

    # ======================= 项目相关页面 ========================

    @property
    def ProjectListPage(self) -> ProjectListPage:
        return self.get(PageId.PROJECT_LIST)

    @property
    def ProjectDetailPage(self) -> ProjectDetailPage:
        return self.get(PageId.PROJECT_DETAIL)

    @property
    def ReportEditorPage(self) -> ReportEditorPage:
        return self.get(PageId.REPORT_EDITOR)

    # ======================= 系统维护模块 ========================
    @property
    def DoctorManagePage(self) -> DoctorManagePage:
        return self.get(PageId.DOCTOR_MANAGE)

