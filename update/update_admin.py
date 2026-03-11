import os

# 1. 更新 app.py (集成 Flask-Admin 和 BasicAuth)
app_code = """
import os
from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from sqlalchemy import func
from datetime import datetime

# --- 新增：后台管理模块 ---
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_basicauth import BasicAuth
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///universe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-key-for-my-universe'

# --- 配置后台管理员账号密码 ---
app.config['BASIC_AUTH_USERNAME'] = 'admin'      # 账号
app.config['BASIC_AUTH_PASSWORD'] = 'flashmud'   # 密码 (建议修改)
app.config['BASIC_AUTH_FORCE'] = False           # 不强制全站验证，只验证后台

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
basic_auth = BasicAuth(app)

# --- 数据库模型 ---
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    content = db.Column(db.Text)
    summary = db.Column(db.String(200))
    tags = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.now)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Post {self.title}>'

    @property
    def css_class(self):
        mapping = {
            'logic': 'cat-logic', 'spirit': 'cat-spirit',
            'senses': 'cat-senses', 'life': 'cat-life'
        }
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

# --- 后台安全控制 (只有登录才能看) ---
class SecureModelView(ModelView):
    def is_accessible(self):
        if not basic_auth.authenticate():
            return False
        return True

    def inaccessible_callback(self, name, **kwargs):
        return basic_auth.challenge()

class SecureIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not basic_auth.authenticate():
            return basic_auth.challenge()
        return super(SecureIndexView, self).index()

# --- 初始化后台 ---
admin = Admin(app, name='闪泥工作室·后台', template_mode='bootstrap3', index_view=SecureIndexView())
admin.add_view(SecureModelView(Post, db.session, name='文章管理'))
admin.add_view(SecureModelView(Comment, db.session, name='评论监控'))
admin.add_view(SecureModelView(VisitStats, db.session, name='流量统计'))

# --- 核心算法：流量统计 ---
@app.before_request
def track_visitor():
    if request.endpoint and 'static' not in request.endpoint and 'admin' not in request.endpoint:
        today_str = datetime.now().strftime('%Y-%m-%d')
        try:
            stat = VisitStats.query.get(today_str)
            if not stat:
                stat = VisitStats(date=today_str, count=1)
                db.session.add(stat)
            else:
                stat.count += 1
            db.session.commit()
        except:
            db.session.rollback()

@app.context_processor
def inject_traffic_data():
    try:
        today_str = datetime.now().strftime('%Y-%m-%d')
        today_stat = VisitStats.query.get(today_str)
        daily = today_stat.count if today_stat else 0
        total = db.session.query(func.sum(VisitStats.count)).scalar() or 0
        return dict(daily_visits=daily, total_visits=total)
    except:
        return dict(daily_visits=0, total_visits=0)

# --- 评论区算法 (时间折叠) ---
def prune_comments(post_id):
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    if len(comments) > 50:
        head_ids = [c.id for c in comments[:10]]
        tail_ids = [c.id for c in comments[-40:]]
        keep_ids = set(head_ids + tail_ids)
        for c in comments:
            if c.id not in keep_ids:
                db.session.delete(c)
        db.session.commit()

# --- 聊天室逻辑 ---
@socketio.on('send_message')
def handle_message(data):
    msg = data.get('message')
    nickname = data.get('nickname', '***')
    if len(nickname) < 1: nickname = "***"
    if len(nickname) > 16: nickname = nickname[:16]
    if msg:
        emit('receive_message', {'user': nickname, 'msg': msg}, broadcast=True)

# --- 路由 ---
@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts, title="首页")

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        content = request.form.get('content')
        if not nickname or nickname.strip() == "": nickname = "匿名访客"
        if content and content.strip() != "":
            new_comment = Comment(post_id=post.id, nickname=nickname[:20], content=content[:500])
            db.session.add(new_comment)
            db.session.commit()
            prune_comments(post.id)
            return redirect(url_for('post_detail', post_id=post_id))
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    return render_template('post_html.html', post=post, comments=comments, title=post.title)

@app.route('/category/<category_name>')
def category(category_name):
    posts = Post.query.filter_by(category=category_name).order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts, title=category_name.upper())

if __name__ == '__main__':
    if not os.path.exists('universe.db'):
        with app.app_context():
            db.create_all()
    
    print("启动服务器 (Port 80)...")
    print("后台管理入口: http://你的IP/admin")
    print("默认账号: admin")
    print("默认密码: flashmud")
    
    # 注意：Port 80 需要 root 权限
    socketio.run(app, host='0.0.0.0', port=80, debug=True)
"""

def update_files():
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_code.strip())
    print("[OK] V6.0 升级完成：后台管理系统已集成。")
    print("-------------------------------------")
    print("1. 请确保安装了依赖: pip install Flask-Admin Flask-BasicAuth")
    print("2. 运行网站: python3 app.py")
    print("3. 访问后台: 浏览器输入 http://你的IP/admin")
    print("-------------------------------------")

if __name__ == "__main__":
    update_files()
