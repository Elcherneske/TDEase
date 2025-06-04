import os
import streamlit as st
from src.Pages.ReportPage import ReportPage

import tkinter as tk
from tkinter import filedialog

class MainPage():
    def __init__(self):
        st.session_state.setdefault("language", "zh")

    def run(self):
        self.show_language_switcher()
        with st.sidebar:
            if st.button("📁", key="select_folder"):
                selected_dir = self._open_directory_dialog()
                if selected_dir:
                    st.session_state["user_select_file"] = selected_dir
                    # 选择新文件夹时清除所有样本选择
                    st.session_state.pop("sample", None)
                    st.session_state.pop("sample2", None)

        ReportPage().run()



    def show_language_switcher(self):
        # 添加语言切换下拉框
        with st.sidebar:
            lang = st.selectbox(
                "🌐 Language / 语言",
                ["zh", "en"],
            )
            # 保存用户选择的语言
            st.session_state["language"] = lang



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
            


if __name__ == "__main__":
    # 初始化streamlit运行时配置
    st.set_page_config(
        page_title="TDvis",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 初始化语言配置
    st.session_state.setdefault("language", "zh")
    main_page = MainPage()
    main_page.run()
