#!/bin/bash
# PyMuPDF安装修复脚本

echo "🔧 修复PyMuPDF安装问题..."

# 检查系统
echo "系统信息:"
uname -a
python --version

# 方法1: 先尝试系统依赖安装
echo "📦 安装系统依赖..."
if command -v brew &> /dev/null; then
    echo "使用Homebrew安装依赖..."
    brew install mupdf-tools
    brew install freetype
else
    echo "⚠️  未安装Homebrew，建议安装: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
fi

# 方法2: 升级pip和setuptools
echo "📦 升级pip和构建工具..."
pip install --upgrade pip setuptools wheel

# 方法3: 先安装基础依赖（不包含PyMuPDF）
echo "📦 安装基础依赖包..."
pip install -r requirements.txt

echo "✅ 基础依赖安装完成"

# 方法4: 尝试不同版本的PyMuPDF
echo "🔄 尝试安装PyMuPDF..."

# 尝试预编译版本
pip install --upgrade pymupdf

if [ $? -eq 0 ]; then
    echo "✅ PyMuPDF安装成功"
else
    echo "⚠️  PyMuPDF安装失败，使用PyPDF2替代方案"
    echo "系统将使用PyPDF2进行PDF处理，功能略有差异但基本可用"
fi

echo "🎉 安装修复完成！可以继续运行程序"