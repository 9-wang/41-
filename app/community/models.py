from app import db

# 标签模型
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return '<Tag {}>'.format(self.name)

# 帖子-标签关联表
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category = db.Column(db.String(50), nullable=True)  # 添加分类字段
    created_at = db.Column(db.DateTime, default=db.func.now())
    comments = db.relationship('Comment', backref='post', lazy=True)
    likes = db.Column(db.Integer, default=0)  # 添加点赞数
    views = db.Column(db.Integer, default=0)  # 添加浏览数
    author = db.relationship('User', backref='posts', lazy=True)
    tags = db.relationship('Tag', secondary=post_tags, lazy='subquery',
        backref=db.backref('posts', lazy=True))
    
    def __repr__(self):
        return '<Post {}>'.format(self.title)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=True)  # 支持故事评论
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    def __repr__(self):
        return '<Comment {}>'.format(self.id)

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ethnicity = db.Column(db.String(50), nullable=False)
    school = db.Column(db.String(100), nullable=False)
    likes = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)  # 添加浏览数
    created_at = db.Column(db.DateTime, default=db.func.now())
    author = db.relationship('User', backref='stories', lazy=True)
    comments = db.relationship('Comment', backref='story', lazy=True)  # 故事评论关系
    
    def __repr__(self):
        return '<Story {}>'.format(self.title)

# 点赞模型
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # 唯一约束，防止重复点赞
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='uq_user_post_like'),
        db.UniqueConstraint('user_id', 'story_id', name='uq_user_story_like'),
    )
    
    def __repr__(self):
        return '<Like user_id={} post_id={} story_id={}>'.format(self.user_id, self.post_id, self.story_id)

class Task(db.Model):
    """共学共乐任务模型"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), nullable=False)  # 图标名称，如 'mdi:music'
    color = db.Column(db.String(20), nullable=False)  # 主题色，如 '#F39C12'
    task_type = db.Column(db.String(50), default='text', index=True)  # 任务类型：text, image, video, document
    file_required = db.Column(db.Boolean, default=False)  # 是否需要上传文件
    file_types = db.Column(db.String(200), nullable=True)  # 允许的文件类型，如 'jpg,jpeg,png'
    file_size_limit = db.Column(db.Integer, default=10)  # 文件大小限制，单位MB
    deadline = db.Column(db.DateTime, nullable=True, index=True)  # 任务截止日期
    reward = db.Column(db.String(100), nullable=True)  # 任务奖励
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)  # 创建者ID
    created_at = db.Column(db.DateTime, default=db.func.now(), index=True)
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    # 关系
    submissions = db.relationship('TaskSubmission', backref='task', lazy=True)
    creator = db.relationship('User', backref='created_tasks', lazy=True)
    
    def __repr__(self):
        return '<Task {}>'.format(self.title)

class UserTask(db.Model):
    """用户任务进度模型"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    progress = db.Column(db.Integer, default=0)  # 任务进度，0-100
    is_completed = db.Column(db.Boolean, default=False, index=True)  # 是否完成
    completed_at = db.Column(db.DateTime, nullable=True, index=True)  # 完成时间
    submission_id = db.Column(db.Integer, db.ForeignKey('task_submission.id'), nullable=True)  # 关联的任务提交记录
    created_at = db.Column(db.DateTime, default=db.func.now(), index=True)
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    # 添加复合索引，优化用户任务查询
    __table_args__ = (
        db.Index('idx_user_task', 'user_id', 'task_id'),
    )
    
    # 关系
    user = db.relationship('User', backref='user_tasks', lazy=True)
    task = db.relationship('Task', backref='user_tasks', lazy=True)
    submission = db.relationship('TaskSubmission', backref='user_task', lazy=True)
    
    def __repr__(self):
        return '<UserTask user_id={} task_id={} progress={}>'.format(self.user_id, self.task_id, self.progress)

