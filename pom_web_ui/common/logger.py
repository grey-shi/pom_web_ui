import json
import logging
import os
import time
from common import all_path

SUCCESS_LEVEL_NUM = 25
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")


class Log(object):
    """静态日志处理类"""

    flag = True

    # 在类级别定义logger, 避免重复创建
    log_path = all_path.LOGS_DIR
    log_name = os.path.join(log_path, f'{time.strftime("%Y-%m-%d")}.log')

    # 创建存储目录
    if not os.path.exists(log_path):
        os.mkdir(log_path)

    # 创建或获取一个名为 "custom_logger" 的日志器对象
    logger = logging.getLogger('custom_logger')
    # 设置日志等级为 DEBUG，意味着输出 所有等级日志 DEBUG < INFO < WARNING < ERROR < CRITICAL
    logger.setLevel(logging.DEBUG)

    # 设置日志格式 formatter  时间戳 - 日志级别 - 当前日志语句所在的文件名 - 日志语句所在行 - 所在函数名 - 实际日志内容
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d - %(funcName)s] - %(message)s')

    # 创建文件日志处理器
    file_handler = logging.FileHandler(log_name, mode='a+', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # 给处理器设置格式器
    file_handler.setFormatter(formatter)

    # 将处理器添加到logger中
    logger.addHandler(file_handler)

    if flag:
        #  创建控制台日志处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        # 给处理器设置格式器
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    @staticmethod
    def log(level, meg):
        """记录日志"""
        if isinstance(meg, (dict, list)):
            meg = json.dumps(meg, indent=4, ensure_ascii=False)
        if level == 'info':
            Log.logger.info(meg, stacklevel=3)
        elif level == 'debug':
            Log.logger.debug(meg, stacklevel=3)
        elif level == 'warning':
            Log.logger.warning(meg, stacklevel=3)
        elif level == 'error':
            Log.logger.error(meg, stacklevel=3)

    @staticmethod
    def debug(meg):
        Log.log('debug', meg)

    @staticmethod
    def info(message):
        Log.log('info', message)

    @staticmethod
    def warning(message):
        Log.log('warning', message)

    @staticmethod
    def error(message):
        Log.log('error', message)

    @staticmethod
    def success(message):
        Log.logger.log(SUCCESS_LEVEL_NUM, message, stacklevel=2)


if __name__ == '__main__':
    Log.info('123')