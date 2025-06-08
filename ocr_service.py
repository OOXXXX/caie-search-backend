#!/usr/bin/env python3
"""
OCR识别服务
支持数学公式和化学符号的高精度识别
"""

import cv2
import numpy as np
from PIL import Image
import paddleocr
from typing import Dict, List, Any
import asyncio
import logging
from math_formula_processor import MathFormulaProcessor


class OCRService:
    def __init__(self):
        """初始化OCR服务"""
        self.logger = logging.getLogger(__name__)

        # 初始化数学公式处理器
        self.math_processor = MathFormulaProcessor()

        # 初始化PaddleOCR
        try:
            self.ocr = paddleocr.PaddleOCR(
                use_angle_cls=True,  # 使用角度分类器
                lang='en',  # 英文识别
                use_gpu=False,  # CPU模式（云服务器通常无GPU）
                show_log=False
            )
            self.logger.info("✅ PaddleOCR初始化成功")
        except Exception as e:
            self.logger.error(f"❌ PaddleOCR初始化失败: {e}")
            raise

    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        """图像预处理"""
        try:
            # 转换为numpy数组
            img_array = np.array(image)

            # 如果是RGBA，转换为RGB
            if len(img_array.shape) == 3 and img_array.shape[2] == 4:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)

            # 转换为灰度图
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array

            # 图像增强
            # 1. 降噪
            denoised = cv2.medianBlur(gray, 3)

            # 2. 对比度增强
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)

            # 3. 二值化
            _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            return binary

        except Exception as e:
            self.logger.error(f"图像预处理失败: {e}")
            # 如果预处理失败，返回原图
            return np.array(image.convert('RGB'))

    async def extract_text(self, image: Image.Image) -> Dict[str, Any]:
        """提取图像中的文字"""
        try:
            # 预处理图像
            processed_img = self.preprocess_image(image)

            # 异步执行OCR (在线程池中运行)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._run_ocr,
                processed_img
            )

            return result

        except Exception as e:
            self.logger.error(f"OCR识别失败: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "boxes": []
            }

    def _run_ocr(self, image: np.ndarray) -> Dict[str, Any]:
        """执行OCR识别"""
        try:
            # 使用PaddleOCR识别
            results = self.ocr.ocr(image, cls=True)

            if not results or not results[0]:
                return {
                    "text": "",
                    "confidence": 0.0,
                    "boxes": []
                }

            # 解析结果
            text_lines = []
            confidences = []
            boxes = []

            for line in results[0]:
                if line:
                    box, (text, confidence) = line
                    text_lines.append(text)
                    confidences.append(confidence)
                    boxes.append([int(coord) for point in box for coord in point])

            # 组合文本
            full_text = " ".join(text_lines)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            # 后处理：数学公式识别增强
            enhanced_text = self.math_processor.process_pdf_text(full_text)

            # 提取数学特征用于匹配
            math_features = self.math_processor.extract_formula_features(full_text)
            formula_tokens = self.math_processor.tokenize_formula(full_text)

            return {
                "text": enhanced_text,
                "original_text": full_text,
                "math_features": math_features,
                "formula_tokens": formula_tokens,
                "confidence": avg_confidence,
                "boxes": boxes
            }

        except Exception as e:
            self.logger.error(f"PaddleOCR执行失败: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "boxes": []
            }

    def _enhance_math_text(self, text: str) -> str:
        """数学公式文本增强"""
        if not text:
            return text

        # 常见数学符号替换
        replacements = {
            " x ": " × ",
            " / ": " ÷ ",
            ">=": "≥",
            "<=": "≤",
            "!=": "≠",
            "+-": "±",
            "sqrt": "√",
            "pi": "π",
            "alpha": "α",
            "beta": "β",
            "gamma": "γ",
            "theta": "θ",
            "lambda": "λ",
            "sigma": "σ",
        }

        enhanced = text
        for old, new in replacements.items():
            enhanced = enhanced.replace(old, new)

        # 移除多余空格
        enhanced = " ".join(enhanced.split())

        return enhanced

    def detect_math_formulas(self, image: Image.Image) -> List[Dict]:
        """检测数学公式区域（扩展功能）"""
        # TODO: 实现专门的数学公式检测
        # 可以使用深度学习模型检测公式区域
        # 然后对这些区域使用专门的数学OCR
        pass

    def detect_chemical_formulas(self, image: Image.Image) -> List[Dict]:
        """检测化学分子式（扩展功能）"""
        # TODO: 实现化学分子式检测
        # 识别化学元素符号、下标、上标等
        pass