# PyCharm 开发环境配置指南

> **完整的 PyCharm 本地开发环境搭建和调试指南**

## 📋 目录

- [🏗️ 项目结构概览](#️-项目结构概览)
- [🚀 环境准备](#-环境准备)
- [🔧 PyCharm 配置](#-pycharm-配置)
- [🐳 Docker 服务启动](#-docker-服务启动)
- [📊 数据处理与索引](#-数据处理与索引)
- [🔍 API 服务测试](#-api-服务测试)
- [🖼️ OCR 功能测试](#️-ocr-功能测试)
- [🐛 调试技巧](#-调试技巧)
- [🔧 常见问题解决](#-常见问题解决)
- [📈 性能测试](#-性能测试)
- [📱 iOS 集成准备](#-ios-集成准备)

## 🏗️ 项目结构概览

```
caie-search-backend/
├── 📄 main.py                     # FastAPI 主服务器入口
├── 📊 caie_math_processor.py      # CAIE 数学试卷数据处理器
├── 👁️ ocr_service.py             # OCR 文字识别服务
├── 🔍 search_service.py          # Elasticsearch 搜索服务
├── 🧮 math_search_optimizer.py    # 数学搜索优化器
├── 🧠 math_formula_processor.py   # 数学公式处理器
├── 📝 models.py                   # 数据模型定义
├── 📦 requirements.txt            # Python 依赖包清单
├── 🐳 docker-compose.yml         # Docker 服务配置
├── 📚 PYCHARM_GUIDE.md           # 本开发指南
├── 📖 README.md                  # 项目文档
├── 🗂️ caie_math_questions.json   # 处理后的题目数据
└── ⚙️ elasticsearch_mapping.json  # ES 索引映射配置
```

## 🚀 环境准备

### 1️⃣ 系统要求

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| **Python** | 3.8+ | 推荐 3.9 或 3.10 |
| **Docker Desktop** | 最新版 | 必需，用于 ES 和 Redis |
| **内存** | 4GB+ | 推荐 8GB，ES 需要较多内存 |
| **硬盘空间** | 2GB+ | 包含 Docker 镜像和数据 |

### 2️⃣ Docker Desktop 安装

#### macOS 用户
```bash
# 方法1: 官网下载
# 访问 https://www.docker.com/products/docker-desktop/
# 下载并安装 Docker Desktop for Mac

# 方法2: Homebrew 安装
brew install --cask docker

# 验证安装
docker --version
docker-compose --version
```

#### Windows 用户
```powershell
# 下载并安装 Docker Desktop for Windows
# https://www.docker.com/products/docker-desktop/

# 启用 WSL2 (如果需要)
wsl --install
```

### 3️⃣ 验证 Docker 状态
```bash
# 检查 Docker 是否运行
docker info

# 测试 Docker 功能
docker run hello-world
```

## 🔧 PyCharm 配置

### 1️⃣ 项目导入

1. **启动 PyCharm**
   - 选择 `File` → `Open`
   - 导航到 `/Users/patrick/Desktop/caie-search-backend`
   - 点击 `Open` 并选择 `Trust Project`

2. **项目设置检查**
   - 确认项目根目录正确显示所有文件
   - 检查 `.gitignore` 文件是否正确加载

### 2️⃣ Python 解释器配置

#### 创建虚拟环境
1. **打开设置**
   - macOS: `PyCharm` → `Preferences`
   - Windows: `File` → `Settings`

2. **配置解释器**
   ```
   路径: Project: caie-search-backend → Python Interpreter
   操作: 点击 ⚙️ → Add... → Virtual Environment → New Environment
   位置: /Users/patrick/Desktop/caie-search-backend/venv
   基础解释器: Python 3.8+ (自动检测)
   ```

3. **确认配置**
   - 点击 `OK` 并等待虚拟环境创建完成
   - 在 Terminal 中验证: `which python` 应指向 venv 目录

### 3️⃣ 依赖包安装

在 PyCharm 内置 Terminal 中执行：

```bash
# 升级 pip
python -m pip install --upgrade pip

# 安装依赖 (使用清华源加速)
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 验证关键包安装
python -c "import fastapi, elasticsearch, paddleocr; print('✅ 核心依赖安装成功')"
```

> ⏳ **注意**: 首次安装 PaddleOCR 和相关 AI 模型可能需要 5-15 分钟，请耐心等待。

### 4️⃣ 运行配置设置

#### 配置 FastAPI 服务器
1. **创建运行配置**
   - 点击右上角 `Add Configuration...`
   - 选择 `+` → `Python`

2. **配置参数**
   ```
   Name: CAIE API Server
   Script path: /Users/patrick/Desktop/caie-search-backend/main.py
   Working directory: /Users/patrick/Desktop/caie-search-backend
   Environment variables:
     - ELASTICSEARCH_URL=http://localhost:9200
     - REDIS_URL=redis://localhost:6379
     - PYTHONPATH=/Users/patrick/Desktop/caie-search-backend
   ```

3. **保存配置**
   - 点击 `OK` 保存
   - 在下拉菜单中确认看到 "CAIE API Server" 配置

## 🐳 Docker 服务启动

### 1️⃣ 启动服务容器

在 PyCharm Terminal 中执行：

```bash
# 启动 Elasticsearch 和 Redis
docker-compose up -d

# 查看容器状态
docker-compose ps
```

**期望输出**:
```
NAME                IMAGE                                                 STATUS
caie-elasticsearch  docker.elastic.co/elasticsearch/elasticsearch:8.11.0  Up 2 minutes
caie-redis          redis:7-alpine                                        Up 2 minutes
```

### 2️⃣ 验证服务状态

```bash
# 检查 Elasticsearch (应返回集群信息)
curl http://localhost:9200

# 检查 Redis (应返回 PONG)
docker exec caie-redis redis-cli ping

# 查看容器日志
docker-compose logs elasticsearch
docker-compose logs redis
```

**Elasticsearch 正常响应示例**:
```json
{
  "name" : "es-node",
  "cluster_name" : "caie-cluster",
  "cluster_uuid" : "...",
  "version" : {
    "number" : "8.11.0",
    "build_flavor" : "default"
  },
  "tagline" : "You Know, for Search"
}
```

### 3️⃣ 资源监控

```bash
# 查看容器资源使用
docker stats

# 查看 Docker 磁盘使用
docker system df
```

## 📊 数据处理与索引

### 1️⃣ 运行数据处理器

在 PyCharm 中打开 `caie_math_processor.py` 并运行：

**预期处理流程**:
```
🚀 CAIE A-Level 数学试卷处理器启动
🔍 扫描 CAIE 数学试卷文件...
📅 处理年份: 2001-2022
📄 处理 Question Papers...
📋 处理 Mark Schemes...
🔗 匹配题目和答案...
💾 保存到 caie_math_questions.json
✅ 数据处理完成！

📊 统计信息:
   试卷总数: 600+
   题目总数: 3000+
   匹配成功: 95%+
   数据文件: caie_math_questions.json (15MB)
```

### 2️⃣ 验证生成文件

```bash
# 检查生成的数据文件
ls -la caie_math_questions.json elasticsearch_mapping.json

# 查看数据文件大小和格式
head -n 5 caie_math_questions.json

# 统计题目数量
cat caie_math_questions.json | jq length
```

### 3️⃣ 检查数据质量

在 PyCharm 中创建测试脚本 `test_data.py`:

```python
import json

def analyze_data():
    with open('caie_math_questions.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 数据分析结果:")
    print(f"   总题目数: {len(data)}")
    
    # 年份分布
    years = {}
    for item in data:
        year = item.get('year', 'unknown')
        years[year] = years.get(year, 0) + 1
    
    print(f"   年份分布: {dict(sorted(years.items()))}")
    
    # 有答案的题目
    with_answers = sum(1 for item in data if item.get('mark_scheme'))
    print(f"   包含答案: {with_answers}/{len(data)} ({with_answers/len(data)*100:.1f}%)")

if __name__ == "__main__":
    analyze_data()
```

## 🔍 API 服务测试

### 1️⃣ 启动 FastAPI 服务器

在 PyCharm 中：
1. 选择 "CAIE API Server" 运行配置
2. 点击 `▶️` 运行按钮

**预期启动日志**:
```
🚀 启动 CAIE 搜题系统...
✅ Redis 连接成功
✅ OCR 服务初始化成功  
✅ 搜索服务初始化完成
✅ 数学搜索优化器初始化成功
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 2️⃣ API 接口测试

#### 健康检查
```bash
# 基础健康检查
curl -s http://localhost:8000/health | jq

# 预期响应
{
  "status": {
    "elasticsearch": true,
    "redis": true,
    "ocr": true
  },
  "healthy": true
}
```

#### 创建搜索索引
```bash
# 创建 Elasticsearch 索引
curl -X POST http://localhost:8000/admin/index

# 检查索引状态
curl http://localhost:8000/admin/stats
```

#### 文本搜索测试
```bash
# 简单关键词搜索
curl -X POST "http://localhost:8000/search/text" \
     -H "Content-Type: application/json" \
     -d '{"query": "differentiate", "limit": 3}' | jq

# 复杂数学搜索
curl -X POST "http://localhost:8000/search/text" \
     -H "Content-Type: application/json" \
     -d '{"query": "find the derivative of x^2 + 3x", "limit": 5}' | jq

# 带过滤条件的搜索
curl -X POST "http://localhost:8000/search/text" \
     -H "Content-Type: application/json" \
     -d '{"query": "integration", "limit": 3, "filters": {"year": "2022"}}' | jq
```

### 3️⃣ API 文档访问

在浏览器中访问:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🖼️ OCR 功能测试

### 1️⃣ 准备测试图片

创建测试图片或使用项目中的样例:
```bash
# 使用项目中的测试图片
ls img*.jpg

# 或者准备包含数学公式的图片
# 推荐: 包含简单数学表达式如 "2x + 3 = 7" 的清晰图片
```

### 2️⃣ OCR 识别测试

```bash
# 测试 OCR 识别
curl -X POST "http://localhost:8000/ocr" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@img1.jpg" | jq

# 预期响应格式
{
  "text": "识别出的文字内容",
  "confidence": 0.85,
  "boxes": [[x1, y1, x2, y2], ...]
}
```

### 3️⃣ 拍照搜题测试

```bash
# 基础拍照搜题
curl -X POST "http://localhost:8000/search/image" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@img1.jpg" \
     -F "limit=5" | jq

# 详细分析搜索
curl -X POST "http://localhost:8000/search/image/analysis" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@img1.jpg" \
     -F "limit=3" | jq
```

### 4️⃣ OCR 质量评估

创建 OCR 测试脚本 `test_ocr_quality.py`:

```python
import requests
import json
import os

def test_ocr_quality():
    """测试 OCR 识别质量"""
    
    # 测试图片列表
    test_images = ['img1.jpg', 'img2.jpg']
    
    for img_path in test_images:
        if not os.path.exists(img_path):
            continue
            
        print(f"\n🖼️ 测试图片: {img_path}")
        
        with open(img_path, 'rb') as f:
            response = requests.post(
                "http://localhost:8000/ocr",
                files={"file": f}
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   识别文字: {result['text'][:100]}...")
            print(f"   置信度: {result['confidence']:.2f}")
            print(f"   检测框数: {len(result['boxes'])}")
        else:
            print(f"   ❌ OCR 失败: {response.text}")

if __name__ == "__main__":
    test_ocr_quality()
```

## 🐛 调试技巧

### 1️⃣ PyCharm 调试功能

#### 设置断点
1. **添加断点**: 在代码行号左侧点击
2. **条件断点**: 右键断点 → Add Condition
3. **断点管理**: `View` → `Tool Windows` → `Debugger`

#### 调试启动
1. 选择 Debug 模式: 点击 `🐛` 而不是 `▶️`
2. 观察变量: 在 `Variables` 面板查看当前变量值
3. 执行控制: 使用 `Step Over`, `Step Into`, `Resume` 等

#### 调试示例
```python
# 在 search_service.py 中设置断点
async def search_by_text(self, query: str, limit: int = 10):
    # 在这里设置断点，查看 query 参数
    processed_query = self.math_processor.process_text(query)
    # 在这里设置断点，查看处理后的查询
    results = await self._elasticsearch_search(processed_query, limit)
    return results
```

### 2️⃣ 日志分析

#### 查看应用日志
```python
# 在 main.py 中添加更详细的日志
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 查看特定模块日志
logger = logging.getLogger("search_service")
logger.setLevel(logging.DEBUG)
```

#### 分析 Docker 日志
```bash
# 实时查看 Elasticsearch 日志
docker-compose logs -f elasticsearch

# 查看最近的错误
docker-compose logs elasticsearch | grep ERROR

# 查看特定时间段的日志
docker-compose logs --since="1h" elasticsearch
```

### 3️⃣ 网络调试

```bash
# 检查服务端口
netstat -an | grep :8000
netstat -an | grep :9200

# 测试网络连接
telnet localhost 8000
telnet localhost 9200

# 使用 curl 详细调试
curl -v http://localhost:8000/health
```

## 🔧 常见问题解决

### 1️⃣ Docker 相关问题

#### Docker Desktop 未启动
```bash
# 检查 Docker 状态
docker info

# 启动 Docker Desktop
open -a Docker  # macOS
# 或手动启动 Docker Desktop 应用
```

#### Elasticsearch 内存不足
```bash
# 检查容器资源使用
docker stats

# 修改 docker-compose.yml 中的内存限制
environment:
  - "ES_JAVA_OPTS=-Xms256m -Xmx512m"  # 减少内存使用

# 重启容器
docker-compose down && docker-compose up -d
```

#### 端口冲突
```bash
# 查找占用端口的进程
lsof -i :8000
lsof -i :9200

# 终止进程
kill -9 <PID>

# 或修改端口配置
# 编辑 docker-compose.yml 和 main.py 中的端口设置
```

### 2️⃣ Python 环境问题

#### 虚拟环境问题
```bash
# 重新创建虚拟环境
rm -rf venv
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

#### 依赖冲突
```bash
# 清除 pip 缓存
pip cache purge

# 强制重新安装关键包
pip uninstall paddleocr -y
pip install paddleocr -i https://pypi.tuna.tsinghua.edu.cn/simple

# 检查依赖冲突
pip check
```

#### PaddleOCR 安装问题
```bash
# 问题1: 网络下载慢
pip install paddleocr -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 300

# 问题2: GPU 相关错误
pip install paddlepaddle -i https://pypi.tuna.tsinghua.edu.cn/simple
# 确保使用 CPU 版本

# 问题3: 模型下载失败
# 手动下载模型到 ~/.paddleocr/
```

### 3️⃣ API 服务问题

#### 服务启动失败
```python
# 检查端口占用
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('localhost', 8000))
if result == 0:
    print("端口 8000 已被占用")
sock.close()
```

#### Elasticsearch 连接失败
```bash
# 检查 ES 服务状态
curl -s http://localhost:9200/_cluster/health

# 重启 ES 服务
docker-compose restart elasticsearch

# 检查 ES 配置
docker-compose exec elasticsearch cat /usr/share/elasticsearch/config/elasticsearch.yml
```

#### OCR 服务异常
```python
# 测试 PaddleOCR 是否正常
import paddleocr
ocr = paddleocr.PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)
print("✅ PaddleOCR 初始化成功")
```

## 📈 性能测试

### 1️⃣ 系统统计信息

```bash
# 获取系统统计
curl -s http://localhost:8000/admin/stats | jq

# 检查 Elasticsearch 索引信息
curl -s http://localhost:9200/caie_math_questions/_stats | jq '.indices.caie_math_questions.total'
```

### 2️⃣ 搜索性能测试

创建性能测试脚本 `benchmark_search.py`:

```python
import requests
import time
import json
import statistics

def benchmark_search():
    """搜索性能基准测试"""
    
    # 测试查询列表
    test_queries = [
        "differentiate function",
        "integrate polynomial", 
        "solve quadratic equation",
        "find derivative of x^2",
        "calculate area under curve",
        "matrix multiplication",
        "trigonometric identity",
        "binomial theorem",
        "probability distribution",
        "geometric series"
    ]
    
    response_times = []
    
    print("🚀 开始搜索性能测试...")
    print(f"📝 测试查询数量: {len(test_queries)}")
    print("-" * 60)
    
    for i, query in enumerate(test_queries, 1):
        start_time = time.time()
        
        try:
            response = requests.post(
                "http://localhost:8000/search/text",
                json={"query": query, "limit": 5},
                timeout=10
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            
            if response.status_code == 200:
                results = response.json()
                print(f"{i:2d}. {query:<25} | {response_time:.3f}s | {len(results)} 结果")
            else:
                print(f"{i:2d}. {query:<25} | ERROR {response.status_code}")
                
        except requests.RequestException as e:
            print(f"{i:2d}. {query:<25} | TIMEOUT/ERROR")
    
    # 统计分析
    if response_times:
        print("-" * 60)
        print(f"📊 性能统计:")
        print(f"   平均响应时间: {statistics.mean(response_times):.3f}s")
        print(f"   最快响应: {min(response_times):.3f}s")
        print(f"   最慢响应: {max(response_times):.3f}s")
        print(f"   响应时间中位数: {statistics.median(response_times):.3f}s")
        print(f"   成功率: {len(response_times)}/{len(test_queries)} ({len(response_times)/len(test_queries)*100:.1f}%)")

if __name__ == "__main__":
    benchmark_search()
```

### 3️⃣ OCR 性能测试

创建 OCR 性能测试脚本 `benchmark_ocr.py`:

```python
import requests
import time
import os

def benchmark_ocr():
    """OCR 性能基准测试"""
    
    test_images = ['img1.jpg', 'img2.jpg']  # 添加更多测试图片
    
    print("🖼️ 开始 OCR 性能测试...")
    
    for img_path in test_images:
        if not os.path.exists(img_path):
            print(f"   ⚠️ 图片不存在: {img_path}")
            continue
            
        file_size = os.path.getsize(img_path) / 1024  # KB
        
        start_time = time.time()
        
        with open(img_path, 'rb') as f:
            response = requests.post(
                "http://localhost:8000/ocr",
                files={"file": f}
            )
        
        end_time = time.time()
        process_time = end_time - start_time
        
        print(f"📷 {img_path}:")
        print(f"   文件大小: {file_size:.1f} KB")
        print(f"   处理时间: {process_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   识别置信度: {result['confidence']:.2f}")
            print(f"   识别文字长度: {len(result['text'])} 字符")
            print(f"   检测区域数: {len(result['boxes'])}")
        else:
            print(f"   ❌ 处理失败: {response.status_code}")
        
        print("-" * 40)

if __name__ == "__main__":
    benchmark_ocr()
```

### 4️⃣ 系统资源监控

```bash
# 监控脚本 monitor_system.sh
#!/bin/bash

echo "🖥️ 系统资源监控 (按 Ctrl+C 停止)"
echo "时间                CPU%   内存%   Docker容器状态"
echo "================================================"

while true; do
    # CPU 和内存使用率
    cpu_usage=$(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')
    mem_usage=$(vm_stat | perl -ne '/page size of (\d+)/ and $size=$1; /Pages\s+([^:]+)[^\d]+(\d+)/ and printf("%.2f\n", $2 * $size / 1073741824), $total += $2 * $size / 1073741824; END { printf "%.1f%%\n", ($total - $free) / $total * 100 }')
    
    # Docker 容器状态
    containers=$(docker-compose ps --services --filter status=running | wc -l)
    
    timestamp=$(date +"%H:%M:%S")
    
    printf "%-8s %6s %7s     %d/2 容器运行\n" "$timestamp" "$cpu_usage" "$mem_usage" "$containers"
    
    sleep 5
done
```

## 📱 iOS 集成准备

### 1️⃣ API 基础配置

在你的 iOS 项目中创建 API 配置:

```swift
// APIConfig.swift
import Foundation

struct APIConfig {
    // 开发环境
    static let developmentBaseURL = "http://localhost:8000"
    
    // 生产环境 (部署后更新)
    static let productionBaseURL = "https://your-domain.com"
    
    // 当前使用的环境
    #if DEBUG
    static let baseURL = developmentBaseURL
    #else
    static let baseURL = productionBaseURL
    #endif
    
    // API 端点
    struct Endpoints {
        static let health = "/health"
        static let ocr = "/ocr"
        static let searchText = "/search/text"
        static let searchImage = "/search/image"
        static let searchImageAnalysis = "/search/image/analysis"
    }
}
```

### 2️⃣ 网络服务封装

```swift
// NetworkService.swift
import Foundation
import UIKit

class NetworkService {
    static let shared = NetworkService()
    private let session = URLSession.shared
    
    private init() {}
    
    // 健康检查
    func healthCheck() async throws -> HealthStatus {
        let url = URL(string: "\(APIConfig.baseURL)\(APIConfig.Endpoints.health)")!
        let (data, _) = try await session.data(from: url)
        return try JSONDecoder().decode(HealthStatus.self, from: data)
    }
    
    // OCR 识别
    func performOCR(image: UIImage) async throws -> OCRResult {
        let url = URL(string: "\(APIConfig.baseURL)\(APIConfig.Endpoints.ocr)")!
        
        // 准备 multipart/form-data
        let boundary = UUID().uuidString
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        // 构建请求体
        var body = Data()
        
        // 添加图片数据
        if let imageData = image.jpegData(compressionQuality: 0.8) {
            body.append("--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"file\"; filename=\"image.jpg\"\r\n".data(using: .utf8)!)
            body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
            body.append(imageData)
            body.append("\r\n".data(using: .utf8)!)
        }
        
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        request.httpBody = body
        
        let (data, _) = try await session.data(for: request)
        return try JSONDecoder().decode(OCRResult.self, from: data)
    }
    
    // 拍照搜题
    func searchByImage(image: UIImage, limit: Int = 10) async throws -> [SearchResult] {
        let url = URL(string: "\(APIConfig.baseURL)\(APIConfig.Endpoints.searchImage)")!
        
        // 构建 multipart 请求 (类似 OCR 方法)
        let boundary = UUID().uuidString
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var body = Data()
        
        // 添加图片
        if let imageData = image.jpegData(compressionQuality: 0.8) {
            body.append("--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"file\"; filename=\"image.jpg\"\r\n".data(using: .utf8)!)
            body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
            body.append(imageData)
            body.append("\r\n".data(using: .utf8)!)
        }
        
        // 添加 limit 参数
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"limit\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(limit)".data(using: .utf8)!)
        body.append("\r\n".data(using: .utf8)!)
        
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        request.httpBody = body
        
        let (data, _) = try await session.data(for: request)
        return try JSONDecoder().decode([SearchResult].self, from: data)
    }
    
    // 文本搜索
    func searchByText(_ query: String, limit: Int = 10) async throws -> [SearchResult] {
        let url = URL(string: "\(APIConfig.baseURL)\(APIConfig.Endpoints.searchText)")!
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let searchRequest = TextSearchRequest(query: query, limit: limit)
        request.httpBody = try JSONEncoder().encode(searchRequest)
        
        let (data, _) = try await session.data(for: request)
        return try JSONDecoder().decode([SearchResult].self, from: data)
    }
}

// 数据模型
struct HealthStatus: Codable {
    let status: ServiceStatus
    let healthy: Bool
}

struct ServiceStatus: Codable {
    let elasticsearch: Bool
    let redis: Bool
    let ocr: Bool
}

struct OCRResult: Codable {
    let text: String
    let confidence: Double
    let boxes: [[Int]]
}

struct SearchResult: Codable {
    let id: String
    let title: String
    let content: String
    let year: String
    let season: String
    let paperCode: String
    let markScheme: String?
    let confidence: Double
    
    enum CodingKeys: String, CodingKey {
        case id, title, content, year, season, confidence
        case paperCode = "paper_code"
        case markScheme = "mark_scheme"
    }
}

struct TextSearchRequest: Codable {
    let query: String
    let limit: Int
}
```

### 3️⃣ 测试 iOS 集成

在你的 iOS 项目中创建测试代码:

```swift
// 在某个 ViewController 中测试
override func viewDidLoad() {
    super.viewDidLoad()
    testAPIIntegration()
}

private func testAPIIntegration() {
    Task {
        do {
            // 测试健康检查
            let health = try await NetworkService.shared.healthCheck()
            print("✅ 健康检查: \(health.healthy)")
            
            // 测试文本搜索
            let textResults = try await NetworkService.shared.searchByText("differentiate", limit: 3)
            print("✅ 文本搜索: 找到 \(textResults.count) 个结果")
            
            // 测试图片搜索 (需要有测试图片)
            if let testImage = UIImage(named: "test_math_image") {
                let imageResults = try await NetworkService.shared.searchByImage(image: testImage, limit: 5)
                print("✅ 图片搜索: 找到 \(imageResults.count) 个结果")
            }
            
        } catch {
            print("❌ API 测试失败: \(error)")
        }
    }
}
```

## 🎯 成功验证标准

当你完成所有配置后，应该能够看到以下成功指标:

### ✅ Docker 服务
- Elasticsearch 容器正常运行 (端口 9200)
- Redis 容器正常运行 (端口 6379)
- 容器内存使用 < 2GB

### ✅ 数据处理
- 成功处理 600+ 份 CAIE 数学试卷
- 生成 `caie_math_questions.json` 文件 (~15MB)
- 提取 3000+ 道题目到 Elasticsearch

### ✅ API 服务
- FastAPI 服务运行在端口 8000
- 健康检查返回所有服务正常
- API 文档可以访问 (http://localhost:8000/docs)

### ✅ 搜索功能
- 文本搜索响应时间 < 2 秒
- 搜索结果包含题目和答案
- 支持数学公式搜索

### ✅ OCR 功能
- 图片识别置信度 > 80%
- 支持数学符号识别
- 拍照搜题正常工作

## 🚀 下一步行动

完成本地开发环境配置后，你可以:

1. **📱 iOS 应用集成**: 使用上面提供的 Swift 代码模板
2. **☁️ 云端部署**: 参考 README.md 中的部署指南
3. **🔧 功能扩展**: 添加更多科目支持 (化学、物理等)
4. **📊 数据扩展**: 添加更多年份的考试数据
5. **🎯 性能优化**: 根据性能测试结果进行优化

---

<div align="center">

**🎉 恭喜！你已经完成了完整的开发环境配置**

如有问题，请在 PyCharm 中设置断点进行调试，或查看相关日志文件。

**Happy Coding! 🚀**

</div>