#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sys
import time

def install_package(package_name):
    """
    安装指定的Python包
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"TDPipe: {package_name} installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print(f"TDPipe: {package_name} installation failed!")
        return False

def main():
    # 要安装的包列表
    packages = [
        "numpy",
        "matplotlib",
        "streamlit",
        "plotly",
        "pyopenms",
        # 在这里添加更多需要安装的包
    ]
    # packages = ["numpy", "plotly"]

    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
        time.sleep(1)  # 添加短暂延迟，避免过快安装
    
    print(f"TDPipe: installation completed! successfully installed {success_count}/{len(packages)} packages")

if __name__ == "__main__":
    main()
