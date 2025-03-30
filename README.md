# 📚 番茄小说下载器 | Fanqie Novel Downloader

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/POf-L/Fanqie-Tomato-Downloader?style=flat-square&logo=github)
![GitHub forks](https://img.shields.io/github/forks/POf-L/Fanqie-Tomato-Downloader?style=flat-square&logo=github)
![GitHub issues](https://img.shields.io/github/issues/POf-L/Fanqie-Tomato-Downloader?style=flat-square&logo=github)
![GitHub license](https://img.shields.io/github/license/POf-L/Fanqie-Tomato-Downloader?style=flat-square)
![GitHub last commit](https://img.shields.io/github/last-commit/POf-L/Fanqie-Tomato-Downloader?style=flat-square)
[![Windows Support](https://img.shields.io/badge/Windows-0078D6?style=flat-square&logo=windows&logoColor=white)](https://github.com/POf-L/Fanqie-Tomato-Downloader/releases)
[![MacOS Support](https://img.shields.io/badge/MacOS-000000?style=flat-square&logo=apple&logoColor=white)](https://github.com/POf-L/Fanqie-Tomato-Downloader/releases)
[![Linux Support](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)](https://github.com/POf-L/Fanqie-Tomato-Downloader/releases)

**🌟 高效、优雅且功能强大的番茄小说下载解决方案 🌟**

[✨ 特性](#-特性) •
[🚀 快速开始](#-快速开始) •
[💻 使用指南](#-使用指南) •
[🛠️ 技术架构](#-技术架构) •
[🔄 自动化构建](#-自动化构建) •
[❓ 常见问题](#-常见问题) •
[📜 许可证](#-许可证)

</div>

## ✨ 特性

<table>
  <tr>
    <td width="50%">
      <h3>📚 高质量内容获取</h3>
      <ul>
        <li>支持番茄小说内容下载</li>
        <li>智能解析章节结构与内容</li>
        <li>通过 <code>request_handler.py</code> 与番茄小说服务器交互</li>
        <li>自动处理 Cookie 获取与管理 (<code>cookie.json</code>)</li>
      </ul>
    </td>
    <td width="50%">
      <h3>📖 集成书库与阅读器</h3>
      <ul>
        <li>本地书库管理 (<code>library.py</code>, <code>library.json</code>)，支持添加、删除、搜索</li>
        <li>内置小说阅读器 (<code>reader.py</code>)</li>
        <li>阅读器支持章节跳转、字体/颜色/主题自定义</li>
        <li>自动保存和加载阅读进度</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>
      <h3>⚡ 高效下载引擎</h3>
      <ul>
        <li>多线程并发下载（可配置线程数）</li>
        <li>清晰的下载进度显示</li>
        <li>下载任务在主界面 (<code>gui.py</code>) 中管理</li>
      </ul>
    </td>
    <td>
      <h3>🖥️ 现代化界面</h3>
      <ul>
        <li>基于 <code>customtkinter</code> 构建的现代风格图形界面</li>
        <li>直观友好的用户交互 (<code>gui.py</code>)</li>
        <li>提供启动画面 (<code>splash.py</code>)</li>
        <li>丰富的自定义设置选项 (<code>settings.py</code>, <code>config.py</code>, <code>user_config.json</code>)</li>
        <li>跨平台一致性体验 (Windows, MacOS, Linux)</li>
      </ul>
    </td>
  </tr>
</table>

## 🚀 快速开始

### 🌐 在线下载（零安装，零依赖）

<details>
<summary><b>点击展开详细步骤</b></summary>

利用GitHub Actions的强大功能，无需在本地安装任何软件即可下载小说：

1. 在GitHub仓库页面，点击 **"Actions"** 选项卡
2. 左侧选择 **"在线下载小说"** 工作流 (`.github/workflows/download-novel.yml`)
3. 点击 **"Run workflow"** 按钮
4. 填写以下信息：
   - **小说ID**：从番茄小说网址中获取（例如：`https://fanqienovel.com/page/7105916563` 中的 `7105916563`）
   - **下载线程数**：默认为5，可选1-10
   - **输出格式**：目前仅支持 txt
5. 点击 **"Run workflow"** 开始下载
6. 下载完成后，点击运行记录中的 **"Summary"** 标签
7. 在 **"Artifacts"** 部分找到并下载小说文件（保存期限为7天）

</details>

### 📦 一键式安装与使用

<details>
<summary><b>点击查看各平台预编译版本</b></summary>

从 [📥 官方发布页](https://github.com/POf-L/Fanqie-Tomato-Downloader/releases) 下载适合您系统的预编译版本：

| 平台 | 下载链接 | 说明 |
|------|---------|------|
| Windows | [`Fanqie-Novel-Downloader-Windows.zip`](https://github.com/POf-L/Fanqie-Tomato-Downloader/releases) | 解压后双击运行 `番茄小说下载器.exe` |
| MacOS | [`Fanqie-Novel-Downloader-MacOS.zip`](https://github.com/POf-L/Fanqie-Tomato-Downloader/releases) | 解压后运行 `番茄小说下载器` 应用 |
| Linux | [`Fanqie-Novel-Downloader-Linux.zip`](https://github.com/POf-L/Fanqie-Tomato-Downloader/releases) | 解压后运行 `番茄小说下载器` 可执行文件 |

</details>

### 💻 从源码运行（开发者选项）

<details>
<summary><b>点击展开开发者指南</b></summary>

**依赖:**
*   Python 3.x
*   主要库 (详见 `requirements.txt`):
    *   `customtkinter`: 用于构建图形用户界面
    *   `requests`: 用于发送网络请求
    *   `Pillow`: 用于图像处理 (如图标)
    *   `beautifulsoup4`: 用于解析HTML内容 (如果需要)
    *   `pyinstaller`: (可选) 用于打包成可执行文件

```bash
# 1. 克隆代码仓库
git clone https://github.com/POf-L/Fanqie-Tomato-Downloader.git
cd Fanqie-Tomato-Downloader

# 2. 安装依赖库
pip install -r requirements.txt

# 3. 启动应用
python gui.py
```

</details>

## 💻 使用指南

### 界面概览

*   **主窗口 (`gui.py`)**:
    *   **小说ID输入框**: 输入从番茄小说网站获取的小说ID。
    *   **保存路径**: 选择下载的小说文件保存的位置。
    *   **开始下载**: 启动下载任务。
    *   **打开书库**: 打开本地已下载小说的书库窗口。
    *   **设置**: 打开应用程序设置窗口。
    *   **日志区域**: 显示下载过程中的信息和状态。
    *   **进度条**: 可视化显示当前下载进度。
*   **书库窗口 (`library.py`)**:
    *   显示已添加到书库的小说列表。
    *   提供搜索功能。
    *   按钮：打开小说所在文件夹、阅读小说、从书库移除。
*   **阅读器窗口 (`reader.py`)**:
    *   显示小说内容。
    *   顶部工具栏：章节选择、字体/颜色/背景设置、主题切换。
    *   底部状态栏：显示阅读进度。
*   **设置窗口 (`settings.py`)**:
    *   **下载设置**: 配置默认保存路径、下载线程数等。
    *   **阅读器设置**: 配置阅读器默认字体、颜色等。
    *   **外观设置**: 配置应用程序的主题和颜色。

### 🔍 如何查找小说ID

在番茄小说网站上，打开您想要下载的小说页面，URL中的数字部分就是小说ID。

> 例如：`https://fanqienovel.com/page/7105916563` 中的 `7105916563` 就是小说ID。

### 📂 下载文件位置

- **GUI应用**: 下载的文件保存在您通过设置窗口或主界面指定的“保存路径”中。下载完成后会自动添加到书库。
- **在线下载**: 文件将作为GitHub Artifacts提供下载，保存期限为7天。

## 🛠️ 技术架构

本项目主要使用 Python 和 `customtkinter` 构建。核心模块交互如下：

```mermaid
graph LR
    subgraph UI_Layer 用户界面层
        GUI[主界面 (gui.py)]
        LibWin[书库窗口 (library.py)]
        ReaderWin[阅读器 (reader.py)]
        SettingsWin[设置窗口 (settings.py)]
        Splash[启动画面 (splash.py)]
    end

    subgraph Application_Logic 应用逻辑层
        DownloaderModule[下载模块 (gui.py)]
        LibraryManagerModule[书库管理模块 (library.py)]
        ConfigManagerModule[配置管理模块 (config.py)]
    end

    subgraph Data_Interaction 数据交互层
        RequestHandler[网络请求 (request_handler.py)]
    end

    subgraph Storage_Layer 数据存储层
        UserConfig[用户配置 (user_config.json)]
        LibData[书库数据 (library.json)]
        CookieData[Cookie (cookie.json)]
        NovelFiles[小说文件 (*.txt)]
    end

    GUI --> DownloaderModule
    GUI --> LibWin
    GUI --> SettingsWin
    GUI -- 调用 --> LibraryManagerModule
    GUI -- 调用 --> ConfigManagerModule
    LibWin --> LibraryManagerModule
    LibWin --> ReaderWin
    ReaderWin -- 调用 --> ConfigManagerModule
    SettingsWin -- 调用 --> ConfigManagerModule

    DownloaderModule -- 使用 --> RequestHandler
    LibraryManagerModule -- 使用 --> RequestHandler
    LibraryManagerModule -- 操作 --> LibData
    ConfigManagerModule -- 操作 --> UserConfig
    RequestHandler -- 获取/更新 --> CookieData
    DownloaderModule -- 生成 --> NovelFiles

    style UserConfig fill:#f9f,stroke:#333,stroke-width:2px
    style LibData fill:#f9f,stroke:#333,stroke-width:2px
    style CookieData fill:#f9f,stroke:#333,stroke-width:2px
    style NovelFiles fill:#ccf,stroke:#333,stroke-width:2px
```

*   **UI层**: 使用 `customtkinter` 构建，包含主界面、书库、阅读器、设置和启动画面。
*   **业务逻辑层**: 处理核心功能，如配置加载/保存、书库操作、下载流程控制。
*   **数据交互层**: `request_handler.py` 负责与番茄小说服务器通信，获取书籍信息和章节内容。
*   **数据存储**: 使用 JSON 文件存储用户配置、书库信息和 Cookie，下载的小说保存为 TXT 文件。

## 🔄 自动化构建

本项目采用现代化的CI/CD流程，通过GitHub Actions (`.github/workflows/build-and-release.yml`) 自动构建并发布多平台应用。

### ⚙️ 自动构建流程

当创建新的Release或手动触发工作流时，GitHub Actions会自动：

1. 在Windows、MacOS和Linux三大平台进行并行构建 (使用 `pyinstaller`)
2. 优化可执行文件大小和性能
3. 将构建产物打包为便于分发的压缩文件
4. 上传构建文件并创建正式发布页面

### 🚀 手动触发构建与发布

1. 在GitHub仓库页面，点击 **"Actions"** 选项卡
2. 左侧选择 **"构建与发布"** 工作流
3. 点击 **"Run workflow"** 按钮并填写版本信息
4. 等待自动化流程完成全部构建与发布

## ❓ 常见问题

<details>
<summary><b>遇到下载失败或速度慢的问题</b></summary>

- 尝试在设置中减少并行下载线程数。
- 检查网络连接是否稳定。
- 检查 `cookie.json` 是否有效或尝试清空 Cookie 文件后重试。
- 部分小说可能由于版权或其他原因无法下载。

</details>

<details>
<summary><b>应用无法启动或崩溃</b></summary>

- 确保您下载了正确的操作系统版本。
- 如果从源码运行，请确保所有依赖 (`requirements.txt`) 都已正确安装。
- 检查系统是否满足最低要求。
- 尝试删除 `user_config.json` 和 `library.json` (会丢失配置和书库记录) 后重新启动。
- 尝试重新下载最新版本。

</details>

<details>
<summary><b>EPUB 格式支持?</b></summary>

- 当前版本主要支持下载为 TXT 格式。EPUB 格式转换是未来可能添加的功能。

</details>

## 📜 许可证

本项目采用 [MIT 许可证](LICENSE) 进行授权和分发。

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请考虑给它一个星标！⭐**

[反馈问题](https://github.com/POf-L/Fanqie-Tomato-Downloader/issues) •
[贡献代码](https://github.com/POf-L/Fanqie-Tomato-Downloader/pulls) •
[查看更新](https://github.com/POf-L/Fanqie-Tomato-Downloader/releases)

</div>
