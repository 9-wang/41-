from app import db

# 文化元素模型
class CultureElement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)  # 文化元素名称（如：茶、丝绸）
    description = db.Column(db.Text, nullable=False)  # 文化元素描述
    image = db.Column(db.String(120))  # 文化元素图片
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    # 关系定义
    ethnic_relations = db.relationship('CultureEthnicRelation', backref='culture_element', lazy=True)
    
    def __repr__(self):
        return '<CultureElement {}>'.format(self.name)

# 民族模型
class EthnicGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)  # 民族名称（如：汉族、藏族）
    description = db.Column(db.Text)  # 民族描述
    image = db.Column(db.String(120))  # 民族图片
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    # 关系定义
    culture_relations = db.relationship('CultureEthnicRelation', backref='ethnic_group', lazy=True)
    
    def __repr__(self):
        return '<EthnicGroup {}>'.format(self.name)

# 文化习俗模型
class CulturalPractice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)  # 习俗名称（如：酥油茶、奶茶）
    description = db.Column(db.Text)  # 习俗描述
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    # 关系定义
    relation_id = db.Column(db.Integer, db.ForeignKey('culture_ethnic_relation.id'))
    
    def __repr__(self):
        return '<CulturalPractice {}>'.format(self.name)

# 文化-民族关联表
class CultureEthnicRelation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    culture_element_id = db.Column(db.Integer, db.ForeignKey('culture_element.id'), nullable=False)
    ethnic_group_id = db.Column(db.Integer, db.ForeignKey('ethnic_group.id'), nullable=False)
    culture = db.Column(db.Text, nullable=False)  # 该民族的相关文化
    customs = db.Column(db.Text, nullable=False)  # 该民族的相关习俗
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    # 关系定义
    practices = db.relationship('CulturalPractice', backref='relation', lazy=True)
    
    def __repr__(self):
        return '<CultureEthnicRelation {} - {}>'.format(self.culture_element_id, self.ethnic_group_id)

class Culture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    def __repr__(self):
        return '<Culture {}>'.format(self.title)

# 收藏关联表
favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('ethnic_impression_id', db.Integer, db.ForeignKey('ethnic_impression.id'), primary_key=True)
)

# 民族印象生成模型
class EthnicImpression(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    original_image = db.Column(db.String(120), nullable=False)
    generated_image = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ethnic_elements = db.Column(db.String(255), nullable=True)  # 存储融合的民族文化元素标签
    generated_at = db.Column(db.DateTime, default=db.func.now())
    favorited_by = db.relationship('User', secondary=favorites, backref=db.backref('favorited_ethnic_impressions', lazy='dynamic'))
    
    def __repr__(self):
        return '<EthnicImpression {}>'.format(self.title)

# 非遗项目模型
class HeritageProject(db.Model):
    """非物质文化遗产项目模型"""
    id = db.Column(db.Integer, primary_key=True)
    project_code = db.Column(db.String(20), unique=True, nullable=False)  # 项目编号(Ⅰ-1)
    project_name = db.Column(db.String(120), nullable=False)  # 项目名称
    category = db.Column(db.String(50), nullable=False)  # 所属门类(民间文学)
    announcement_time = db.Column(db.String(50), nullable=False)  # 公布时间(2006第一批)
    declaration_region = db.Column(db.String(120), nullable=False)  # 申报地区
    protection_unit = db.Column(db.String(120), nullable=False)  # 保护单位
    inheritors = db.Column(db.Text, nullable=True)  # 传承人
    description = db.Column(db.Text, nullable=True)  # 项目描述
    image = db.Column(db.String(120), nullable=True)  # 项目图片
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    def __repr__(self):
        return '<HeritageProject {}>'.format(self.project_name)

# 古籍模型
class AncientBook(db.Model):
    """古籍模型"""
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(200), nullable=False)  # 书名(昌黎先生集：四十卷...)
    author = db.Column(db.String(120), nullable=False)  # 责任者(韓愈;廖瑩中)
    version_type = db.Column(db.String(50), nullable=False)  # 版本类型(刻本)
    publication_date = db.Column(db.String(50), nullable=True)  # 出版日期(宋咸淳)
    quantity = db.Column(db.String(20), nullable=True)  # 数量(32冊)
    four_part_classification = db.Column(db.String(120), nullable=True)  # 四部分类(集部 別集類 唐五代別集)
    binding_form = db.Column(db.String(50), nullable=True)  # 装帧形式
    collection_unit = db.Column(db.String(120), nullable=True)  # 收藏单位
    description = db.Column(db.Text, nullable=True)  # 古籍描述
    image = db.Column(db.String(120), nullable=True)  # 古籍图片
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    def __repr__(self):
        return '<AncientBook {}>'.format(self.book_name)

# 文化图案模型
class CulturePattern(db.Model):
    """文化图案模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)  # 图案名称
    era = db.Column(db.String(50), nullable=True)  # 时代
    region = db.Column(db.String(120), nullable=True)  # 地域
    category = db.Column(db.String(50), nullable=True)  # 类别
    carrier = db.Column(db.String(120), nullable=True)  # 载体
    technique = db.Column(db.String(120), nullable=True)  # 工艺
    description = db.Column(db.Text, nullable=True)  # 图案描述
    image_url = db.Column(db.String(200), nullable=True)  # 图案图片URL
    pattern_features = db.Column(db.Text, nullable=True)  # 图案特征描述，用于纹样识别
    similarity_score = db.Column(db.Float, nullable=True)  # 相似度评分
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    # 关系定义
    recognition_results = db.relationship('PatternRecognitionResult', backref='culture_pattern', lazy=True)
    
    def __repr__(self):
        return '<CulturePattern {}>'.format(self.name)

# 纹样识别结果模型
class PatternRecognitionResult(db.Model):
    """纹样识别结果模型"""
    id = db.Column(db.Integer, primary_key=True)
    pattern_id = db.Column(db.Integer, db.ForeignKey('culture_pattern.id'), nullable=False)  # 关联的文化图案
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # 操作用户
    input_image = db.Column(db.String(200), nullable=False)  # 输入图像路径
    recognized_pattern = db.Column(db.String(120), nullable=False)  # 识别出的纹样名称
    recognition_score = db.Column(db.Float, nullable=False)  # 识别评分
    features = db.Column(db.Text, nullable=True)  # 识别特征向量
    similarity_matrix = db.Column(db.Text, nullable=True)  # 相似度矩阵
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    def __repr__(self):
        return '<PatternRecognitionResult {}>'.format(self.id)

# 旅游资源模型
class TourismResource(db.Model):
    """旅游资源模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)  # 景区名称
    star_level = db.Column(db.String(10), nullable=True)  # 星级(5A级)
    address = db.Column(db.String(200), nullable=True)  # 地址
    region = db.Column(db.String(120), nullable=True)  # 所属地区
    rating = db.Column(db.Float, nullable=True)  # 评分
    type = db.Column(db.String(50), nullable=True)  # 类型(旅游景区、五星级饭店等)
    description = db.Column(db.Text, nullable=True)  # 资源描述
    image = db.Column(db.String(120), nullable=True)  # 资源图片
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    def __repr__(self):
        return '<TourismResource {}>'.format(self.name)