class TaskSubmission(db.Model):
    """任务提交记录模型"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    file_url = db.Column(db.String(200), nullable=True)  # 提交的文件URL
    content = db.Column(db.Text, nullable=True)  # 提交的内容
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    feedback = db.Column(db.Text, nullable=True)  # 管理员反馈
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    # 关系
    user = db.relationship('User', backref='task_submissions', lazy=True)
    
    def __repr__(self):
        return '<TaskSubmission user_id={} task_id={} status={}>'.format(self.user_id, self.task_id, self.status)

# 舞蹈比赛相关模型
class DanceCompetition(db.Model):
    """舞蹈比赛活动模型"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(20), default='active', index=True)  # active, ended
    created_at = db.Column(db.DateTime, default=db.func.now(), index=True)
    
    def __repr__(self):
        return '<DanceCompetition {}>'.format(self.title)

class Dance(db.Model):
    """舞蹈模板模型"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    video_url = db.Column(db.String(200), nullable=False)  # 参考舞蹈视频URL
    ethnicity = db.Column(db.String(50), nullable=False)  # 民族
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    competition_id = db.Column(db.Integer, db.ForeignKey('dance_competition.id'))
    created_at = db.Column(db.DateTime, default=db.func.now())
    competition = db.relationship('DanceCompetition', backref='dances', lazy=True)
    
    def __repr__(self):
        return '<Dance {}>'.format(self.title)

class DanceSubmission(db.Model):
    """舞蹈参赛作品模型"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    dance_id = db.Column(db.Integer, db.ForeignKey('dance.id'), index=True)
    video_url = db.Column(db.String(200), nullable=False)  # 参赛视频URL
    status = db.Column(db.String(20), default='pending', index=True)  # pending, scored
    score = db.Column(db.Float, nullable=True, index=True)  # 总分，用于排行榜排序
    # 添加详细评分字段
    accuracy = db.Column(db.Float, nullable=True)  # 准确性
    rhythm = db.Column(db.Float, nullable=True)  # 节奏感
    expression = db.Column(db.Float, nullable=True)  # 表现力
    completeness = db.Column(db.Float, nullable=True)  # 完整性
    score_details = db.Column(db.JSON, nullable=True)  # AI评分详细信息（包含反馈和建议）
    share_count = db.Column(db.Integer, default=0)  # 分享次数
    created_at = db.Column(db.DateTime, default=db.func.now(), index=True)
    
    # 复合索引，优化舞蹈排行榜查询
    __table_args__ = (
        db.Index('idx_dance_score', 'dance_id', 'score', unique=False),
        db.Index('idx_dance_status', 'dance_id', 'status'),
    )
    
    # 关系
    user = db.relationship('User', backref='dance_submissions', lazy=True)
    dance = db.relationship('Dance', backref='submissions', lazy=True)
    
    def __repr__(self):
        return '<DanceSubmission user_id={} dance_id={} score={}>'.format(self.user_id, self.dance_id, self.score)
    
    def update_score(self, score_result):
        """更新评分信息"""
        self.score = score_result['overall']
        self.accuracy = score_result['dimensions']['accuracy']
        self.rhythm = score_result['dimensions']['rhythm']
        self.expression = score_result['dimensions']['expression']
        self.completeness = score_result['dimensions']['completeness']
        self.score_details = {
            'feedback': score_result['feedback'],
            'suggestions': score_result['suggestions']
        }
        self.status = 'scored'

class Share(db.Model):
    """分享统计模型"""
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('dance_submission.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    platform = db.Column(db.String(20), nullable=False)  # wechat, weibo, qq, copy
    share_time = db.Column(db.DateTime, default=db.func.now())
    ip_address = db.Column(db.String(50), nullable=True)
    
    # 关系
    submission = db.relationship('DanceSubmission', backref='shares', lazy=True)
    user = db.relationship('User', backref='shares', lazy=True)
    
    def __repr__(self):
        return '<Share submission_id={} platform={} time={}>'.format(self.submission_id, self.platform, self.share_time)