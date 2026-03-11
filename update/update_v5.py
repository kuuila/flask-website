import os

# 1. 更新 app.py (包含统计模型、计数逻辑、上下文注入)
app_code = """
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from sqlalchemy import func
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

# 新增：访问统计表
class VisitStats(db.Model):
    date = db.Column(db.String(20), primary_key=True) # 格式: YYYY-MM-DD
    count = db.Column(db.Integer, default=0)

# --- 核心算法：流量统计 ---
@app.before_request
def track_visitor():
    # 排除静态文件和SocketIO请求，只统计页面访问
    if request.endpoint and 'static' not in request.endpoint:
        today_str = datetime.now().strftime('%Y-%m-%d')
        try:
            # 查询今天的记录
            stat = VisitStats.query.get(today_str)
            if not stat:
                # 如果今天还没记录，创建一条
                stat = VisitStats(date=today_str, count=1)
                db.session.add(stat)
            else:
                # 如果有，+1
                stat.count += 1
            db.session.commit()
        except Exception as e:
            # 并发写入可能会冲突，简单回滚忽略即可
            db.session.rollback()

# --- 全局注入：让所有模版都能直接使用统计数据 ---
@app.context_processor
def inject_traffic_data():
    try:
        today_str = datetime.now().strftime('%Y-%m-%d')
        # 今日访问
        today_stat = VisitStats.query.get(today_str)
        daily = today_stat.count if today_stat else 0
        
        # 总访问 (求和)
        total = db.session.query(func.sum(VisitStats.count)).scalar() or 0
        
        return dict(daily_visits=daily, total_visits=total)
    except:
        return dict(daily_visits=0, total_visits=0)

# --- 评论区算法 ---
def prune_comments(post_id):
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    total = len(comments)
    if total > 50:
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
    # 自动创建所有表 (包括新加的 VisitStats)
    if not os.path.exists('universe.db'):
        with app.app_context():
            db.create_all()
    else:
        with app.app_context():
            db.create_all()
            
    print("启动服务器 (Port 80) + 流量统计模块...")
    socketio.run(app, host='0.0.0.0', port=80, debug=True)
"""

# 2. 更新 layout.html (在底部增加统计显示)
layout_code = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} | 个人宇宙</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
</head>
<body>
    <nav>
        <div class="logo tech-font"><a href="/">CODE & SPIRIT</a></div>
        <div class="menu tech-font">
            <a href="/category/logic" class="menu-item cat-logic">逻辑·C++</a>
            <a href="/category/senses" class="menu-item cat-senses">感知·音画</a>
            <a href="/category/spirit" class="menu-item cat-spirit">灵性·玄术</a>
            <a href="/category/life" class="menu-item cat-life">生活·诗歌</a>
        </div>
    </nav>
    
    <div class="container">
        {% block content %}{% endblock %}
    </div>

    <!-- 悬浮聊天室按钮 -->
    <div id="chat-btn" onclick="toggleChat()">
        💬 匿名连接
    </div>

    <!-- 聊天室窗口 -->
    <div id="chat-box" class="hidden">
        <div class="chat-header tech-font">
            <span>> /dev/chat/anonymous</span>
            <span style="cursor:pointer; float:right;" onclick="toggleChat()">[x]</span>
        </div>
        <div class="chat-settings tech-font">
            <label>ID:</label>
            <input type="text" id="nickname-input" value="***" placeholder="4-16位昵称">
        </div>
        <div id="chat-messages" class="tech-font">
            <div class="sys-msg">--- 链路已接通 ---</div>
        </div>
        <div class="chat-input-area">
            <input type="text" id="msg-input" placeholder="发送信号..." onkeypress="handleKey(event)">
            <button onclick="sendMessage()">发送</button>
        </div>
    </div>

    <!-- 底部 (包含流量统计) -->
    <footer style="text-align:center; padding: 40px; margin-top: 50px; border-top: 1px solid #333; opacity: 0.6; font-size: 0.8rem;">
        <div class="tech-font" style="margin-bottom: 10px; color: var(--accent-spirit);">
            [ 流量监控 ] 今日: <span style="color:white; font-weight:bold;">{{ daily_visits }}</span> 
            | 总计: <span style="color:white; font-weight:bold;">{{ total_visits }}</span>
        </div>
        <p class="tech-font">System.exit(0); // Constructed by You</p>
    </footer>

    <script>
        var socket = io();
        var chatBox = document.getElementById('chat-box');
        
        socket.on('connect', function() { console.log('Connected'); });
        socket.on('receive_message', function(data) {
            var msgs = document.getElementById('chat-messages');
            var div = document.createElement('div');
            div.className = 'msg-item';
            div.innerHTML = "<span class='msg-user'>[" + data.user + "]</span> " + data.msg; 
            msgs.appendChild(div);
            msgs.scrollTop = msgs.scrollHeight;
        });

        function sendMessage() {
            var input = document.getElementById('msg-input');
            var nickInput = document.getElementById('nickname-input');
            var msg = input.value;
            var nick = nickInput.value.trim();

            if (nick.length < 4 || nick.length > 16) {
                if (nick !== "***") {
                    alert("昵称长度限制 4-16 位");
                    return;
                }
            }
            if(msg.trim() !== "") {
                socket.emit('send_message', { message: msg, nickname: nick });
                input.value = "";
            }
        }
        function toggleChat() {
            if(chatBox.classList.contains('hidden')) {
                chatBox.classList.remove('hidden');
            } else {
                chatBox.classList.add('hidden');
            }
        }
        function handleKey(e) { if(e.keyCode === 13) sendMessage(); }
    </script>
</body>
</html>
"""

def update_files():
    # 写入 app.py
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_code.strip())
    print("[OK] app.py 已更新 (访问统计模块)")

    # 写入 layout.html
    with open('templates/layout.html', 'w', encoding='utf-8') as f:
        f.write(layout_code.strip())
    print("[OK] layout.html 已更新 (底部数据显示)")

if __name__ == "__main__":
    update_files()
    print("-" * 30)
    print("V5.0 更新完成！")
    print("请重启服务: python3 app.py")
    print("现在每次刷新页面，底部的数字都会增加。")