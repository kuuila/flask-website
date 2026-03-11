import os

# 1. 更新 templates/post_html.html (增加分享栏)
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
        
        <!-- 新增：社交分享栏 -->
        <div class="share-bar tech-font">
            <span style="opacity:0.6; margin-right:10px;">[传播信号] ::</span>
            <a href="javascript:void(0)" onclick="shareTo('wechat')" class="share-btn">WeChat</a>
            <a href="javascript:void(0)" onclick="shareTo('weibo')" class="share-btn">Weibo</a>
            <a href="javascript:void(0)" onclick="shareTo('twitter')" class="share-btn">X / Twitter</a>
            <a href="javascript:void(0)" onclick="copyLink()" class="share-btn">Copy Link</a>
        </div>
        <!-- 微信二维码弹窗 (默认隐藏) -->
        <div id="wx-qr-modal" class="hidden" style="margin-top:15px; text-align:center;">
            <p style="font-size:0.8rem; color:#888;">扫描二维码分享到微信</p>
            <img id="qr-img" src="" style="width:150px; border: 5px solid white;">
        </div>

    </header>
    
    <div style="font-size: 1.1rem; min-height: 200px; line-height: 1.8;">
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

<script>
    // 分享逻辑
    function shareTo(platform) {
        var url = encodeURIComponent(window.location.href);
        var title = encodeURIComponent("{{ post.title }} | 个人宇宙");
        var targetUrl = "";

        if (platform === 'weibo') {
            targetUrl = "http://service.weibo.com/share/share.php?url=" + url + "&title=" + title;
            window.open(targetUrl, '_blank');
        } else if (platform === 'twitter') {
            targetUrl = "https://twitter.com/intent/tweet?text=" + title + "&url=" + url;
            window.open(targetUrl, '_blank');
        } else if (platform === 'wechat') {
            // 调用一个公开的二维码 API
            var qrApi = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=" + url;
            var modal = document.getElementById('wx-qr-modal');
            var img = document.getElementById('qr-img');
            
            if (modal.classList.contains('hidden')) {
                img.src = qrApi;
                modal.classList.remove('hidden');
            } else {
                modal.classList.add('hidden');
            }
        }
    }

    function copyLink() {
        var dummy = document.createElement('input'),
        text = window.location.href;
        document.body.appendChild(dummy);
        dummy.value = text;
        dummy.select();
        document.execCommand('copy');
        document.body.removeChild(dummy);
        alert('链接已复制到剪贴板，请手动分享。');
    }
</script>
{% endblock %}
"""

# 2. 全新重写的 style.css (重点修复响应式和聊天室)
# 注意：这里我们重写整个 CSS 文件以确保覆盖顺序正确
css_full_content = """
:root {
    --bg-color: #0f111a;
    --text-color: #c0c5ce;
    --accent-logic: #82aaff;
    --accent-spirit: #ffcb6b;
    --accent-life: #c3e88d;
    --accent-senses: #f07178;
    --nav-bg: #1a1c25;
}

body {
    background-color: var(--bg-color);
    color: var(--text-color);
    font-family: 'Georgia', serif;
    margin: 0;
    line-height: 1.6;
    /* 防止iOS横向滚动 */
    overflow-x: hidden; 
}

code, pre, .tech-font { font-family: 'Consolas', 'Monaco', monospace; }

a { text-decoration: none; color: inherit; transition: 0.3s; }
a:hover { color: white; }

/* 导航栏 */
nav {
    background: var(--nav-bg);
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #333;
    flex-wrap: wrap; /* 允许换行 */
}
.logo { font-size: 1.5rem; font-weight: bold; letter-spacing: 2px; }
.menu { display: flex; gap: 20px; flex-wrap: wrap; }
.menu-item { font-size: 0.9rem; opacity: 0.8; }
.menu-item:hover { opacity: 1; text-shadow: 0 0 8px rgba(255,255,255,0.3); }

/* 分类颜色 */
.cat-logic { color: var(--accent-logic); }
.cat-spirit { color: var(--accent-spirit); }
.cat-senses { color: var(--accent-senses); }
.cat-life { color: var(--accent-life); }

/* 主容器响应式 */
.container { 
    max-width: 900px; 
    margin: 0 auto; 
    padding: 40px 20px; 
}

