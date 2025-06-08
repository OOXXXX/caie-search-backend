# PyCharm 本地测试完整指南

## 📁 项目结构

```
caie-search-backend/
├── main.py                    # FastAPI 主服务器
├── caie_math_processor.py     # 试卷数据处理器
├── ocr_service.py            # OCR识别服务
├── search_service.py         # Elasticsearch搜索服务
├── models.py                 # 数据模型定义
├── requirements.txt          # Python依赖包
├── docker-compose.yml        # Docker服务配置
├── PYCHARM_GUIDE.md         # 本指南
└── README.md                # 项目说明
```

## 🚀 第一步：Docker安装（如果没装过）

### macOS 安装Docker Desktop
1. 访问 https://www.docker.com/products/docker-desktop/
2. 下载 Docker Desktop for Mac
3. 安装并启动 Docker Desktop
4. 确认安装成功：
   ```bash
   docker --version
   docker-compose --version
   ```

## 🔧 第二步：PyCharm 项目设置

### 1. 打开项目
1. 启动 PyCharm
2. `File` → `Open` → 选择 `/Users/patrick/Desktop/caie-search-backend`
3. 点击 `Trust Project`

### 2. 配置Python解释器
1. `PyCharm` → `Settings` (macOS) 或 `File` → `Settings` (Windows)
2. `Project: caie-search-backend` → `Python Interpreter`
3. 点击 `⚙️` → `Add...`
4. 选择 `Virtual Environment` → `New Environment`
5. Location: `/Users/patrick/Desktop/caie-search-backend/venv`
6. 点击 `OK`

### 3. 安装依赖包
在PyCharm底部的Terminal中运行：
```bash
pip install -r requirements.txt
```

> ⏳ **注意**: 首次安装PaddleOCR和PyTorch可能需要5-10分钟

### 4. 配置运行配置
1. 点击右上角 `Add Configuration...`
2. 点击 `+` → `Python`
3. 配置如下：
   - **Name**: `CAIE API Server`
   - **Script path**: `/Users/patrick/Desktop/caie-search-backend/main.py`
   - **Working directory**: `/Users/patrick/Desktop/caie-search-backend`
   - **Environment variables**: 点击 `...` 添加：
     - `ELASTICSEARCH_URL=http://localhost:9200`
     - `REDIS_URL=redis://localhost:6379`
4. 点击 `OK`

## 🐳 第三步：启动Docker服务

### 在PyCharm Terminal中运行：
```bash
# 启动Elasticsearch和Redis
docker-compose up -d

# 查看容器状态
docker-compose ps

# 检查Elasticsearch是否启动成功
curl http://localhost:9200
```

**预期输出**:
```json
{
  "name" : "es-node",
  "cluster_name" : "caie-cluster",
  "version" : { ... }
}
```

如果看到这个输出，说明Elasticsearch启动成功！

## 📊 第四步：数据处理测试

### 1. 测试数据处理器
在PyCharm中打开 `caie_math_processor.py`，点击 `▶️` 运行

**预期输出**：
```
🚀 CAIE A-Level数学试卷处理器启动
🔍 扫描CAIE数学试卷文件...
📅 处理年份: 2001
📅 处理年份: 2002
...
✅ 总共找到 600+ 个试卷文件
📊 统计信息:
   Question Papers: 300+
   Mark Schemes: 300+
   年份范围: 2001 - 2022
🎉 处理完成！
```

### 2. 检查生成的文件
处理完成后，项目目录应该出现：
- `caie_math_questions.json` - 提取的题目数据
- `elasticsearch_mapping.json` - ES索引配置

## 🔍 第五步：启动API服务器

### 1. 运行FastAPI服务器
点击PyCharm右上角的 `CAIE API Server` 配置，然后点击 `▶️`

