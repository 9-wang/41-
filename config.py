import os
from datetime import timedelta

# 定义项目根目录
basedir = os.path.abspath(os.path.dirname(__file__))

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    TASK_FILES_FOLDER = os.path.join(basedir, 'app', 'static', 'task_files')
    DANCE_VIDEOS_FOLDER = os.path.join(basedir, 'app', 'static', 'videos')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB，用于视频上传
    
    # 用于会话管理
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # 用于AI评分（模拟）
    AI_SCORE_WEIGHTS = {
        '动作准确性': 0.3,
        '节奏把握': 0.25,
        '表现力': 0.2,
        '完整性': 0.15,
        '技巧难度': 0.1
    }
    
    # 用于舞蹈难度
    DANCE_DIFFICULTY = ['初级', '中级', '高级']
    
    # 用于民族
    ETHNICITIES = ['藏族', '蒙古族', '维吾尔族', '汉族', '其他']
    
    # 扣子智能体配置
    COZE_API_KEY = os.environ.get('COZE_API_KEY') or 'pat_VcQkFWmwvfMZxRhsr3grVaXtFkGjsOMneeGsaOJWbhupM8ENVBVSGuCygqkhGhyb'
    COZE_APP_ID = os.environ.get('COZE_APP_ID') or '7575561277872029702'
    COZE_API_URL = os.environ.get('COZE_API_URL') or 'https://api.coze.cn/open_api/v2/chat'  # 扣子智能体API地址
    COZE_CALLBACK_URL = os.environ.get('COZE_CALLBACK_URL') or 'http://127.0.0.1:8080/callback'  # 回调URL

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app', 'data-dev.sqlite')

class ProductionConfig(Config):
    # 处理Render平台的PostgreSQL数据库URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        # 将postgres://转换为postgresql://，因为SQLAlchemy 1.4+需要
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://')
    # 提供默认的SQLite数据库作为备选
    if not SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app', 'data.sqlite')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}