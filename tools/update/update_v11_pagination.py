import os

# 1. 更新 app.py
# 核心改动：
# - Post 模型增加 views
# - post_detail 增加阅读量计数
# - index 路由增加 tab 和 page 参数处理
app_code = """
import os
from flask import Flask, render_template, request, redirect, url_for, flash, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from sqlalchemy import func, or_
from datetime import datetime
import threading

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

# --- 玫瑰经用户数据存储 ---
class RosaryData(db.Model):
    uid = db.Column(db.String(36), primary_key=True)
    data = db.Column(db.Text, nullable=False)
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
    # 新增阅读量字段
    views = db.Column(db.Integer, default=0)
    
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

class RosaryDataAdmin(SecureModelView):
    column_list = ('uid', 'updated_at', 'data_preview')
    column_default_sort = ('updated_at', True)
    can_create = False
    form_widget_args = {'data': {'rows': 15, 'style': 'font-family:"Consolas";font-size:12px;'}, 'uid': {'readonly': True}}
    def data_preview(self, context, model, name):
        if not model.data: return ""
        return model.data[:100] + '...' if len(model.data) > 100 else model.data

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

@app.route('/api/search')
def search_api():
    query = request.args.get('q', '')
    if not query: return jsonify([])
    results = Post.query.filter(or_(Post.title.contains(query),Post.summary.contains(query),Post.tags.contains(query))).order_by(Post.created_at.desc()).limit(10).all()
    data = []
    for p in results:
        data.append({'id': p.id, 'title': p.title, 'summary': p.summary, 'date': p.created_at.strftime('%Y-%m-%d'), 'category': p.category})
    return jsonify(data)

# --- 首页路由 (核心修改：分页与分栏) ---
@app.route('/')
def index():
    # 获取参数，默认第1页，默认 'latest' 标签
    page = request.args.get('page', 1, type=int)
    tab = request.args.get('tab', 'latest')
    per_page = 9 # 每页显示9篇

    query = Post.query

    # 根据标签筛选/排序
    if tab == 'popular':
        # 人气最高：按 views 倒序
        query = query.order_by(Post.views.desc())
    elif tab == 'recommend':
        # 闪泥推荐：筛选标题含"闪泥"的文章
        query = query.filter(Post.title.contains('闪泥')).order_by(Post.created_at.desc())
    else: # latest
        # 最新发布
        query = query.order_by(Post.created_at.desc())

    # 执行分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('index.html', pagination=pagination, current_tab=tab, title="首页")

@app.route('/s/<sub_web>')
def subweb(sub_web):
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template(sub_web+'.html', posts=posts)

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    
    # 增加阅读量 (简单防刷：仅GET请求且非后台)
    if request.method == 'GET':
        post.views = (post.views or 0) + 1
        db.session.commit()

    if request.method == 'POST':
        nickname = request.form.get('nickname')
        content = request.form.get('content')
        if not nickname or nickname.strip() == "": nickname = "匿名访客"
        if content and content.strip() != "":
            new_comment = Comment(post_id=post.id, nickname=nickname[:20], content=content[:500])
            db.session.add(new_comment)
            db.session.commit()
            comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.asc()).all()
            if len(comments) > 50:
                head = [c.id for c in comments[:10]]
                tail = [c.id for c in comments[-40:]]
                for c in comments:
                    if c.id not in set(head+tail): db.session.delete(c)
                db.session.commit()
            return redirect(url_for('post_detail', post_id=post_id))
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.asc()).all()
    return render_template('post_html.html', post=post, comments=comments, title=post.title)

@app.route('/category/<category_name>')
def category(category_name):
    # 分类页面也加上简单的分页
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(category=category_name).order_by(Post.created_at.desc()).paginate(page=page, per_page=12, error_out=False)
    # 复用 index.html，但需要传 current_tab 为 None 或特定值避免显示首页 Tab
    return render_template('index.html', pagination=pagination, current_tab='category', title=category_name.upper())

@app.route('/api/rose/sync', methods=['POST'])
def rose_sync_upload():
    try:
        uid = request.json.get('uid'); data_str = request.json.get('data')
        if not uid or not data_str: return jsonify({'status': 'error', 'msg': '缺少参数'}), 400
        record = RosaryData.query.get(uid)
        if not record:
            record = RosaryData(uid=uid, data=data_str)
            db.session.add(record)
        else: record.data = data_str
        db.session.commit()
        return jsonify({'status': 'success', 'msg': '云端存档已更新'})
    except Exception as e: return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/api/rose/sync/<uid>', methods=['GET'])
def rose_sync_download(uid):
    record = RosaryData.query.get(uid)
    if record: return jsonify({'status': 'success', 'data': record.data, 'time': record.updated_at})
    else: return jsonify({'status': 'error', 'msg': '未找到云端存档'}), 404

# --- SocketIO ---
@socketio.on('send_message')
def handle_message(data):
    msg = data.get('message')
    nickname = data.get('nickname', '***')
    if len(nickname) < 1: nickname = "***"
    if len(nickname) > 16: nickname = nickname[:16]
    if msg: emit('receive_message', {'user': nickname, 'msg': msg}, broadcast=True)

# --- HTTPS Redirect ---
def run_http_redirect():
    from flask import Flask, redirect, request
    redirect_app = Flask(__name__)
    @redirect_app.route('/', defaults={'path': ''})
    @redirect_app.route('/<path:path>')
    def https_redirect(path):
        return redirect(request.url.replace('http://', 'https://'), code=301)
    redirect_app.run(host='0.0.0.0', port=80)

if __name__ == '__main__':
    if not os.path.exists('universe.db'):
        with app.app_context(): db.create_all()
    
    import threading
    t = threading.Thread(target=run_http_redirect, daemon=True)
    t.start()
    print(">>> 闪泥工作室 HTTPS 主服务启动 (Port 443)...")
    
    socketio.run(app, host='0.0.0.0', port=443, debug=False,
                 certfile='/etc/letsencrypt/live/www.mxle.net/fullchain.pem',
                 keyfile='/etc/letsencrypt/live/www.mxle.net/privkey.pem')
"""

