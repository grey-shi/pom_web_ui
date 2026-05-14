import base64
import os
import random
import time
import re
from datetime import datetime
from common import all_path
from common.yaml_util import YamlUtil
from common.logger import Log


class Extractor(object):
    """ 提取接口返回的变量（如 token） """

    @staticmethod
    def extract_value_by_key(data, keys):
        """根据路径获取嵌套字典或列表中的值
        :param data: 需要查询的数据（字典或列表）
        :param keys: 访问键值，如 ['roles', '0', 'role_perm', 'create_user']
        :return: 目标值，若路径不存在则返回 None
        """
        try:
            result = data
            for key in keys:
                key = int(key) if key.isdigit() else key  # 转换列表索引
                result = result[key]
            return result
        except (KeyError, IndexError, TypeError):
            return None  # 如果路径不正确，返回 None

    @staticmethod
    def replace_variables(data):
        """替换 YAML 变量，如 ${config.ss[0].ip}， 循环查找${}数据
        用点分割， config表示文件名称，ip为文件中的变量
        """
        # 定义函数映射表
        function_map = {
            "read_yaml": YamlUtil.read_yaml,
        }
        yaml_list = ['config', 'extract', 'role_pool', 'user_pool', 'get_token']

        if isinstance(data, str):
            matches = re.findall(r"\$\{(.*?)}", data)  # 查找 ${} 格式的字符串
            for match in matches:  # 遍历所有匹配的变量
                file_keys = match.replace("[", ".").replace("]", "").split(".")  # 包含文件名，键名的列表  其中file_keys[0]为文件名
                filename = file_keys[0]
                keys = file_keys[1:]
                if filename in yaml_list:
                    # 读取yaml文件数据
                    file_path = f"{all_path.configPath}\\{filename}.yaml"  # yaml路径
                    func = function_map["read_yaml"]  # 获取对应的函数
                    dict_yaml = func(file_path)  # 调用函数并传递参数
                    result = Extractor.extract_value_by_key(dict_yaml, keys)
                    # Log.info(f"执行 {function_name}({params_str}) 结果: {result}")
                    data = data.replace(f"${{{match}}}", str(result))  # 先替换成字符串
                    # # 如果替换后的数据是int类型，转换回 int
                    data = int(data) if isinstance(result, int) else data

                elif filename == 'get_num':
                    # 保证生成一组 fix 和 actual，使其和大于等于0
                    fix = random.randint(0, 50)
                    actual = 0
                    write_dict = {'fix_num': fix, 'actual_num': actual}
                    YamlUtil.write_yaml(write_dict)
                    data = fix

                elif filename == 'get_name':
                    # 生成一个随机时间戳
                    random_name = Extractor.get_name(keys[0])
                    data = data.replace(f"${{{match}}}", str(random_name))  # 替换变量

                elif filename == 'org_config':
                    # 后续无法附加字符串，传入什么就是什么
                    file_path = f"{all_path.configPath}\\config.yaml"  # yaml路径
                    func = function_map["read_yaml"]  # 获取对应的函数
                    dict_yaml = func(file_path)  # 调用函数并传递参数
                    result = Extractor.extract_value_by_key(dict_yaml, keys)
                    data = result

        elif isinstance(data, dict):
            for key, value in data.items():
                # 将replace_variables(value)返回的值赋值给key，能够替换查找的键的值
                data[key] = Extractor.replace_variables(value)  # 递归替换字典中的值

        elif isinstance(data, list):
            data = [Extractor.replace_variables(i) for i in data]  # 递归替换列表中的每个元素
        return data
