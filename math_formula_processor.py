#!/usr/bin/env python3
"""
数学公式处理器
专门处理数学符号标准化和公式识别
"""

import re
from typing import Dict, List, Tuple
import logging

class MathFormulaProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 数学符号标准化映射
        self.symbol_mappings = {
            # 基础操作符
            "×": "*", "÷": "/", "≠": "!=", "≤": "<=", "≥": ">=", "±": "+-",
            
            # 希腊字母
            "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta", 
            "θ": "theta", "λ": "lambda", "μ": "mu", "π": "pi", "σ": "sigma",
            "φ": "phi", "ψ": "psi", "ω": "omega",
            
            # 数学函数
            "√": "sqrt", "∫": "integral", "∑": "sum", "∏": "product",
            "∂": "partial", "∇": "nabla", "∞": "infinity",
            
            # 集合符号
            "∈": "in", "∉": "not_in", "⊂": "subset", "⊃": "superset",
            "∪": "union", "∩": "intersection", "∅": "empty_set",
            
            # 逻辑符号
            "∧": "and", "∨": "or", "¬": "not", "→": "implies", "↔": "iff",
            
            # 特殊符号
            "°": "degree", "′": "prime", "″": "double_prime"
        }
        
        # 常见数学术语同义词
        self.math_synonyms = {
            "differentiate": ["derivative", "diff", "d/dx", "differentiation"],
            "integrate": ["integration", "integral", "antiderivative"],
            "solve": ["find", "calculate", "determine", "compute"],
            "function": ["equation", "formula", "expression"],
            "graph": ["plot", "curve", "sketch", "draw"],
            "root": ["solution", "zero", "x-intercept"],
            "maximum": ["max", "peak", "highest", "supremum"],
            "minimum": ["min", "lowest", "infimum"],
            "derivative": ["gradient", "slope", "rate of change"],
            "coefficient": ["constant", "parameter"],
            "polynomial": ["quadratic", "cubic", "quartic", "quintic"],
            "exponential": ["exp", "e^x", "exponential function"],
            "logarithm": ["log", "ln", "natural log", "logarithmic"],
            "trigonometric": ["trig", "sin", "cos", "tan", "sine", "cosine", "tangent"],
            "matrix": ["matrices", "array", "grid"],
            "vector": ["vectors", "direction", "magnitude"],
            "limit": ["approach", "tends to", "as x approaches"],
            "continuous": ["smooth", "unbroken", "continuous function"],
            "domain": ["input", "x-values", "independent variable"],
            "range": ["output", "y-values", "dependent variable"]
        }
    
    def normalize_math_symbols(self, text: str) -> str:
        """标准化数学符号"""
        if not text:
            return text
            
        normalized = text
        
        # 替换数学符号
        for symbol, replacement in self.symbol_mappings.items():
            normalized = normalized.replace(symbol, f" {replacement} ")
        
        # 处理上标和下标（简化版）
        # x^2 -> x squared, x^3 -> x cubed, x^n -> x to the power n
        normalized = re.sub(r'(\w)\^2\b', r'\1 squared', normalized)
        normalized = re.sub(r'(\w)\^3\b', r'\1 cubed', normalized)
        normalized = re.sub(r'(\w)\^(\d+)', r'\1 to the power \2', normalized)
        normalized = re.sub(r'(\w)\^([a-zA-Z])', r'\1 to the power \2', normalized)
        
        # 处理下标
        normalized = re.sub(r'(\w)_(\d+)', r'\1 sub \2', normalized)
        normalized = re.sub(r'(\w)_([a-zA-Z])', r'\1 sub \2', normalized)
        
        # 处理分数 a/b -> a over b
        normalized = re.sub(r'(\w+)/(\w+)', r'\1 over \2', normalized)
        
        # 处理括号中的表达式
        normalized = re.sub(r'\(([^)]+)\)', r'bracket \1 bracket', normalized)
        
        # 清理多余空格
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def extract_mathematical_concepts(self, text: str) -> List[str]:
        """提取数学概念和关键词"""
        concepts = []
        text_lower = text.lower()
        
        # 检查基础数学概念
        for concept, synonyms in self.math_synonyms.items():
            if concept in text_lower or any(syn in text_lower for syn in synonyms):
                concepts.append(concept)
        
        # 检查数学模式
        patterns = [
            (r'x\^(\d+)', 'polynomial'),
            (r'e\^', 'exponential'),
            (r'log|ln', 'logarithmic'),
            (r'sin|cos|tan', 'trigonometric'),
            (r'd/dx|derivative', 'calculus'),
            (r'integral|∫', 'calculus'),
            (r'matrix|determinant', 'linear_algebra'),
            (r'vector', 'vector_math'),
            (r'limit|approach', 'limits'),
            (r'equation.*=', 'equation_solving')
        ]
        
        for pattern, concept in patterns:
            if re.search(pattern, text_lower):
                concepts.append(concept)
        
        return list(set(concepts))
    
    def enhance_search_query(self, query: str) -> Dict[str, str]:
        """增强搜索查询，添加数学同义词"""
        enhanced_queries = {}
        
        # 原始查询
        enhanced_queries['original'] = query
        
        # 标准化查询
        enhanced_queries['normalized'] = self.normalize_math_symbols(query)
        
        # 概念扩展查询
        concepts = self.extract_mathematical_concepts(query)
        if concepts:
            concept_terms = []
            for concept in concepts:
                if concept in self.math_synonyms:
                    concept_terms.extend(self.math_synonyms[concept])
            enhanced_queries['expanded'] = f"{query} {' '.join(concept_terms)}"
        
        return enhanced_queries
    
    def process_pdf_text(self, raw_text: str) -> str:
        """处理从PDF提取的原始文本"""
        if not raw_text:
            return raw_text
        
        processed = raw_text
        
        # 修复常见PDF提取问题
        processed = re.sub(r'\s+', ' ', processed)  # 合并多余空格
        processed = re.sub(r'([a-z])([A-Z])', r'\1 \2', processed)  # 分离连接的词
        
        # 识别和标准化数学表达式
        processed = self.normalize_math_symbols(processed)
        
        # 添加数学概念标签
        concepts = self.extract_mathematical_concepts(processed)
        if concepts:
            processed += f" [math_concepts: {', '.join(concepts)}]"
        
        return processed
    
    def identify_formula_regions(self, text: str) -> List[Tuple[int, int, str]]:
        """识别文本中的公式区域"""
        formula_regions = []
        
        # 增强的公式检测模式
        patterns = [
            r'[a-zA-Z]\^[0-9a-zA-Z\{\}]+',     # 指数（支持花括号）
            r'[a-zA-Z]_[0-9a-zA-Z\{\}]+',      # 下标（支持花括号）
            r'\b\w+\s*[=≠<>≤≥]\s*\w+',        # 等式和不等式
            r'\b[a-zA-Z]\([^)]*\)',            # 函数调用
            r'[0-9]+[a-zA-Z]+[0-9]*',          # 混合数字字母
            r'√[^√]*',                         # 根号表达式
            r'∫[^∫]*d[a-zA-Z]',               # 积分表达式
            r'\b(?:sin|cos|tan|log|ln|exp)\([^)]*\)',  # 三角函数和对数
            r'\b[a-zA-Z]\s*\+\s*[a-zA-Z]',    # 代数表达式
            r'\b\d*[a-zA-Z]\d*[+-]\d*[a-zA-Z]\d*',  # 多项式
            r'\([^)]*\)\^[0-9a-zA-Z]+',        # 括号表达式的幂
            r'\b\d+/\d+',                      # 分数
            r'[a-zA-Z]+[0-9]*\s*[*/]\s*[a-zA-Z]+[0-9]*',  # 乘除表达式
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                start, end = match.span()
                formula_regions.append((start, end, match.group()))
        
        return formula_regions
    
    def extract_formula_features(self, text: str) -> List[str]:
        """提取数学公式的结构特征"""
        features = []
        
        # 公式结构特征
        structure_patterns = {
            'has_exponent': r'[a-zA-Z]\^',
            'has_subscript': r'[a-zA-Z]_',
            'has_fraction': r'\d+/\d+',
            'has_root': r'√',
            'has_integral': r'∫',
            'has_summation': r'∑',
            'has_product': r'∏',
            'has_trigonometric': r'\b(sin|cos|tan|sec|csc|cot)',
            'has_logarithm': r'\b(log|ln)',
            'has_exponential': r'\be\^',
            'has_inequality': r'[<>≤≥≠]',
            'has_equation': r'=',
            'has_parentheses': r'\([^)]+\)',
            'has_brackets': r'\[[^\]]+\]',
            'has_absolute_value': r'\|[^|]+\|',
            'has_derivative': r'd[a-zA-Z]/d[a-zA-Z]',
            'has_partial': r'∂[a-zA-Z]/∂[a-zA-Z]',
            'has_limit': r'\blim\b',
            'has_matrix': r'\[.*\].*\[.*\]',
            'has_vector': r'\b[a-zA-Z]\s*\+\s*[a-zA-Z]\s*i\b',
            'polynomial_degree_2': r'[a-zA-Z]\^2',
            'polynomial_degree_3': r'[a-zA-Z]\^3',
            'linear_equation': r'[a-zA-Z]\s*[+-]\s*\d+\s*=',
            'quadratic_formula': r'[a-zA-Z]\^2\s*[+-].*[a-zA-Z]\s*[+-]',
        }
        
        for feature_name, pattern in structure_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                features.append(feature_name)
        
        # 复杂度级别
        complexity_score = len(features)
        if complexity_score >= 8:
            features.append('high_complexity')
        elif complexity_score >= 4:
            features.append('medium_complexity')
        else:
            features.append('low_complexity')
        
        return features
    
    def tokenize_formula(self, formula: str) -> List[str]:
        """将数学公式分解为标准化token"""
        tokens = []
        
        # 首先标准化符号
        normalized = self.normalize_math_symbols(formula)
        
        # 提取数学元素
        patterns = [
            (r'\b(?:sin|cos|tan|log|ln|exp|sqrt|lim)\b', 'FUNCTION'),
            (r'\b(?:pi|e|alpha|beta|gamma|theta|lambda|sigma|phi|omega)\b', 'CONSTANT'),
            (r'\b\d+(?:\.\d+)?\b', 'NUMBER'),
            (r'\b[a-zA-Z](?:_\w+)?\b', 'VARIABLE'),
            (r'\^', 'POWER'),
            (r'[+\-*/=<>≤≥≠]', 'OPERATOR'),
            (r'[()]', 'BRACKET'),
            (r'integral|sum|product|partial|nabla', 'CALCULUS'),
        ]
        
        for pattern, token_type in patterns:
            for match in re.finditer(pattern, normalized):
                tokens.append(f"{token_type}:{match.group()}")
        
        return tokens