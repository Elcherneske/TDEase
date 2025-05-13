from src import *
from src.utils import *
from src.Pages import *
from src.DBUtils import *
from src.UserPages import *
from src.AdminPages import *

# Add missing imports at the top
import sys
import os
from streamlit.web import cli as stcli  # <-- Add this import
import traceback
import logging  # 新增日志模块

# 初始化日志配置
logging.basicConfig(
    filename='launch_error.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def resolve_path(path):
    resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
    return resolved_path


if __name__ == "__main__":
    try:
        sys.argv = [
            "streamlit",
            "run",
            resolve_path("MainPage.py"),
            "--server.headless=false",
            "--logger.level=debug"  # 开启Streamlit调试日志
        ]
        exit_code = stcli.main()
        if exit_code != 0:
            raise RuntimeError(f"Streamlit exited with code {exit_code}")
    except Exception as e:
        error_msg = f"启动失败: {str(e)}"
        logging.error(error_msg, exc_info=True)
        print(error_msg)
        traceback.print_exc()
        os.system("pause")  # 更可靠的暂停方式
    finally:
        # 自动打开日志文件（仅限Windows）
        if os.path.exists('launch_error.log'):
            os.startfile('launch_error.log')