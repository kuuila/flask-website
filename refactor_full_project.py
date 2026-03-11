import os

def refactor_full_project():
    print("正在执行全站模块化重构...")

    # ========================================================
    # 1. 创建 extensions.py (共享组件)
    # ========================================================
    extensions_code = """
from flask_sqlalchemy import SQLAlchemy
from flask_basicauth import BasicAuth
from flask_socketio import SocketIO

# 初始化扩展，但不绑定 app (解决循环引用)
db = SQLAlchemy()
basic_auth = BasicAuth()
socketio = SocketIO(cors_allowed_origins="*")
"""
    with open('extensions.py', 'w', encoding='utf-8') as f:
        f.write(extensions_code.strip())
    print("[OK] extensions.py 已创建")

    # ========================================================
    # 2. 创建 models.py (统一管理数据库模型)
    # ========================================================
    models_code = """
from datetime import datetime
from extensions import db

# --- 主站模型 (文章/评论/统计) ---
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    content = db.Column(db.Text)
    summary = db.Column(db.String(500))
    tags = db.Column(db.String(100))
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")

    @property
    def css_class(self):
        mapping = {'logic': 'cat-logic', 'spirit': 'cat-spirit', 'senses': 'cat-senses', 'life': 'cat-life'}
        return mapping.get(self.category, '')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    nickname = db.Column(db.String(50), default='Anonymous')
    content = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

class VisitStats(db.Model):
    date = db.Column(db.String(20), primary_key=True)
    count = db.Column(db.Integer, default=0)

# --- 玫瑰经模型 ---
class RosaryData(db.Model):
    uid = db.Column(db.String(36), primary_key=True)
    data = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class DailyPrayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(36))
    name = db.Column(db.String(50))
    content = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)
"""
    with open('models.py', 'w', encoding='utf-8') as f:
        f.write(models_code.strip())
    print("[OK] models.py 已创建")

    # ========================================================
    # 3. 创建 main_backend.py (文章与主站逻辑)
    # ========================================================
    main_backend_code = """
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from sqlalchemy import or_
from extensions import db
from models import Post, Comment

# 创建主站蓝图
main_bp = Blueprint('main', __name__)

# --- 辅助函数 ---
def prune_comments(post_id):
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    if len(comments) > 50:
        head = [c.id for c in comments[:10]]
        tail = [c.id for c in comments[-40:]]
        keep_ids = set(head + tail)
        for c in comments:
            if c.id not in keep_ids: db.session.delete(c)
        db.session.commit()

# --- 路由 ---
@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    tab = request.args.get('tab', 'latest')
    per_page = 9
    query = Post.query

    if tab == 'popular': query = query.order_by(Post.views.desc())
    elif tab == 'recommend': query = query.filter(Post.title.contains('闪泥')).order_by(Post.created_at.desc())
    else: query = query.order_by(Post.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('index.html', pagination=pagination, current_tab=tab, title="首页")

@main_bp.route('/category/<category_name>')
def category(category_name):
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(category=category_name).order_by(Post.created_at.desc()).paginate(page=page, per_page=12, error_out=False)
    return render_template('index.html', pagination=pagination, current_tab='category', title=category_name.upper())

@main_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    
    # 增加阅读量
    if request.method == 'GET':
        post.views = (post.views or 0) + 1
        db.session.commit()

    if request.method == 'POST':
        nickname = request.form.get('nickname') or "匿名访客"
        content = request.form.get('content')
        if content and content.strip():
            db.session.add(Comment(post_id=post.id, nickname=nickname[:20], content=content[:500]))
            db.session.commit()
            prune_comments(post.id)
            return redirect(url_for('main.post_detail', post_id=post_id))
            
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.asc()).all()
    return render_template('post_html.html', post=post, comments=comments, title=post.title)

@main_bp.route('/s/<sub_web>')
def subweb(sub_web):
    # 如果玫瑰经需要文章列表数据，可以在这里传递，或者玫瑰经页面改为纯静态+API
    return render_template(sub_web+'.html')

@main_bp.route('/api/search')
def search_api():
    query = request.args.get('q', '')
    if not query: return jsonify([])
    results = Post.query.filter(or_(Post.title.contains(query),Post.summary.contains(query),Post.tags.contains(query))).order_by(Post.created_at.desc()).limit(10).all()
    return jsonify([{'id': p.id, 'title': p.title, 'summary': p.summary, 'date': p.created_at.strftime('%Y-%m-%d'), 'category': p.category} for p in results])
"""
    with open('main_backend.py', 'w', encoding='utf-8') as f:
        f.write(main_backend_code.strip())
    print("[OK] main_backend.py 已创建")

    # ========================================================
    # 4. 创建 rose_backend.py (玫瑰经/祷告逻辑)
    # ========================================================
    rose_backend_code = """
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from extensions import db
from models import RosaryData, DailyPrayer

rose_bp = Blueprint('rose', __name__, url_prefix='/api/rose')

@rose_bp.route('/sync', methods=['POST'])
def rose_sync_upload():
    try:
        uid = request.json.get('uid'); data_str = request.json.get('data')
        if not uid or not data_str: return jsonify({'status': 'error', 'msg': '缺少参数'}), 400
        record = RosaryData.query.get(uid)
        if not record:
            db.session.add(RosaryData(uid=uid, data=data_str))
        else: record.data = data_str
        db.session.commit()
        return jsonify({'status': 'success', 'msg': '云端存档已更新'})
    except Exception as e: return jsonify({'status': 'error', 'msg': str(e)}), 500

@rose_bp.route('/sync/<uid>', methods=['GET'])
def rose_sync_download(uid):
    record = RosaryData.query.get(uid)
    return jsonify({'status': 'success', 'data': record.data, 'time': record.updated_at}) if record else (jsonify({'status': 'error', 'msg': '未找到'}), 404)

@rose_bp.route('/prayers', methods=['GET'])
def get_prayers():
    try: # 清理过期数据
        DailyPrayer.query.filter(DailyPrayer.created_at < datetime.now() - timedelta(days=2)).delete()
        db.session.commit()
    except: db.session.rollback()
    
    offset = request.args.get('offset', 0, type=int)
    query = DailyPrayer.query.order_by(DailyPrayer.created_at.desc())
    total = query.count()
    prayers = query.offset(offset).limit(10).all()
    return jsonify({'status': 'success', 'data': [{'time': p.created_at.strftime('%H:%M'), 'name': p.name, 'content': p.content} for p in prayers], 'has_more': (offset + 10) < total})

@rose_bp.route('/prayer', methods=['POST'])
def submit_prayer():
    data = request.json
    content = data.get('content')
    if not content or len(content) < 5: return jsonify({'status': 'error', 'msg': '内容太短'}), 400
    db.session.add(DailyPrayer(uid=data.get('uid'), name=data.get('name'), content=content))
    db.session.commit()
    return jsonify({'status': 'success'})
"""
    with open('rose_backend.py', 'w', encoding='utf-8') as f:
        f.write(rose_backend_code.strip())
    print("[OK] rose_backend.py 已创建")

    # ========================================================
    # 5. 重写 app.py (只保留配置、Admin 和 启动逻辑)
    # ========================================================
    app_py_code = """
import os
import threading
from datetime import datetime
from flask import Flask, request, redirect
from sqlalchemy import func
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

# 引入模块
from extensions import db, basic_auth, socketio
from models import Post, Comment, VisitStats, RosaryData, DailyPrayer
from main_backend import main_bp
from rose_backend import rose_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///universe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-key-for-my-universe'
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'flashmud'
app.config['BASIC_AUTH_FORCE'] = False

# 初始化扩展
db.init_app(app)
basic_auth.init_app(app)
socketio.init_app(app, cors_allowed_origins="*")

# 注册蓝图
app.register_blueprint(main_bp)
app.register_blueprint(rose_bp)

# ================= 后台管理 =================
class SecureModelView(ModelView):
    def is_accessible(self): return basic_auth.authenticate()
    def inaccessible_callback(self, name, **kwargs): return basic_auth.challenge()

class SecureIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not basic_auth.authenticate(): return basic_auth.challenge()
        return super(SecureIndexView, self).index()

class RosaryDataAdmin(SecureModelView):
    column_list = ('uid', 'updated_at')
    can_create = False
    form_widget_args = {'data': {'rows': 10, 'style': 'font-family:monospace;'}, 'uid': {'readonly': True}}

class DailyPrayerAdmin(SecureModelView):
    column_list = ('created_at', 'name', 'content', 'uid')
    column_default_sort = ('created_at', True)
    can_create = False

admin = Admin(app, name='闪泥后台', template_mode='bootstrap3', index_view=SecureIndexView())
admin.add_view(SecureModelView(Post, db.session, name='文章'))
admin.add_view(SecureModelView(Comment, db.session, name='评论'))
admin.add_view(SecureModelView(VisitStats, db.session, name='流量'))
admin.add_view(DailyPrayerAdmin(DailyPrayer, db.session, name='祷告墙'))
admin.add_view(RosaryDataAdmin(RosaryData, db.session, name='玫瑰经存档'))

# ================= 全局逻辑 =================
@app.before_request
def track_visitor():
    if request.endpoint and 'static' not in request.endpoint and 'admin' not in request.endpoint:
        today = datetime.now().strftime('%Y-%m-%d')
        try:
            stat = VisitStats.query.get(today)
            if not stat: db.session.add(VisitStats(date=today, count=1))
            else: stat.count += 1
            db.session.commit()
        except: db.session.rollback()

@app.context_processor
def inject_traffic_data():
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        daily = VisitStats.query.get(today).count if VisitStats.query.get(today) else 0
        total = db.session.query(func.sum(VisitStats.count)).scalar() or 0
        return dict(daily_visits=daily, total_visits=total)
    except: return dict(daily_visits=0, total_visits=0)

@socketio.on('send_message')
def handle_message(data):
    msg = data.get('message')
    if msg: socketio.emit('receive_message', {'user': data.get('nickname', '***'), 'msg': msg})

# ================= 启动逻辑 =================
def run_http_redirect():
    from flask import Flask, redirect, request
    r_app = Flask(__name__)
    @r_app.route('/', defaults={'path': ''})
    @r_app.route('/<path:path>')
    def https_redirect(path): return redirect(request.url.replace('http://', 'https://'), code=301)
    r_app.run(host='0.0.0.0', port=80)

def run_server():
    socketio.run(app, host='0.0.0.0', port=80, debug=True)

if __name__ == '__main__':
    if not os.path.exists('universe.db'):
        with app.app_context(): db.create_all()
    
    # 自动识别环境：如果有证书则跑 HTTPS，否则跑 HTTP
    # 这里默认生成 HTTP 版本以便调试，生产环境请解开下方注释
    
    # threading.Thread(target=run_http_redirect, daemon=True).start()
    # print(">>> HTTPS 启动 (Port 443)...")
    # socketio.run(app, host='0.0.0.0', port=443, debug=False, certfile='...', keyfile='...')
    
    print(">>> HTTP 开发模式启动 (Port 80)...")
    run_server()
"""
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_py_code.strip())
    print("[OK] app.py 已重构")

if __name__ == "__main__":
    refactor_full_project()
    print("-" * 30)
    print("重构完成！项目结构已更新：")
    print("1. models.py (数据库模型)")
    print("2. main_backend.py (文章/主站路由)")
    print("3. rose_backend.py (玫瑰经路由)")
    print("4. extensions.py (共享组件)")
    print("5. app.py (入口文件)")
    print("-" * 30)
    print("请重启服务: python3 app.py")