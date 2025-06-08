#!/usr/bin/env python3
"""
数学公式搜索优化器
专门优化数学公式的OCR识别和搜索匹配
"""

import asyncio
import logging
from typing import Dict, List, Any, Tuple
from math_formula_processor import MathFormulaProcessor
from search_service import SearchService

class MathSearchOptimizer:
    def __init__(self, search_service: SearchService):
        """初始化数学搜索优化器"""
        self.logger = logging.getLogger(__name__)
        self.search_service = search_service
        self.math_processor = MathFormulaProcessor()
        
    async def optimize_ocr_search(self, ocr_result: Dict[str, Any]) -> List[Dict]:
        """优化OCR结果的搜索匹配"""
        try:
            # 获取OCR识别的文本和特征
            original_text = ocr_result.get('original_text', '')
            enhanced_text = ocr_result.get('text', '')
            math_features = ocr_result.get('math_features', [])
            formula_tokens = ocr_result.get('formula_tokens', [])
            confidence = ocr_result.get('confidence', 0.0)
            
            # 构建多层次搜索策略
            search_strategies = []
            
            # 策略1: 公式token精确匹配 (最高优先级)
            if formula_tokens:
                token_query = " ".join(formula_tokens)
                search_strategies.append({
                    'method': 'formula_tokens',
                    'query': token_query,
                    'weight': 1.0,
                    'description': '数学公式token精确匹配'
                })
            
            # 策略2: 数学特征匹配
            if math_features:
                features_query = " ".join(math_features)
                search_strategies.append({
                    'method': 'math_features',
                    'query': features_query,
                    'weight': 0.9,
                    'description': '数学特征结构匹配'
                })
            
            # 策略3: 增强文本搜索
            if enhanced_text:
                search_strategies.append({
                    'method': 'enhanced_text',
                    'query': enhanced_text,
                    'weight': 0.8,
                    'description': '增强文本搜索'
                })
            
            # 策略4: 原始文本模糊匹配
            if original_text:
                search_strategies.append({
                    'method': 'original_fuzzy',
                    'query': original_text,
                    'weight': 0.6,
                    'description': '原始文本模糊匹配'
                })
            
            # 策略5: 部分匹配 - 分解复杂公式
            partial_queries = self._extract_partial_formulas(original_text)
            for partial in partial_queries:
                search_strategies.append({
                    'method': 'partial_formula',
                    'query': partial,
                    'weight': 0.5,
                    'description': f'部分公式匹配: {partial[:20]}...'
                })
            
            # 执行并行搜索
            search_results = await self._execute_parallel_search(search_strategies)
            
            # 融合和排序结果
            final_results = self._merge_and_rank_results(search_results, confidence)
            
            return final_results
            
        except Exception as e:
            self.logger.error(f"OCR搜索优化失败: {e}")
            return []
    
    async def _execute_parallel_search(self, strategies: List[Dict]) -> List[Tuple[Dict, List]]:
        """并行执行多个搜索策略"""
        tasks = []
        
        for strategy in strategies:
            task = asyncio.create_task(
                self._search_with_strategy(strategy)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤异常结果
        valid_results = []
        for i, result in enumerate(results):
            if not isinstance(result, Exception):
                valid_results.append((strategies[i], result))
            else:
                self.logger.warning(f"搜索策略失败: {strategies[i]['method']} - {result}")
        
        return valid_results
    
    async def _search_with_strategy(self, strategy: Dict) -> List:
        """使用特定策略执行搜索"""
        try:
            method = strategy['method']
            query = strategy['query']
            
            if method == 'formula_tokens':
                # 使用特殊的token搜索
                return await self._search_by_tokens(query)
            elif method == 'math_features':
                # 数学特征搜索
                return await self._search_by_features(query)
            else:
                # 标准文本搜索
                return await self.search_service.search_by_text(query, limit=5)
                
        except Exception as e:
            self.logger.error(f"搜索策略执行失败 {strategy['method']}: {e}")
            return []
    
    async def _search_by_tokens(self, token_query: str) -> List:
        """基于数学token的专门搜索"""
        # 这里可以实现更精确的token匹配逻辑
        return await self.search_service.search_by_text(token_query, limit=5)
    
    async def _search_by_features(self, features_query: str) -> List:
        """基于数学特征的搜索"""
        # 可以根据数学特征调整搜索参数
        return await self.search_service.search_by_text(features_query, limit=5)
    
    def _extract_partial_formulas(self, text: str) -> List[str]:
        """提取部分公式用于匹配"""
        partials = []
        
        # 识别公式区域
        formula_regions = self.math_processor.identify_formula_regions(text)
        
        for start, end, formula in formula_regions:
            # 添加完整公式
            partials.append(formula)
            
            # 如果公式较长，提取关键部分
            if len(formula) > 10:
                # 提取函数名
                import re
                functions = re.findall(r'\b(?:sin|cos|tan|log|ln|exp|sqrt)\b', formula)
                partials.extend(functions)
                
                # 提取变量组合
                variables = re.findall(r'[a-zA-Z]+', formula)
                if len(variables) >= 2:
                    partials.append(" ".join(variables[:2]))
        
        # 去重并过滤太短的片段
        partials = list(set([p for p in partials if len(p.strip()) >= 2]))
        
        return partials[:5]  # 限制数量避免搜索过多
    
    def _merge_and_rank_results(self, search_results: List[Tuple[Dict, List]], ocr_confidence: float) -> List[Dict]:
        """融合多个搜索结果并重新排序"""
        merged_results = {}
        
        for strategy, results in search_results:
            weight = strategy['weight']
            method = strategy['method']
            
            for result in results:
                result_id = result.id
                
                if result_id not in merged_results:
                    merged_results[result_id] = {
                        'result': result,
                        'total_score': 0.0,
                        'method_scores': {},
                        'method_count': 0
                    }
                
                # 计算加权分数
                method_score = result.confidence * weight
                
                # OCR置信度加权
                if ocr_confidence > 0.8:
                    method_score *= 1.2  # 高置信度OCR提升权重
                elif ocr_confidence < 0.5:
                    method_score *= 0.8  # 低置信度OCR降低权重
                
                # 特殊加权：公式token匹配给予额外奖励
                if method == 'formula_tokens':
                    method_score *= 1.5
                
                merged_results[result_id]['total_score'] += method_score
                merged_results[result_id]['method_scores'][method] = method_score
                merged_results[result_id]['method_count'] += 1
        
        # 计算最终分数并排序
        final_results = []
        for item in merged_results.values():
            # 多方法匹配奖励
            if item['method_count'] > 2:
                item['total_score'] *= 1.3
            elif item['method_count'] > 1:
                item['total_score'] *= 1.1
            
            # 归一化分数
            item['total_score'] = min(item['total_score'], 1.0)
            
            final_results.append({
                'result': item['result'],
                'confidence': item['total_score'],
                'method_scores': item['method_scores'],
                'method_count': item['method_count']
            })
        
        # 按最终分数排序
        final_results.sort(key=lambda x: x['confidence'], reverse=True)
        
        return final_results[:10]  # 返回top 10
    
    def analyze_match_quality(self, ocr_result: Dict, search_result: Dict) -> Dict[str, float]:
        """分析OCR结果与搜索结果的匹配质量"""
        quality_metrics = {}
        
        try:
            ocr_text = ocr_result.get('original_text', '')
            ocr_features = set(ocr_result.get('math_features', []))
            ocr_tokens = set(ocr_result.get('formula_tokens', []))
            
            result_content = search_result['result'].content
            result_features = set(self.math_processor.extract_formula_features(result_content))
            result_tokens = set(self.math_processor.tokenize_formula(result_content))
            
            # Token重叠度
            if ocr_tokens and result_tokens:
                token_overlap = len(ocr_tokens & result_tokens) / len(ocr_tokens | result_tokens)
                quality_metrics['token_overlap'] = token_overlap
            else:
                quality_metrics['token_overlap'] = 0.0
            
            # 特征重叠度
            if ocr_features and result_features:
                feature_overlap = len(ocr_features & result_features) / len(ocr_features | result_features)
                quality_metrics['feature_overlap'] = feature_overlap
            else:
                quality_metrics['feature_overlap'] = 0.0
            
            # 文本相似度（简单版）
            from difflib import SequenceMatcher
            text_similarity = SequenceMatcher(None, ocr_text.lower(), result_content.lower()).ratio()
            quality_metrics['text_similarity'] = text_similarity
            
            # 综合质量分数
            quality_metrics['overall_quality'] = (
                quality_metrics['token_overlap'] * 0.4 +
                quality_metrics['feature_overlap'] * 0.3 +
                quality_metrics['text_similarity'] * 0.3
            )
            
        except Exception as e:
            self.logger.error(f"匹配质量分析失败: {e}")
            quality_metrics = {
                'token_overlap': 0.0,
                'feature_overlap': 0.0,
                'text_similarity': 0.0,
                'overall_quality': 0.0
            }
        
        return quality_metrics