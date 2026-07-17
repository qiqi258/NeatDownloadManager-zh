@echo off
chcp 65001 >nul 2>&1
title Neat Download Manager 中文汉化安装器
color 0A

echo ============================================================
echo   Neat Download Manager (Windows) 中文汉化安装器
echo ============================================================
echo.

REM 检查是否以管理员身份运行
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 需要管理员权限，正在自动请求...
    echo.
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

echo [1/3] 检查环境...
echo.

REM 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python！
    echo 请先安装 Python 3：https://www.python.org/downloads/
    echo 安装时请勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo   Python 版本: %PYVER%

REM 检查 NDM 是否安装
if not exist "C:\Program Files (x86)\Neat Download Manager\NeatDM.exe" (
    echo   [错误] 未找到 NeatDM.exe
    echo   请确认 Neat Download Manager 已安装到默认路径。
    echo   如果安装在其他位置，请直接运行: python translate_ndm_win.py
    echo   并修改脚本顶部的 EXE_PATH 变量。
    echo.
    pause
    exit /b 1
)
echo   NDM 已安装: C:\Program Files (x86)\Neat Download Manager\NeatDM.exe
echo.

REM 检查 NDM 是否正在运行
echo [2/3] 关闭正在运行的 Neat Download Manager...
taskkill /f /im NeatDM.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo   已关闭 NeatDM.exe
) else (
    echo   NeatDM 未在运行
)
timeout /t 1 /nobreak >nul
echo.

REM 运行汉化脚本
echo [3/3] 开始汉化...
echo.
python "%~dp0translate_ndm_win.py"
set RET=%errorlevel%

echo.
echo ============================================================
if %RET% equ 0 (
    echo   汉化完成！
    echo.
    echo   现在可以启动 Neat Download Manager 查看中文界面。
    echo.
    echo   如需恢复英文原版，运行: restore_win.bat
) else (
    echo   汉化过程中出现错误，请查看上方信息。
)
echo ============================================================
echo.
pause
