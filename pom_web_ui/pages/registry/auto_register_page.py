# pages/registry/auto_register_page.py
from pages.enums.page_id import PageId

# 全局注册表
_PAGE_REGISTRY = {}


def register_page(page_id: PageId):
    """装饰器：注册 Page 到全局 PageRegistry"""

    def decorator(cls):
        _PAGE_REGISTRY[page_id] = cls
        return cls

    return decorator


def get_registered_pages():
    """返回注册映射 PageId -> Page Class"""
    return dict(_PAGE_REGISTRY)
