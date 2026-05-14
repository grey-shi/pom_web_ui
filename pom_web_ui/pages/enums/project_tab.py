# enums/project_tab.py
from enum import Enum


class ProjectTab(Enum):
    """项目列表页 Tab 状态"""

    MY_TODO = "我的待办"
    ALL = "全部待办"
    RECYCLE = "回收站"