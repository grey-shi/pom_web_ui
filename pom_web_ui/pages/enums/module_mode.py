# enums/module_mode.py
from enum import Enum


class ModuleMode(Enum):
    """项目模块模式（权限 / 行为差异）"""

    DIGITAL_READING = "数字阅片"
    GRAPHIC_REPORT = "图文报告"
    REPORT_MANAGEMENT = "报告管理"
