import os

# 1. 更新 app.py (增加 jsonify 库，增加搜索 API)
app_code = """
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

class SecureIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not basic_auth.authenticate(): return basic_auth.challenge()
        return super(SecureIndexView, self).index()

admin = Admin(app, name='闪泥工作室·后台', template_mode='bootstrap3', index_view=SecureIndexView())
admin.add_view(SecureModelView(Post, db.session, name='文章管理'))
admin.add_view(SecureModelView(Comment, db.session, name='评论监控'))
admin.add_view(SecureModelView(VisitStats, db.session, name='流量统计'))

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

if __name__ == '__main__':
    if not os.path.exists('universe.db'):
        with app.app_context(): db.create_all()
    socketio.run(app, host='0.0.0.0', port=80, debug=True)
"""

# 2. 更新 layout.html (加入搜索按钮、遮罩层、JS逻辑)
layout_code = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} | 闪泥电影工作室</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
</head>
<body>
    <nav>
        <div class="logo tech-font"><a href="/">FLASH MUD STUDIO</a></div>
        <div class="menu tech-font">
            <a href="/category/logic" class="menu-item cat-logic">虚空·构筑</a>
            <a href="/category/senses" class="menu-item cat-senses">幻象·共鸣</a>
            <a href="/category/spirit" class="menu-item cat-spirit">无壁·场域</a>
            <a href="/category/life" class="menu-item cat-life">风暴·行迹</a>
        </div>
    </nav>
    
    <div class="container">
        {% block content %}{% endblock %}
    </div>

    <!-- 悬浮按钮组 -->
    <div id="float-btns">
        <!-- 搜索按钮 -->
        <div id="search-btn" onclick="toggleSearch()">
            🔍 检索
        </div>
        <!-- 聊天按钮 -->
        <div id="chat-btn" onclick="toggleChat()">
            💬 匿名连接
        </div>
    </div>

    <!-- 全屏搜索遮罩层 -->
    <div id="search-overlay" class="hidden">
        <div class="search-container">
            <div class="search-header tech-font">
                <span>> SEARCHING DATABASE...</span>
                <span style="cursor:pointer; float:right; font-size:1.5rem;" onclick="toggleSearch()">[ × ]</span>
            </div>
            <input type="text" id="search-input" placeholder="输入关键词检索宇宙..." autocomplete="off">
            <div id="search-results" class="tech-font">
                <!-- 结果将在这里显示 -->
            </div>
        </div>
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

    <footer style="text-align:center; padding: 40px; margin-top: 50px; border-top: 1px solid #333; opacity: 0.6; font-size: 0.8rem;">
        <div class="tech-font" style="margin-bottom: 10px; color: var(--accent-spirit);">
            [ 流量监控 ] 今日: <span style="color:white; font-weight:bold;">{{ daily_visits }}</span> 
            | 总计: <span style="color:white; font-weight:bold;">{{ total_visits }}</span>
        </div>
        <p class="tech-font" style="margin-top:10px;">&copy; 2024 Flash Mud Studios. All Rights Reserved.</p>
    </footer>

    <script>
        // --- 聊天室逻辑 ---
        var socket = io();
        var chatBox = document.getElementById('chat-box');
        
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
                if (nick !== "***") { alert("昵称长度限制 4-16 位"); return; }
            }
            if(msg.trim() !== "") {
                socket.emit('send_message', { message: msg, nickname: nick });
                input.value = "";
            }
        }
        function toggleChat() {
            chatBox.classList.toggle('hidden');
        }
        function handleKey(e) { if(e.keyCode === 13) sendMessage(); }

        // --- 搜索逻辑 (AJAX) ---
        var searchOverlay = document.getElementById('search-overlay');
        var searchInput = document.getElementById('search-input');
        var resultsBox = document.getElementById('search-results');

        function toggleSearch() {
            searchOverlay.classList.toggle('hidden');
            if (!searchOverlay.classList.contains('hidden')) {
                searchInput.focus(); // 自动聚焦
            }
        }

        // 监听输入，实时搜索
        searchInput.addEventListener('input', function() {
            var query = this.value.trim();
            if (query.length < 1) {
                resultsBox.innerHTML = "";
                return;
            }

            fetch('/api/search?q=' + encodeURIComponent(query))
                .then(response => response.json())
                .then(data => {
                    resultsBox.innerHTML = "";
                    if (data.length === 0) {
                        resultsBox.innerHTML = "<div style='padding:20px; opacity:0.5;'>[虚空] 未探测到相关信号...</div>";
                    } else {
                        data.forEach(item => {
                            var div = document.createElement('div');
                            div.className = 'search-item';
                            div.innerHTML = `
                                <a href="/post/${item.id}">
                                    <div class="s-title">${item.title}</div>
                                    <div class="s-meta">${item.date} | ${item.category}</div>
                                    <div class="s-summary">${item.summary}</div>
                                </a>
                            `;
                            resultsBox.appendChild(div);
                        });
                    }
                });
        });
    </script>
