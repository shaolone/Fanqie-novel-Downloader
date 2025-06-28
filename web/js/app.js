// 番茄小说下载器 - 主要JavaScript文件

class FanqieDownloader {
    constructor() {
        this.apiBase = 'http://localhost:5000';
        this.currentTask = null;
        this.progressInterval = null;
        this.settings = this.loadSettings();
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadInitialData();
        this.applySettings();
    }

    // 绑定事件
    bindEvents() {
        // 导航切换
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const tab = link.dataset.tab;
                this.switchTab(tab);
            });
        });

        // 移动端导航切换
        document.querySelector('.nav-toggle').addEventListener('click', () => {
            document.querySelector('.nav-menu').classList.toggle('active');
        });

        // 下载相关事件
        document.getElementById('check-btn').addEventListener('click', () => this.checkNovel());
        document.getElementById('download-btn').addEventListener('click', () => this.startDownload());
        document.getElementById('book-id').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.checkNovel();
        });

        // 进度控制
        document.getElementById('pause-btn').addEventListener('click', () => this.pauseDownload());
        document.getElementById('cancel-btn').addEventListener('click', () => this.cancelDownload());
        document.getElementById('download-file-btn').addEventListener('click', () => this.downloadFile());
        document.getElementById('new-download-btn').addEventListener('click', () => this.newDownload());

        // 书库相关
        document.getElementById('refresh-library').addEventListener('click', () => this.loadLibrary());
        document.getElementById('library-search').addEventListener('input', (e) => this.searchLibrary(e.target.value));

        // 设置相关
        document.getElementById('save-settings').addEventListener('click', () => this.saveSettings());
        document.getElementById('reset-settings').addEventListener('click', () => this.resetSettings());

        // 设置实时预览
        document.getElementById('batch-size').addEventListener('input', (e) => this.previewSetting('batchSize', e.target.value));
        document.getElementById('retry-count').addEventListener('input', (e) => this.previewSetting('retryCount', e.target.value));
        document.getElementById('download-delay').addEventListener('input', (e) => this.previewSetting('downloadDelay', e.target.value));
        document.getElementById('api-endpoint').addEventListener('input', (e) => this.previewSetting('apiEndpoint', e.target.value));
        document.getElementById('debug-mode').addEventListener('change', (e) => this.previewSetting('debugMode', e.target.checked));

        // 模态框
        document.getElementById('modal-close').addEventListener('click', () => this.hideModal());
        document.getElementById('modal-cancel').addEventListener('click', () => this.hideModal());
        document.getElementById('modal-overlay').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) this.hideModal();
        });

        // 清空历史
        document.getElementById('clear-history').addEventListener('click', () => this.clearHistory());
    }

    // 加载初始数据
    async loadInitialData() {
        await Promise.all([
            this.loadStats(),
            this.loadLibrary(),
            this.loadHistory()
        ]);
    }

    // 切换标签页
    switchTab(tabName) {
        // 更新导航状态
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // 更新内容区域
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');

        // 特定页面的加载逻辑
        if (tabName === 'library') {
            this.loadLibrary();
        } else if (tabName === 'history') {
            this.loadHistory();
        }

        // 关闭移动端菜单
        document.querySelector('.nav-menu').classList.remove('active');
    }

    // 检查小说
    async checkNovel() {
        const bookId = document.getElementById('book-id').value.trim();
        if (!bookId) {
            this.showNotification('请输入小说ID', 'error');
            return;
        }

        this.showLoading();
        
        try {
            const response = await fetch(`${this.apiBase}/api/check_novel`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ book_id: bookId })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showBookPreview(result.data);
                document.getElementById('download-btn').disabled = false;
            } else {
                this.showNotification(result.message, 'error');
                this.hideBookPreview();
            }
        } catch (error) {
            this.showNotification('检查失败：' + error.message, 'error');
            this.hideBookPreview();
        } finally {
            this.hideLoading();
        }
    }

    // 显示书籍预览
    showBookPreview(bookData) {
        
        const preview = document.getElementById('book-preview');
        const title = document.getElementById('book-title');
        const author = document.getElementById('book-author');
        const status = document.getElementById('book-status');
        const chapters = document.getElementById('book-chapters');

        title.textContent = bookData.book_name || '未知小说';
        author.textContent = bookData.author || '未知作者';
        chapters.textContent = `${bookData.total_chapters || 0} 章节`;
        
        
        if (bookData.exists) {
            status.textContent = '已下载';
            status.className = 'status downloaded';
            document.getElementById('force-download').checked = false;
        } else {
            status.textContent = '未下载';
            status.className = 'status not-downloaded';
        }

        preview.style.display = 'block';
    }

    // 隐藏书籍预览
    hideBookPreview() {
        document.getElementById('book-preview').style.display = 'none';
        document.getElementById('download-btn').disabled = true;
    }

    // 开始下载
    async startDownload() {
        const bookId = document.getElementById('book-id').value.trim();
        const forceDownload = document.getElementById('force-download').checked;

        if (!bookId) {
            this.showNotification('请输入小说ID', 'error');
            return;
        }

        // 获取当前设置
        const downloadSettings = {
            batch_size: parseInt(this.settings.batchSize),
            retry_count: parseInt(this.settings.retryCount),
            download_delay: parseInt(this.settings.downloadDelay)
        };

        // 调试模式显示设置信息
        if (this.settings.debugMode) {
            console.log('当前设置对象:', this.settings);
            console.log('下载设置:', downloadSettings);
            console.log('批量大小原始值:', this.settings.batchSize);
            console.log('批量大小转换后:', downloadSettings.batch_size);
            this.showNotification(`调试模式：批量大小=${downloadSettings.batch_size}，重试次数=${downloadSettings.retry_count}，下载间隔=${downloadSettings.download_delay}秒`, 'info');
        }

        try {
            const requestBody = { 
                book_id: bookId,
                force_download: forceDownload,
                settings: downloadSettings
            };
            
            if (this.settings.debugMode) {
                console.log('发送到后端的请求体:', requestBody);
            }
            
            const response = await fetch(`${this.apiBase}/api/download`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            const result = await response.json();
            
            if (result.success) {
                this.currentTask = result.data.task_id;
                this.showDownloadProgress(result.data);
                this.startProgressMonitoring();
                this.showNotification('下载任务已启动', 'success');
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            if (this.settings.debugMode) {
                console.error('下载请求失败:', error);
            }
            this.showNotification('下载失败：' + error.message, 'error');
        }
    }

    // 显示下载进度
    showDownloadProgress(taskData) {
        document.querySelector('.download-form').style.display = 'none';
        document.getElementById('book-preview').style.display = 'none';
        document.getElementById('download-complete').style.display = 'none';
        
        const progressSection = document.getElementById('download-progress');
        progressSection.style.display = 'block';
        
        document.getElementById('progress-title').textContent = `正在下载：${taskData.title}`;
        document.getElementById('start-time').textContent = new Date().toLocaleString();
        
        // 调试模式显示调试信息
        if (this.settings.debugMode) {
            document.getElementById('debug-info').style.display = 'block';
            document.getElementById('debug-task-id').textContent = this.currentTask || '--';
            document.getElementById('debug-api-url').textContent = this.apiBase;
            document.getElementById('debug-settings').textContent = `批量:${this.settings.batchSize}, 重试:${this.settings.retryCount}, 间隔:${this.settings.downloadDelay}s`;
        } else {
            document.getElementById('debug-info').style.display = 'none';
        }
        
        this.updateProgress(0, '准备中', 0, taskData.total_chapters || 0);
    }

    // 更新进度
    updateProgress(progress, status, downloaded, total) {
        document.getElementById('progress-fill').style.width = `${progress}%`;
        document.getElementById('progress-text').textContent = `${progress}%`;
        document.getElementById('download-status').textContent = status;
        document.getElementById('chapter-progress').textContent = `${downloaded} / ${total}`;
        
        // 调试模式显示详细信息
        if (this.settings.debugMode) {
            console.log(`进度更新: ${progress}%, 状态: ${status}, 已下载: ${downloaded}/${total}`);
        }
    }

    // 开始进度监控
    startProgressMonitoring() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }

        this.progressInterval = setInterval(async () => {
            if (!this.currentTask) return;

            try {
                const response = await fetch(`${this.apiBase}/api/status/${this.currentTask}`);
                const result = await response.json();

                if (result.success) {
                    this.updateProgress(
                        result.progress,
                        result.status,
                        result.downloaded_chapters,
                        result.total_chapters
                    );

                    // 调试模式显示详细状态
                    if (this.settings.debugMode) {
                        console.log('任务状态详情:', {
                            task_id: this.currentTask,
                            status: result.status,
                            progress: result.progress,
                            downloaded: result.downloaded_chapters,
                            total: result.total_chapters,
                            error: result.error_message,
                            start_time: result.start_time,
                            end_time: result.end_time
                        });
                    }

                    // 检查是否完成
                    if (result.status === 'completed') {
                        this.showDownloadComplete(true, '下载完成！');
                        this.stopProgressMonitoring();
                        this.loadStats();
                        this.loadLibrary();
                    } else if (result.status === 'failed') {
                        this.showDownloadComplete(false, result.error_message || '下载失败');
                        this.stopProgressMonitoring();
                    }
                }
            } catch (error) {
                if (this.settings.debugMode) {
                    console.error('获取进度失败:', error);
                }
            }
        }, 2000);
    }

    // 停止进度监控
    stopProgressMonitoring() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
    }

    // 显示下载完成
    showDownloadComplete(success, message) {
        document.getElementById('download-progress').style.display = 'none';
        
        const completeSection = document.getElementById('download-complete');
        const icon = completeSection.querySelector('.complete-icon i');
        const messageEl = document.getElementById('complete-message');
        
        if (success) {
            icon.className = 'fas fa-check-circle';
            icon.style.color = '#10b981';
            completeSection.querySelector('h3').textContent = '下载完成！';
        } else {
            icon.className = 'fas fa-exclamation-circle';
            icon.style.color = '#ef4444';
            completeSection.querySelector('h3').textContent = '下载失败';
        }
        
        messageEl.textContent = message;
        completeSection.style.display = 'block';
        
        // 播放通知音
        if (success && this.settings.soundNotifications) {
            this.playNotificationSound();
        }
    }

    // 暂停下载
    async pauseDownload() {
        if (!this.currentTask) return;

        try {
            const response = await fetch(`${this.apiBase}/api/pause_download/${this.currentTask}`, {
                method: 'POST'
            });
            const result = await response.json();
            
            if (result.success) {
                document.getElementById('pause-btn').innerHTML = '<i class="fas fa-play"></i> 继续';
                document.getElementById('pause-btn').onclick = () => this.resumeDownload();
                this.showNotification('下载已暂停', 'info');
            }
        } catch (error) {
            this.showNotification('暂停失败：' + error.message, 'error');
        }
    }

    // 继续下载
    async resumeDownload() {
        if (!this.currentTask) return;

        try {
            const response = await fetch(`${this.apiBase}/api/resume_download/${this.currentTask}`, {
                method: 'POST'
            });
            const result = await response.json();
            
            if (result.success) {
                document.getElementById('pause-btn').innerHTML = '<i class="fas fa-pause"></i> 暂停';
                document.getElementById('pause-btn').onclick = () => this.pauseDownload();
                this.showNotification('下载已继续', 'info');
            }
        } catch (error) {
            this.showNotification('继续失败：' + error.message, 'error');
        }
    }

    // 取消下载
    async cancelDownload() {
        if (!this.currentTask) return;

        const confirmed = await this.showConfirm('确认取消', '确定要取消当前下载吗？');
        if (!confirmed) return;

        try {
            const response = await fetch(`${this.apiBase}/api/cancel_download/${this.currentTask}`, {
                method: 'POST'
            });
            const result = await response.json();
            
            if (result.success) {
                this.stopProgressMonitoring();
                this.newDownload();
                this.showNotification('下载已取消', 'info');
            }
        } catch (error) {
            this.showNotification('取消失败：' + error.message, 'error');
        }
    }

    // 下载文件
    async downloadFile() {
        if (!this.currentTask) return;

        try {
            window.open(`${this.apiBase}/api/download/${this.currentTask}`, '_blank');
        } catch (error) {
            this.showNotification('下载文件失败：' + error.message, 'error');
        }
    }

    // 新建下载
    newDownload() {
        this.currentTask = null;
        this.stopProgressMonitoring();
        
        document.querySelector('.download-form').style.display = 'block';
        document.getElementById('download-progress').style.display = 'none';
        document.getElementById('download-complete').style.display = 'none';
        
        document.getElementById('book-id').value = '';
        this.hideBookPreview();
    }

    // 加载统计信息
    async loadStats() {
        try {
            const [libraryResponse, historyResponse] = await Promise.all([
                fetch(`${this.apiBase}/api/novels`),
                fetch(`${this.apiBase}/api/history`)
            ]);

            const libraryResult = await libraryResponse.json();
            const historyResult = await historyResponse.json();

            if (libraryResult.success) {
                const novels = libraryResult.novels;
                document.getElementById('total-books').textContent = novels.length;
                
                const totalSize = novels.reduce((sum, novel) => sum + novel.file_size_mb, 0);
                document.getElementById('library-size').textContent = totalSize.toFixed(1) + ' MB';
            }

            if (historyResult.success) {
                const history = historyResult.history;
                const totalDownloads = history.length;
                const successCount = history.filter(h => h.status === 'completed').length;
                const successRate = totalDownloads > 0 ? Math.round((successCount / totalDownloads) * 100) : 100;
                
                document.getElementById('total-downloads').textContent = totalDownloads;
                document.getElementById('success-rate').textContent = successRate + '%';
            }

            // 活跃任务数（简化为0，实际应该查询正在进行的任务）
            document.getElementById('active-tasks').textContent = this.currentTask ? '1' : '0';

        } catch (error) {
            console.error('加载统计信息失败:', error);
        }
    }

    // 加载书库
    async loadLibrary() {
        try {
            const response = await fetch(`${this.apiBase}/api/novels`);
            const result = await response.json();

            if (result.success) {
                this.renderLibrary(result.novels);
                document.getElementById('library-count').textContent = result.novels.length;
            } else {
                this.showNotification('加载书库失败', 'error');
            }
        } catch (error) {
            this.showNotification('加载书库失败：' + error.message, 'error');
        }
    }

    // 渲染书库
    renderLibrary(novels) {
        const grid = document.getElementById('library-grid');
        const empty = document.getElementById('library-empty');

        if (novels.length === 0) {
            grid.style.display = 'none';
            empty.style.display = 'block';
            return;
        }

        grid.style.display = 'grid';
        empty.style.display = 'none';

        grid.innerHTML = novels.map(novel => `
            <div class="book-card" data-filename="${novel.filename}">
                <div class="book-cover">
                    <i class="fas fa-book"></i>
                </div>
                <div class="book-info">
                    <h3 class="book-title">${novel.book_name}</h3>
                    <p class="book-author">${novel.author}</p>
                    <div class="book-meta">
                        <span class="book-size">${novel.file_size_mb} MB</span>
                        <span class="book-date">${novel.download_time}</span>
                    </div>
                </div>
                <div class="book-actions">
                    <button class="action-btn download" onclick="app.downloadNovelFile('${novel.filename}')">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="action-btn delete" onclick="app.deleteNovel('${novel.filename}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    // 搜索书库
    searchLibrary(query) {
        const cards = document.querySelectorAll('.book-card');
        const searchTerm = query.toLowerCase();

        cards.forEach(card => {
            const title = card.querySelector('.book-title').textContent.toLowerCase();
            const author = card.querySelector('.book-author').textContent.toLowerCase();
            
            if (title.includes(searchTerm) || author.includes(searchTerm)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }

    // 下载小说文件
    downloadNovelFile(filename) {
        window.open(`${this.apiBase}/api/download_novel/${filename}`, '_blank');
    }

    // 删除小说
    async deleteNovel(filename) {
        const confirmed = await this.showConfirm('确认删除', `确定要删除《${filename.replace('.txt', '')}》吗？`);
        if (!confirmed) return;

        try {
            const response = await fetch(`${this.apiBase}/api/delete_novel/${filename}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('删除成功', 'success');
                // 重新加载书库
                this.loadLibrary();
            } else {
                this.showNotification('删除失败：' + result.message, 'error');
            }
        } catch (error) {
            this.showNotification('删除失败：' + error.message, 'error');
        }
    }

    // 加载历史记录
    async loadHistory() {
        try {
            const response = await fetch(`${this.apiBase}/api/history`);
            const result = await response.json();

            if (result.success) {
                this.renderHistory(result.history);
            } else {
                this.showNotification('加载历史失败', 'error');
            }
        } catch (error) {
            this.showNotification('加载历史失败：' + error.message, 'error');
        }
    }

    // 渲染历史记录
    renderHistory(history) {
        const list = document.getElementById('history-list');
        const empty = document.getElementById('history-empty');

        if (history.length === 0) {
            list.style.display = 'none';
            empty.style.display = 'block';
            return;
        }

        list.style.display = 'block';
        empty.style.display = 'none';

        list.innerHTML = history.map(item => `
            <div class="history-item ${item.status}">
                <div class="history-icon">
                    <i class="fas ${item.status === 'completed' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                </div>
                <div class="history-content">
                    <h4>${item.book_name}</h4>
                    <p class="history-meta">
                        <span>任务ID: ${item.task_id}</span>
                        <span>开始时间: ${item.start_time}</span>
                        ${item.end_time ? `<span>结束时间: ${item.end_time}</span>` : ''}
                    </p>
                    <div class="history-stats">
                        ${item.status === 'completed' ? 
                            `<span class="success">成功下载 ${item.success_count}/${item.total_chapters} 章</span>` :
                            `<span class="error">下载失败: ${item.error_message || '未知错误'}</span>`
                        }
                    </div>
                </div>
                ${item.status === 'completed' && item.output_file ? 
                    `<div class="history-actions">
                        <button class="action-btn" onclick="app.downloadTaskFile('${item.task_id}')">
                            <i class="fas fa-download"></i>
                        </button>
                    </div>` : ''
                }
            </div>
        `).join('');
    }

    // 下载任务文件
    downloadTaskFile(taskId) {
        window.open(`${this.apiBase}/api/download/${taskId}`, '_blank');
    }

    // 清空历史
    async clearHistory() {
        const confirmed = await this.showConfirm('确认清空', '确定要清空所有历史记录吗？');
        if (!confirmed) return;

        try {
            const response = await fetch(`${this.apiBase}/api/clear_history`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('历史记录已清空', 'success');
                // 重新加载历史
                this.loadHistory();
            } else {
                this.showNotification('清空失败：' + result.message, 'error');
            }
        } catch (error) {
            this.showNotification('清空失败：' + error.message, 'error');
        }
    }

    // 保存设置
    saveSettings() {
        const settings = {
            batchSize: document.getElementById('batch-size').value,
            retryCount: document.getElementById('retry-count').value,
            downloadDelay: document.getElementById('download-delay').value,
            theme: document.getElementById('theme-select').value,
            autoRefresh: document.getElementById('auto-refresh').checked,
            soundNotifications: document.getElementById('sound-notifications').checked,
            apiEndpoint: document.getElementById('api-endpoint').value,
            debugMode: document.getElementById('debug-mode').checked
        };

        localStorage.setItem('fanqie_settings', JSON.stringify(settings));
        this.settings = settings;
        this.applySettings();
        
        // 调试模式切换时的特殊处理
        if (this.settings.debugMode) {
            this.showNotification('调试模式已启用，将显示详细信息', 'info');
            console.log('当前设置:', this.settings);
        } else {
            // 隐藏调试信息区域
            document.getElementById('debug-info').style.display = 'none';
        }
        
        this.showNotification('设置已保存', 'success');
    }

    // 重置设置
    resetSettings() {
        const defaultSettings = {
            batchSize: '300',
            retryCount: '3',
            downloadDelay: '3',
            theme: 'light',
            autoRefresh: true,
            soundNotifications: true,
            apiEndpoint: 'http://localhost:5000',
            debugMode: false
        };

        localStorage.setItem('fanqie_settings', JSON.stringify(defaultSettings));
        this.settings = defaultSettings;
        this.loadSettingsToForm();
        this.applySettings();
        this.showNotification('设置已重置', 'success');
    }

    // 加载设置
    loadSettings() {
        const defaultSettings = {
            batchSize: '300',
            retryCount: '3',
            downloadDelay: '3',
            theme: 'light',
            autoRefresh: true,
            soundNotifications: true,
            apiEndpoint: 'http://localhost:5000',
            debugMode: false
        };

        const saved = localStorage.getItem('fanqie_settings');
        return saved ? { ...defaultSettings, ...JSON.parse(saved) } : defaultSettings;
    }

    // 将设置加载到表单
    loadSettingsToForm() {
        document.getElementById('batch-size').value = this.settings.batchSize;
        document.getElementById('retry-count').value = this.settings.retryCount;
        document.getElementById('download-delay').value = this.settings.downloadDelay;
        document.getElementById('theme-select').value = this.settings.theme;
        document.getElementById('auto-refresh').checked = this.settings.autoRefresh;
        document.getElementById('sound-notifications').checked = this.settings.soundNotifications;
        document.getElementById('api-endpoint').value = this.settings.apiEndpoint;
        document.getElementById('debug-mode').checked = this.settings.debugMode;
    }

    // 应用设置
    applySettings() {
        this.apiBase = this.settings.apiEndpoint;
        this.loadSettingsToForm();
        
        // 应用主题
        document.body.className = `theme-${this.settings.theme}`;
        
        // 自动刷新
        if (this.settings.autoRefresh) {
            this.startAutoRefresh();
        } else {
            this.stopAutoRefresh();
        }
    }

    // 开始自动刷新
    startAutoRefresh() {
        if (this.autoRefreshInterval) return;
        
        this.autoRefreshInterval = setInterval(() => {
            const activeTab = document.querySelector('.tab-content.active').id;
            if (activeTab === 'library') {
                this.loadLibrary();
            } else if (activeTab === 'history') {
                this.loadHistory();
            }
            this.loadStats();
        }, 30000); // 30秒刷新一次
    }

    // 停止自动刷新
    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }

    // 播放通知音
    playNotificationSound() {
        try {
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUarm7blmGgU7k9n1unEiBC13yO/eizEIHWq+8+OWT');
            audio.play().catch(() => {
                // 忽略播放失败
            });
        } catch (error) {
            // 忽略音频错误
        }
    }

    // 显示通知
    showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        
        notification.innerHTML = `
            <i class="fas ${icons[type]}"></i>
            <span>${message}</span>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
        
        container.appendChild(notification);
        
        // 自动移除
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    // 显示确认对话框
    showConfirm(title, message) {
        return new Promise((resolve) => {
            document.getElementById('modal-title').textContent = title;
            document.getElementById('modal-message').textContent = message;
            document.getElementById('modal-overlay').style.display = 'flex';
            
            const handleConfirm = () => {
                this.hideModal();
                resolve(true);
            };
            
            const handleCancel = () => {
                this.hideModal();
                resolve(false);
            };
            
            document.getElementById('modal-confirm').onclick = handleConfirm;
            document.getElementById('modal-cancel').onclick = handleCancel;
        });
    }

    // 隐藏模态框
    hideModal() {
        document.getElementById('modal-overlay').style.display = 'none';
    }

    // 显示加载
    showLoading() {
        document.getElementById('loading-overlay').style.display = 'flex';
    }

    // 隐藏加载
    hideLoading() {
        document.getElementById('loading-overlay').style.display = 'none';
    }

    // 设置实时预览
    previewSetting(setting, value) {
        this.settings[setting] = value;
        this.applySettings();
        this.showNotification(`${setting.charAt(0).toUpperCase() + setting.slice(1)}已更新为${value}`, 'info');
    }
}

// 全局函数
function switchTab(tabName) {
    if (window.app) {
        window.app.switchTab(tabName);
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.app = new FanqieDownloader();
});

