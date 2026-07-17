# Neat Download Manager (Windows 版) 中文汉化

> Neat Download Manager (NDM) Windows 版界面简体中文汉化补丁

## 项目简介

Neat Download Manager 是一款免费的 Windows/macOS 下载管理器，支持多线程下载、断点续传、浏览器扩展集成等功能。官方仅提供英文界面，本项目为其 **Windows 版** 提供简体中文汉化。

本项目通过直接修改 `NeatDM.exe` 可执行文件中的 UTF-16LE 编码字符串，实现界面汉化。

> 本项目同时保留原 macOS 版汉化方案（见 `translate_nib.py` / `translated_nibs/`），以下文档针对 **Windows 版**。

## 参考项目

本项目参考了以下 macOS 版汉化项目的思路：

- **[NeatDownloadManager-zh](https://github.com/hardwin2023/NeatDownloadManager-zh)** —— macOS 版 NDM 中文汉化补丁，本项目在其基础上扩展了 Windows 版的汉化支持。

## 声明

> ⚠️ **本项目代码由 AI 辅助编写。**
>
> 汉化脚本、分析工具、安装脚本及说明文档均借助 AI 工具生成并经人工测试验证。代码逻辑、翻译内容和技术方案由 AI 协助完成，使用者请自行评估风险。
>
> 本项目仅提供汉化补丁，不包含 Neat Download Manager 本身。Neat Download Manager 的版权归其原作者 Javad Motallebi 所有。

---

## 系统要求

- Windows 10 / 11（64 位或 32 位均可）
- Neat Download Manager 1.4.24（Windows 版）
- Python 3.6+（[下载地址](https://www.python.org/downloads/)，安装时勾选 "Add Python to PATH"）
- 管理员权限（修改 Program Files 下的文件需要）

---

## 快速使用

### 方式一：一键汉化（推荐，适合小白）

1. **关闭正在运行的 Neat Download Manager**
2. **双击运行 `中文汉化安装器.bat`**
3. 弹出管理员权限确认时，点击"是"
4. 脚本会自动完成：检查环境 → 关闭 NDM → 备份原文件 → 汉化
5. 看到"汉化完成"提示后，启动 NDM 即可看到中文界面

### 方式二：手动运行

以管理员身份打开 cmd 或 PowerShell：

```cmd
cd /d "你的项目路径"
python translate_ndm_win.py
```

---

## 恢复英文原版

如果汉化后出现问题，或想恢复英文原版：

### 方式一：一键恢复

双击运行 `恢复英文原版`（同样需要管理员权限）。

### 方式二：手动恢复

```cmd
python restore_ndm_win.py
```

### 方式三：重新安装

从官网 https://neatdownloadmanager.com 重新下载安装，会覆盖汉化版本。

---

## 文件说明

| 文件 | 作用 |
|------|------|
| `translate_ndm_win.py` | **核心汉化脚本**：读取 exe → 替换字符串 → 备份 → 写回 |
| `restore_ndm_win.py` | 恢复英文原版脚本：从备份还原 exe |
| `中文汉化安装器.bat` | 一键汉化批处理（自动请求管理员权限） |
| `恢复英文原版.bat` | 一键恢复批处理（自动请求管理员权限） |
| `analyze_ndm.py` | 字符串分析工具（开发用，提取 exe 中的英文字符串） |
| `verify_layout.py` | 字节布局验证工具（开发用，确认字符串存储格式） |
| `work/` | 运行时目录，存放备份文件和分析结果 |

---

## 技术原理

### Windows 版和 macOS 版的区别

| | macOS 版 | Windows 版 |
|---|---------|-----------|
| 界面技术 | NIB 文件（二进制 plist） | 直接硬编码在 exe 中 |
| 字符串编码 | NSKeyedArchiver 格式 | UTF-16LE |
| 修改方式 | 用 plistlib 解析替换 | 按字节查找替换 |
| 签名问题 | 需重新 ad-hoc 签名 | 无签名问题 |

### 汉化原理（用小白的话讲）

1. **界面文字存在哪里？**
   Windows 版 NDM 的所有界面文字都硬编码在 `NeatDM.exe` 这个文件里，没有外部资源文件。

2. **文字用什么编码？**
   用 UTF-16LE 编码（每个字符占 2 个字节，英文字符第二个字节是 `\x00`）。每个字符串以 `\x00\x00` 结尾（空终止符），字符串之间有 `\x00` 填充对齐。

3. **怎么替换？**
   - 把英文转成 UTF-16LE 字节，在 exe 里找到它的位置
   - 用中文的 UTF-16LE 字节替换
   - 如果中文比英文短，多出来的位置用 `\x00` 填充（保持文件长度不变）
   - 如果中文比英文长，跳过该条（避免破坏 exe 结构）

4. **为什么安全？**
   - 替换时使用"英文 + 空终止符"精确匹配，不会误伤包含该词的长字符串
   - 文件总长度始终保持不变
   - 替换前自动备份原文件

---

## 自定义翻译

如果你想修改某些翻译用语，编辑 `translate_ndm_win.py` 中的 `TRANSLATIONS` 字典：

```python
TRANSLATIONS = {
    "About NeatDownloadManager": "关于 NeatDownloadManager",  # 修改右侧中文
    "Settings": "设置",
    "Download": "下载",
    # ... 添加或修改翻译
}
```

修改后重新运行 `中文汉化安装器.bat` 即可。

### 注意事项

- **英文必须和 exe 里存储的完全一致**（包括空格、标点），否则匹配不到
- **中文不能比英文长太多**（UTF-16LE 字节数不能超过原字符串 + 填充空间），否则会被跳过
- 如果不确定 exe 里有哪些字符串，运行 `python analyze_ndm.py` 可以提取完整清单

---

## 已知限制

1. **错误信息未汉化**：大量下载错误信息（如 "Connection TimeOut."、"SSL HandShake Error." 等）未汉化。这些字符串较多且可能影响问题排查，建议保留英文。如需汉化，可在 `TRANSLATIONS` 中添加对应条目。

2. **NDM 更新会覆盖汉化**：每次 NDM 更新后，需重新运行汉化脚本。

3. **版本兼容性**：本补丁针对 NDM 1.4.24 (Windows) 开发。其他版本的字符串偏移可能不同，但脚本使用动态查找（非固定偏移），有一定兼容性。如果新版本界面文字有变化，需更新翻译表。

4. **杀毒软件可能误报**：修改 exe 文件可能被部分杀毒软件标记。这是正常现象，可添加信任。

---

## 常见问题

**Q: 运行脚本报"没有写入权限"怎么办？**
A: 需要以管理员身份运行。双击 `install_win.bat` 会自动请求管理员权限；或手动以管理员身份打开 cmd 再运行 Python 脚本。

**Q: 汉化后 NDM 闪退怎么办？**
A: 可能是 exe 被损坏。运行 `restore_win.bat` 恢复原版，然后重新汉化。如果仍然闪退，请把汉化脚本的输出信息反馈给我。

**Q: 部分界面还是英文怎么办？**
A: 有些文字可能是动态生成的（程序运行时拼接），不在静态字符串里。可以运行 `analyze_ndm.py` 查看完整字符串清单，确认是否有遗漏，然后在翻译表中补充。

**Q: 支持其他版本的 NDM 吗？**
A: 脚本使用动态字符串查找，不依赖固定偏移量，理论上兼容 1.4.x 系列。但不同版本的字符串内容可能略有差异，如遇问题请反馈。

**Q: 汉化会影响下载功能吗？**
A: 不会。汉化只修改界面显示文字，不涉及任何功能逻辑代码。

---

## 许可证

本项目仅提供汉化补丁，不包含 Neat Download Manager 本身。Neat Download Manager 的版权归其原作者 Javad Motallebi 所有。

汉化补丁代码采用 MIT 许可证发布，可自由使用、修改和分发。

---

## 致谢

- [Neat Download Manager](https://neatdownloadmanager.com) —— 感谢 Javad Motallebi 开发的优秀免费下载管理器
- [NeatDownloadManager-zh (macOS 版)](https://github.com/hardwin2023/NeatDownloadManager-zh) —— 本项目参考了其 macOS 版汉化思路
- 本项目代码由 AI 辅助编写，经人工测试验证