/* 首页网格 */
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
    margin-top: 40px;
}
.card {
    background: #1f222e;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #333;
    transition: transform 0.2s;
}
.card:hover { transform: translateY(-5px); border-color: #555; }
.card h3 { margin-top: 0; font-size: 1.2rem; }
.meta { font-size: 0.8rem; opacity: 0.6; margin-bottom: 10px; display: block; }
.tag { 
    display: inline-block; padding: 2px 8px; border-radius: 4px; 
    font-size: 0.75rem; background: #333; margin-right: 5px;
}

/* 文章详情 */
.post-content { background: #1f222e; padding: 40px; border-radius: 8px; }
.post-header { margin-bottom: 30px; border-bottom: 1px solid #333; padding-bottom: 20px; }

/* 分享栏 */
.share-bar { margin-top: 15px; font-size: 0.85rem; }
.share-btn {
    border: 1px solid #444; padding: 2px 8px; margin-right: 5px; border-radius: 2px;
    background: #0f111a; color: #888;
}
.share-btn:hover { border-color: var(--accent-logic); color: var(--accent-logic); }

/* 评论区 */
.comment-section { max-width: 900px; margin: 40px auto 0; padding: 0 20px; }
.comment-list { margin-bottom: 40px; }
.comment-item {
    background: #15171f; border-left: 3px solid #333; padding: 15px; margin-bottom: 15px;
    transition: 0.2s;
}
.comment-item:hover { border-left-color: var(--accent-spirit); background: #1a1c25; }
.comment-meta { font-size: 0.8rem; color: #666; margin-bottom: 5px; display: flex; justify-content: space-between; }
.c-user { color: var(--accent-logic); font-weight: bold; }
.comment-body { font-size: 0.95rem; line-height: 1.5; color: #ccc; word-wrap: break-word; }

.comment-form { background: #1f222e; padding: 20px; border-radius: 8px; border: 1px solid #333; }
.form-group { margin-bottom: 15px; }
.comment-form input, .comment-form textarea {
    width: 100%; background: #0f111a; border: 1px solid #444; color: white;
    padding: 10px; box-sizing: border-box; font-family: 'Consolas', monospace; outline: none;
}
.comment-form input:focus, .comment-form textarea:focus { border-color: var(--accent-spirit); }
.comment-form textarea { height: 80px; resize: vertical; }
.comment-form button {
    background: var(--accent-logic); color: black; border: none; padding: 10px 20px;
    cursor: pointer; font-weight: bold; font-family: 'Consolas', monospace;
}

/* --- 聊天室核心样式 (PC默认) --- */
#chat-btn {
    position: fixed; top: 110px; left: 20px;
    background: var(--nav-bg); border: 1px solid var(--accent-spirit); color: var(--accent-spirit);
    padding: 8px 15px; cursor: pointer; border-radius: 4px; z-index: 1000;
    font-family: 'Consolas', monospace; font-size: 0.9rem;
    box-shadow: 0 0 10px rgba(0,0,0,0.5);
}
#chat-box {
    position: fixed; top: 160px; left: 20px;
    width: 320px; height: 400px;
    background: rgba(15, 17, 26, 0.95);
    border: 1px solid var(--accent-logic); border-radius: 4px;
    z-index: 2000; display: flex; flex-direction: column;
    box-shadow: 5px 5px 20px rgba(0,0,0,0.8);
    backdrop-filter: blur(5px);
}
.hidden { display: none !important; }
.chat-header { background: rgba(26, 28, 37, 0.9); padding: 10px; border-bottom: 1px solid #333; font-size: 0.8rem; color: var(--accent-logic); }
.chat-settings { padding: 5px 10px; background: #15171f; border-bottom: 1px solid #333; display: flex; align-items: center; font-size: 0.8rem; }
.chat-settings input { background: #0f111a; border: 1px solid #333; color: #ffcb6b; padding: 2px 5px; margin-left: 10px; width: 120px; outline: none; font-family: monospace; }
#chat-messages { flex: 1; padding: 10px; overflow-y: auto; font-size: 0.85rem; color: #ddd; }
.chat-input-area { display: flex; border-top: 1px solid #333; min-height: 45px; }
.chat-input-area input { flex: 1; background: transparent; border: none; color: white; padding: 10px; outline: none; font-size: 14px; }
.chat-input-area button { background: var(--accent-logic); border: none; color: black; padding: 0 15px; cursor: pointer; font-weight: bold; }

/* --- 移动端与平板 响应式适配 --- */
@media (max-width: 768px) {
    /* 导航栏调整 */
    nav { padding: 1rem; flex-direction: column; gap: 10px; }
    .menu { gap: 10px; justify-content: center; width: 100%; }
    
    /* 容器调整 */
    .container { padding: 20px 15px; }
    .post-content { padding: 20px; }
    
    /* 聊天室按钮位置调整 (放到底部或悬浮右下，避免挡住Logo) */
    #chat-btn {
        top: auto; bottom: 20px; right: 20px; left: auto;
        background: rgba(26,28,37, 0.9);
        border-color: var(--accent-logic);
        color: var(--accent-logic);
    }

    /* 聊天室移动端全屏模式 (关键修复) */
    #chat-box {
        top: 0; left: 0; bottom: 0; right: 0;
        width: 100%; height: 100%; /* 全屏覆盖 */
        border: none; border-radius: 0;
        background: #0f111a; /* 不透明，避免视觉干扰 */
    }
    
    .chat-header { padding: 15px; font-size: 1rem; display: flex; justify-content: space-between; }
    /* 增大关闭按钮点击区域 */
    .chat-header span[onclick] { padding: 0 10px; font-size: 1.2rem; }
    
    /* 增大输入框文字，防止iOS自动缩放 (iOS < 16px 会zoom) */
    .chat-input-area input { font-size: 16px !important; }
    
    /* 调整输入区域高度，适应手指 */
    .chat-input-area { min-height: 55px; }
    
    /* 确保消息区域可滚动且不被键盘完全遮挡 */
    #chat-messages { -webkit-overflow-scrolling: touch; }
}
"""

def update_files():
    # 1. 更新 post_html.html
    with open('templates/post_html.html', 'w', encoding='utf-8') as f:
        f.write(post_html_code.strip())
    print("[OK] post_html.html 已更新 (增加分享栏)")

    # 2. 重写 style.css
    with open('static/style.css', 'w', encoding='utf-8') as f:
        f.write(css_full_content.strip())
    print("[OK] style.css 已全面重构 (移动端适配 + 聊天室修复)")

if __name__ == "__main__":
    update_files()
    print("-" * 30)
    print("V4.0 更新完成！")
    print("1. 增加文章分享功能")
    print("2. 移动端聊天室改为全屏沉浸式，修复输入框跳动问题")
    print("3. 全站 CSS 响应式适配")
    print("请重启服务: python3 app.py")