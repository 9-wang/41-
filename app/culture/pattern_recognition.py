import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import current_app
from app import db
from app.culture.models import CulturePattern, PatternRecognitionResult

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PatternRecognition')

class PatternRecognitionManager:
    """纹样识别管理器，负责纹样识别的数据管理和操作"""
    
    def __init__(self):
        """初始化纹样识别管理器"""
        self.logger = logger
    
    def get_culture_patterns(self, category: Optional[str] = None, region: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取文化图案列表
        
        Args:
            category: 图案类别
            region: 地域
            
        Returns:
            文化图案列表
        """
        try:
            query = CulturePattern.query
            
            # 应用筛选条件
            if category:
                query = query.filter_by(category=category)
            if region:
                query = query.filter_by(region=region)
            
            patterns = query.all()
            
            # 转换为字典列表
            result = []
            for pattern in patterns:
                result.append({
                    'id': pattern.id,
                    'name': pattern.name,
                    'era': pattern.era,
                    'region': pattern.region,
                    'category': pattern.category,
                    'carrier': pattern.carrier,
                    'technique': pattern.technique,
                    'description': pattern.description,
                    'image_url': pattern.image_url,
                    'pattern_features': pattern.pattern_features,
                    'similarity_score': pattern.similarity_score,
                    'created_at': pattern.created_at.isoformat()
                })
            
            return result
        except Exception as e:
            self.logger.error(f"获取文化图案列表失败: {str(e)}")
            return []
    
    def add_culture_pattern(self, name: str, era: Optional[str] = None, region: Optional[str] = None,
                           category: Optional[str] = None, carrier: Optional[str] = None,
                           technique: Optional[str] = None, description: Optional[str] = None,
                           image_url: Optional[str] = None, pattern_features: Optional[str] = None) -> Dict[str, Any]:
        """
        添加文化图案
        
        Args:
            name: 图案名称
            era: 时代
            region: 地域
            category: 类别
            carrier: 载体
            technique: 工艺
            description: 图案描述
            image_url: 图案图片URL
            pattern_features: 图案特征
            
        Returns:
            操作结果
        """
        try:
            # 检查是否已存在同名图案
            existing_pattern = CulturePattern.query.filter_by(name=name).first()
            if existing_pattern:
                return {
                    "success": False,
                    "error": f"已存在名为 '{name}' 的文化图案"
                }
            
            # 创建新的文化图案
            new_pattern = CulturePattern(
                name=name,
                era=era,
                region=region,
                category=category,
                carrier=carrier,
                technique=technique,
                description=description,
                image_url=image_url,
                pattern_features=pattern_features
            )
            
            db.session.add(new_pattern)
            db.session.commit()
            
            return {
                "success": True,
                "message": f"成功添加文化图案 '{name}'",
                "data": {
                    "id": new_pattern.id,
                    "name": new_pattern.name,
                    "image_url": new_pattern.image_url
                }
            }
        except Exception as e:
            self.logger.error(f"添加文化图案失败: {str(e)}")
            return {
                "success": False,
                "error": f"添加文化图案失败: {str(e)}"
            }
    
    def recognize_pattern(self, input_image: str, 
                        recognized_pattern: str, recognition_score: float,
                        user_id: Optional[int] = None, features: Optional[str] = None, 
                        similarity_matrix: Optional[str] = None, pattern_id: Optional[int] = None) -> Dict[str, Any]:
        """
        记录纹样识别结果
        
        Args:
            user_id: 用户ID
            input_image: 输入图像路径
            recognized_pattern: 识别出的纹样名称
            recognition_score: 识别评分
            features: 识别特征向量
            similarity_matrix: 相似度矩阵
            pattern_id: 关联的文化图案ID
            
        Returns:
            操作结果
        """
        try:
            # 创建新的识别结果记录
            new_result = PatternRecognitionResult(
                user_id=user_id,
                input_image=input_image,
                recognized_pattern=recognized_pattern,
                recognition_score=recognition_score,
                features=features,
                similarity_matrix=similarity_matrix,
                pattern_id=pattern_id
            )
            
            db.session.add(new_result)
            db.session.commit()
            
            return {
                "success": True,
                "message": "纹样识别结果已记录",
                "data": {
                    "id": new_result.id,
                    "recognized_pattern": new_result.recognized_pattern,
                    "recognition_score": new_result.recognition_score,
                    "created_at": new_result.created_at.isoformat()
                }
            }
        except Exception as e:
            self.logger.error(f"记录纹样识别结果失败: {str(e)}")
            return {
                "success": False,
                "error": f"记录纹样识别结果失败: {str(e)}"
            }
    
    def get_recognition_results(self, user_id: Optional[int] = None, limit: int = 10, 
                              offset: int = 0) -> Dict[str, Any]:
        """
        获取纹样识别结果列表
        
        Args:
            user_id: 用户ID，可选，用于筛选特定用户的识别结果
            limit: 返回结果数量限制
            offset: 结果偏移量
            
        Returns:
            识别结果列表
        """
        try:
            query = PatternRecognitionResult.query
            
            # 应用筛选条件
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            # 排序并分页
            total = query.count()
            results = query.order_by(PatternRecognitionResult.created_at.desc())\
                .limit(limit).offset(offset).all()
            
            # 转换为字典列表
            result_list = []
            for result in results:
                result_dict = {
                    'id': result.id,
                    'user_id': result.user_id,
                    'input_image': result.input_image,
                    'recognized_pattern': result.recognized_pattern,
                    'recognition_score': result.recognition_score,
                    'features': result.features,
                    'similarity_matrix': result.similarity_matrix,
                    'pattern_id': result.pattern_id,
                    'created_at': result.created_at.isoformat(),
                    'updated_at': result.updated_at.isoformat()
                }
                
                # 如果关联了文化图案，添加图案信息
                if result.culture_pattern:
                    result_dict['culture_pattern'] = {
                        'id': result.culture_pattern.id,
                        'name': result.culture_pattern.name,
                        'image_url': result.culture_pattern.image_url
                    }
                
                result_list.append(result_dict)
            
            return {
                "success": True,
                "data": result_list,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            self.logger.error(f"获取纹样识别结果列表失败: {str(e)}")
            return {
                "success": False,
                "error": f"获取纹样识别结果列表失败: {str(e)}"
            }
    
    def analyze_pattern_similarity(self, pattern_id: int, other_pattern_ids: List[int]) -> Dict[str, Any]:
        """
        分析图案相似度
        
        Args:
            pattern_id: 基准图案ID
            other_pattern_ids: 其他图案ID列表
            
        Returns:
            相似度分析结果
        """
        try:
            # 获取基准图案
            base_pattern = CulturePattern.query.get(pattern_id)
            if not base_pattern:
                return {
                    "success": False,
                    "error": f"未找到ID为 {pattern_id} 的文化图案"
                }
            
            # 获取其他图案
            other_patterns = CulturePattern.query.filter(CulturePattern.id.in_(other_pattern_ids)).all()
            
            # 简单的相似度计算（实际项目中应使用更复杂的算法）
            similarity_results = []
            for pattern in other_patterns:
                # 这里使用简单的字符串相似度计算（实际项目中应使用图像处理算法）
                # 示例：基于名称和特征的简单相似度
                similarity_score = 0.0
                
                # 名称相似度（示例）
                if base_pattern.name == pattern.name:
                    similarity_score += 0.5
                
                # 特征相似度（示例）
                if base_pattern.pattern_features and pattern.pattern_features:
                    # 简单的字符串重叠率计算
                    base_features = set(base_pattern.pattern_features.split(','))
                    other_features = set(pattern.pattern_features.split(','))
                    intersection = base_features.intersection(other_features)
                    if base_features or other_features:
                        similarity_score += len(intersection) / max(len(base_features), len(other_features)) * 0.5
                
                similarity_results.append({
                    'pattern_id': pattern.id,
                    'name': pattern.name,
                    'similarity_score': round(similarity_score, 2),
                    'image_url': pattern.image_url
                })
            
            return {
                "success": True,
                "data": {
                    "base_pattern": {
                        "id": base_pattern.id,
                        "name": base_pattern.name,
                        "image_url": base_pattern.image_url
                    },
                    "similarity_results": similarity_results
                }
            }
        except Exception as e:
            self.logger.error(f"分析图案相似度失败: {str(e)}")
            return {
                "success": False,
                "error": f"分析图案相似度失败: {str(e)}"
            }
    
    def delete_recognition_result(self, result_id: int) -> Dict[str, Any]:
        """
        删除纹样识别结果
        
        Args:
            result_id: 识别结果ID
            
        Returns:
            操作结果
        """
        try:
            # 查找识别结果
            result = PatternRecognitionResult.query.get(result_id)
            if not result:
                return {
                    "success": False,
                    "error": f"未找到ID为 {result_id} 的识别结果"
                }
            
            # 删除识别结果
            db.session.delete(result)
            db.session.commit()
            
            return {
                "success": True,
                "message": "纹样识别结果已删除"
            }
        except Exception as e:
            self.logger.error(f"删除纹样识别结果失败: {str(e)}")
            return {
                "success": False,
                "error": f"删除纹样识别结果失败: {str(e)}"
            }
