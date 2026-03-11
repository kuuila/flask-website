import os

# 1. 更新 templates/layout.html 
# (我们需要把之前的 搜索、聊天、统计 全都保留，并加入 功德箱)
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
        <div class="logo tech-font"><a href="/">Shine Shanni Film STUDIO</a></div>
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
        <!-- 功德箱 (新增) -->
        <div id="donate-btn" onclick="toggleDonate()">
            🧧 功德箱
        </div>
        <!-- 搜索按钮 -->
        <div id="search-btn" onclick="toggleSearch()">
            🔍 检索
        </div>
        <!-- 聊天按钮 -->
        <div id="chat-btn" onclick="toggleChat()">
            💬 匿名连接
        </div>
    </div>

    <!-- 功德箱弹窗 (新增) -->
    <div id="donate-overlay" class="hidden">
        <div class="donate-container">
            <div class="donate-header tech-font">
                <span>> CYBER_MERIT_BOX (电子功德)</span>
                <span style="cursor:pointer; float:right; font-size:1.5rem;" onclick="toggleDonate()">[ × ]</span>
            </div>
            
            <div class="donate-intro tech-font">
                <p>“施主，服务器也是要吃电费的。每一次扫码，都是一次量子纠缠的善缘。”</p>
                <p style="font-size:0.8rem; opacity:0.6;">(请选择你想要供养的那个灵魂分身)</p>
            </div>

            <!-- 收款码网格 -->
            <div class="qr-grid">
                
                <!-- 朋友 A: 程序员 -->
                <div class="qr-card">
                    <div class="qr-img-box">
                        <!-- 这里放图片，暂时用占位符 -->
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=AliPay_Code_Here" alt="收款码">
                    </div>
                    <div class="qr-title cat-logic">秃头程序员</div>
                    <div class="qr-desc">
                        “这哥们昨晚修 Bug 修到凌晨四点。赏杯咖啡，防止他写出死循环。”
                    </div>
                </div>

                <!-- 朋友 B: 风水师 -->
                <div class="qr-card">
                    <div class="qr-img-box">
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=WeChat_Pay_Here" alt="收款码">
                    </div>
                    <div class="qr-title cat-spirit">赛博道士</div>
                    <div class="qr-desc">
                        “随喜功德。此款项将用于购买电子香火，为您在服务器后台祈福挡煞。”
                    </div>
                </div>

                <!-- 朋友 C: 艺术家 -->
                <div class="qr-card">
                    <div class="qr-img-box">
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=Art_Fund_Here" alt="收款码">
                    </div>
                    <div class="qr-title cat-senses">饥饿艺术家</div>
                    <div class="qr-desc">
                        “颜料很贵，灵感很费。助养一位艺术家，让他继续在虚空中画大饼。”
                    </div>
                </div>

                <!-- 朋友 D: 猫/宠物 -->
                <div class="qr-card">
                    <div class="qr-img-box">
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=Cat_Food_Here" alt="收款码">
                    </div>
                    <div class="qr-title cat-life">护法神兽(猫)</div>
                    <div class="qr-desc">
                        “喵。（翻译：冻干吃完了。再不打钱，我就要去拔服务器网线了。）”
                    </div>
                </div>

            </div>
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
            <div id="search-results" class="tech-font"></div>
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
        <div id="chat-messages" class="tech-font"><div class="sys-msg">--- 链路已接通 ---</div></div>
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
        // --- 功德箱逻辑 ---
        function toggleDonate() {
            var overlay = document.getElementById('donate-overlay');
            overlay.classList.toggle('hidden');
        }

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
            if (nick.length < 4 || nick.length > 16) { if (nick !== "***") { alert("昵称长度限制 4-16 位"); return; } }
            if(msg.trim() !== "") { socket.emit('send_message', { message: msg, nickname: nick }); input.value = ""; }
        }
        function toggleChat() { chatBox.classList.toggle('hidden'); }
        function handleKey(e) { if(e.keyCode === 13) sendMessage(); }

        // --- 搜索逻辑 ---
        var searchOverlay = document.getElementById('search-overlay');
        var searchInput = document.getElementById('search-input');
        var resultsBox = document.getElementById('search-results');
        function toggleSearch() {
            searchOverlay.classList.toggle('hidden');
            if (!searchOverlay.classList.contains('hidden')) { searchInput.focus(); }
        }
        searchInput.addEventListener('input', function() {
            var query = this.value.trim();
            if (query.length < 1) { resultsBox.innerHTML = ""; return; }
            fetch('/api/search?q=' + encodeURIComponent(query))
                .then(response => response.json())
                .then(data => {
                    resultsBox.innerHTML = "";
                    if (data.length === 0) { resultsBox.innerHTML = "<div style='padding:20px; opacity:0.5;'>[虚空] 未探测到相关信号...</div>"; } 
                    else {
                        data.forEach(item => {
                            var div = document.createElement('div');
                            div.className = 'search-item';
                            div.innerHTML = `<a href="/post/${item.id}"><div class="s-title">${item.title}</div><div class="s-meta">${item.date} | ${item.category}</div><div class="s-summary">${item.summary}</div></a>`;
                            resultsBox.appendChild(div);
                        });
                    }
                });
        });
    </script>
