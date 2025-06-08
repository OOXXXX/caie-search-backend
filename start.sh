#!/bin/bash
# CAIE搜题系统快速启动脚本

echo "🚀 启动CAIE搜题系统..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker Desktop"
    exit 1
fi

# 检查Python虚拟环境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  建议使用虚拟环境"
    echo "💡 运行: python -m venv venv && source venv/bin/activate"
fi

# 检查当前目录
if [ ! -f "main.py" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 启动Docker服务
echo "🔄 启动Elasticsearch和Redis..."
docker-compose up -d

# 等待Elasticsearch启动
echo "⏳ 等待Elasticsearch启动..."
for i in {1..30}; do
    if curl -s http://localhost:9200/_cluster/health > /dev/null; then
        echo "✅ Elasticsearch已启动"
        break
    fi
    echo "等待中... ($i/30)"
    sleep 2
done

# 检查Elasticsearch是否成功启动
if ! curl -s http://localhost:9200/_cluster/health > /dev/null; then
    echo "❌ Elasticsearch启动失败"
    echo "🔍 检查日志: docker-compose logs elasticsearch"
    exit 1
fi

# 安装Python依赖（如果需要）
if [ ! -f "requirements_installed.flag" ]; then
    echo "📦 安装Python依赖..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        touch requirements_installed.flag
        echo "✅ 依赖安装完成"
    else
        echo "❌ 依赖安装失败"
        exit 1
    fi
fi

# 检查是否已处理数据
if [ ! -f "caie_math_questions.json" ]; then
    echo "📚 首次运行，开始处理CAIE数学试卷数据..."
    echo "⏳ 这可能需要几分钟时间..."
    python caie_math_processor.py
    if [ $? -ne 0 ]; then
        echo "❌ 数据处理失败"
        exit 1
    fi
fi

# 启动API服务器
echo "🌐 启动API服务器..."
echo ""
echo "📱 API地址: http://localhost:8000"
echo "📖 API文档: http://localhost:8000/docs"
echo "🔍 Elasticsearch: http://localhost:9200"
echo "💾 Redis: localhost:6379"
echo ""
echo "📚 使用指南: 查看 PYCHARM_GUIDE.md"
echo "🏥 健康检查: curl http://localhost:8000/health"
echo ""
echo "按 Ctrl+C 停止服务"

# 启动FastAPI服务器
python main.py