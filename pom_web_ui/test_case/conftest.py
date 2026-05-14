import time, os, json, shutil, chardet, socket
import traceback

import pytest, win32gui, win32con
import requests
import allure
import pyautogui
from configparser import ConfigParser
from pathlib import Path
from common import all_path
from common.logger import Log
from common.yaml_util import YamlUtil

SCREENSHOT_DIR = all_path.SCREENSHOT_DIR
CONFIG_ENV = YamlUtil.read_yaml(f"{all_path.CONFIG_DIR}\\env.yaml")

"""+++++++++++++++++++++++++++++++++++++++++++++++用于设置所有对接功能登录采集端前置/后置+++++++++++++++++++++++++++++++++++++++++++++++++++++"""


"""+++++++++++++++++++++++++++++++++++++++++++++++用于设置所有对接功能登录采集端前置/后置+++++++++++++++++++++++++++++++++++++++++++++++++++++"""


"""***************************************************************module****************************************************************"""
# module在一个模块(也就是一个py文件)中最后一个测试用例结束时销毁!
# @pytest.fixture(scope="module", autouse=True)
# def 前置条件():
#     关闭程序()
#     ChangeSystemConfigFile().清理system文件()
#     ChangeConfigFIle().删除LibUrlCfg文件()
#     ChangeConfigFIle().修改4个端的ServerIP和UrlConfig文件()
#     yield
#     关闭程序()

"""***************************************************************session****************************************************************"""
# @pytest.fixture(scope="session", autouse=True)
# def 前置条件():
#     关闭程序()
#     ChangeConfigFIle().导入服务器IP配置()
#     ChangeConfigFIle().导入标准对接库文件()
#     ChangeConfigFIle().导入urlconfig文件()
#     ChangeConfigFIle().导入libMorphogoServerIP文件()
#     ChangeSystemConfigFile().清理system文件()
#     # 可更换对接地址
#     LanAction().添加默认4个端登录医生(A01_ip, g_password)
#     LanAction().添加json文件默认机器码(A01_ip, g_password)
#     yield
#     关闭程序()
"""***************************************************************结果统计模块****************************************************************"""


class CaseCountName:
    ERROR: str = "error_count"
    FAILED: str = "failed_count"
    PASSED: str = "passed_count"
    SKIP: str = "skip_count"
    TOTAL: str = "total_count"


class CaseCount:
    """
    cache_dict 缓存统计用例执行情况
    """

    def __init__(self):
        self.cache_dict = dict()  # redis主机地址可以写死在这里，也可以从配置类中获取
        self.cache_dict[CaseCountName.TOTAL] = 0
        self.cache_dict[CaseCountName.SKIP] = 0
        self.cache_dict[CaseCountName.PASSED] = 0
        self.cache_dict[CaseCountName.FAILED] = 0
        self.cache_dict[CaseCountName.ERROR] = 0

    def failed_count(self):
        """失败用例数"""
        return self.cache_dict[CaseCountName.FAILED]

    def passed_count(self):
        """通过用例总数"""
        return self.cache_dict[CaseCountName.PASSED]

    def skip_count(self):
        """跳过用例数"""
        return self.cache_dict[CaseCountName.SKIP]

    def error_count(self):
        """报错用例数"""
        return self.cache_dict[CaseCountName.ERROR]

    def total_count(self):
        """用例总数"""
        return self.cache_dict[CaseCountName.TOTAL]

    def incr(self, key):
        self.cache_dict[key] = self.cache_dict[key] + 1

    def pass_rate(self):
        """用例成功率"""
        try:
            rate = round((self.passed_count() + self.skip_count()) / self.total_count() * 100, 2)
            return rate
        except ZeroDivisionError:
            raise Exception("执行失败，未检测到用例执行数量")


class EnterpriseWechatNotification:
    def __init__(self):
        # 企业微信群机器人的hook地址，一个机器人就一个，多个就定义多个，可以写死，也可以写在配置类中
        self.hook_url_list = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=58c49916-bb19-4d0e-ac6f-6fb47f283f65"
        # allure生成报告的地址，Jenkins执行时会用到，Windows暂未配置allure地址
        self.header = {'Content-Type': 'application/json'}

    def send_msg(self, result=''):
        """发送企业微信消息通知"""
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": result
            }
        }
        requests.post(url=self.hook_url_list, headers=self.header, data=json.dumps(payload))


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # 连接到Google的DNS服务器，也可以选择其他公共DNS服务器
        ip = s.getsockname()[0]
        s.close()
        Log.info(ip)
        return ip
    except Exception as e:
        Log.error(f"获取本地IP地址时出错: {e}")
        return None


