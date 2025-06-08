# CAIE 搜题系统后端

> 基于Elasticsearch和PaddleOCR的智能搜题系统，支持拍照搜题和文本搜索

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Docker Desktop
- PyCharm 或 VS Code

### 一键启动
```bash
# 1. 启动Docker服务
docker-compose up -d

# 2. 安装Python依赖
pip install -r requirements.txt

# 3. 处理数据
python caie_math_processor.py

# 4. 启动API服务器
python main.py
```

### 健康检查
```bash
curl http://localhost:8000/health
```

## 📚 详细指南

- **PyCharm用户**: 查看 [PYCHARM_GUIDE.md](./PYCHARM_GUIDE.md)
- **API文档**: http://localhost:8000/docs
- **Elasticsearch**: http://localhost:9200

## 🎯 核心功能

- ✅ **拍照搜题**: OCR识别 + 智能搜索
- ✅ **文本搜索**: 关键词 + 语义搜索  
- ✅ **数据处理**: 自动解析CAIE数学试卷
- ✅ **答案匹配**: Question Paper + Mark Scheme

## 📊 数据规模

- **试卷数量**: 600+ (2001-2022年)
- **题目数量**: 3000+
- **搜索响应**: <2秒
- **识别准确率**: 85%+

## 💰 部署成本

- **本地开发**: 免费
- **云端部署**: ¥75/月 (腾讯云轻量服务器)

## 🔧 故障排除

### Docker启动失败
```bash
# 重启Docker Desktop
# 增加内存限制: Settings → Resources → Memory (4GB+)
```

### Elasticsearch连接失败
```bash
# 检查容器状态
docker-compose ps

# 重启Elasticsearch
docker-compose restart elasticsearch
```

### PaddleOCR模型下载慢
```bash
# 使用国内镜像
pip install paddleocr -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 📡 API接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/ocr` | POST | OCR识别 |
| `/search/text` | POST | 文本搜索 |
| `/search/image` | POST | 拍照搜题 |
| `/admin/index` | POST | 创建索引 |

## 🏗️ 项目架构

```
用户拍照 → OCR识别 → 文本搜索 → Elasticsearch → 返回结果
    ↓
iOS App → FastAPI → PaddleOCR → 语义匹配 → 题目+答案
```

## 📱 iOS集成

在你的iOS项目中更新API地址：
```swift
let apiURL = "http://localhost:8000"  // 本地测试
// let apiURL = "http://your-server.com:8000"  // 生产环境
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 License

MIT License