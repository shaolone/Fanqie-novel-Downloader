<?php
require_once 'config.php';

class FanqieAPI {
    private $baseUrl;
    private $timeout;
    
    public function __construct() {
        $this->baseUrl = API_BASE_URL;
        $this->timeout = REQUEST_TIMEOUT;
    }
    
    /**
     * 获取章节内容
     */
    public function getContent($bookId, $itemIds) {
        $url = $this->baseUrl . API_ENDPOINT;
        
        // 准备POST数据
        $postData = json_encode([
            'book_id' => $bookId,
            'item_ids' => is_array($itemIds) ? $itemIds : [$itemIds]
        ]);
        
        $context = stream_context_create([
            'http' => [
                'method' => 'POST',
                'header' => [
                    'Content-Type: application/json',
                    'Content-Length: ' . strlen($postData)
                ],
                'content' => $postData,
                'timeout' => $this->timeout
            ]
        ]);
        
        $response = @file_get_contents($url, false, $context);
        
        if ($response === false) {
            throw new Exception('API请求失败');
        }
        
        $data = json_decode($response, true);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new Exception('API响应解析失败');
        }
        
        return $data;
    }
    
    /**
     * 获取小说信息（模拟）
     */
    public function getBookInfo($bookId) {
        // 这里可以扩展为实际的API调用
        return [
            'book_id' => $bookId,
            'title' => '未知小说',
            'author' => '未知作者',
            'description' => '暂无描述',
            'total_chapters' => 0
        ];
    }
    
    /**
     * 批量获取章节列表（模拟）
     */
    public function getChapterList($bookId, $page = 1, $limit = 100) {
        // 这里可以扩展为实际的API调用
        $chapters = [];
        for ($i = 1; $i <= $limit; $i++) {
            $chapters[] = [
                'chapter_id' => $bookId . '_' . (($page - 1) * $limit + $i),
                'title' => '第' . (($page - 1) * $limit + $i) . '章',
                'order' => ($page - 1) * $limit + $i
            ];
        }
        
        return [
            'chapters' => $chapters,
            'total' => 1000, // 假设总共1000章
            'page' => $page,
            'limit' => $limit
        ];
    }
    
    /**
     * 测试API连接
     */
    public function testConnection() {
        try {
            $testData = $this->getContent('test', ['test']);
            return true;
        } catch (Exception $e) {
            return false;
        }
    }
    
    /**
     * 清理HTML标签
     */
    public function cleanContent($content) {
        // 移除HTML标签
        $content = strip_tags($content);
        
        // 清理多余的空白字符
        $content = preg_replace('/\s+/', ' ', $content);
        
        // 清理特殊字符
        $content = html_entity_decode($content, ENT_QUOTES, 'UTF-8');
        
        return trim($content);
    }
    
    /**
     * 格式化文件大小
     */
    public static function formatFileSize($bytes) {
        $units = ['B', 'KB', 'MB', 'GB'];
        $bytes = max($bytes, 0);
        $pow = floor(($bytes ? log($bytes) : 0) / log(1024));
        $pow = min($pow, count($units) - 1);
        
        $bytes /= pow(1024, $pow);
        
        return round($bytes, 2) . ' ' . $units[$pow];
    }
    
    /**
     * 生成随机字符串
     */
    public static function generateRandomString($length = 10) {
        $characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
        $charactersLength = strlen($characters);
        $randomString = '';
        for ($i = 0; $i < $length; $i++) {
            $randomString .= $characters[rand(0, $charactersLength - 1)];
        }
        return $randomString;
    }
}
?>

