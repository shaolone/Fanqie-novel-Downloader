<?php
require_once 'config.php';

class Database {
    private $pdo;
    
    public function __construct() {
        try {
            $this->pdo = new PDO('sqlite:' . DB_PATH);
            $this->pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            $this->initTables();
        } catch (PDOException $e) {
            die('数据库连接失败: ' . $e->getMessage());
        }
    }
    
    private function initTables() {
        // 下载任务表
        $sql = "CREATE TABLE IF NOT EXISTS download_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id TEXT NOT NULL,
            book_title TEXT,
            total_chapters INTEGER DEFAULT 0,
            downloaded_chapters INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            file_path TEXT,
            file_size INTEGER DEFAULT 0
        )";
        $this->pdo->exec($sql);
        
        // 章节表
        $sql = "CREATE TABLE IF NOT EXISTS chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            chapter_id TEXT,
            chapter_title TEXT,
            content TEXT,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES download_tasks(id)
        )";
        $this->pdo->exec($sql);
        
        // 用户设置表
        $sql = "CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE,
            setting_value TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )";
        $this->pdo->exec($sql);
    }
    
    public function createDownloadTask($bookId, $bookTitle = '') {
        $sql = "INSERT INTO download_tasks (book_id, book_title, status) VALUES (?, ?, 'pending')";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute([$bookId, $bookTitle]);
        return $this->pdo->lastInsertId();
    }
    
    public function updateTaskStatus($taskId, $status, $downloadedChapters = null) {
        $sql = "UPDATE download_tasks SET status = ?, updated_at = CURRENT_TIMESTAMP";
        $params = [$status];
        
        if ($downloadedChapters !== null) {
            $sql .= ", downloaded_chapters = ?";
            $params[] = $downloadedChapters;
        }
        
        $sql .= " WHERE id = ?";
        $params[] = $taskId;
        
        $stmt = $this->pdo->prepare($sql);
        return $stmt->execute($params);
    }
    
    public function getDownloadTasks($limit = 20) {
        $sql = "SELECT * FROM download_tasks ORDER BY created_at DESC LIMIT ?";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute([$limit]);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
    
    public function getTaskById($taskId) {
        $sql = "SELECT * FROM download_tasks WHERE id = ?";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute([$taskId]);
        return $stmt->fetch(PDO::FETCH_ASSOC);
    }
    
    public function addChapter($taskId, $chapterId, $chapterTitle, $content) {
        $sql = "INSERT INTO chapters (task_id, chapter_id, chapter_title, content, status) VALUES (?, ?, ?, ?, 'completed')";
        $stmt = $this->pdo->prepare($sql);
        return $stmt->execute([$taskId, $chapterId, $chapterTitle, $content]);
    }
    
    public function getChaptersByTaskId($taskId) {
        $sql = "SELECT * FROM chapters WHERE task_id = ? ORDER BY id ASC";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute([$taskId]);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
    
    public function updateTaskFile($taskId, $filePath, $fileSize) {
        $sql = "UPDATE download_tasks SET file_path = ?, file_size = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?";
        $stmt = $this->pdo->prepare($sql);
        return $stmt->execute([$filePath, $fileSize, $taskId]);
    }
    
    public function getSetting($key, $default = null) {
        $sql = "SELECT setting_value FROM user_settings WHERE setting_key = ?";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute([$key]);
        $result = $stmt->fetch(PDO::FETCH_ASSOC);
        return $result ? $result['setting_value'] : $default;
    }
    
    public function setSetting($key, $value) {
        $sql = "INSERT OR REPLACE INTO user_settings (setting_key, setting_value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)";
        $stmt = $this->pdo->prepare($sql);
        return $stmt->execute([$key, $value]);
    }
}
?>

