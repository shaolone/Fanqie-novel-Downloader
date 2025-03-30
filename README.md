# 📚 番茄小说下载器 | Fanqie Novel Downloader

<div align="center">

[![GitHub stars](https://img.shields.io/github/stars/POf-L/Fanqie-Tomato-Downloader?style=flat-square&logo=github)](https://github.com/POf-L/Fanqie-Tomato-Downloader/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/POf-L/Fanqie-Tomato-Downloader?style=flat-square&logo=github)](https://github.com/POf-L/Fanqie-Tomato-Downloader/network/members)
[![GitHub issues](https://img.shields.io/github/issues/POf-L/Fanqie-Tomato-Downloader?style=flat-square&logo=github)](https://github.com/POf-L/Fanqie-Tomato-Downloader/issues)
[![GitHub license](https://img.shields.io/github/license/POf-L/Fanqie-Tomato-Downloader?style=flat-square)](LICENSE)
[![GitHub last commit](https://img.shields.io/github/last-commit/POf-L/Fanqie-Tomato-Downloader?style=flat-square)](https://github.com/POf-L/Fanqie-Tomato-Downloader/commits/main)

[![Windows Support](https://img.shields.io/badge/Windows-0078D6?style=flat-square&logo=windows&logoColor=white)](https://github.com/POf-L/Fanqie-Tomato-Downloader/releases)
[![MacOS Support](https://img.shields.io/badge/MacOS-000000?style=flat-square&logo=apple&logoColor=white)](https://github.com/POf-L/Fanqie-Tomato-Downloader/releases)
[![Linux Support](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)](https://github.com/POf-L/Fanqie-Tomato-Downloader/releases)

**🌟 高效、优雅且功能强大的番茄小说下载解决方案 🌟**

</div>

## ✨ 特性

|  |  |
|---|---|
| **📚 高质量内容获取** | **🔄 多格式转换** |
| * 支持番茄小说全平台内容下载  | * 支持输出纯净 TXT 格式 |
| * 智能解析章节结构与内容 | * 生成精美排版的 EPUB 电子书 |
| * 自动校正小说格式与标点 | * 保留原书籍章节结构 |
| **⚡ 高效下载引擎** | **🖥️ 界面体验** |
| * 多线程并发下载技术 | * 直观友好的图形界面 |
| * 智能调节网络请求频率 | * 实时下载进度可视化 |
| * 断点续传与状态恢复 | * 跨平台一致性体验 |

## 🚀 快速开始

### 🌐 在线下载

<details>
<summary><b>零安装，零依赖，点击展开详细步骤</b></summary>

利用 GitHub Actions 即可在线下载小说，无需本地安装任何软件！

1.  访问 GitHub 仓库页面，点击 **"Actions"** 选项卡。
2.  在左侧导航栏，选择 **"在线下载小说"** 工作流。
3.  点击 **"Run workflow"** 按钮，根据提示填写：
    -   **小说 ID**：从番茄小说网址获取 (例如 `https://fanqienovel.com/page/7105916563` 的 `7105916563`)。
    -   **下载线程数**：默认为 5，可选 1-10。
    -   **输出格式**：选择 `txt` 或 `epub`。
4.  点击 **"Run workflow"** 开始下载。
5.  下载完成后，在 Actions 运行记录的 **"Summary"** 标签页中，找到 **"Artifacts"**  部分，下载小说文件 (7天有效期)。

</details>

### 📦 客户端下载

<details>
<summary><b>一键安装，点击查看各平台预编译版本</b></summary>

无需 Python 环境，下载即用！

访问 [📥 官方发布页](https://github.com/POf-L/Fanqie-Tomato-Downloader/releases) 下载预编译版本：

| 平台    | 下载链接                                                                                                | 说明                                        |
| ------- | ------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| Windows | [`Fanqie-Novel-Downloader-Windows.zip`](https://github.com/POf-L/Fanqie-Tomato-Downloader/releases) | 解压后双击运行 `番茄小说下载器.exe`          |
| MacOS   | [`Fanqie-Novel-Downloader-MacOS.zip`](https://github.com/POf-L/Fanqie-Tomato-Downloader/releases)   | 解压后运行 `番茄小说下载器` 应用              |
| Linux   | [`Fanqie-Novel-Downloader-Linux.zip`](https://github.com/POf-L/Fanqie-Tomato-Downloader/releases)   | 解压后运行 `番茄小说下载器` 可执行文件        |

</details>

### 💻 开发者选项

<details>
<summary><b>从源码运行，点击展开开发者指南</b></summary>

```bash
# 1. 克隆代码仓库
git clone https://github.com/POf-L/Fanqie-Tomato-Downloader.git
cd Fanqie-Tomato-Downloader

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动应用
python gui.py
```

</details>

## 💻 使用指南

### 🔍 如何查找小说 ID？

在番茄小说网站，打开想要下载的小说页面，浏览器地址栏 URL 中的数字即为小说 ID。

>  **示例：** `https://fanqienovel.com/page/7105916563`  的 ID 为 `7105916563`。

### 📂 文件保存位置？

- **GUI 客户端**：文件保存在您在设置中指定的路径。
- **在线下载**：文件将作为 GitHub Artifacts 提供下载 (7 天有效期)。

## 🛠️ 技术架构

本项目基于 Python 和 `customtkinter` 构建，采用分层架构：

```mermaid
graph LR
    subgraph UI_Layer 用户界面层
        GUI_Module[主界面模块 (gui.py)]
        LibraryWindowModule[书库窗口模块 (library.py)]
        ReaderWindowModule[阅读器模块 (reader.py)]
        SettingsDialogModule[设置对话框模块 (settings.py)]
        SplashScreenModule[启动画面模块 (splash.py)]
    end

    subgraph Application_Logic 应用逻辑层
        DownloaderLogic[下载逻辑模块 (gui.py)]
        LibraryManager[书库管理模块 (library.py)]
        ConfigManager[配置管理模块 (config.py)]
    end

    subgraph Data_Interaction 数据交互层
        RequestHandlerModule[请求处理模块 (request_handler.py)]
    end

    subgraph Storage_Layer 数据存储层
        UserConfig[用户配置 (user_config.json)]
        LibData[书库数据 (library.json)]
        CookieData[Cookie数据 (cookie.json)]
        NovelFiles[小说文件 (*.txt, *.epub)]
    end

    GUI_Module --> DownloaderLogic
    GUI_Module --> LibraryWindowModule
    GUI_Module --> SettingsDialogModule
    GUI_Module -- 调用 --> LibraryManager
    GUI_Module -- 调用 --> ConfigManager
    LibraryWindowModule --> LibraryManager
    LibraryWindowModule --> ReaderWindowModule
    ReaderWindowModule -- 调用 --> ConfigManager
    SettingsDialogModule --> ConfigManager

    DownloaderLogic -- 使用 --> RequestHandlerModule
    LibraryManager -- 使用 --> RequestHandlerModule
    LibraryManager -- 操作 --> LibData
    ConfigManager -- 操作 --> UserConfig
    RequestHandlerModule -- 获取/更新 --> CookieData
    DownloaderLogic -- 生成 --> NovelFiles

    style UserConfig fill:#f9f,stroke:#333,stroke-width:2px
    style LibData fill:#f9f,stroke:#333,stroke-width:2px
    style CookieData fill:#f9f,stroke:#333,stroke-width:2px
    style NovelFiles fill:#ccf,stroke:#333,stroke-width:2px
```

*   **UI 层**：`customtkinter` 构建图形界面。
*   **应用逻辑层**：核心业务逻辑，控制下载、书库、配置等。
*   **数据交互层**：`request_handler.py` 负责网络请求和数据处理。
*   **数据存储层**：JSON 和 TXT/EPUB 文件存储数据。

## 🔄 自动化构建

GitHub Actions 实现 CI/CD，`build-and-release.yml` 定义构建流程。

### ⚙️ 自动构建流程

1.  **平台兼容**：支持 Windows, macOS, Linux。
2.  **环境配置**：自动配置 Python 环境和依赖。
3.  **代码编译**：PyInstaller 打包 Python 代码。
4.  **性能优化**：优化体积和性能。
5.  **版本发布**：上传到 GitHub Releases。

### 🚀 手动构建与发布

1.  **Actions 页面**：在 GitHub 仓库 Actions 页面选择 "build-and-release" 工作流。
2.  **运行工作流**：点击 "Run workflow"，填写版本信息。
3.  **等待完成**：等待 GitHub Actions 完成构建和发布。

## ❓ 常见问题

<details>
<summary><b>下载失败或速度慢？</b></summary>

* 检查网络连接。
* 调整设置中线程数。
* 尝试分批下载或稍后重试。

</details>

<details>
<summary><b>程序启动异常？</b></summary>

* 检查操作系统版本兼容性。
* 源码运行检查依赖安装。
* 系统配置是否满足最低要求。
* 重新下载最新发布版。

</details>

## 📜 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

---

<p align="center">

**⭐ 觉得好用？请 Star 支持一下！⭐** 

[GitHub 仓库](https://github.com/POf-L/Fanqie-Tomato-Downloader) | [问题反馈](https://github.com/POf-L/Fanqie-Tomato-Downloader/issues)

</p>
