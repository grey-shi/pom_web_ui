import os
from typing import Union, Dict, List, Optional, Any
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap


class YamlUtil:
    """ 基于 ruamel.yaml 的通用 YAML 工具类
    支持：读、写、更新（保留注释）、清空、读取单个键 """
    yaml = YAML()
    yaml.preserve_quotes = True  # 保留引号风格
    yaml.indent(mapping=2, sequence=4, offset=2)  # 缩进风格

    @staticmethod
    def read_yaml(file_path: str) -> Union[Dict, List]:
        """
        读取 YAML 文件
        :param file_path: 文件路径
        :return dict / list
        """
        if not os.path.exists(file_path):
            return {}
        with open(file_path, 'r', encoding='utf-8') as f:
            data = YamlUtil.yaml.load(f)
            return data

    @staticmethod
    def write_yaml(data: Union[Dict, List], file_path: str) -> None:
        """
        写入 YAML 文件（会保留注释、格式）
        :param data: dict 或 list
        :param file_path:文件路径
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            YamlUtil.yaml.dump(data, f)

    @staticmethod
    def update_yaml(updates: Dict[str, Any], file_path: str, comments: Optional[Dict[str, str]] = None) -> None:
        """
        更新 YAML 文件中的内容（保留原有注释）
        :param updates: 要更新或新增的键值对
        :param file_path: YAML 文件路径
        :param comments: 可选，键名->注释 的字典，表示对新增键值的注释
        """
        comments = comments or {}
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data: CommentedMap = YamlUtil.yaml.load(f)
        else:
            data: CommentedMap = CommentedMap()

        # 更新数据并添加注释
        for key, value in updates.items():
            data[key] = value
            # 如果有注释，写入行尾注释
            if key in comments:
                data.yaml_add_eol_comment(comments[key], key=key)

        # 写回
        with open(file_path, 'w', encoding='utf=8') as f:
            YamlUtil.yaml.dump(data, f)

    @staticmethod
    def clear_yaml(file_path: str) -> None:
        """清空 YAML 文件"""
        if os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.truncate(0)

    @staticmethod
    def read_param(file_path: str, key: str) -> Any:
        """
        读取 YAML 中某个键的值
        :param file_path: 文件路径
        :param key: 键名
        :return: 该键对应的值 or None
        """
        data = YamlUtil.read_yaml(file_path)
        if isinstance(data, dict):
            return data.get(key)
        return None
