<?php
// 番茄小说下载器 - 配置文件

// API配置
define('API_BASE_URL', 'http://localhost:8000');
define('API_ENDPOINT', '/dragon/content');

// 文件配置
define('DOWNLOAD_DIR', __DIR__ . '/downloads/');
define('MAX_FILE_SIZE', 50 * 1024 * 1024); // 50MB

// 下载配置
define('BATCH_SIZE', 300);
define('MAX_RETRIES', 3);
define('REQUEST_TIMEOUT', 30);

// 数据库配置（SQLite）
define('DB_PATH', __DIR__ . '/data/fanqie.db');

// 确保必要目录存在
if (!file_exists(DOWNLOAD_DIR)) {
    mkdir(DOWNLOAD_DIR, 0755, true);
}

if (!file_exists(dirname(DB_PATH))) {
    mkdir(dirname(DB_PATH), 0755, true);
}

// 错误报告
error_reporting(E_ALL);
ini_set('display_errors', 1);

// 设置时区
date_default_timezone_set('Asia/Shanghai');

// 会话配置
session_start();
?>