**预期输出**：
```
🚀 启动CAIE搜题系统...
✅ Redis连接成功
✅ OCR服务初始化成功
✅ 搜索服务初始化完成
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. 测试API接口

在PyCharm Terminal中测试：

#### 健康检查
```bash
curl http://localhost:8000/health
```

#### 创建搜索索引
```bash
curl -X POST http://localhost:8000/admin/index
```

#### 文本搜索测试
```bash
curl -X POST "http://localhost:8000/search/text" \
     -H "Content-Type: application/json" \
     -d '{"query": "differentiate", "limit": 3}'
```

#### 查看API文档
在浏览器打开: http://localhost:8000/docs

## 🖼️ 第六步：OCR识别测试

### 1. 准备测试图片
找一张包含数学题目的图片，保存为 `test_math.jpg`

### 2. 测试OCR识别
```bash
curl -X POST "http://localhost:8000/ocr" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@test_math.jpg"
```

### 3. 测试拍照搜题
```bash
curl -X POST "http://localhost:8000/search/image" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@test_math.jpg" \
     -F "limit=5"
```

## 🔧 调试技巧

### 1. 查看日志
在PyCharm的 `Run` 窗口中可以看到详细日志

### 2. 断点调试
- 在代码行号左侧点击设置断点
- 点击 `🐛` Debug运行
- 当程序执行到断点时会暂停

### 3. 检查Docker容器
```bash
# 查看容器状态
docker-compose ps

# 查看Elasticsearch日志
docker-compose logs elasticsearch

# 重启服务
docker-compose restart elasticsearch redis
```

### 4. 常见问题解决

#### Elasticsearch启动失败
```bash
# 增加虚拟内存
sudo sysctl -w vm.max_map_count=262144

# 重启Docker Desktop
```

#### PaddleOCR下载慢
```bash
# 设置清华源镜像
pip install paddleocr -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 端口被占用
```bash
# 查看端口占用
lsof -i :8000
lsof -i :9200

# 杀死进程
kill -9 <PID>
```

## 📈 第七步：性能测试

### 1. 查看系统统计
```bash
curl http://localhost:8000/admin/stats
```

### 2. 批量测试搜索
创建测试脚本 `test_search.py`:
```python
import requests
import time

def test_search_performance():
    queries = [
        "differentiate function",
        "integrate polynomial", 
        "solve equation",
        "graph parabola",
        "matrix multiplication"
    ]
    
    for query in queries:
        start = time.time()
        response = requests.post(
            "http://localhost:8000/search/text",
            json={"query": query, "limit": 5}
        )
        end = time.time()
        
        print(f"查询: {query}")
        print(f"响应时间: {end-start:.2f}秒")
        print(f"结果数量: {len(response.json())}")
        print("-" * 50)

if __name__ == "__main__":
    test_search_performance()
```

### 3. 运行性能测试
```bash
python test_search.py
```

## 🎯 预期测试结果

**成功标准**：
- ✅ Docker服务正常启动
- ✅ 处理600+份CAIE数学试卷
- ✅ 提取3000+个题目到Elasticsearch
- ✅ OCR识别准确率>80%
- ✅ 搜索响应时间<2秒
- ✅ API接口正常响应

**如果一切正常，你应该看到**：
- Elasticsearch索引大小: ~50-100MB
- OCR识别：英文和数学符号
- 搜索结果：包含题目内容和对应答案
- API响应：JSON格式的结构化数据

## 📱 第八步：iOS App集成准备

测试成功后，在你的iOS项目 `SearchService.swift` 中更新：

```swift
// 开发环境
private let baseURL = "http://localhost:8000"

// 生产环境（云端部署后）  
private let baseURL = "http://your-server-ip:8000"
```

## 🚀 下一步

本地测试成功后，你可以：
1. 购买腾讯云轻量服务器（¥45/月）
2. 部署到云端
3. 集成到iOS App
4. 添加更多考试局数据（Chemistry, Physics等）

有任何问题都可以在PyCharm中设置断点调试！