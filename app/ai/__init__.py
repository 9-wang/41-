from flask import Blueprint

# 创建扣子智能体蓝图
bp = Blueprint('ai', __name__)

# 导入路由
from app.ai import routes
