#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NDM exe 字符串字节布局验证脚本
================================
作用：检查几个关键界面字符串在 exe 里的实际字节布局，
      确认它们前后是否有 \x00 填充、是否有长度前缀，
      从而确定安全的替换策略。

使用方法：
    python verify_layout.py
    运行完会生成 work\layout_report.txt，把内容贴给我
"""

import os
import sys

EXE_PATH = r"C:\Program Files (x86)\Neat Download Manager\NeatDM.exe"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    if not os.path.exists(EXE_PATH):
        print(f"错误：找不到 {EXE_PATH}")
        sys.exit(1)

    with open(EXE_PATH, "rb") as f:
        data = f.read()

    # 要验证的字符串（来自分析结果，带前导字母的）
    # 格式：(描述, UTF-16LE 字节序列, 预期偏移)
    targets = [
        ("Check For Update", "Check For Update".encode('utf-16-le'), 1459792),
        ("Open Folder", "Open Folder".encode('utf-16-le'), 1462826),
        ("Download Completed", "Download Completed".encode('utf-16-le'), 1462852),
        ("About NeatDownloadManager", "About NeatDownloadManager".encode('utf-16-le'), 1459328),
        ("( Basic Version - Free License )", "( Basic Version - Free License )".encode('utf-16-le'), 1459832),
        ("Add Chrome Extension", "Add Chrome Extension".encode('utf-16-le'), 1461436),
        ("Neat Download Manager Settings", "Neat Download Manager Settings".encode('utf-16-le'), 1468560),
        ("Max Connections per Download", "Max Connections per Download".encode('utf-16-le'), 1468728),
        ("Download Properties", "Download Properties".encode('utf-16-le'), 1467402),
        ("Quit Application Totally", "Quit Application Totally".encode('utf-16-le'), 1468304),
    ]

    report_path = os.path.join(OUT_DIR, "layout_report.txt")
    with open(report_path, "w", encoding="utf-8") as out:
        out.write("=" * 70 + "\n")
        out.write("NDM exe 字符串字节布局验证报告\n")
        out.write("=" * 70 + "\n\n")

        for desc, needle, expected_off in targets:
            # 在整个文件里搜索
            actual_off = data.find(needle)
            out.write(f"--- {desc!r} ---\n")
            out.write(f"  预期偏移: {expected_off}\n")
            out.write(f"  实际偏移: {actual_off}\n")

            if actual_off == -1:
                out.write(f"  状态: 未找到！\n\n")
                continue

            # 检查字符串前面的字节（前 8 字节）
            pre_start = max(0, actual_off - 8)
            pre = data[pre_start:actual_off]
            out.write(f"  前 8 字节: {pre!r}\n")
            out.write(f"  前 8 字节(hex): {pre.hex(' ')}\n")

            # 字符串本身的字节
            slen = len(needle)
            out.write(f"  字符串字节长度: {slen} (={len(desc)} 字符 × 2)\n")

            # 检查字符串后面的字节（后 16 字节）
            post_start = actual_off + slen
            post = data[post_start:post_start + 16]
            out.write(f"  后 16 字节: {post!r}\n")
            out.write(f"  后 16 字节(hex): {post.hex(' ')}\n")

            # 统计后面连续的 \x00 数量
            zero_count = 0
            i = post_start
            while i < len(data) and data[i] == 0:
                zero_count += 1
                i += 1
            out.write(f"  字符串后连续 \\x00 数量: {zero_count}\n")

            # 判断：如果后面紧跟 \x00\x00（UTF-16 的空终止符），说明是标准 C 字符串
            # 如果后面紧跟另一个可打印字符，说明是连续存储的字符串表
            if zero_count >= 2:
                out.write(f"  推断: 标准空终止 UTF-16 字符串（后跟 \\x00\\x00）\n")
            elif zero_count == 0 and post[0:1] != b'\x00':
                # 看后面是不是另一个字符串的开头
                try:
                    nxt = post[0:2].decode('utf-16-le')
                    if nxt.isprintable():
                        out.write(f"  推断: 连续字符串表，后接字符 {nxt!r}（可能是下一个字符串）\n")
                except:
                    pass
            out.write("\n")

        # 额外：检查两个相邻字符串之间的边界
        out.write("=" * 70 + "\n")
        out.write("相邻字符串边界检查\n")
        out.write("=" * 70 + "\n\n")

        # Check For Update (1459792) 和 ( Basic Version... (1459832) 之间
        s1 = "Check For Update".encode('utf-16-le')
        o1 = data.find(s1)
        s2 = "( Basic Version - Free License )".encode('utf-16-le')
        o2 = data.find(s2)
        if o1 != -1 and o2 != -1:
            gap = data[o1 + len(s1):o2]
            out.write(f"'Check For Update' 结束 → '( Basic Version...)' 开始\n")
            out.write(f"  间隔字节: {gap!r} (长度 {len(gap)})\n")
            out.write(f"  间隔字节(hex): {gap.hex(' ')}\n\n")

        # Open Folder (1462826) 和 Download Completed (1462852)
        s3 = "Open Folder".encode('utf-16-le')
        o3 = data.find(s3)
        s4 = "Download Completed".encode('utf-16-le')
        o4 = data.find(s4)
        if o3 != -1 and o4 != -1:
            gap2 = data[o3 + len(s3):o4]
            out.write(f"'Open Folder' 结束 → 'Download Completed' 开始\n")
            out.write(f"  间隔字节: {gap2!r} (长度 {len(gap2)})\n")
            out.write(f"  间隔字节(hex): {gap2.hex(' ')}\n\n")

    print(f"验证完成！结果已写入: {report_path}")
    print(f"请把 {report_path} 的内容贴给我")


if __name__ == "__main__":
    main()
