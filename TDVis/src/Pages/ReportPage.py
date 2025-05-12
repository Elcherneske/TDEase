import streamlit as st
import pandas as pd
import os

from . import ToppicPage
from . import FeaturePage
from . import UserGuide
from . import UserGuide

from ..Utils.FileUtils import FileUtils
from ..Utils.ServerUtils import ServerControl

import tkinter as tk
from tkinter import filedialog
import json
        

class ReportPage():
    def __init__(self):
        self.language = st.session_state.get('language', "en")
        self.selected_file = None
        self.df = None
        self._load_locale()  # 新增本地化加载方法

    def _load_locale(self):
        """加载本地化文本"""
        try:
            pages_dir = os.path.dirname(os.path.abspath(__file__))
            locale_dir = os.path.join(pages_dir, '..','..', 'locales')  # 根据实际情况调整'..'的数量
            locale_path = os.path.join(locale_dir, f"{self.language}.json")
            with open(locale_path, "r", encoding="utf-8") as f:
                self.locale = json.loads(f.read())
        except FileNotFoundError:
            st.error(f"未找到本地化文件: {locale_path}\n请检查以下路径是否存在: {os.path.abspath(locale_dir)}")
            self.locale = {}
        except Exception as e:
            st.error(f"加载本地化文件时出错: {str(e)}\n文件路径尝试: {locale_path}")
            self.locale = {}


    def run(self):
        self._sidebar()
        if not st.session_state.get('user_select_file'):
            guide = UserGuide.UserGuide()
            guide.run()
        else:
            self.show_report_page()

    def _sidebar(self):
        """整合所有侧边栏组件"""
        with st.sidebar:
            if st.button(self.locale.get("selectFolder", "📁 Select Report Folder"), key="select_folder"):
                selected_dir = self._open_directory_dialog()
                if selected_dir:
                    st.session_state["user_select_file"] = selected_dir
                    # 选择新文件夹时清除所有样本选择
                    st.session_state.pop("sample", None)
                    st.session_state.pop("sample2", None)

            # 主样本选择
            if st.session_state.get('user_select_file'):
                file_suffix = os.path.splitext(st.session_state['user_select_file'])[1]
                if file_suffix not in [".pptx", ".docx"]:
                    file_utils = FileUtils()
                    samples = file_utils.list_samples(st.session_state['user_select_file'])
                    
                    # 主样本选择
                    st.session_state["sample"] = st.selectbox(
                        self.locale.get("select_sample", "选择检测样品"), 
                        samples,
                        key="sample_selection"
                    )


    def show_report_page(self):
        # 首先直接启动toppic服务（保持不变）
        self.html_path = FileUtils.get_html_report_path(st.session_state['user_select_file'],st.session_state['sample'])
        ServerControl.start_report_server(self.html_path)

        st.title("TDvis")
        # 缓存特征文件列表（新增）
        @st.cache_data
        def get_feature_files():
            return [
                FileUtils.get_file_path("_ms1.feature",selected_path=st.session_state['user_select_file'],sample_name=st.session_state['sample']),
                FileUtils.get_file_path("_ms2.feature",selected_path=st.session_state['user_select_file'],sample_name=st.session_state['sample'])
            ]
        feature_files = get_feature_files()

        #tab选择界面
        feature_tab,report_tab,toppic_tab,guide_tab = st.tabs([
            self.locale.get("feature_tab_label", "特征图谱"),
            self.locale.get("report_tab_label", "汇总信息"),
            self.locale.get("toppic_tab_label", "二级报告"),
            self.locale.get("guide_tab_label", "使用指南")
        ])
        with feature_tab:
            # 使用独立容器包裹组件
            with st.container():
                feature = FeaturePage.Featuremap(self.locale)
                feature.run()        

        # 主报告页逻辑（保持不变）
        with report_tab:
            self._count_report_files()
            if feature_files:
                self.selected_file = st.selectbox(self.locale.get("selec_feature_file","选择特征文件"), feature_files,key="feature_file")
            self.df = pd.read_csv(self.selected_file, sep='\t')
            self._display_data_grid()

        with toppic_tab:
            toppic=ToppicPage.ToppicShowPage(self.locale)
            toppic.run()

        with guide_tab:
            guide=UserGuide.UserGuide()
            guide.run()
        


    def _count_report_files(self):
        """统计HTML报告相关文件数量"""
        try:
            base_path = os.path.join(
                self.html_path,
                "toppic_proteoform_cutoff",
                "data_js"
            )
            target_folders = [
                ("proteins", self.locale.get("proteins", "蛋白")),
                ("proteoforms", self.locale.get("proteoforms", "变体")), 
                ("prsms", self.locale.get("prsms", "特征"))
            ]
            results = []
            for folder, display_name in target_folders:
                folder_path = os.path.join(base_path, folder)
                if os.path.exists(folder_path):
                    file_count = len([
                        f for f in os.listdir(folder_path) 
                        if os.path.isfile(os.path.join(folder_path, f))
                    ])
                    results.append(f" **{display_name}**: {file_count} {self.locale.get('units', '个')}")
                else:
                    results.append(f"{self.locale.get('folder_not_found_prefix', '⚠️')} {display_name}{self.locale.get('folder_not_found_suffix', '目录不存在')}")
            st.markdown(self.locale.get("sample_detected_prefix", "__本样品共检测到:__"))
            st.markdown("\n".join(results))
        except Exception as e:
            st.sidebar.error(self.locale.get("file_count_failed", "文件统计失败: ") + str(e))
            
    def _display_data_grid(self):
        """配置Streamlit原生表格显示"""
        # 获取本地化文本，若不存在则使用默认值
        current_file_text = self.locale.get("current_file", "**当前文件:** ")
        download_button_text = self.locale.get("download_button", "📥 下载选中文件")
        fullscreen_tip = self.locale.get("fullscreen_tip", '''提示：使用表格右上角的按钮可进行全屏查看''')
        
        st.markdown(f"{current_file_text} `{os.path.basename(self.selected_file)}`")
        # 文件下载按钮
        csv_data = self.df.to_csv(index=False, sep='\t').encode('utf-8')
        st.download_button(
            label=download_button_text,
            data=csv_data,
            file_name=os.path.basename(self.selected_file),
            mime='text/csv',
            key='btn_download_feature'
        )
        
        # 替换AgGrid为streamlit原生表格
        st.dataframe(
            self.df,
            height=600,
            use_container_width=True,
            hide_index=True
        )
        st.markdown(fullscreen_tip)
        
    def _open_directory_dialog(self):
        """Open system directory dialog using Tkinter"""
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.wm_attributes('-topmost', 1)  # Add this line
        root.withdraw()
        
        # Force focus on the dialog
        root.update_idletasks()
        folder_path = filedialog.askdirectory(parent=root)
        
        # Cleanup
        root.destroy()
        
        return os.path.normpath(folder_path) if folder_path else None
        