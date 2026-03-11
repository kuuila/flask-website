import os

def refactor_admin_split():
    print("正在执行后台管理模块拆分...")

    # ========================================================
    # 1. 创建 admin_backend.py (后台管理逻辑)
    # ========================================================
    admin_backend_code = """
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from extensions import db, basic_auth
from models import Post, Comment, VisitStats, RosaryData, DailyPrayer, UserDevice

# --- 基础安全视图 ---
class SecureModelView(ModelView):
    def is_accessible(self):
        return basic_auth.authenticate()
    def inaccessible_callback(self, name, **kwargs):
        return basic_auth.challenge()

class SecureIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not basic_auth.authenticate():
            return basic_auth.challenge()
        return super(SecureIndexView, self).index()

# --- 自定义管理视图 ---
class RosaryDataAdmin(SecureModelView):
    column_list = ('uid', 'updated_at', 'data_preview')
    column_default_sort = ('updated_at', True)
    can_create = False
    form_widget_args = {'data': {'rows': 10, 'style': 'font-family:monospace;'}, 'uid': {'readonly': True}}
    
    def data_preview(self, context, model, name):
        if not model.data: return ""
        return model.data[:50] + '...' if len(model.data) > 50 else model.data

class DailyPrayerAdmin(SecureModelView):
    column_list = ('created_at', 'name', 'content', 'uid')
    column_default_sort = ('created_at', True)
    column_searchable_list = ['name', 'content']
    can_create = False

class UserDeviceAdmin(SecureModelView):
    column_list = ('device_name', 'updated_at', 'last_ip', 'device_key', 'fingerprint')
    column_searchable_list = ['device_name', 'device_key', 'fingerprint', 'last_ip']
    column_default_sort = ('updated_at', True)
    form_widget_args = {'data': {'rows': 10, 'style': 'font-family:monospace;'}, 'device_key': {'readonly': True}}

# --- 初始化函数 (由 app.py 调用) ---
def init_admin(app):
    admin = Admin(app, name='闪泥后台', template_mode='bootstrap3', index_view=SecureIndexView())
    
    # 主站管理
    admin.add_view(SecureModelView(Post, db.session, name='文章管理'))
    admin.add_view(SecureModelView(Comment, db.session, name='评论监控'))
    admin.add_view(SecureModelView(VisitStats, db.session, name='流量统计'))
    
    # 玫瑰经/闪泥管理
    admin.add_view(DailyPrayerAdmin(DailyPrayer, db.session, name='今日祷告墙'))
    admin.add_view(UserDeviceAdmin(UserDevice, db.session, name='用户设备(新)'))
    admin.add_view(RosaryDataAdmin(RosaryData, db.session, name='旧·存档(待迁移)'))
    
    print("[System] 后台管理模块加载完成。")
"""
    with open('admin_backend.py', 'w', encoding='utf-8') as f:
        f.write(admin_backend_code.strip())
    print("[OK] admin_backend.py 已创建")

    # ========================================================
    # 2. 重写 app.py (极简入口，保留启动逻辑)
    # ========================================================
    app_py_code = """
import os
import threading
from datetime import datetime
from flask import Flask, redirect, request
from sqlalchemy import func

# --- 引入扩展与模块 ---
from extensions import db, basic_auth, socketio
from models import VisitStats
from main_backend import main_bp
from rose_backend import rose_bp
from admin_backend import init_admin  # 引入后台初始化函数

# --- App 配置 ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///universe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-key-for-my-universe'
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'flashmud'
app.config['BASIC_AUTH_FORCE'] = False

# --- 初始化组件 ---
db.init_app(app)
basic_auth.init_app(app)
socketio.init_app(app, cors_allowed_origins="*")

# --- 注册蓝图 ---
app.register_blueprint(main_bp)
app.register_blueprint(rose_bp)

# --- 初始化后台 ---
init_admin(app)

# --- 全局逻辑 (流量统计) ---
@app.before_request
def track_visitor():
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

@app.context_processor
def inject_traffic_data():
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        daily = VisitStats.query.get(today).count if VisitStats.query.get(today) else 0
        total = db.session.query(func.sum(VisitStats.count)).scalar() or 0
        return dict(daily_visits=daily, total_visits=total)
    except:
        return dict(daily_visits=0, total_visits=0)

@socketio.on('send_message')
def handle_message(data):
    msg = data.get('message')
    if msg:
        socketio.emit('receive_message', {'user': data.get('nickname', '***'), 'msg': msg})

# --- 启动逻辑 (保留原有的 HTTPS Redirect) ---
def run_http_redirect():
    from flask import Flask, redirect, request
    redirect_app = Flask(__name__)
    @redirect_app.route('/', defaults={'path': ''})
    @redirect_app.route('/<path:path>')
    def https_redirect(path):
        return redirect(request.url.replace('http://', 'https://'), code=301)
    print(">>> HTTP 重定向服务启动 (Port 80)")
    redirect_app.run(host='0.0.0.0', port=80)

def run_dev_server():
    print(">>> 开发模式启动 (Port 5000)")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    # 自动建表检查
    if not os.path.exists('universe.db'):
        with app.app_context():
            db.create_all()
            print("[System] 数据库初始化完成")

    # === 生产环境启动逻辑 (解开注释使用) ===
    # t = threading.Thread(target=run_http_redirect, daemon=True)
    # t.start()
    # print(">>> HTTPS 主服务启动 (Port 443)...")
    # socketio.run(app, host='0.0.0.0', port=443, debug=False,
    #              certfile='/etc/letsencrypt/live/www.mxle.net/fullchain.pem',
    #              keyfile='/etc/letsencrypt/live/www.mxle.net/privkey.pem')
    
    # === 开发环境启动逻辑 ===
    run_dev_server()
"""
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_py_code.strip())
    print("[OK] app.py 已瘦身 (后台逻辑已移出)")

if __name__ == "__main__":
    refactor_admin_split()
    print("-" * 30)
    print("重构完成！")
    print("1. admin_backend.py: 负责所有后台管理视图定义。")
    print("2. app.py: 只负责组装各模块和启动服务。")
    print("-" * 30)
    print("请重启服务: python3 app.py")