</body>
</html>
"""

# 3. 追加 CSS (搜索框的赛博风格)
# 为了保证顺序，我们读取原有 css，追加在最后，或者重写
css_append = """
/* --- 悬浮按钮组 --- */
#float-btns {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: 10px;
    align-items: flex-end;
}

#chat-btn, #search-btn {
    position: relative; /* 覆盖旧样式 */
    top: auto; left: auto; bottom: auto; right: auto;
    background: rgba(26,28,37, 0.9);
    border: 1px solid var(--accent-spirit);
    color: var(--accent-spirit);
    padding: 10px 15px;
    cursor: pointer;
    border-radius: 4px;
    font-family: 'Consolas', monospace;
    box-shadow: 0 0 10px rgba(0,0,0,0.5);
    transition: 0.3s;
    text-align: center;
    min-width: 100px;
}
#search-btn {
    border-color: var(--accent-logic);
    color: var(--accent-logic);
}
#search-btn:hover {
    background: var(--accent-logic);
    color: black;
    box-shadow: 0 0 15px var(--accent-logic);
}

/* --- 全屏搜索遮罩 --- */
#search-overlay {
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(15, 17, 26, 0.95);
    z-index: 3000;
    backdrop-filter: blur(10px);
    display: flex;
    justify-content: center;
    padding-top: 100px;
}

.search-container {
    width: 90%;
    max-width: 700px;
}

.search-header {
    color: var(--accent-logic);
    font-size: 1.2rem;
    margin-bottom: 20px;
    border-bottom: 2px solid #333;
    padding-bottom: 10px;
}

#search-input {
    width: 100%;
    background: transparent;
    border: none;
    border-bottom: 2px solid #555;
    color: white;
    font-size: 2rem;
    padding: 10px 0;
    outline: none;
    font-family: 'Consolas', monospace;
    transition: 0.3s;
}
#search-input:focus {
    border-color: var(--accent-spirit);
}

#search-results {
    margin-top: 30px;
    max-height: 60vh;
    overflow-y: auto;
}

.search-item {
    padding: 15px;
    border-bottom: 1px dashed #333;
    transition: 0.2s;
}
.search-item:hover {
    background: rgba(255,255,255,0.05);
}
.s-title {
    font-size: 1.2rem;
    color: var(--accent-life);
    margin-bottom: 5px;
}
.s-meta {
    font-size: 0.8rem;
    color: #666;
    margin-bottom: 5px;
}
.s-summary {
    font-size: 0.9rem;
    color: #aaa;
}
"""

def update_search_v7():
    # 1. 重写 app.py
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_code.strip())
    print("[OK] app.py 已更新 (新增 /api/search 接口)")

    # 2. 重写 layout.html
    with open('templates/layout.html', 'w', encoding='utf-8') as f:
        f.write(layout_code.strip())
    print("[OK] layout.html 已更新 (新增搜索界面)")

    # 3. 追加 CSS
    # 先读取现在的 CSS
    css_path = 'static/style.css'
    with open(css_path, 'r', encoding='utf-8') as f:
        old_css = f.read()
    
    # 避免重复添加
    if "#search-overlay" not in old_css:
        with open(css_path, 'a', encoding='utf-8') as f:
            f.write(css_append)
        print("[OK] style.css 已更新 (新增搜索样式)")
    else:
        print("[SKIP] CSS 似乎已经包含搜索样式")

if __name__ == "__main__":
    update_search_v7()
    print("-" * 30)
    print("V7.0 升级完毕！")
    print("功能：新增悬浮搜索雷达 (AJAX实时检索)")
    print("请重启服务: python3 app.py")
