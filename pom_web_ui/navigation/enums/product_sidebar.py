# navigation/entry/sidebar_menu.py
from enum import Enum


class EnumProductSidebar(Enum):
    """产品维护模块 - 左侧菜单"""

    # ===== 账号维护 =====
    DOCTOR_MANAGE = ("账户维护", "医生管理")
    ROLE_MANAGE = ("账户维护", "角色权限管理")

    # ===== 形态学管理 =====
    MORPH_BONE = ("形态学管理", "骨髓")
    MORPH_BLOOD = ("形态学管理", "外周血")
    MORPH_BRAIN = ("形态学管理", "脑脊液")

    # ===== 分类方法参考值 =====
    CLASS_BONE = ("分类方法参考值管理", "骨髓")
    CLASS_BLOOD = ("分类方法参考值管理", "外周血")
    CLASS_BRAIN = ("分类方法参考值管理", "脑脊液")