def log_exception_detail(item, call):
    excinfo = call.excinfo
    if not excinfo:
        return

    Log.error("======== 用例执行失败 ========")
    Log.error(f"用例节点: {item.nodeid}")
    Log.error(f"异常类型: {excinfo.type.__name__}")
    Log.error(f"异常信息: {excinfo.value}")

    # pytest traceback（结构化）
    Log.error("-------- Pytest Traceback --------")
    for entry in excinfo.traceback:
        Log.error(
            f"文件: {entry.path}, 行号: {entry.lineno}, 函数: {entry.name}"
        )

    # Python 原生 traceback（完整）
    etype, evalue, tb = excinfo._excinfo
    Log.error("-------- 原生 Python Traceback --------")
    Log.error("".join(traceback.format_exception(etype, evalue, tb)))

    # chained exception
    cause = excinfo.value.__cause__
    if cause:
        Log.error("-------- 原始异常 cause --------")
        Log.error(f"{type(cause).__name__}: {cause}")

    # Selenium 专属
    if hasattr(excinfo.value, "stacktrace") and excinfo.value.stacktrace:
        Log.error("-------- Selenium stacktrace --------")
        Log.error(excinfo.value.stacktrace)

    Log.error("================================")


global_case_count = CaseCount()
global_screenshot_count = 0


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """ 执行失败时增加截图附件 """
    global global_screenshot_count
    global global_case_count
    outcome = yield
    report = outcome.get_result()

    # ---------- 统计 ----------
    if report.when == 'setup':
        global_case_count.incr(CaseCountName.TOTAL)
        if report.outcome == 'skipped':
            global_case_count.incr(CaseCountName.SKIP)
        elif report.outcome == 'failed':
            global_case_count.incr(CaseCountName.ERROR)

    if report.when == 'call':
        # print(f"用例id：{report.nodeid}")
        # print(f"用例描述：{str(item.function.__doc__)}")
        # print(f"运行结果：{report.outcome}")
        """将用例执行结果写入缓存"""
        if report.outcome == 'passed':
            global_case_count.incr(CaseCountName.PASSED)
        elif report.outcome == 'failed':
            global_case_count.incr(CaseCountName.FAILED)

    # ---------- 失败处理 ----------
    if report.failed:
        # 打印异常详情
        if call.excinfo:
            log_exception_detail(item, call)

        # 截图
        try:
            os.makedirs(SCREENSHOT_DIR, exist_ok=True)
            global_screenshot_count += 1
            save_file = SCREENSHOT_DIR / f'{global_screenshot_count}_{int(time.time())}.jpg'
            pyautogui.screenshot().save(save_file)
            Log.error(f'已保存失败截图：{save_file}')
            allure.attach.file(
                source=save_file,
                name="执行失败的截图",
                attachment_type=allure.attachment_type.JPG
            )
        except Exception as e:
            Log.error(f"截图失败: {e}")


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """收集测试结果，从Redis缓存数据中获取"""
    global global_case_count
    local_ip = get_local_ip()
    total_case = global_case_count.total_count()
    pass_case = global_case_count.passed_count()
    fail_case = global_case_count.failed_count()
    skip_case = global_case_count.skip_count()
    error_case = global_case_count.error_count()
    pass_rate = global_case_count.pass_rate()

    Log.info(f"企业微信通知 ? :{CONFIG_ENV.get('notice', False)}")
    if CONFIG_ENV.get('notice', False):
        desc = f"""
            ******对接库测试用例[{local_ip}]本次执行结果******
            总用例数为：{total_case}
            通过用例数：<font color=\"info\">{pass_case}条</font>
            失败用例数：<font color=\"warning\">{fail_case}条</font>
            错误用例数：{error_case}
            跳过用例数：{skip_case}
            通过率为：{pass_rate} %
            """

        Log.info(desc)  # 执行结果发送企业微信
        EnterpriseWechatNotification().send_msg(desc)
    else:
        desc = f"""
            ******本次用例执行结果统计(仅打印展示)******
            总用例数为：{total_case}
            通过用例数：<font color=\"info\">{pass_case}条</font>
            失败用例数：<font color=\"warning\">{fail_case}条</font>
            错误用例数：{error_case}
            跳过用例数：{skip_case}
            通过率为：{pass_rate} %
            """
        Log.info(desc)
