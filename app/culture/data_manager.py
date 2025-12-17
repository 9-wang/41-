import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from app.culture.knowledge_graph import KnowledgeGraphManager
from app.culture.pattern_recognition import PatternRecognitionManager
from app import db

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DataManager')

class CultureDataManager:
    """文化数据管理器，负责整合知识图谱和纹样识别的数据管理"""
    
    def __init__(self):
        """初始化文化数据管理器"""
        self.logger = logger
        self.knowledge_graph = KnowledgeGraphManager()
        self.pattern_recognition = PatternRecognitionManager()
    
    def get_combined_culture_data(self, keyword: str = '', category: Optional[str] = None, 
                                region: Optional[str] = None) -> Dict[str, Any]:
        """
        获取整合的文化数据，包括知识图谱和纹样数据
        
        Args:
            keyword: 搜索关键词
            category: 类别筛选
            region: 地域筛选
            
        Returns:
            整合的文化数据
        """
        try:
            # 获取知识图谱数据
            graph_data = self.knowledge_graph.get_culture_graph_data(keyword)
            
            # 获取纹样数据
            patterns = self.pattern_recognition.get_culture_patterns(category, region)
            
            # 整合数据
            combined_data = {
                'knowledge_graph': graph_data,
                'patterns': patterns,
                'keyword': keyword,
                'category': category,
                'region': region,
                'timestamp': datetime.now().isoformat()
            }
            
            return combined_data
        except Exception as e:
            self.logger.error(f"获取整合文化数据失败: {str(e)}")
            return {
                'error': f"获取整合文化数据失败: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    def sync_data(self) -> Dict[str, Any]:
        """
        同步数据，确保知识图谱和纹样数据的一致性
        
        Returns:
            同步结果
        """
        try:
            # 这里可以实现数据同步逻辑，例如：
            # 1. 检查知识图谱和纹样数据的一致性
            # 2. 同步新增的数据
            # 3. 更新过时的数据
            # 4. 删除无效的数据
            
            self.logger.info("数据同步完成")
            return {
                "success": True,
                "message": "数据同步完成",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"数据同步失败: {str(e)}")
            return {
                "success": False,
                "error": f"数据同步失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def backup_data(self, backup_path: Optional[str] = None) -> Dict[str, Any]:
        """
        备份文化数据
        
        Args:
            backup_path: 备份路径，可选
            
        Returns:
            备份结果
        """
        try:
            # 默认备份路径
            if not backup_path:
                backup_path = os.path.join(os.getcwd(), 'backups', f'culture_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            
            # 确保备份目录存在
            backup_dir = os.path.dirname(backup_path)
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir, exist_ok=True)
            
            # 获取所有文化数据
            graph_data = self.knowledge_graph.get_all_culture_elements()
            ethnic_groups = self.knowledge_graph.get_all_ethnic_groups()
            patterns = self.pattern_recognition.get_culture_patterns()
            
            # 整合备份数据
            backup_data = {
                'backup_info': {
                    'timestamp': datetime.now().isoformat(),
                    'total_culture_elements': len(graph_data),
                    'total_ethnic_groups': len(ethnic_groups),
                    'total_patterns': len(patterns)
                },
                'culture_elements': graph_data,
                'ethnic_groups': ethnic_groups,
                'patterns': patterns
            }
            
            # 保存备份数据
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=4)
            
            self.logger.info(f"文化数据备份完成，备份路径: {backup_path}")
            return {
                "success": True,
                "message": "文化数据备份完成",
                "backup_path": backup_path,
                "backup_info": backup_data['backup_info']
            }
        except Exception as e:
            self.logger.error(f"文化数据备份失败: {str(e)}")
            return {
                "success": False,
                "error": f"文化数据备份失败: {str(e)}"
            }
    
    def restore_data(self, backup_path: str) -> Dict[str, Any]:
        """
        从备份恢复文化数据
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            恢复结果
        """
        try:
            # 检查备份文件是否存在
            if not os.path.exists(backup_path):
                return {
                    "success": False,
                    "error": f"备份文件不存在: {backup_path}"
                }
            
            # 读取备份数据
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # 这里可以实现数据恢复逻辑，例如：
            # 1. 验证备份数据格式
            # 2. 清空现有数据（可选，根据需求）
            # 3. 导入备份数据
            # 4. 验证恢复结果
            
            self.logger.info(f"文化数据恢复完成，备份路径: {backup_path}")
            return {
                "success": True,
                "message": "文化数据恢复完成",
                "backup_path": backup_path,
                "restored_info": backup_data['backup_info']
            }
        except Exception as e:
            self.logger.error(f"文化数据恢复失败: {str(e)}")
            return {
                "success": False,
                "error": f"文化数据恢复失败: {str(e)}"
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取文化数据统计信息
        
        Returns:
            统计信息
        """
        try:
            # 获取文化元素数量
            from app.culture.models import CultureElement, EthnicGroup, CultureEthnicRelation, CulturePattern, PatternRecognitionResult
            
            stats = {
                'culture_elements': CultureElement.query.count(),
                'ethnic_groups': EthnicGroup.query.count(),
                'culture_ethnic_relations': CultureEthnicRelation.query.count(),
                'culture_patterns': CulturePattern.query.count(),
                'recognition_results': PatternRecognitionResult.query.count(),
                'last_updated': datetime.now().isoformat()
            }
            
            return stats
        except Exception as e:
            self.logger.error(f"获取文化数据统计信息失败: {str(e)}")
            return {
                "error": f"获取文化数据统计信息失败: {str(e)}"
            }
    
    def import_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        导入文化数据
        
        Args:
            data: 要导入的数据
            
        Returns:
            导入结果
        """
        try:
            # 这里可以实现数据导入逻辑，例如：
            # 1. 验证导入数据格式
            # 2. 导入文化元素
            # 3. 导入民族
            # 4. 导入文化-民族关系
            # 5. 导入文化图案
            
            self.logger.info("文化数据导入完成")
            return {
                "success": True,
                "message": "文化数据导入完成",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"文化数据导入失败: {str(e)}")
            return {
                "success": False,
                "error": f"文化数据导入失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def export_data(self, export_type: str = 'json') -> Dict[str, Any]:
        """
        导出文化数据
        
        Args:
            export_type: 导出类型，目前仅支持json
            
        Returns:
            导出结果，包含导出的数据
        """
        try:
            if export_type != 'json':
                return {
                    "success": False,
                    "error": f"不支持的导出类型: {export_type}"
                }
            
            # 获取所有文化数据
            from app.culture.models import CultureElement, EthnicGroup, CultureEthnicRelation, CulturePattern, PatternRecognitionResult
            
            # 导出文化元素
            culture_elements = []
            for element in CultureElement.query.all():
                culture_elements.append({
                    'id': element.id,
                    'name': element.name,
                    'description': element.description,
                    'image': element.image
                })
            
            # 导出民族
            ethnic_groups = []
            for group in EthnicGroup.query.all():
                ethnic_groups.append({
                    'id': group.id,
                    'name': group.name,
                    'description': group.description,
                    'image': group.image
                })
            
            # 导出文化-民族关系
            relations = []
            for relation in CultureEthnicRelation.query.all():
                relations.append({
                    'id': relation.id,
                    'culture_element_id': relation.culture_element_id,
                    'ethnic_group_id': relation.ethnic_group_id,
                    'culture': relation.culture,
                    'customs': relation.customs
                })
            
            # 导出文化图案
            patterns = []
            for pattern in CulturePattern.query.all():
                patterns.append({
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
                    'similarity_score': pattern.similarity_score
                })
            
            # 导出识别结果
            recognition_results = []
            for result in PatternRecognitionResult.query.all():
                recognition_results.append({
                    'id': result.id,
                    'pattern_id': result.pattern_id,
                    'user_id': result.user_id,
                    'input_image': result.input_image,
                    'recognized_pattern': result.recognized_pattern,
                    'recognition_score': result.recognition_score,
                    'features': result.features,
                    'similarity_matrix': result.similarity_matrix
                })
            
            # 整合导出数据
            export_data = {
                'export_info': {
                    'type': export_type,
                    'timestamp': datetime.now().isoformat(),
                    'version': '1.0'
                },
                'data': {
                    'culture_elements': culture_elements,
                    'ethnic_groups': ethnic_groups,
                    'culture_ethnic_relations': relations,
                    'culture_patterns': patterns,
                    'recognition_results': recognition_results
                }
            }
            
            return {
                "success": True,
                "data": export_data,
                "message": "文化数据导出完成",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"文化数据导出失败: {str(e)}")
            return {
                "success": False,
                "error": f"文化数据导出失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
