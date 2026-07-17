#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neat Download Manager (Windows 版) 中文汉化脚本
================================================
作用：把 NeatDM.exe 里的英文界面文字替换成中文。

原理（小白版讲解）：
    1. Windows 程序的界面文字用 UTF-16LE 编码存在 exe 里，
       每个字符串以 \\x00\\x00 结尾（空终止符），后面还有填充对齐。
    2. 我们把英文转成 UTF-16LE 字节去 exe 里"找位置"，
       找到后用中文的 UTF-16LE 字节替换它。
    3. 如果中文比英文短，多出来的位置用 \\x00 填上（保持长度不变，不破坏 exe）。
    4. 如果中文比英文长，就跳过这条（避免撑爆原位置导致 exe 损坏）。
    5. 替换前会自动备份原 exe 到 work\\NeatDM.exe.backup。

使用方法：
    python translate_ndm_win.py

注意：
    - 需要以管理员权限运行（因为要写入 Program Files 目录）
    - 运行前请先关闭 Neat Download Manager
    - 如果安装路径不同，修改下面的 EXE_PATH
"""

import os
import sys
import shutil
import datetime

# ============================================================
# 配置区
# ============================================================
EXE_PATH = r"C:\Program Files (x86)\Neat Download Manager\NeatDM.exe"

# 备份目录（脚本所在目录下的 work 文件夹）
WORK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work")


# ============================================================
# 翻译映射表（英文 → 中文）
# ============================================================
# 说明：这里的英文必须和 exe 里存储的"完全一致"（包括空格、标点），
#       否则匹配不到。所有条目都来自 analyze_ndm.py 的分析结果。
#       只翻译"界面文字"，不翻译错误信息/技术术语/文件名等。
# ============================================================

TRANSLATIONS = {
    # ===== 关于窗口 =====
    "About NeatDownloadManager": "关于 NeatDownloadManager",
    "Neat Download Manager 1.4.24": "Neat 下载管理器 1.4.24",
    "( Basic Version - Free License )": "( 基础版 - 免费许可证 )",
    "Copyright": "版权",
    " 2022 Javad Motallebi , All rights reserved.": " 2022 Javad Motallebi，保留所有权利。",
    "Website : neatdownloadmanager.com": "网站：neatdownloadmanager.com",
    "Contact : support@neatdownloadmanager.com": "联系方式：support@neatdownloadmanager.com",
    "Check For Update": "检查更新",
    "Checking For Update...": "正在检查更新...",
    "Download New Version": "下载新版本",
    "Application is Up To Date.": "应用已是最新版本。",
    "Unable to Check For Update , Please Try Again Later": "无法检查更新，请稍后重试",
    "NOT Up To Date, Click Above Button to get the New Version": "不是最新版本，点击上方按钮获取新版本",

    # ===== 认证窗口 =====
    "Authentication": "身份验证",
    "User Name": "用户名",
    " Authentication For :": " 身份验证：",
    "Remember": "记住",
    "Password": "密码",

    # ===== 浏览器窗口 =====
    "Browsers": "浏览器",
    "Google Chrome": "谷歌浏览器",
    "Mozilla Firefox": "火狐浏览器",
    "Microsoft Edge": "微软 Edge",
    "Add Chrome Extension": "添加 Chrome 扩展",
    "Add Firefox Extension": "添加 Firefox 扩展",
    "Add Edge Extension": "添加 Edge 扩展",
    "* Sends download links from Chrome to the application.": "* 将下载链接从 Chrome 发送到本应用。",
    "* Sends download links from Firefox to the application.": "* 将下载链接从 Firefox 发送到本应用。",
    "* Catches Video/Audio links on many websites.": "* 捕获多种网站的视频/音频链接。",
    "* YouTube is not supported ( Chrome store doesn't allow )": "* 不支持 YouTube（Chrome 商店不允许）",
    "* YouTube is supported partially.": "* 部分支持 YouTube。",
    "* Compatible with Chromium-based browsers like Opera, Brave, ...": "* 兼容 Opera、Brave 等 Chromium 内核浏览器...",
    "Show Download Panel on Web Media Players": "在网页媒体播放器上显示下载面板",
    "Chrome is not Installed.": "未安装 Chrome。",
    "MS Edge is not Installed.": "未安装 MS Edge。",
    "Firefox is not Installed.": "未安装 Firefox。",

    # ===== 主窗口 - 侧边栏分类 =====
    "All Downloads": "所有下载",
    "Compressed": "压缩包",
    "Application": "应用程序",
    "Document": "文档",
    "Complete": "已完成",
    "Incomplete": "未完成",
    "Misc": "杂项",
    "Audio": "音频",

    # ===== 主窗口 - 列标题 =====
    "Status": "状态",
    "Protocol": "协议",
    "Target": "目标",
    "File Name": "文件名",
    "Bandwidth": "带宽",
    "Size": "大小",
    "Last Try (z-a)": "上次尝试 (z-a)",
    "Remaining Time": "剩余时间",

    # ===== 主窗口 - 工具栏/菜单 =====
    "Neat Download Manager 1.4": "Neat 下载管理器 1.4",
    "Neat Download Manager": "Neat 下载管理器",
    "New URL": "新建下载",
    "Resume": "继续",
    "Delete": "删除",
    "Stop": "停止",
    "About": "关于",
    "Settings": "设置",
    "Quit": "退出",
    "Redownload": "重新下载",
    "Properties": "属性",
    "Show Window": "显示窗口",
    "Open Folder": "打开文件夹",
    "Download Completed": "下载完成",
    "NeatDownloadManager Main Window": "NeatDownloadManager 主窗口",

    # ===== 下载窗口 =====
    "NeatDownloadWindow": "Neat下载窗口",
    " Download ": " 下载 ",
    " Connections ": " 连接数 ",
    " Options ": " 选项 ",
    "File Size": "文件大小",
    "Starting...": "启动中...",
    "Downloaded": "已下载",
    "Unknown": "未知",
    "Resumable": "可断点续传",
    "Limit Bandwidth to ": "限制带宽为 ",
    "0 or Blank = No Limit": "0 或留空 = 不限速",
    "KB/sec": "KB/秒",
    "Show Completion Dialog": "显示完成对话框",
    "Remember on Resume": "续传时记住",
    "Segments : 0  Completed : 0": "分片：0  已完成：0",
    "Connections": "连接数",
    "Segments : 0": "分片：0",
    "Download...": "下载中...",
    "Paused -   ": "已暂停 -   ",
    "Paused -    ": "已暂停 -    ",
    "Segments : 0  Completed : 0 ": "分片：0  已完成：0 ",
    " Authentication Failed for ": " 身份验证失败：",

    # ===== MKV 下载窗口 =====
    "Video Status": "视频状态",
    "Audio Status": "音频状态",
    "Total Downloaded": "总已下载",
    "Total File Size": "文件总大小",
    "Total Bandwidth": "总带宽",
    "Size : ": "大小：",
    "Video : ": "视频：",
    "Audio : ": "音频：",
    "Muxing MKV...": "正在合成 MKV...",

    # ===== 错误窗口 =====
    "Error : ": "错误：",
    "Download Error": "下载错误",
    "Log File": "日志文件",
    "URL :": "URL：",

    # ===== 属性窗口 =====
    "Download Properties": "下载属性",
    "File Size :": "文件大小：",
    "Status :": "状态：",
    "Temp Path :": "临时路径：",
    "Saved To :": "保存至：",
    "Page URL :": "页面 URL：",
    "Page Title :": "页面标题：",
    "Show Page": "显示页面",
    "Browser :": "浏览器：",
    "Last Try :": "上次尝试：",
    "Added On :": "添加日期：",
    "Has Window": "有窗口",
    "Invalid URL": "无效 URL",
    "Database Error": "数据库错误",

    # ===== 退出窗口 =====
    "Quit NeatDownloadManager": "退出 NeatDownloadManager",
    "Are you sure you want to Quit Totally ?": "确定要完全退出吗？",
    "Quit Application Totally": "完全退出应用",
    "Hide in Notification Area": "隐藏到通知区域",
    "You can hide NeatDownloadManager in Notification Area by clicking on MainWindow close button and then bring it to front by clicking on Notification item Menu.":
        "您可以点击主窗口的关闭按钮将 NeatDownloadManager 隐藏到通知区域，然后点击通知项菜单将其重新调出。",

    # ===== 设置窗口 =====
    " General ": " 常规 ",
    "Neat Download Manager Settings": "Neat 下载管理器设置",
    " Passwords ": " 密码管理 ",
    " Proxy/Socks": " 代理/Socks",
    "8 Connections Recommended": "推荐 8 个连接",
    "Max Connections per Download": "每个下载最大连接数",
    "When first Connection Starts Downloading  , :": "当首个连接开始下载时：",
    "Bandwidth Limit per Download (KB/s)": "单个下载带宽限制 (KB/s)",
    "Default User-Agent": "默认 User-Agent",
    "0 or blank for No limit": "0 或留空表示不限速",
    "Use this UA for both Manual and Browser-Sent Downloads ( Be Careful )":
        "手动和浏览器发送的下载均使用此 UA（请谨慎使用）",
    "Create Category Folders ( e.g.  Video, Document, ...  )": "创建分类文件夹（如：视频、文档等）",
    "Download Directory": "下载目录",
    "Temporary Directory": "临时目录",
    "Start Application on System Startup ( Recommended )": "开机时启动应用（推荐）",
    "Show Download Completion Dialog": "显示下载完成对话框",
    "HTTP Proxy": "HTTP 代理",
    "No Proxy/Socks": "无代理/Socks",
    "Socks V5": "Socks V5",
    "Socks Proxy": "Socks 代理",
    "Socks V4": "Socks V4",
    "Address": "地址",
    "Port": "端口",
    "ftp Protocol": "FTP 协议",
    "https Protocol": "HTTPS 协议",
    "Select Folder": "选择文件夹",
    "Remove": "移除",
    "Select a Folder for Downloaded Files :": "选择下载文件保存文件夹：",
    "Select a Folder for Temporary Segment Files :": "选择临时分片文件文件夹：",
    "Directory doesn't exist": "目录不存在",
    "Select a Directory": "选择目录",
    "Directory is READ-ONLY": "目录是只读的",
    "Please Correct Focused Item.": "请修正当前项。",
    "Create Additional Connections All at Once": "同时创建所有附加连接",
    "Create Additional Connections One by One": "逐一创建附加连接",
    "Get File Creation Date From Server": "从服务器获取文件创建日期",

    # ===== URL/下载对话框 =====
    "Download": "下载",
    "URL :  ": "URL：",
    "Renew Download Link": "更新下载链接",
    "You should Resend the URL from Browser to NeatDownloadManager.": "您需要从浏览器重新发送 URL 到 NeatDownloadManager。",
    "The URL has been changed or Download Session has expired.": "URL 已更改或下载会话已过期。",
    "Resend": "重新发送",
    "Title = ": "标题 = ",
    " Waiting for new URL from Browser Extension .....": " 等待浏览器扩展发送新 URL .....",

    # ===== 其他 =====
    "Cancel": "取消",
    "Apply": "应用",
    "Pause": "暂停",
    "Close": "关闭",
    "Reset": "重置",
    "Tree View": "树视图",
    "Warning": "警告",
    "No": "否",
}


# ============================================================
# 核心替换函数
# ============================================================

def replace_string_in_data(data, eng, chs, verbose=True):
    """
    在 exe 字节数据里，把一个英文字符串替换成中文。

    策略（小白版）：
        1. 把英文转成 UTF-16LE 字节，末尾加上 \\x00\\x00（空终止符），
           这样能"精确匹配"整个字符串，不会误伤包含它的长字符串。
           例如 "Download" 不会匹配到 "Download Completed"。
        2. 在 exe 里找到这个字节序列的位置。
        3. 把中文也转成 UTF-16LE，末尾加 \\x00\\x00。
        4. 如果中文比英文短：用中文替换，多出来的位置填 \\x00。
        5. 如果中文比英文长：跳过（避免破坏 exe）。

    返回：替换的次数
    """
    # 英文的 UTF-16LE 字节 + 空终止符（精确匹配，避免子串误伤）
    eng_bytes = eng.encode('utf-16-le') + b'\x00\x00'
    chs_bytes = chs.encode('utf-16-le') + b'\x00\x00'

    # 中文比英文长太多就跳过（安全第一）
    if len(chs_bytes) > len(eng_bytes):
        if verbose:
            print(f"  ⚠ 跳过（中文过长）：{eng!r} → {chs!r}")
            print(f"      英文 {len(eng_bytes)} 字节 vs 中文 {len(chs_bytes)} 字节")
        return 0

    count = 0
    pos = 0
    while True:
        idx = data.find(eng_bytes, pos)
        if idx == -1:
            break
        # 替换：写入中文字节，剩余位置填 \x00
        new_data = chs_bytes + b'\x00' * (len(eng_bytes) - len(chs_bytes))
        data[idx:idx + len(eng_bytes)] = new_data
        count += 1
        pos = idx + len(eng_bytes)

    return count


def main():
    os.makedirs(WORK_DIR, exist_ok=True)

    # 检查 exe 是否存在
    if not os.path.exists(EXE_PATH):
        print(f"错误：找不到 {EXE_PATH}")
        print("请确认 NDM 安装路径，并修改脚本顶部的 EXE_PATH 变量。")
        sys.exit(1)

    # 读取 exe
    print(f"读取: {EXE_PATH}")
    with open(EXE_PATH, "rb") as f:
        data = bytearray(f.read())
    original_size = len(data)
    print(f"文件大小: {original_size} 字节 ({original_size / 1024 / 1024:.2f} MB)")

    # 备份原文件（带时间戳）
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(WORK_DIR, f"NeatDM.exe.backup_{timestamp}")
    print(f"备份原文件到: {backup_path}")
    shutil.copy2(EXE_PATH, backup_path)
    # 同时保留一个固定名字的备份，方便恢复
    fixed_backup = os.path.join(WORK_DIR, "NeatDM.exe.backup")
    shutil.copy2(EXE_PATH, fixed_backup)

    # 开始替换
    print("\n" + "=" * 60)
    print("开始汉化")
    print("=" * 60)

    total_replaced = 0
    total_skipped = 0
    not_found = 0

    for eng, chs in TRANSLATIONS.items():
        count = replace_string_in_data(data, eng, chs, verbose=True)
        if count > 0:
            total_replaced += count
            print(f"  ✓ {eng!r} → {chs!r}  ({count} 处)")
        else:
            # 区分"中文过长跳过"和"没找到"
            eng_bytes = eng.encode('utf-16-le') + b'\x00\x00'
            chs_bytes = chs.encode('utf-16-le') + b'\x00\x00'
            if len(chs_bytes) > len(eng_bytes):
                total_skipped += 1
            else:
                not_found += 1
                print(f"  ✗ 未找到: {eng!r}")

    print("\n" + "=" * 60)
    print("汉化统计")
    print("=" * 60)
    print(f"  成功替换: {total_replaced} 处")
    print(f"  因中文过长跳过: {total_skipped} 条")
    print(f"  未找到（exe 里没有）: {not_found} 条")

    # 检查文件大小是否变化（应该不变）
    if len(data) != original_size:
        print(f"\n⚠ 警告：文件大小发生变化！{original_size} → {len(data)}")
        print("  这不应该发生，请检查脚本逻辑。已中止写入。")
        sys.exit(1)

    # 写回 exe
    print(f"\n写入汉化后的文件到: {EXE_PATH}")
    try:
        with open(EXE_PATH, "wb") as f:
            f.write(data)
    except PermissionError:
        print("\n错误：没有写入权限！")
        print("请以管理员身份运行此脚本：")
        print("  1. 右键点击 cmd/PowerShell → '以管理员身份运行'")
        print("  2. cd 到脚本目录")
        print("  3. 重新运行 python translate_ndm_win.py")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✓ 汉化完成！")
    print("=" * 60)
    print(f"\n原文件已备份到: {fixed_backup}")
    print(f"  （带时间戳的备份: {backup_path}）")
    print("\n现在可以启动 Neat Download Manager 查看中文界面。")
    print("\n如需恢复英文原版，运行: python restore_ndm_win.py")


if __name__ == "__main__":
    main()
