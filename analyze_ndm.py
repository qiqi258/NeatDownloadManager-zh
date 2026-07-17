#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NDM Windows 版 (NeatDM.exe) 字符串分析脚本
==========================================
作用：把 exe 里的英文界面字符串"挖"出来，生成一份清单，
      方便我们确认编码方式（UTF-8 / UTF-16）和翻译范围。

使用方法（小白版）：
    1. 把这个脚本放到一个文件夹里
    2. 打开 PowerShell 或 cmd，cd 到这个文件夹
    3. 运行：python analyze_ndm.py
    4. 运行完会生成 3 个文件：
         - analysis_result.txt   （分析摘要，把这个贴给我）
         - strings_utf16.txt     （UTF-16 字符串清单）
         - strings_utf8.txt      （UTF-8 字符串清单）
    5. 把 analysis_result.txt 的内容复制粘贴给我

注意：脚本默认读取 C:\\Program Files (x86)\\Neat Download Manager\\NeatDM.exe
      如果你的安装路径不同，修改下面的 EXE_PATH 变量即可。
"""

import os
import re
import sys

# ============================================================
# 配置区：NDM 的安装路径，按需修改
# ============================================================
EXE_PATH = r"C:\Program Files (x86)\Neat Download Manager\NeatDM.exe"

# 输出目录（脚本所在目录下的 work 文件夹）
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work")


def read_exe(path):
    """读取 exe 的全部字节"""
    with open(path, "rb") as f:
        return f.read()


def extract_utf16_strings(data):
    """
    提取 UTF-16LE 编码的字符串（Windows 程序常用这种编码）。
    规则：连续的可打印 ASCII 字符（每两个字节表示一个字符，第二个字节为 0x00）。
    """
    # 匹配：可打印字符 + 0x00 的重复，至少 4 个字符
    pattern = re.compile(rb'(?:[\x20-\x7e]\x00){4,}')
    results = []
    for m in pattern.finditer(data):
        raw = m.group()
        # 去掉每两个字节里的 0x00，还原成普通字符串
        text = raw.decode('utf-16-le', errors='ignore')
        results.append((m.start(), text))
    return results


def extract_utf8_strings(data):
    """
    提取 UTF-8 / ASCII 编码的字符串。
    规则：连续 4 个以上可打印 ASCII 字符。
    """
    pattern = re.compile(rb'[\x20-\x7e]{4,}')
    results = []
    for m in pattern.finditer(data):
        text = m.group().decode('ascii', errors='ignore')
        results.append((m.start(), text))
    return results


def is_ui_text(s):
    """
    粗略判断一个字符串是不是"界面文字"（而不是函数名、路径、注册表键等）。
    标准：包含空格、或以大写字母开头且长度>=4、或包含常见 UI 词。
    """
    if len(s) < 4:
        return False
    # 跳过明显是代码/路径的
    if any(x in s for x in ('\\', '/', '.dll', '.exe', '.ini', 'HKEY_', 'Software\\',
                             'Microsoft\\', 'http://', 'https://', '__', '::',
                             'Get', 'Set', 'Create', 'Delete', 'Query', 'Reg',
                             'VirtualAlloc', 'HeapFree', 'kernel32', 'user32')):
        return False
    # 包含空格的多词短语，很可能是界面文字
    if ' ' in s and any(c.isupper() for c in s):
        return True
    # 以大写开头、含小写、长度>=6 的单词
    if s[0].isupper() and any(c.islower() for c in s) and len(s) >= 6:
        return True
    return False


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    if not os.path.exists(EXE_PATH):
        print(f"错误：找不到 {EXE_PATH}")
        print("请确认 NDM 安装路径，并修改脚本顶部的 EXE_PATH 变量。")
        sys.exit(1)

    print(f"读取: {EXE_PATH}")
    data = read_exe(EXE_PATH)
    size = len(data)
    print(f"文件大小: {size} 字节 ({size/1024/1024:.2f} MB)")

    # 提取两种编码的字符串
    utf16 = extract_utf16_strings(data)
    utf8 = extract_utf8_strings(data)
    print(f"UTF-16 字符串: {len(utf16)} 条")
    print(f"UTF-8/ASCII 字符串: {len(utf8)} 条")

    # 筛选可能是界面文字的
    utf16_ui = [(off, s) for off, s in utf16 if is_ui_text(s)]
    utf8_ui = [(off, s) for off, s in utf8 if is_ui_text(s)]
    print(f"UTF-16 疑似界面文字: {len(utf16_ui)} 条")
    print(f"UTF-8 疑似界面文字: {len(utf8_ui)} 条")

    # 写出完整清单
    with open(os.path.join(OUT_DIR, "strings_utf16.txt"), "w", encoding="utf-8") as f:
        f.write(f"# UTF-16 字符串清单（共 {len(utf16)} 条，疑似界面文字 {len(utf16_ui)} 条）\n")
        f.write(f"# 格式：偏移量 | 字符串\n\n")
        for off, s in utf16:
            mark = "  <== UI?" if is_ui_text(s) else ""
            f.write(f"{off:>10} | {s}{mark}\n")

    with open(os.path.join(OUT_DIR, "strings_utf8.txt"), "w", encoding="utf-8") as f:
        f.write(f"# UTF-8/ASCII 字符串清单（共 {len(utf8)} 条，疑似界面文字 {len(utf8_ui)} 条）\n")
        f.write(f"# 格式：偏移量 | 字符串\n\n")
        for off, s in utf8:
            mark = "  <== UI?" if is_ui_text(s) else ""
            f.write(f"{off:>10} | {s}{mark}\n")

    # 生成分析摘要
    summary_path = os.path.join(OUT_DIR, "analysis_result.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("NDM Windows 版 NeatDM.exe 字符串分析摘要\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"文件路径: {EXE_PATH}\n")
        f.write(f"文件大小: {size} 字节 ({size/1024/1024:.2f} MB)\n\n")
        f.write(f"UTF-16 字符串总数: {len(utf16)}\n")
        f.write(f"UTF-8/ASCII 字符串总数: {len(utf8)}\n")
        f.write(f"UTF-16 疑似界面文字: {len(utf16_ui)}\n")
        f.write(f"UTF-8 疑似界面文字: {len(utf8_ui)}\n\n")

        f.write("=" * 60 + "\n")
        f.write("UTF-16 疑似界面文字清单（前 200 条）\n")
        f.write("=" * 60 + "\n")
        for off, s in utf16_ui[:200]:
            f.write(f"{off:>10} | {s}\n")

        f.write("\n" + "=" * 60 + "\n")
        f.write("UTF-8 疑似界面文字清单（前 200 条）\n")
        f.write("=" * 60 + "\n")
        for off, s in utf8_ui[:200]:
            f.write(f"{off:>10} | {s}\n")

        # 额外：搜索一些 NDM 常见界面词，确认编码方式
        f.write("\n" + "=" * 60 + "\n")
        f.write("关键词探测（确认编码方式）\n")
        f.write("=" * 60 + "\n")
        keywords = ["Download", "Settings", "About", "Pause", "Resume",
                    "Cancel", "Browser", "Proxy", "Bandwidth", "Connections",
                    "Neat Download Manager", "Check For Update", "Open Folder"]
        for kw in keywords:
            # UTF-16LE 编码
            kw_u16 = kw.encode('utf-16-le')
            cnt_u16 = data.count(kw_u16)
            # UTF-8/ASCII 编码
            kw_u8 = kw.encode('utf-8')
            cnt_u8 = data.count(kw_u8)
            f.write(f"  {kw:30s} | UTF-16命中: {cnt_u16:3d} | UTF-8命中: {cnt_u8:3d}\n")

    print(f"\n分析完成！结果已写入: {OUT_DIR}")
    print(f"  - analysis_result.txt  （请把这个文件内容贴给我）")
    print(f"  - strings_utf16.txt")
    print(f"  - strings_utf8.txt")


if __name__ == "__main__":
    main()
