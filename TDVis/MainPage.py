import os
import streamlit as st
from src.Pages.ReportPage import ReportPage

class MainPage():
    def __init__(self):
        st.session_state.setdefault("language", "zh")

    def run(self):
        self.show_language_switcher()
        ReportPage().run()

    def show_language_switcher(self):
        # 添加语言切换下拉框
        with st.sidebar:
            lang = st.selectbox(
                "🌐 Language / 语言",
                ["zh", "en","ar","ru"],
            )
            # 保存用户选择的语言
            st.session_state["language"] = lang



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