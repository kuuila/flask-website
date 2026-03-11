import os

# 1. 新的 app.py 内容 (加入了 SocketIO)
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
# 初始化 SocketIO (允许跨域)
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
    if msg:
        # 简单的匿名处理
        print(f"收到消息: {msg}")
        # 广播给所有人
        emit('receive_message', {'msg': msg}, broadcast=True)

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
    # 只要运行过一次 init_db 就不需要再运行了，或者加个判断
    if not os.path.exists('universe.db'):
        with app.app_context():
            db.create_all()
            
    print("启动服务器... 聊天室已就绪")
    # 注意：使用 socketio.run 代替 app.run
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True, debug=True)
"""

# 2. 新的 layout.html 内容 (加入了聊天室 UI 和 JS)
layout_code = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} | 个人宇宙</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <!-- 引入 SocketIO 客户端库 -->
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
        <div id="chat-messages" class="tech-font">
            <div class="sys-msg">--- 已连接到个人宇宙 ---</div>
        </div>
        <div class="chat-input-area">
            <input type="text" id="msg-input" placeholder="输入消息..." onkeypress="handleKey(event)">
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
            console.log('Connected to server');
        });

        socket.on('receive_message', function(data) {
            var msgs = document.getElementById('chat-messages');
            var div = document.createElement('div');
            div.className = 'msg-item';
            // 简单的防 XSS
            div.textContent = "> Guest: " + data.msg; 
            msgs.appendChild(div);
            msgs.scrollTop = msgs.scrollHeight; // 自动滚动到底部
        });

        function sendMessage() {
            var input = document.getElementById('msg-input');
            var msg = input.value;
            if(msg.trim() !== "") {
                socket.emit('send_message', {message: msg});
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

# 3. 追加 CSS 样式
css_append = """

/* --- 聊天室样式 --- */
#chat-btn {
    position: fixed;
    top: 20px;
    right: 20px;
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
}
#chat-btn:hover {
    background: var(--accent-spirit);
    color: black;
    box-shadow: 0 0 15px var(--accent-spirit);
}

#chat-box {
    position: fixed;
    top: 60px;
    right: 20px;
    width: 300px;
    height: 400px;
    background: rgba(15, 17, 26, 0.95); /* 半透明黑 */
    border: 1px solid var(--accent-logic);
    border-radius: 4px;
    z-index: 999;
    display: flex;
    flex-direction: column;
    box-shadow: 0 5px 20px rgba(0,0,0,0.8);
    backdrop-filter: blur(5px); /* 磨砂玻璃效果 */
}

.hidden { display: none !important; }

.chat-header {
    background: rgba(26, 28, 37, 0.9);
    padding: 10px;
    border-bottom: 1px solid #333;
    font-size: 0.8rem;
    color: var(--accent-logic);
}

#chat-messages {
    flex: 1;
    padding: 10px;
    overflow-y: auto;
    font-size: 0.85rem;
    color: #ddd;
}

.sys-msg { color: #555; font-style: italic; margin-bottom: 5px; }
.msg-item { margin-bottom: 6px; word-wrap: break-word; }

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

def update_files():
    # 写入 app.py
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_code.strip())
    print("[OK] app.py 已更新")

    # 写入 templates/layout.html
    with open('templates/layout.html', 'w', encoding='utf-8') as f:
        f.write(layout_code.strip())
    print("[OK] layout.html 已更新")

    # 追加写入 static/style.css
    css_path = 'static/style.css'
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "/* --- 聊天室样式 --- */" not in content:
        with open(css_path, 'a', encoding='utf-8') as f:
            f.write(css_append)
        print("[OK] style.css 已更新")
    else:
        print("[SKIP] style.css 似乎已经包含聊天室样式")

if __name__ == "__main__":
    update_files()
    print("-" * 30)
    print("升级完成！请运行 python3 app.py 启动")