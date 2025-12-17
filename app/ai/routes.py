from flask import request, jsonify, current_app
import requests
import logging

# 从__init__.py导入蓝图对象
from app.ai import bp

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@bp.route('/chat', methods=['POST'])
def ai_chat():
    """AI聊天API"""
    try:
        # 获取请求数据
        raw_data = request.get_data(as_text=True)
        logger.info(f"原始请求数据: {raw_data}")
        
        # 从请求中获取用户消息
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': '缺少消息内容'
            }), 400
        
        user_message = data['message']
        user_id = data.get('user_id', 'anonymous_user')  # 可选：用户ID，用于上下文管理
        
        logger.info(f"收到聊天请求: message={user_message}, user_id={user_id}")
        
        # 暂时返回模拟响应，确保前端和后端的连接正常
        # 后续将替换为真实的COZE API调用
        return jsonify({
            'success': True,
            'message': f'你好！我是AI石榴君，你刚才说：{user_message}。这是一个模拟响应，后续将替换为真实的COZE API调用。'
        })
        
    except Exception as e:
        logger.error(f"处理聊天请求失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500
  
@bp.route('/config', methods=['GET'])
def ai_config():
    """获取智能体配置信息"""
    return jsonify({
        'success': True,
        'app_id': current_app.config['COZE_APP_ID'],
        'api_url': current_app.config['COZE_API_URL'].split('/v2')[0],  # 返回API基础地址
        'callback_url': current_app.config['COZE_CALLBACK_URL']
    })