</body>
</html>
"""

# 2. 追加 CSS (功德箱样式)
css_append = """
/* --- 功德箱按钮 --- */
#donate-btn {
    position: relative;
    background: #4a0d0d; /* 暗红色底 */
    border: 1px solid #ffcb6b; /* 金色边框 */
    color: #ffcb6b;
    padding: 10px 15px;
    cursor: pointer;
    border-radius: 4px;
    font-family: 'Consolas', monospace;
    box-shadow: 0 0 10px rgba(0,0,0,0.5);
    transition: 0.3s;
    text-align: center;
    min-width: 100px;
}
#donate-btn:hover {
    background: #ffcb6b;
    color: #4a0d0d;
    box-shadow: 0 0 20px #ffcb6b; /* 金光闪闪 */
}

/* --- 功德箱弹窗 --- */
#donate-overlay {
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(15, 17, 26, 0.98); /* 几乎不透明的黑 */
    z-index: 3000;
    backdrop-filter: blur(5px);
    display: flex;
    justify-content: center;
    align-items: center; /* 垂直居中 */
    padding: 20px;
    box-sizing: border-box;
}

.donate-container {
    width: 100%;
    max-width: 800px;
    background: #1a1c25;
    border: 2px solid var(--accent-spirit); /* 金色边框 */
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 0 30px rgba(0,0,0,0.8);
    max-height: 90vh;
    overflow-y: auto;
}

.donate-header {
    color: var(--accent-spirit);
    font-size: 1.2rem;
    margin-bottom: 20px;
    border-bottom: 1px dashed #555;
    padding-bottom: 10px;
}

.donate-intro {
    text-align: center;
    margin-bottom: 30px;
    color: #ddd;
    font-style: italic;
}

/* --- 二维码网格 --- */
.qr-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); /* 响应式网格 */
    gap: 20px;
}

.qr-card {
    background: #0f111a;
    border: 1px solid #333;
    padding: 15px;
    border-radius: 8px;
    text-align: center;
    transition: 0.3s;
}
.qr-card:hover {
    border-color: var(--accent-spirit);
    transform: translateY(-5px);
}

.qr-img-box img {
    width: 100%;
    max-width: 150px;
    border-radius: 4px;
    border: 2px solid white;
}

.qr-title {
    margin-top: 10px;
    font-weight: bold;
    font-family: 'Consolas', monospace;
    font-size: 1rem;
}

.qr-desc {
    margin-top: 8px;
    font-size: 0.8rem;
    color: #888;
    line-height: 1.4;
}
"""

def update_v9_donate():
    # 1. 重写 layout.html
    with open('templates/layout.html', 'w', encoding='utf-8') as f:
        f.write(layout_code.strip())
    print("[OK] layout.html 已更新 (新增功德箱界面)")

    # 2. 追加 CSS
    css_path = 'static/style.css'
    with open(css_path, 'r', encoding='utf-8') as f:
        old_css = f.read()
    
    if "#donate-overlay" not in old_css:
        with open(css_path, 'a', encoding='utf-8') as f:
            f.write(css_append)
        print("[OK] style.css 已更新 (功德箱样式)")
    else:
        print("[SKIP] CSS 似乎已经包含功德箱样式")

if __name__ == "__main__":
    update_v9_donate()
    print("-" * 30)
    print("V9.0 功德箱上线！")
    print("---------------------------------")
    print("注意：目前的二维码是示例图片。")
    print("请将你朋友的收款码截图，保存为图片。")
    print("然后修改 templates/layout.html 中的 img src 地址。")
    print("例如：<img src='/static/qr_code_1.jpg'>")
    print("---------------------------------")
    print("请重启服务: python3 app.py")