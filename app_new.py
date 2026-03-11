import os
import threading
from datetime import datetime
from flask import Flask, redirect, request
from sqlalchemy import func

# --- 1. 引入扩展与模块 ---
# extensions: 存放 db, socketio, basic_auth 等共享对象
# models: 存放 VisitStats 等数据库模型
# *_backend: 存放具体的业务逻辑蓝图
from extensions import db, basic_auth, socketio
from models import VisitStats
from main_backend import main_bp
from rose_backend import rose_bp
from admin_backend import init_admin

# --- 2. App 配置 ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///universe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-key-for-my-universe'

# 后台管理密码配置
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'flashmud'
app.config['BASIC_AUTH_FORCE'] = False

# --- 3. 初始化组件 ---
db.init_app(app)
basic_auth.init_app(app)
socketio.init_app(app, cors_allowed_origins="*")

# --- 4. 注册蓝图 (Blueprints) ---
# main_bp: 负责文章、评论、搜索、首页
# rose_bp: 负责玫瑰经、祷告墙、同步、指纹
app.register_blueprint(main_bp)
app.register_blueprint(rose_bp)

# --- 5. 初始化后台管理 ---
# 逻辑在 admin_backend.py 中
init_admin(app)

# --- 6. 全局逻辑: 流量统计 ---
@app.before_request
def track_visitor():
    # 排除静态文件和后台请求，只统计前台页面
    if request.endpoint and 'static' not in request.endpoint and 'admin' not in request.endpoint:
        today = datetime.now().strftime('%Y-%m-%d')
        try:
            stat = VisitStats.query.get(today)
            if not stat:
                db.session.add(VisitStats(date=today, count=1))
            else:
                stat.count += 1
            db.session.commit()
        except:
            db.session.rollback()

# 全局逻辑: 注入流量数据到所有模板底部
@app.context_processor
def inject_traffic_data():
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        daily_stat = VisitStats.query.get(today)
        daily = daily_stat.count if daily_stat else 0
        # 统计总访问量
        total = db.session.query(func.sum(VisitStats.count)).scalar() or 0
        return dict(daily_visits=daily, total_visits=total)
    except:
        return dict(daily_visits=0, total_visits=0)

# --- 7. 全局逻辑: 聊天室消息转发 ---
@socketio.on('send_message')
def handle_message(data):
    msg = data.get('message')
    if msg:
        # 广播消息给所有连接的客户端
        socketio.emit('receive_message', {
            'user': data.get('nickname', '***'),
            'msg': msg
        })

# --- 8. 启动逻辑 (保留 HTTPS 线程结构) ---
# ================= 启动逻辑 =================
def run_http_redirect():
    from flask import Flask, redirect, request
    r_app = Flask(__name__)
    @r_app.route('/', defaults={'path': ''})
    @r_app.route('/<path:path>')
    def https_redirect(path): return redirect(request.url.replace('http://', 'https://'), code=301)
    r_app.run(host='0.0.0.0', port=80)

def run_http_server():
    socketio.run(app,host='0.0.0.0', port=80, debug=True)

if __name__ == '__main__':
    if not os.path.exists('universe.db'):
        with app.app_context(): db.create_all()
    
    import threading
    t = threading.Thread(target=run_http_server, daemon=True)
    t.start()
    print(">>> 闪泥工作室 HTTPS 主服务启动 (Port 443)...")
    
    socketio.run(app, host='0.0.0.0', port=443, debug=False,
                 certfile='/etc/letsencrypt/live/www.mxle.net/fullchain.pem',
                 keyfile='/etc/letsencrypt/live/www.mxle.net/privkey.pem')