# 2. 更新 templates/index.html (增加 Tabs UI 和 分页控件)
index_html = """
{% extends 'layout.html' %}

{% block content %}
<div style="text-align: center; margin-bottom: 40px;">
    <h1>FLASH MUD STUDIO</h1>
    <p style="opacity: 0.8;">“以 0.7 元的成本，在你的颅内放映宇宙。”</p>
</div>

<!-- 首页标签栏 (Tab) -->
{% if current_tab != 'category' %}
<div class="home-tabs tech-font">
    <a href="/?tab=latest" class="tab-item {% if current_tab == 'latest' %}active{% endif %}">
        ✨ 最新发布
    </a>
    <a href="/?tab=popular" class="tab-item {% if current_tab == 'popular' %}active{% endif %}">
        🔥 人气最高
    </a>
    <a href="/?tab=recommend" class="tab-item {% if current_tab == 'recommend' %}active{% endif %}">
        ⚡ 闪泥推荐
    </a>
</div>
{% endif %}

<h2 class="tech-font" style="font-size:1rem; margin-bottom:20px; border-bottom:1px dashed #333; padding-bottom:10px;">
    > DATA_STREAM [Page {{ pagination.page }}]
</h2>

<div class="grid">
    {% for post in pagination.items %}
    <a href="{{ url_for('post_detail', post_id=post.id) }}" class="card">
        <span class="meta tech-font">
            {{ post.created_at.strftime('%Y-%m-%d') }} | {{ post.category }} | 👁️ {{ post.views or 0 }}
        </span>
        <h3 class="{{ post.css_class }}">{{ post.title }}</h3>
        <p style="font-size: 0.9rem; opacity: 0.8;">{{ post.summary }}</p>
        <div style="margin-top:10px;">
            {% for tag in post.tags.split(',') %}
            <span class="tag">{{ tag }}</span>
            {% endfor %}
        </div>
    </a>
    {% endfor %}
</div>

<!-- 分页控制器 -->
<div class="pagination tech-font">
    {% if pagination.has_prev %}
        <a href="{{ url_for('index', page=pagination.prev_num, tab=current_tab) }}" class="page-btn">< PREV</a>
    {% else %}
        <span class="page-btn disabled">< PREV</span>
    {% endif %}

    <span class="page-info">PAGE {{ pagination.page }} / {{ pagination.pages }}</span>

    {% if pagination.has_next %}
        <a href="{{ url_for('index', page=pagination.next_num, tab=current_tab) }}" class="page-btn">NEXT ></a>
    {% else %}
        <span class="page-btn disabled">NEXT ></span>
    {% endif %}
</div>
{% endblock %}
"""

# 3. 追加 CSS 样式
css_append = """
/* --- 首页 Tab 样式 --- */
.home-tabs {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-bottom: 40px;
}

.tab-item {
    padding: 8px 20px;
    border: 1px solid #333;
    border-radius: 20px;
    color: #888;
    transition: all 0.3s;
    font-size: 0.9rem;
    text-transform: uppercase;
    background: #0f111a;
}

.tab-item:hover {
    border-color: var(--accent-spirit);
    color: var(--accent-spirit);
}

.tab-item.active {
    background: var(--accent-logic);
    color: #000;
    border-color: var(--accent-logic);
    font-weight: bold;
    box-shadow: 0 0 15px rgba(130, 170, 255, 0.4);
}

/* --- 分页器样式 --- */
.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 50px;
    gap: 20px;
}

.page-btn {
    padding: 10px 20px;
    border: 1px solid var(--accent-logic);
    color: var(--accent-logic);
    border-radius: 4px;
    transition: 0.3s;
    cursor: pointer;
}

.page-btn:hover {
    background: var(--accent-logic);
    color: black;
}

.page-btn.disabled {
    border-color: #333;
    color: #555;
    cursor: not-allowed;
    pointer-events: none;
}

.page-info {
    color: #666;
    letter-spacing: 2px;
}
"""

def update_v11():
    # 1. 更新 app.py
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_code.strip())
    print("[OK] app.py 已更新 (增加 Views 字段、分页逻辑)")

    # 2. 更新 templates/index.html
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(index_html.strip())
    print("[OK] index.html 已更新 (增加 Tabs 和 分页UI)")

    # 3. 追加 CSS
    css_path = 'static/style.css'
    with open(css_path, 'r', encoding='utf-8') as f:
        old_css = f.read()
    
    if ".home-tabs" not in old_css:
        with open(css_path, 'a', encoding='utf-8') as f:
            f.write(css_append)
        print("[OK] style.css 已追加 Tab 和分页样式")
    else:
        print("[SKIP] CSS 似乎已包含相关样式")

if __name__ == "__main__":
    update_v11()
    print("-" * 30)
    print("V11.0 架构升级完成！")
    print("1. 务必先运行: python3 fix_db_views.py")
    print("2. 然后运行: python3 update_v11_pagination.py (已执行)")
    print("3. 最后重启: python3 app.py")