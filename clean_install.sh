#!/bin/bash
# 清理安装脚本 - 解决依赖冲突

echo "🧹 清理环境和重新安装依赖..."

# 1. 清理pip缓存
echo "📦 清理pip缓存..."
pip cache purge

# 2. 卸载问题包
echo "🗑️  卸载可能冲突的包..."
pip uninstall -y PyMuPDF pymupdf fitz
pip uninstall -y paddlepaddle paddleocr
pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless

# 3. 升级pip工具
echo "⬆️  升级pip工具..."
pip install --upgrade pip setuptools wheel

# 4. 分步安装关键依赖
echo "📦 分步安装关键依赖..."

# 安装基础依赖
pip install numpy==1.24.3
pip install pandas==1.5.3
pip install requests==2.31.0
pip install python-dotenv==1.0.0

# 安装PDF处理
pip install PyPDF2==3.0.1

# 安装Web框架
pip install fastapi==0.100.1
pip install uvicorn==0.23.2
pip install python-multipart==0.0.6

# 安装Elasticsearch
pip install elasticsearch==8.8.0

# 安装Redis
pip install redis==4.6.0

# 安装图像处理 (无头版本，避免GUI依赖)
pip install opencv-python-headless==4.8.0.76
pip install Pillow==9.5.0

# 安装OCR (使用稳定版本)
echo "🔍 安装PaddleOCR (可能需要几分钟)..."
pip install paddleocr==2.6.1.3

# 安装AI模型 (可选，如果失败可以跳过)
echo "🤖 安装AI模型..."
pip install sentence-transformers==2.2.2 || echo "⚠️  AI模型安装失败，将禁用语义搜索功能"

echo "✅ 依赖安装完成！"

# 验证关键包
echo "🔍 验证安装..."
python -c "
try:
    import PyPDF2
    print('✅ PyPDF2: OK')
except:
    print('❌ PyPDF2: Failed')

try:
    import paddleocr
    print('✅ PaddleOCR: OK')
except:
    print('❌ PaddleOCR: Failed')

try:
    import fastapi
    print('✅ FastAPI: OK')
except:
    print('❌ FastAPI: Failed')

try:
    import elasticsearch
    print('✅ Elasticsearch: OK')
except:
    print('❌ Elasticsearch: Failed')
"

echo "🎉 安装验证完成！可以运行 python main.py 启动服务"