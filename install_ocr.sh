#!/bin/bash
# OCR安装脚本 - 英国环境优化

echo "🔍 安装OCR功能（英国网络环境）..."

# 1. 清理环境
echo "🧹 清理环境..."
pip uninstall -y PyMuPDF pymupdf paddleocr visualdl

# 2. 安装系统依赖（如果有Homebrew）
if command -v brew &> /dev/null; then
    echo "📦 安装系统依赖..."
    brew install freetype libpng jpeg
fi

# 3. 升级构建工具
echo "⬆️ 升级构建工具..."
pip install --upgrade pip setuptools wheel

# 4. 先安装PaddlePaddle
echo "🏓 安装PaddlePaddle..."
pip install paddlepaddle==2.5.1

# 5. 安装图像处理依赖
echo "🖼️ 安装图像处理库..."
pip install opencv-python-headless==4.8.0.76
pip install Pillow==9.5.0
pip install shapely>=1.7.0
pip install pyclipper>=1.2.0
pip install imgaug>=0.4.0
pip install lmdb>=1.0.0

# 6. 尝试安装PaddleOCR（不包含problematic依赖）
echo "🔍 安装PaddleOCR..."
pip install paddleocr==2.6.1.3 --no-deps

# 7. 手动安装必要的依赖（跳过PyMuPDF）
echo "📦 安装必要依赖..."
pip install python-Levenshtein>=0.12.0
pip install rapidfuzz>=1.1.0

# 8. 验证安装
echo "✅ 验证安装..."
python -c "
try:
    import paddleocr
    print('✅ PaddleOCR安装成功')
    
    # 简单测试
    ocr = paddleocr.PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
    print('✅ PaddleOCR初始化成功')
except Exception as e:
    print(f'❌ PaddleOCR测试失败: {e}')

try:
    import cv2
    print('✅ OpenCV可用')
except:
    print('❌ OpenCV不可用')
"

echo "🎉 OCR安装完成！"