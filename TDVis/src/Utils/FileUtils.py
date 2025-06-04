import os
import streamlit as st
import pandas as pd
from .Args import Args
from ..DBUtils import DBUtils

class FileUtils:
    """文件查询工具,用于统一维护文件查询路径"""

    @staticmethod
    def list_samples(selected_path=None):
        """列出指定目录下的样本"""
        path = selected_path or st.session_state.get('user_select_file')
        if not path or not os.path.exists(path):
            raise FileNotFoundError(f"路径不存在: {path}")

        samples = []
        for filename in os.listdir(path):
            if filename.endswith("ms1.feature"):
                last_underscore_idx = filename.rfind("_")
                sample_name = filename[:last_underscore_idx] if last_underscore_idx != -1 else filename
                samples.append(sample_name)
        return samples

    @staticmethod
    def get_html_report_path(selected_path=None, sample_name=None):
        """获取HTML报告路径"""
        path = selected_path or st.session_state.get('user_select_file')
        if not path or not os.path.exists(path):
            raise FileNotFoundError(f"路径不存在: {path}")
            
        target_folder = f"{sample_name}_html"
        report_path = os.path.join(path, target_folder)
        if os.path.isdir(report_path):
            return report_path
        return None

    @staticmethod
    def get_file_path(suffix, selected_path=None, sample_name=None):
        """获取特定后缀的文件路径"""
        path = selected_path or st.session_state.get('user_select_file')
        if not path or not os.path.exists(path):
            raise FileNotFoundError(f"路径不存在: {path}")

        target_suffix = f"{sample_name}{suffix}"
        for filename in os.listdir(path):
            if filename.endswith(target_suffix):
                return os.path.join(path, filename)
        raise FileNotFoundError(f"未找到指定后缀文件: {target_suffix}")


#  用户管理查询代码
    @staticmethod
    def query_files(username=None):
        """
        通用文件**地址**查询方法
        是为数据库操作
        :param username: 指定用户名时查询单个用户,None时查询所有用户
        :return: 包含(用户名, 文件名)的DataFrame
        """
        args = Args()  
        db_utils = DBUtils(args)  # 显式调用类名

        if username:
            file_addresses = db_utils.get_file_addresses(username)
            return pd.DataFrame([
                {"用户名": username, "文件名": os.path.normpath(f)}
                for f in file_addresses
            ])

        # 处理全部用户查询（管理员模式）
        all_files = []
        users = db_utils.query_users("", 0, 0)  # 获取所有用户
        for _, row in users.iterrows():
            file_addresses = db_utils.get_file_addresses(row['username'])
            all_files.extend([
                {"用户名": row['username'], "文件名": os.path.normpath(f)}
                for f in file_addresses
            ])
        return pd.DataFrame(all_files)

    @staticmethod  
    def query_user_files(username):
        """
        获取指定用户的文件列表
        设计数据库操作
        :param username: 当前登录用户名
        :return: 包含文件名的DataFrame(列名为file_name)
        """
        args = Args()  
        db_utils = DBUtils(args) 
        file_addresses = db_utils.get_file_addresses(username)
        return pd.DataFrame({'file_name': [os.path.normpath(f) for f in file_addresses]})

