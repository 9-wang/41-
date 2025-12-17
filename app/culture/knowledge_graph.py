import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from app import db
from app.culture.models import CultureElement, EthnicGroup, CultureEthnicRelation, CulturalPractice

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('KnowledgeGraph')

class KnowledgeGraphManager:
    """知识图谱管理器，负责知识图谱的数据管理和操作"""
    
    def __init__(self):
        """初始化知识图谱管理器"""
        self.logger = logger
    
    def get_culture_graph_data(self, keyword: str = '茶', ethnic_group: str = '全部', 
                              culture_type: str = '全部', aspect: str = '全部') -> Dict[str, Any]:
        """
        获取文化知识图谱数据
        
        Args:
            keyword: 关键词
            ethnic_group: 民族
            culture_type: 文化类型
            aspect: 文化内涵
            
        Returns:
            知识图谱数据
        """
        try:
            self.logger.info(f"获取图谱数据，关键词: {keyword}, 民族: {ethnic_group}, 文化类型: {culture_type}, 文化内涵: {aspect}")
            
            # 构建默认数据，确保即使数据库中没有数据，也能返回合理的结果
            default_graph_data = {
                'central_topic': keyword,
                'description': f'关于"{keyword}"的文化知识图谱',
                'ethnic_groups': [
                    { 'name': '汉族', 'culture': f'汉族的{keyword}文化', 'customs': f'汉族关于{keyword}的传统习俗' },
                    { 'name': '藏族', 'culture': f'藏族的{keyword}文化', 'customs': f'藏族关于{keyword}的传统习俗' },
                    { 'name': '蒙古族', 'culture': f'蒙古族的{keyword}文化', 'customs': f'蒙古族关于{keyword}的传统习俗' }
                ]
            }
            
            # 查询文化元素，支持模糊搜索
            from sqlalchemy import or_
            
            # 先尝试精确匹配
            culture_element = CultureElement.query.filter_by(name=keyword).first()
            culture_elements = []
            
            if culture_element:
                # 如果精确匹配到，直接使用
                culture_elements = [culture_element]
                self.logger.info(f'精确匹配到文化元素: {culture_element.name}')
            else:
                # 如果没有精确匹配到，尝试模糊匹配
                self.logger.info(f'未精确匹配到文化元素，尝试模糊匹配: {keyword}')
                query = CultureElement.query.filter(
                    or_(
                        CultureElement.name.like(f'%{keyword}%'),
                        CultureElement.description.like(f'%{keyword}%')
                    )
                )
                culture_elements = query.all()
                self.logger.info(f'模糊匹配到 {len(culture_elements)} 个文化元素')
            
            # 如果没有找到匹配的文化元素，返回默认数据
            if not culture_elements:
                self.logger.info(f'没有找到匹配的文化元素，返回关键词"{keyword}"的默认数据')
                return default_graph_data
            
            # 如果有多个匹配，取第一个
            culture_element = culture_elements[0]
            
            # 查询文化-民族关系
            relations_query = CultureEthnicRelation.query.filter_by(culture_element_id=culture_element.id)
            
            # 如果指定了民族，进行筛选
            if ethnic_group and ethnic_group != '全部':
                ethnic = EthnicGroup.query.filter_by(name=ethnic_group).first()
                if ethnic:
                    relations_query = relations_query.filter_by(ethnic_group_id=ethnic.id)
            
            # 处理文化类型筛选
            if culture_type and culture_type != '全部':
                self.logger.info(f'处理文化类型筛选: {culture_type}')
                # 如果文化类型不是全部，先检查是否是精确匹配
                culture_element_by_type = CultureElement.query.filter_by(name=culture_type).first()
                if culture_element_by_type:
                    # 如果是精确匹配，直接使用该文化元素
                    culture_element = culture_element_by_type
                    self.logger.info(f'文化类型精确匹配到文化元素: {culture_element.name}')
                    # 重新查询关系
                    relations_query = CultureEthnicRelation.query.filter_by(
                        culture_element_id=culture_element.id
                    )
                    # 如果同时指定了民族，进一步筛选
                    if ethnic_group and ethnic_group != '全部':
                        ethnic = EthnicGroup.query.filter_by(name=ethnic_group).first()
                        if ethnic:
                            relations_query = relations_query.filter_by(ethnic_group_id=ethnic.id)
                            self.logger.info(f'同时筛选民族: {ethnic.name}')
            
            relations = relations_query.all()
            
            # 构建响应数据
            graph_data = {
                'central_topic': culture_element.name,
                'description': culture_element.description,
                'ethnic_groups': []
            }
            
            # 遍历关系，构建民族文化数据
            for relation in relations:
                # 确保关系中的ethnic_group存在
                if relation.ethnic_group:
                    ethnic_data = {
                        'name': relation.ethnic_group.name,
                        'culture': relation.culture or f'{relation.ethnic_group.name}的{keyword}文化',
                        'customs': relation.customs or f'{relation.ethnic_group.name}关于{keyword}的传统习俗'
                    }
                    graph_data['ethnic_groups'].append(ethnic_data)
            
            # 如果没有找到相关关系，返回默认数据
            if not graph_data['ethnic_groups']:
                self.logger.info(f'没有找到相关的民族文化关系，返回默认数据')
                return default_graph_data
            
            return graph_data
            
        except Exception as db_error:
            self.logger.error(f'数据库查询失败: {str(db_error)}')
            # 如果数据库查询失败，返回默认数据
            return default_graph_data
    
    def add_culture_element(self, name: str, description: str, image: Optional[str] = None) -> Dict[str, Any]:
        """
        添加文化元素
        
        Args:
            name: 文化元素名称
            description: 文化元素描述
            image: 文化元素图片
            
        Returns:
            操作结果
        """
        try:
            # 检查是否已存在同名文化元素
            existing_element = CultureElement.query.filter_by(name=name).first()
            if existing_element:
                return {
                    "success": False,
                    "error": f"已存在名为 '{name}' 的文化元素"
                }
            
            # 创建新的文化元素
            new_element = CultureElement(
                name=name,
                description=description,
                image=image
            )
            
            db.session.add(new_element)
            db.session.commit()
            
            return {
                "success": True,
                "message": f"成功添加文化元素 '{name}'",
                "data": {
                    "id": new_element.id,
                    "name": new_element.name,
                    "description": new_element.description,
                    "image": new_element.image
                }
            }
        except Exception as e:
            self.logger.error(f"添加文化元素失败: {str(e)}")
            return {
                "success": False,
                "error": f"添加文化元素失败: {str(e)}"
            }
    
    def add_ethnic_group(self, name: str, description: str, image: Optional[str] = None) -> Dict[str, Any]:
        """
        添加民族
        
        Args:
            name: 民族名称
            description: 民族描述
            image: 民族图片
            
        Returns:
            操作结果
        """
        try:
            # 检查是否已存在同名民族
            existing_group = EthnicGroup.query.filter_by(name=name).first()
            if existing_group:
                return {
                    "success": False,
                    "error": f"已存在名为 '{name}' 的民族"
                }
            
            # 创建新的民族
            new_group = EthnicGroup(
                name=name,
                description=description,
                image=image
            )
            
            db.session.add(new_group)
            db.session.commit()
            
            return {
                "success": True,
                "message": f"成功添加民族 '{name}'",
                "data": {
                    "id": new_group.id,
                    "name": new_group.name,
                    "description": new_group.description,
                    "image": new_group.image
                }
            }
        except Exception as e:
            self.logger.error(f"添加民族失败: {str(e)}")
            return {
                "success": False,
                "error": f"添加民族失败: {str(e)}"
            }
    
    def add_culture_ethnic_relation(self, culture_element_id: int, ethnic_group_id: int, 
                                  culture: str, customs: str) -> Dict[str, Any]:
        """
        添加文化-民族关系
        
        Args:
            culture_element_id: 文化元素ID
            ethnic_group_id: 民族ID
            culture: 该民族的相关文化
            customs: 该民族的相关习俗
            
        Returns:
            操作结果
        """
        try:
            # 检查文化元素是否存在
            culture_element = CultureElement.query.get(culture_element_id)
            if not culture_element:
                return {
                    "success": False,
                    "error": f"未找到ID为 {culture_element_id} 的文化元素"
                }
            
            # 检查民族是否存在
            ethnic_group = EthnicGroup.query.get(ethnic_group_id)
            if not ethnic_group:
                return {
                    "success": False,
                    "error": f"未找到ID为 {ethnic_group_id} 的民族"
                }
            
            # 检查关系是否已存在
            existing_relation = CultureEthnicRelation.query.filter_by(
                culture_element_id=culture_element_id,
                ethnic_group_id=ethnic_group_id
            ).first()
            if existing_relation:
                return {
                    "success": False,
                    "error": f"文化元素 '{culture_element.name}' 与民族 '{ethnic_group.name}' 的关系已存在"
                }
            
            # 创建新的关系
            new_relation = CultureEthnicRelation(
                culture_element_id=culture_element_id,
                ethnic_group_id=ethnic_group_id,
                culture=culture,
                customs=customs
            )
            
            db.session.add(new_relation)
            db.session.commit()
            
            return {
                "success": True,
                "message": f"成功添加文化-民族关系",
                "data": {
                    "id": new_relation.id,
                    "culture_element": culture_element.name,
                    "ethnic_group": ethnic_group.name,
                    "culture": new_relation.culture,
                    "customs": new_relation.customs
                }
            }
        except Exception as e:
            self.logger.error(f"添加文化-民族关系失败: {str(e)}")
            return {
                "success": False,
                "error": f"添加文化-民族关系失败: {str(e)}"
            }
    
    def get_all_culture_elements(self) -> List[Dict[str, Any]]:
        """
        获取所有文化元素
        
        Returns:
            文化元素列表
        """
        try:
            elements = CultureElement.query.all()
            return [{
                'id': element.id,
                'name': element.name,
                'description': element.description,
                'image': element.image
            } for element in elements]
        except Exception as e:
            self.logger.error(f"获取文化元素列表失败: {str(e)}")
            return []
    
    def get_all_ethnic_groups(self) -> List[Dict[str, Any]]:
        """
        获取所有民族
        
        Returns:
            民族列表
        """
        try:
            groups = EthnicGroup.query.all()
            return [{
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'image': group.image
            } for group in groups]
        except Exception as e:
            self.logger.error(f"获取民族列表失败: {str(e)}")
            return []
    
    def get_culture_relations(self, culture_element_id: int) -> List[Dict[str, Any]]:
        """
        获取文化元素的所有民族关系
        
        Args:
            culture_element_id: 文化元素ID
            
        Returns:
            文化-民族关系列表
        """
        try:
            relations = CultureEthnicRelation.query.filter_by(culture_element_id=culture_element_id).all()
            result = []
            for relation in relations:
                result.append({
                    'id': relation.id,
                    'ethnic_group_id': relation.ethnic_group_id,
                    'ethnic_group_name': relation.ethnic_group.name,
                    'culture': relation.culture,
                    'customs': relation.customs
                })
            return result
        except Exception as e:
            self.logger.error(f"获取文化-民族关系失败: {str(e)}")
            return []
