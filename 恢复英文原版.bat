@echo off
chcp 65001 >nul 2>&1
title Neat Download Manager 恢复英文原版
color 0E

echo ============================================================
echo   Neat Download Manager (Windows) 恢复英文原版
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

REM 关闭 NDM
echo 关闭正在运行的 Neat Download Manager...
taskkill /f /im NeatDM.exe >nul 2>&1
timeout /t 1 /nobreak >nul
echo.

REM 运行恢复脚本
echo 开始恢复...
python "%~dp0restore_ndm_win.py"
set RET=%errorlevel%

echo.
echo ============================================================
if %RET% equ 0 (
    echo   已恢复英文原版！
) else (
    echo   恢复过程中出现错误，请查看上方信息。
)
echo ============================================================
echo.
pause
