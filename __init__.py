import os
import sys

# 将项目的根目录添加到Python的导入路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from flask_caching import Cache
# 显式导入config变量，确保能正确导入
import config as app_config

# 从导入的模块中获取config变量
config = app_config.config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'user.login'
login_manager.login_message_category = 'info'

# 初始化缓存
def configure_cache(app):
    cache = Cache(app, config={
        'CACHE_TYPE': app.config.get('CACHE_TYPE', 'simple'),  # 使用simple缓存类型，生产环境可改为redis或memcached
        'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300),  # 默认缓存5分钟
        'CACHE_THRESHOLD': 500,  # 缓存阈值
    })
    return cache

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 配置JSON响应，确保中文显示正常
    app.config['JSON_AS_ASCII'] = False
    
    # 配置CORS，允许所有来源访问
    CORS(app)
    
    # 性能优化配置
    # 启用gzip压缩
    app.config['COMPRESS_REGISTER'] = True
    
    # 静态文件缓存设置
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600  # 1小时
    
    # 模板缓存设置
    app.config['TEMPLATES_AUTO_RELOAD'] = app.config['DEBUG']  # 开发环境禁用模板缓存，生产环境启用
    
    # 配置响应头，优化浏览器缓存和JSON编码
    @app.after_request
    def add_cache_headers(response):
        # 添加安全响应头
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # 静态资源缓存设置
        if request.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        # 确保JSON响应使用UTF-8编码
        if response.mimetype == 'application/json':
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    
    # 压缩静态文件
    from flask_compress import Compress
    compress = Compress()
    compress.init_app(app)
   # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # 初始化缓存
    cache = configure_cache(app)
    app.cache = cache
    
    # 配置日志记录
    import logging
    from logging.handlers import RotatingFileHandler
    import os
    
    # 确保日志目录存在
    logs_dir = os.path.join(app.root_path, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # 配置文件日志
    file_handler = RotatingFileHandler(os.path.join(logs_dir, 'app.log'), maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    # 设置日志级别
    app.logger.setLevel(logging.INFO)
    app.logger.info('应用启动')
    
    # 配置错误处理
    from flask import render_template
    
    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.error(f'404错误 - {request.path}')
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f'500错误 - {e}')
        return render_template('500.html'), 500
    
    # 注册蓝图
    
    # 在所有扩展初始化后导入模型，避免循环导入
    with app.app_context():
        from app.user import models as user_models
        from app.culture import models as culture_models
        from app.community import models as community_models
        from app.vr import models as vr_models
    from app.home import bp as home_bp
    app.register_blueprint(home_bp)
    
    from app.culture import bp as culture_bp
    app.register_blueprint(culture_bp)
    
    from app.vr import bp as vr_bp
    app.register_blueprint(vr_bp)
    
    from app.community import bp as community_bp
    app.register_blueprint(community_bp)
    
    from app.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    from app.user import bp as user_bp
    app.register_blueprint(user_bp)
    
    # 注册扣子智能体蓝图
    from app.ai import bp as ai_bp
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    
    return app

# 创建默认的应用实例，用于Gunicorn等WSGI服务器的部署
app = create_app()