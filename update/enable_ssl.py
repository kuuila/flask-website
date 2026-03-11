import os

def enable_ssl_in_app():
    app_path = 'app.py'
    
    if not os.path.exists(app_path):
        print("❌ 错误：找不到 app.py")
        return

    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 定义要替换的旧启动代码
    # 我们查找文件末尾的启动部分
    old_startup = "socketio.run(app, host='0.0.0.0', port=80, debug=True)"
    
    # 2. 定义新的启动代码 (包含 HTTP 自动跳转 HTTPS 的逻辑)
    # 注意：这里我们引入了 threading 来同时运行两个服务
    new_startup_logic = """
# --- HTTPS 升级配置 ---
# 定义一个只负责跳转的 HTTP 服务
def run_http_redirect():
    from flask import Flask, redirect, request
    redirect_app = Flask(__name__)
    
    @redirect_app.route('/', defaults={'path': ''})
    @redirect_app.route('/<path:path>')
    def https_redirect(path):
        # 将 http://... 替换为 https://...
        new_url = request.url.replace('http://', 'https://')
        return redirect(new_url, code=301)
        
    print(">>> HTTP 重定向服务已启动 (Port 80 -> 443)")
    redirect_app.run(host='0.0.0.0', port=80)

if __name__ == '__main__':
    if not os.path.exists('universe.db'):
        with app.app_context(): db.create_all()
    
    import threading
    # 1. 启动 HTTP 重定向 (在后台线程运行)
    t = threading.Thread(target=run_http_redirect, daemon=True)
    t.start()
    
    print(">>> 闪泥工作室 HTTPS 主服务启动 (Port 443)...")
    
    # 2. 启动 HTTPS 主服务 (阻塞运行)
    # 注意：开启 SSL 后建议关闭 debug 模式，防止自动重启导致端口冲突
    socketio.run(app, host='0.0.0.0', port=443, debug=False,
                 certfile='/etc/letsencrypt/live/www.mxle.net/fullchain.pem',
                 keyfile='/etc/letsencrypt/live/www.mxle.net/privkey.pem')
"""

    # 3. 执行替换
    # 我们替换整个 if __name__ == '__main__': 块，确保逻辑完整
    # 先尝试定位包含旧 socketio.run 的那一行
    
    if old_startup in content:
        # 为了替换整个 main 块，我们需要找到 if __name__ 的位置
        split_marker = "if __name__ == '__main__':"
        parts = content.split(split_marker)
        
        if len(parts) > 1:
            # 保留前半部分，拼接新的启动逻辑
            new_content = parts[0] + new_startup_logic
            
            with open(app_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ app.py 已配置 SSL 证书！")
            print("-----------------------------------")
            print("主服务：HTTPS (Port 443)")
            print("跳转服务：HTTP (Port 80)")
            print("-----------------------------------")
        else:
            print("❌ 无法定位 main 函数块。")
    else:
        print("⚠️ 无法精确匹配旧的启动代码。")
        print("可能代码已被修改。请手动检查 app.py 末尾。")

if __name__ == "__main__":
    enable_ssl_in_app()