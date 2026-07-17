#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neat Download Manager (Windows 版) 恢复英文原版脚本
==================================================
作用：把汉化过的 NeatDM.exe 恢复成英文原版（从备份还原）。

使用方法：
    python restore_ndm_win.py

注意：需要以管理员权限运行（因为要写入 Program Files 目录）。
"""

import os
import sys
import shutil

# ============================================================
# 配置区
# ============================================================
EXE_PATH = r"C:\Program Files (x86)\Neat Download Manager\NeatDM.exe"
WORK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work")
BACKUP_PATH = os.path.join(WORK_DIR, "NeatDM.exe.backup")


def main():
    # 检查备份是否存在
    if not os.path.exists(BACKUP_PATH):
        print(f"错误：找不到备份文件 {BACKUP_PATH}")
        print("请确认你之前运行过汉化脚本 translate_ndm_win.py")
        sys.exit(1)

    print(f"备份文件: {BACKUP_PATH}")
    print(f"目标位置: {EXE_PATH}")

    # 还原
    try:
        shutil.copy2(BACKUP_PATH, EXE_PATH)
    except PermissionError:
        print("\n错误：没有写入权限！")
        print("请以管理员身份运行此脚本：")
        print("  1. 右键点击 cmd/PowerShell → '以管理员身份运行'")
        print("  2. cd 到脚本目录")
        print("  3. 重新运行 python restore_ndm_win.py")
        sys.exit(1)

    print("\n✓ 已恢复英文原版！")
    print("现在可以启动 Neat Download Manager 查看英文界面。")


if __name__ == "__main__":
    main()
