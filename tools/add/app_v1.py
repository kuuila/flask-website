import os
from flask import Flask, render_template, request, redirect, url_for, flash, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from sqlalchemy import func, or_
from datetime import datetime

# --- 后台管理模块 ---
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_basicauth import BasicAuth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///universe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-key-for-my-universe'

# --- 配置 ---
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'flashmud'
app.config['BASIC_AUTH_FORCE'] = False

db = SQLAlchemy(app)

# --- 新增：玫瑰经用户数据存储 ---
class RosaryData(db.Model):
    uid = db.Column(db.String(36), primary_key=True) # 客户端生成的 UUID
    data = db.Column(db.Text, nullable=False)        # 完整的 JSON 字符串
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


socketio = SocketIO(app, cors_allowed_origins="*")
basic_auth = BasicAuth(app)

# --- 模型 ---
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    content = db.Column(db.Text)
    summary = db.Column(db.String(200))
    tags = db.Column(db.String(100))
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

# --- 后台管理 ---
class SecureModelView(ModelView):
    def is_accessible(self):
        return basic_auth.authenticate()
    def inaccessible_callback(self, name, **kwargs):
        return basic_auth.challenge()


# --- 玫瑰经后台管理视图配置 ---
class RosaryDataAdmin(SecureModelView):
    # 列表页显示的字段
    column_list = ('uid', 'updated_at', 'data_preview')
    # 默认按更新时间倒序排列
    column_default_sort = ('updated_at', True)
    # 禁止创建（数据应由用户上传），允许编辑和删除
    can_create = False
    can_edit = True
    can_delete = True
    
    # 编辑页：让 data 字段显示为大文本框，字体设为等宽方便看 JSON
    form_widget_args = {
        'data': {
            'rows': 15,
            'style': 'font-family: "Consolas", monospace; font-size: 12px;'
        },
        'uid': {
            'readonly': True
        }
    }
    
    # 列表页预览逻辑：只显示前 100 个字符
    def data_preview(self, context, model, name):
        if not model.data: return ""
        return model.data[:100] + '...' if len(model.data) > 100 else model.data
    
    # 自定义标签名
    column_labels = {
        'uid': '设备ID (UUID)',
        'data': 'JSON 数据包',
        'updated_at': '最后同步时间',
        'data_preview': '数据预览'
    }


class SecureIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not basic_auth.authenticate(): return basic_auth.challenge()
        return super(SecureIndexView, self).index()

admin = Admin(app, name='闪泥工作室·后台', template_mode='bootstrap3', index_view=SecureIndexView())
admin.add_view(SecureModelView(Post, db.session, name='文章管理'))
admin.add_view(SecureModelView(Comment, db.session, name='评论监控'))
admin.add_view(SecureModelView(VisitStats, db.session, name='流量统计'))
admin.add_view(RosaryDataAdmin(RosaryData, db.session, name='玫瑰经存档'))

# --- 统计与注入 ---
@app.before_request
def track_visitor():
    if request.endpoint and 'static' not in request.endpoint and 'admin' not in request.endpoint and 'search' not in request.endpoint:
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

# --- 搜索 API (新增) ---
@app.route('/api/search')
def search_api():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    # 搜索标题、简介或标签
    results = Post.query.filter(
        or_(
            Post.title.contains(query),
            Post.summary.contains(query),
            Post.tags.contains(query)
        )
    ).order_by(Post.created_at.desc()).limit(10).all()
    
    data = []
    for p in results:
        data.append({
            'id': p.id,
            'title': p.title,
            'summary': p.summary,
            'date': p.created_at.strftime('%Y-%m-%d'),
            'category': p.category
        })
    return jsonify(data)

# --- 路由 ---
@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts, title="首页")

@app.route('/s/<sub_web>')
def subweb(sub_web):
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template(sub_web+'.html', posts=posts)

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
            # 简单清洗逻辑
            comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.asc()).all()
            if len(comments) > 50:
                head = [c.id for c in comments[:10]]
                tail = [c.id for c in comments[-40:]]
                for c in comments:
                    if c.id not in set(head+tail): db.session.delete(c)
                db.session.commit()
            return redirect(url_for('post_detail', post_id=post_id))
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    return render_template('post_html.html', post=post, comments=comments, title=post.title)

@app.route('/category/<category_name>')
def category(category_name):
    posts = Post.query.filter_by(category=category_name).order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts, title=category_name.upper())

# --- SocketIO ---
@socketio.on('send_message')
def handle_message(data):
    msg = data.get('message')
    nickname = data.get('nickname', '***')
    if len(nickname) < 1: nickname = "***"
    if len(nickname) > 16: nickname = nickname[:16]
    if msg:
        emit('receive_message', {'user': nickname, 'msg': msg}, broadcast=True)


# --- 玫瑰经数据同步 API ---
@app.route('/api/rose/sync', methods=['POST'])
def rose_sync_upload():
    try:
        uid = request.json.get('uid')
        data_str = request.json.get('data')
        
        if not uid or not data_str:
            return jsonify({'status': 'error', 'msg': '缺少参数'}), 400
            
        # 查找或创建
        record = RosaryData.query.get(uid)
        if not record:
            record = RosaryData(uid=uid, data=data_str)
            db.session.add(record)
        else:
            record.data = data_str
            
        db.session.commit()
        return jsonify({'status': 'success', 'msg': '云端存档已更新'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/api/rose/sync/<uid>', methods=['GET'])
def rose_sync_download(uid):
    record = RosaryData.query.get(uid)
    if record:
        return jsonify({'status': 'success', 'data': record.data, 'time': record.updated_at})
    else:
        return jsonify({'status': 'error', 'msg': '未找到云端存档'}), 404

def run_http_server():
    socketio.run(app,host='0.0.0.0', port=80, debug=False)

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
    t = threading.Thread(target=run_http_server, daemon=True)
    t.start()
    
    print(">>> 闪泥工作室 HTTPS 主服务启动 (Port 443)...")
    
    # 2. 启动 HTTPS 主服务 (阻塞运行)
    # 注意：开启 SSL 后建议关闭 debug 模式，防止自动重启导致端口冲突
    socketio.run(app, host='0.0.0.0', port=443, debug=False,
                 certfile='/etc/letsencrypt/live/www.mxle.net/fullchain.pem',
                 keyfile='/etc/letsencrypt/live/www.mxle.net/privkey.pem')
