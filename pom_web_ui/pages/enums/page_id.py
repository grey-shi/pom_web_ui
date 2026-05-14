# enums/page_id.py
from enum import Enum


class PageId(Enum):
    """页面语义标识（用于 PageRegistry）"""

    # ===== 系统入口 =====
    LOGIN = "login_page"
    RESET_PASSWORD = "reset_password_page"

    # ===== 项目模块 =====
    PROJECT_LIST = "project_list_page"
    PROJECT_DETAIL = "project_detail_page"
    REPORT_EDITOR = "report_editor_page"

    # ===== 产品维护模块 =====
    DOCTOR_MANAGE = "doctor_manage_page"
    ROLE_MANAGE = "role_manage_page"
    MORPH_BONE = "morph_bone_page"
    MORPH_BLOOD = "morph_blood_page"
    MORPH_BRAIN = "morph_brain_page"
    CLASS_BONE = "class_bone_page"
    CLASS_BLOOD = "class_blood_page"
    CLASS_BRAIN = "class_brain_page"

    # ===== 用户菜单相关 =====
    SIGNATURE = "signature_page"
    LANGUAGE = "language_page"
    ABOUT = "about_page"

    # ===== 报告管理模块 =====
    REPORT_MANAGEMENT = "report_management_page"
