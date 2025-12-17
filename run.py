import os
import sys

# 将项目的根目录添加到Python的导入路径中
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app

# 根据环境变量选择配置，默认使用开发环境
config_name = os.environ.get('FLASK_CONFIG', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # 使用环境变量中的PORT，默认8000
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=(config_name == 'development'))