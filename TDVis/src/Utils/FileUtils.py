import os
import streamlit as st
import pandas as pd


class FileUtils:
    """_summary_
    文件查询工具,用于统一维护文件查询路径
    可以查询用户名下对应的文件地址
    """

    @staticmethod
    def _resolve_path(input_path):
        """增强版路径解析，兼容本地和云端环境"""
        if not input_path:
            return None
            
        # 通过环境变量判断是否在Streamlit Cloud运行
        is_cloud = os.environ.get("IS_STREAMLIT_CLOUD", "false").lower() == "true"
        
        # 获取项目根目录
        if is_cloud:
            # 云端环境固定路径
            project_root = "/mount/src/tdvis_demo"
        else:
            # 本地环境动态计算
            current_script_path = os.path.abspath(__file__)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))
        
        # 处理路径拼接
        resolved_path = os.path.join(project_root, input_path) if not os.path.isabs(input_path) else input_path
        return os.path.normpath(resolved_path)
    

    
    @staticmethod
    def list_samples(selected_path=None):

        resolved_path = FileUtils._resolve_path(selected_path or st.session_state.get('user_select_file'))

        if not resolved_path or not os.path.exists(resolved_path):
            raise FileNotFoundError(f"路径不存在: {resolved_path}")
            
        samples = []
        # 修复3：遍历解析后的路径
        for filename in os.listdir(resolved_path):
            if filename.endswith("ms1.feature"):
                sample_name = filename.split("_")[0]
                samples.append(sample_name)
        return samples

    @staticmethod
    def get_html_report_path(selected_path=None, sample_name=None):
        # 添加路径解析
        resolved_path = FileUtils._resolve_path(selected_path or st.session_state.get('user_select_file'))
        for filename in os.listdir(resolved_path):  # 使用解析后的路径
            target_suffix = f"{sample_name}_html"
            for filename in os.listdir(resolved_path):
                if filename.endswith(target_suffix):
                    return os.path.join(resolved_path, filename)
            raise FileNotFoundError(f"未找到HTML报告文件: {target_suffix}")


    @staticmethod
    def get_file_path(suffix, selected_path=None, sample_name=None):
        # 确保使用解析后的路径
        resolved_path = FileUtils._resolve_path(selected_path or st.session_state.get('user_select_file'))
        for filename in os.listdir(resolved_path):  # 使用解析后的路径
            """
            获取指定后缀文件的路径
            针对于最开始选中的文件夹,也就是一级文件夹!
            Args:
                suffix (str): 指定的文件后缀，如 ".feature"
                selected_path (str): 指定的文件夹路径，默认为 None，使用 session_state 中的值
                sample_name (str): 指定的样品名称，默认为 None，使用 session_state 中的值
            Returns:
                str: 找到的文件路径
            """
            target_suffix = f"{sample_name}{suffix}"
            for filename in os.listdir(resolved_path):
                if filename.endswith(target_suffix):
                    return os.path.join(resolved_path, filename)
            raise FileNotFoundError(f"未找到指定后缀文件: {target_suffix}")


