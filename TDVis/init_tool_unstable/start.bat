@echo off
cd /d "%~dp0"
chcp 65001 > nul

:: 新增环境路径配置
set "VIRTUAL_ENV=%~dp0.venv"
set "PATH=%VIRTUAL_ENV%\Scripts;%PATH%"

echo 正在启动服务...
call .venv\Scripts\activate.bat  :: 新增显式激活命令
uv pip check >nul 2>&1 && (
    streamlit run "%~dp0scripts\MainPage.py"
) || (
    echo ✗ 环境异常，请先运行init.bat初始化
)

pause
