import os

# 1. 更新 app.py (端口改为 80，后端支持昵称解析)
app_code = """
import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from datetime import datetime
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///universe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-key-for-my-universe'

db = SQLAlchemy(app)
# 初始化 SocketIO
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

    @property
    def css_class(self):
        mapping = {
            'logic': 'cat-logic', 'spirit': 'cat-spirit',
            'senses': 'cat-senses', 'life': 'cat-life'
        }
        return mapping.get(self.category, '')

# --- 聊天室逻辑 ---
@socketio.on('send_message')
def handle_message(data):
    msg = data.get('message')
    nickname = data.get('nickname', '***') # 获取昵称，默认为 ***
    
    # 后端简单校验长度，防止恶意长名
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

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_html.html', post=post, title=post.title)

@app.route('/category/<category_name>')
def category(category_name):
    posts = Post.query.filter_by(category=category_name).order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts, title=category_name.upper())

if __name__ == '__main__':
    if not os.path.exists('universe.db'):
        with app.app_context():
            db.create_all()
            
    print("启动服务器 (Port 80)...")
    # 端口改为 80，移除不兼容参数
    socketio.run(app, host='0.0.0.0', port=80, debug=True)
"""

# 2. 更新 templates/layout.html (左侧布局，增加昵称输入框)
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

    <!-- 悬浮聊天室按钮 (CSS控制位置) -->
    <div id="chat-btn" onclick="toggleChat()">
        💬 匿名连接
    </div>

    <!-- 聊天室窗口 -->
    <div id="chat-box" class="hidden">
        <div class="chat-header tech-font">
            <span>> /dev/chat/anonymous</span>
            <span style="cursor:pointer; float:right;" onclick="toggleChat()">[x]</span>
        </div>
        
        <!-- 昵称设置区域 -->
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

    <footer style="text-align:center; padding: 40px; opacity: 0.5; font-size: 0.8rem;">
        <p class="tech-font">System.exit(0); // Constructed by You</p>
    </footer>

    <script>
        var socket = io();
        var chatBox = document.getElementById('chat-box');
        
        socket.on('connect', function() {
            console.log('Connected');
        });

        socket.on('receive_message', function(data) {
            var msgs = document.getElementById('chat-messages');
            var div = document.createElement('div');
            div.className = 'msg-item';
            // 显示 昵称: 消息
            div.innerHTML = "<span class='msg-user'>[" + data.user + "]</span> " + data.msg; 
            msgs.appendChild(div);
            msgs.scrollTop = msgs.scrollHeight;
        });

        function sendMessage() {
            var input = document.getElementById('msg-input');
            var nickInput = document.getElementById('nickname-input');
            var msg = input.value;
            var nick = nickInput.value.trim();

            // 昵称校验
            if (nick.length < 4 || nick.length > 16) {
                if (nick !== "***") {
                    alert("提示：昵称长度请保持在 4-16 位之间，或者使用默认 '***'");
                    return;
                }
            }

            if(msg.trim() !== "") {
                socket.emit('send_message', {
                    message: msg,
                    nickname: nick
                });
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

        function handleKey(e) {
            if(e.keyCode === 13) sendMessage();
        }
    </script>
</body>
</html>
"""

# 3. 更新 static/style.css (调整位置到左侧)
# 我们读取原文件，去掉旧的 chat 样式，加上新的
def update_css():
    css_path = 'static/style.css'
    with open(css_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 过滤掉之前的聊天室样式
    new_lines = []
    skip = False
    for line in lines:
        if "/* --- 聊天室样式 --- */" in line:
            skip = True
        if not skip:
            new_lines.append(line)
    
    # 定义新的样式
    new_css_block = """
/* --- 聊天室样式 --- */
#chat-btn {
    position: fixed;
    top: 80px;  /* 位于导航栏(约60px)下方 */
    left: 20px; /* 靠左 */
    background: var(--nav-bg);
    border: 1px solid var(--accent-spirit);
    color: var(--accent-spirit);
    padding: 8px 15px;
    cursor: pointer;
    border-radius: 4px;
    font-family: 'Consolas', monospace;
    z-index: 1000;
    transition: 0.3s;
    box-shadow: 0 0 10px rgba(0,0,0,0.5);
    font-size: 0.9rem;
}
#chat-btn:hover {
    background: var(--accent-spirit);
    color: black;
    box-shadow: 0 0 15px var(--accent-spirit);
}

#chat-box {
    position: fixed;
    top: 130px; /* 按钮下方 */
    left: 20px; /* 靠左对齐 */
    width: 320px;
    height: 400px;
    background: rgba(15, 17, 26, 0.95);
    border: 1px solid var(--accent-logic);
    border-radius: 4px;
    z-index: 999;
    display: flex;
    flex-direction: column;
    box-shadow: 5px 5px 20px rgba(0,0,0,0.8);
    backdrop-filter: blur(5px);
}

.hidden { display: none !important; }

.chat-header {
    background: rgba(26, 28, 37, 0.9);
    padding: 10px;
    border-bottom: 1px solid #333;
    font-size: 0.8rem;
    color: var(--accent-logic);
}

.chat-settings {
    padding: 5px 10px;
    background: #15171f;
    border-bottom: 1px solid #333;
    display: flex;
    align-items: center;
    font-size: 0.8rem;
}
.chat-settings input {
    background: #0f111a;
    border: 1px solid #333;
    color: #ffcb6b;
    padding: 2px 5px;
    margin-left: 10px;
    width: 120px;
    outline: none;
    font-family: monospace;
}

#chat-messages {
    flex: 1;
    padding: 10px;
    overflow-y: auto;
    font-size: 0.85rem;
    color: #ddd;
}

.sys-msg { color: #555; font-style: italic; margin-bottom: 5px; }
.msg-item { margin-bottom: 8px; word-wrap: break-word; line-height: 1.4; }
.msg-user { color: #82aaff; font-weight: bold; margin-right: 5px; }

.chat-input-area {
    display: flex;
    border-top: 1px solid #333;
}
.chat-input-area input {
    flex: 1;
    background: transparent;
    border: none;
    color: white;
    padding: 10px;
    outline: none;
}
.chat-input-area button {
    background: var(--accent-logic);
    border: none;
    color: black;
    padding: 0 15px;
    cursor: pointer;
    font-weight: bold;
}
.chat-input-area button:hover { background: white; }
"""
    
    with open(css_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
        f.write(new_css_block)
    print("[OK] style.css 已更新 (位置: 左侧)")

def update_files():
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_code.strip())
    print("[OK] app.py 已更新 (端口: 80)")

    with open('templates/layout.html', 'w', encoding='utf-8') as f:
        f.write(layout_code.strip())
    print("[OK] layout.html 已更新 (昵称功能)")

    update_css()

if __name__ == "__main__":
    update_files()
    print("-" * 30)
    print("升级完成！请运行 python3 app.py 启动")