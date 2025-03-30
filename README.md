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
    <td>
      <h3>📚 高质量内容获取</h3>
      <ul>
        <li>支持番茄小说全平台内容下载</li>
        <li>智能解析章节结构与内容</li>
        <li>自动校正小说格式与标点</li>
      </ul>
    </td>
    <td>
      <h3>🔄 多格式转换</h3>
      <ul>
        <li>支持输出纯净TXT格式</li>
        <li>生成精美排版的EPUB电子书</li>
        <li>保留原书籍章节结构</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>
      <h3>⚡ 高效下载引擎</h3>
      <ul>
        <li>多线程并发下载技术</li>
        <li>智能调节网络请求频率</li>
        <li>断点续传与状态恢复</li>
      </ul>
    </td>
    <td>
      <h3>🖥️ 界面体验</h3>
      <ul>
        <li>直观友好的图形界面</li>
        <li>实时下载进度可视化</li>
        <li>跨平台一致性体验</li>
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
2. 左侧选择 **"在线下载小说"** 工作流
3. 点击 **"Run workflow"** 按钮
4. 填写以下信息：
   - **小说ID**：从番茄小说网址中获取（例如：`https://fanqienovel.com/page/7105916563` 中的 `7105916563`）
   - **下载线程数**：默认为5，可选1-10
   - **输出格式**：选择txt或epub
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

### 🔍 如何查找小说ID

在番茄小说网站上，打开您想要下载的小说页面，URL中的数字部分就是小说ID。

> 例如：`https://fanqienovel.com/page/7105916563` 中的 `7105916563` 就是小说ID。

### 📂 下载文件位置

- **GUI应用**：下载的文件保存在您指定的保存路径中
- **在线下载**：文件将作为GitHub Artifacts提供下载，保存期限为7天

## 🛠️ 技术架构

本项目主要使用 Python 和 `customtkinter` 构建。核心模块交互如下：

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
        NovelFiles[小说文件 (*.txt)]
    end

    GUI_Module --> DownloaderLogic
    GUI_Module --> LibraryWindowModule
    GUI_Module --> SettingsDialogModule
    GUI_Module -- 调用 --> LibraryManager
    GUI_Module -- 调用 --> ConfigManager
    LibraryWindowModule --> LibraryManager
    LibraryWindowModule --> ReaderWindowModule
    ReaderWindowModule -- 调用 --> ConfigManager
    SettingsDialogModule --> 调用 --> ConfigManager

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

*   **UI层**：使用 `customtkinter` 构建，包含主界面、书库、阅读器、设置和启动画面。
*   **应用逻辑层**：处理核心功能，包括下载流程控制、书库管理、配置加载与保存等。
*   **数据交互层**：`request_handler.py` 负责与外部数据源（番茄小说服务器、API）进行通信。
*   **数据存储层**：使用 JSON 文件和 TXT 文件分别存储配置、书库信息、Cookie 及小说内容。

## 🔄 自动化构建

本项目采用 GitHub Actions 进行自动化构建和发布流程，`build-and-release.yml` 描述了详细的构建步骤。

### ⚙️ 自动构建流程

1.  **多平台构建**：支持 Windows、macOS 和 Linux 三大平台并行构建。
2.  **环境配置**：设置 Python 环境，安装依赖，为不同平台配置构建环境。
3.  **代码打包**：使用 PyInstaller 将 Python 代码打包为独立可执行文件。
4.  **资源优化**：优化构建产物体积和运行性能。
5.  **版本发布**：自动上传构建好的文件到 GitHub Release 页面。

### 🚀 手动触发构建与发布

1.  **GitHub Actions 页面**：在仓库 Actions 页面找到 "build-and-release" 工作流。
2.  **手动运行**：点击 "Run workflow" 手动触发构建流程。
3.  **填写版本信息**：根据提示填写 Release 版本号等信息。
4.  **等待完成**：等待 GitHub Actions 自动完成构建和发布。

## ❓ 常见问题

<details>
<summary><b>遇到下载问题？</b></summary>

-   **检查网络**：确保网络连接正常。
-   **线程调整**：尝试在设置中调整下载线程数。
-   **Cookie**：检查或清除 `cookie.json` 文件，重新获取 Cookie。
-   **API 限制**：部分小说可能存在下载限制，请更换其他源或稍后重试。

</details>

<details>
<summary><b>程序启动异常？</b></summary>

-   **版本兼容**：确认下载版本与操作系统匹配。
-   **依赖安装**：源码运行请检查 `requirements.txt` 依赖是否安装完整。
-   **系统环境**：确保系统满足运行最低配置要求。
-   **文件完整性**：尝试重新下载发布版本，避免文件损坏。

</details>

## 📜 许可证

本项目基于 [MIT License](LICENSE) 开源，您可以自由使用和修改。

---

<div align="center">

**⭐ 感谢您的使用，欢迎 Star 项目以支持维护和更新！⭐**

[GitHub 仓库](https://github.com/POf-L/Fanqie-Tomato-Downloader) | [问题反馈](https://github.com/POf-L/Fanqie-Tomato-Downloader/issues)

</div>
