# navigation/entry/top_module.py
from enum import Enum


class EnumTopModule(Enum):
    """顶部主模块"""

    PRODUCT_MAINTENANCE = {
        "name": "产品维护模块",
        "enter": "hover_click",
    }

    DIGITAL_READING = {
        "name": "数字阅片",
        "enter": "click",
    }

    GRAPHIC_REPORT = {
        "name": "图文报告",
        "enter": "click",
    }

    REPORT_MANAGEMENT = {
        "name": "报告管理",
        "enter": "click",
    }

    @property
    def name(self):
        return self.value["name"]

    @property
    def enter_type(self):
        return self.value["enter"]