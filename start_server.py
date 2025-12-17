import os
import socket
from waitress import serve
from app import create_app

# 根据环境变量选择配置
config_name = os.environ.get('FLASK_CONFIG', 'production')
app = create_app(config_name)

# 获取本机IP地址
def get_local_ip():
    try:
        # 创建一个UDP套接字连接到外部地址，获取本地IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # 连接到公共DNS服务器，不需要实际通信
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception as e:
        print(f"获取本地IP地址失败: {e}")
        return '127.0.0.1'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    host = '0.0.0.0'  # 监听所有网络接口
    local_ip = get_local_ip()
    
    print(f"\n=============================")
    print(f"文化传播应用启动")
    print(f"=============================")
    print(f"配置环境: {config_name}")
    print(f"启动服务器: Waitress")
    print(f"监听地址: {host}:{port}")
    print(f"本地访问: http://127.0.0.1:{port}")
    print(f"局域网访问: http://{local_ip}:{port}")
    print(f"=============================")
    print(f"按 Ctrl+C 停止服务器")
    print(f"=============================\n")
    
    # 使用Waitress启动应用
    serve(app, host=host, port=port, threads=4)
