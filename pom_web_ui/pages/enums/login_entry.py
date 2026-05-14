# 当你后期有 SSO / 自动跳转时再用
# enums/login_entry.py
from enum import Enum


class LoginEntry(Enum):
    NORMAL = "normal"
    SSO = "sso"
    TOKEN = "token"

