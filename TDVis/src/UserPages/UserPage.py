import streamlit as st
from src.Pages.ReportPage import ReportPage 
from src.Utils.FileUtils import FileUtils   
import os
from src.DBUtils.DBUtils import DBUtils  

class UserPage():
    def __init__(self):
        pass

    def run(self):
        self.init_session_state()
        self.show_user_page()

    def show_user_page(self):
        with st.sidebar:
            if st.button("退出登录"):
                st.session_state['authentication_status'] = None
                st.session_state['authentication_username'] = None
                st.session_state['user_select_file'] = None
                st.rerun()
        
        if not st.session_state['user_select_file']:
            username=st.session_state.get('authentication_username', '')
            st.title(username+"的个人中心")
            df = FileUtils.query_user_files(username)
            df.index = df.index + 1

            filetab,passwordtab=st.tabs(["文件选择","修改密码"])
            with filetab:
                selected_file = st.radio(
                    "**📃请选择您要查看报告的文件:**",
                    df['file_name'],
                    index=None,  # No default selection
                    key="file_radio"
                )
                
                if st.button("选择文件"):
                    if selected_file:
                        st.session_state['user_select_file'] = selected_file  # Store single file
                        st.rerun()
                    else:
                        st.error("请先选择一个文件!")


            with passwordtab:
                old_password = st.text_input("原密码", type="password")
                new_password = st.text_input("新密码", type="password")
                new_password2 = st.text_input("确认新密码", type="password")
                if st.button("修改密码"):
                    if old_password and new_password and new_password2:
                        if new_password == new_password2:
                            args = Args()
                            db_utils = DBUtils(args)
                            username = st.session_state.get('authentication_username', '')
                            if db_utils.user_login(username, old_password).empty:
                                st.error("原密码错误!")
                            else:
                                if db_utils.update_password(username, old_password, new_password):
                                    st.success("密码修改成功!")
                                else:
                                    st.error("密码修改失败!")
                        else:
                            st.error("两次输入的新密码不一致!")

        else:
            st.rerun()

    def init_session_state(self):
        if 'user_select_file' not in st.session_state:
            st.session_state['user_select_file'] = None
