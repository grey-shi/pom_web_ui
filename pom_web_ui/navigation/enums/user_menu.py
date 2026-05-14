# navigation/entry/user_menu.py
from enum import Enum


class EnumUserMenu(Enum):
    SIGNATURE = "签名设置"
    UPDATE_PASSWORD = "修改密码"
    LANGUAGE = "语言切换"
    ABOUT = "关于我们"
    LOGOUT = "退出登录"
