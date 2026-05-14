from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 基础目录
COMMON_DIR = BASE_DIR / 'common'
CONFIG_DIR = BASE_DIR / 'config'
KEYWORDS_DIR = BASE_DIR / 'keywords'
LOGS_DIR = BASE_DIR / 'logs'
PAGES_DIR = BASE_DIR / 'pages'
RESOURCES_DIR = BASE_DIR / 'resources'
SCREENSHOT_DIR = BASE_DIR / 'screenshot'
TEST_CASE_DIR = BASE_DIR / 'test_case'

# 元素定位（主目录）
LOCATORS_DIR = RESOURCES_DIR / 'locators'

# 页面路径
# 通用类路径
WIDGETS = LOCATORS_DIR / 'widgets'

# 主页面
HOME_PAGE = LOCATORS_DIR / 'homepage'

COMPONENTS_PAGE = LOCATORS_DIR / 'components'   # 组件
REVIEW_PAGE = LOCATORS_DIR / 'project'  # 项目审核

# 填写报告
FILL_REPORT_PAGE = LOCATORS_DIR / 'fill_report'
FILL_REPORT_DIALOGS_PAGE = FILL_REPORT_PAGE / "dialogs"

SYSTEM_MANAGEMENT_PAGE = LOCATORS_DIR / 'system_management'  # 系统设置
