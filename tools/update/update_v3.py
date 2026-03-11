import os

# 1. 更新 app.py (增加评论模型 + 清洗算法)
app_code = """
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from datetime import datetime
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///universe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-key-for-my-universe'

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# --- 数据库模型 ---
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    content = db.Column(db.Text)
    summary = db.Column(db.String(200))
    tags = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.now)
    # 关联评论
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")

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

# --- 核心算法：时间折叠 (保留前10和后40) ---
def prune_comments(post_id):
    # 获取该文章所有评论，按时间正序排列
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    total = len(comments)
    
    # 阈值：10 (头) + 40 (尾) = 50
    if total > 50:
        # 需要保留的头部 ID
        head_ids = [c.id for c in comments[:10]]
        # 需要保留的尾部 ID
        tail_ids = [c.id for c in comments[-40:]]
        
        keep_ids = set(head_ids + tail_ids)
        
        # 找出不在保留列表中的 ID (中间的平庸之辈)
        for c in comments:
            if c.id not in keep_ids:
                db.session.delete(c)
        
        db.session.commit()
        print(f"[System] 文章 {post_id} 触发时间折叠，中间层评论已删除。")

# --- 聊天室逻辑 (保持不变) ---
@socketio.on('send_message')
def handle_message(data):
    msg = data.get('message')
    nickname = data.get('nickname', '***')
    if len(nickname) < 1: nickname = "***"
    if len(nickname) > 16: nickname = nickname[:16]
    if msg:
        print(f"[{nickname}] 说: {msg}")
        emit('receive_message', {'user': nickname, 'msg': msg}, broadcast=True)

# --- 路由 ---
@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts, title="首页")

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    
    # 处理提交评论
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        content = request.form.get('content')
        
        if not nickname or nickname.strip() == "":
            nickname = "匿名访客"
        
        if content and content.strip() != "":
            new_comment = Comment(
                post_id=post.id,
                nickname=nickname[:20], # 限制名字长度
                content=content[:500]   # 限制内容长度
            )
            db.session.add(new_comment)
            db.session.commit()
            
            # 触发清洗算法
            prune_comments(post.id)
            
            return redirect(url_for('post_detail', post_id=post_id))

    # 获取评论展示：分离头部和尾部，或者直接按时间展示
    # 为了直观，我们直接展示留存下来的所有评论
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
    else:
        # 确保新表存在 (针对老数据库升级)
        with app.app_context():
            db.create_all()
            
    print("启动服务器 (Port 80)...")
    socketio.run(app, host='0.0.0.0', port=80, debug=True)
"""

# 2. 更新 post_html.html (增加评论区 UI)
post_html_code = """
{% extends 'layout.html' %}

{% block content %}
<article class="post-content">
    <header class="post-header">
        <span class="tag {{ post.css_class }}" style="margin-bottom: 10px;">{{ post.category }}</span>
        <h1>{{ post.title }}</h1>
        <div class="meta tech-font">
            发布于: {{ post.created_at.strftime('%Y-%m-%d %H:%M') }} | 标签: {{ post.tags }}
        </div>
    </header>
    
    <div style="font-size: 1.1rem; min-height: 200px;">
        {{ post.content | safe }}
    </div>

    <div style="margin-top: 40px; padding-top: 20px; border-top: 1px dashed #444; opacity: 0.7;">
        <a href="/" class="tech-font"><< 返回首页</a>
    </div>
</article>

<!-- 评论区 -->
<div class="comment-section">
    <h3 class="tech-font" style="border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px;">
        > 数据痕迹 (只保留最初10条与最后40条)
    </h3>

    <!-- 评论列表 -->
    <div class="comment-list">
        {% if comments %}
            {% for c in comments %}
                <div class="comment-item">
                    <div class="comment-meta tech-font">
                        <span class="c-user">[{{ c.nickname }}]</span>
                        <span class="c-time">{{ c.created_at.strftime('%Y-%m-%d %H:%M') }}</span>
                        <span class="c-id">#{{ loop.index }}</span>
                    </div>
                    <div class="comment-body">
                        {{ c.content }}
                    </div>
                </div>
                <!-- 如果是第10条，且后面还有评论，显示一个折叠标记 -->
                {% if loop.index == 10 and comments|length > 10 %}
                <div style="text-align:center; color:#555; margin: 20px 0; font-family: monospace;">
                    [ ... 时间的裂缝: 中间的数据已丢失 ... ]
                </div>
                {% endif %}
            {% endfor %}
        {% else %}
            <div style="opacity: 0.5; font-style: italic;">暂无痕迹，留下你的第一条记录...</div>
        {% endif %}
    </div>

    <!-- 评论表单 -->
    <form class="comment-form" method="POST" action="{{ url_for('post_detail', post_id=post.id) }}">
        <div class="form-group">
            <input type="text" name="nickname" placeholder="署名 (可选)" maxlength="20">
        </div>
        <div class="form-group">
            <textarea name="content" placeholder="输入你的信号..." required maxlength="500"></textarea>
        </div>
        <button type="submit">写入数据</button>
    </form>
</div>
{% endblock %}
"""

# 3. 追加 CSS 样式
def update_css():
    css_path = 'static/style.css'
    css_append = """

/* --- 评论区样式 --- */
.comment-section {
    max-width: 900px;
    margin: 40px auto 0;
    padding: 0 20px;
}
.comment-list {
    margin-bottom: 40px;
}
.comment-item {
    background: #15171f;
    border-left: 3px solid #333;
    padding: 15px;
    margin-bottom: 15px;
    transition: 0.2s;
}
.comment-item:hover {
    border-left-color: var(--accent-spirit);
    background: #1a1c25;
}
.comment-meta {
    font-size: 0.8rem;
    color: #666;
    margin-bottom: 5px;
    display: flex;
    justify-content: space-between;
}
.c-user { color: var(--accent-logic); font-weight: bold; }
.comment-body {
    font-size: 0.95rem;
    line-height: 1.5;
    color: #ccc;
}

.comment-form {
    background: #1f222e;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #333;
}
.form-group { margin-bottom: 15px; }
.comment-form input, .comment-form textarea {
    width: 100%;
    background: #0f111a;
    border: 1px solid #444;
    color: white;
    padding: 10px;
    box-sizing: border-box;
    font-family: 'Consolas', monospace;
    outline: none;
}
.comment-form input:focus, .comment-form textarea:focus {
    border-color: var(--accent-spirit);
}
.comment-form textarea { height: 80px; resize: vertical; }
.comment-form button {
    background: var(--accent-logic);
    color: black;
    border: none;
    padding: 10px 20px;
    cursor: pointer;
    font-weight: bold;
    text-transform: uppercase;
    font-family: 'Consolas', monospace;
}
.comment-form button:hover { background: white; }
"""
    # 读取检查是否已存在
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "/* --- 评论区样式 --- */" not in content:
        with open(css_path, 'a', encoding='utf-8') as f:
            f.write(css_append)
        print("[OK] style.css 已追加评论区样式")
    else:
        print("[SKIP] 评论区样式已存在")

def update_files():
    # 更新 app.py
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_code.strip())
    print("[OK] app.py 已更新 (时间折叠算法)")

    # 更新 templates/post_html.html
    with open('templates/post_html.html', 'w', encoding='utf-8') as f:
        f.write(post_html_code.strip())
    print("[OK] post_html.html 已更新 (评论表单)")

    # 更新 CSS
    update_css()

if __name__ == "__main__":
    update_files()
    print("-" * 30)
    print("评论系统 V1.0 已上线。")
    print("规则：保留 TOP 10 + LAST 40")
    print("请运行 python3 app.py 重启")