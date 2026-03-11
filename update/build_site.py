import os
import sys

# 定义项目结构和文件内容
project_name = "personal_universe"

# CSS 样式：赛博禅意风格 (Cyber-Zen)
css_content = """
:root {
    --bg-color: #0f111a; /* 深邃黑 */
    --text-color: #c0c5ce; /* 雾灰 */
    --accent-logic: #82aaff; /* C++ 蓝 */
    --accent-spirit: #ffcb6b; /* 玄学金 */
    --accent-life: #c3e88d; /* 生命绿 */
    --accent-senses: #f07178; /* 审美红 */
    --nav-bg: #1a1c25;
}

body {
    background-color: var(--bg-color);
    color: var(--text-color);
    font-family: 'Georgia', serif; /* 默认衬线体，适合文学与玄学 */
    margin: 0;
    line-height: 1.6;
}

code, pre, .tech-font {
    font-family: 'Consolas', 'Monaco', monospace; /* 代码体 */
}

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
}
.logo { font-size: 1.5rem; font-weight: bold; letter-spacing: 2px; }
.menu { display: flex; gap: 20px; }
.menu-item { font-size: 0.9rem; opacity: 0.8; }
.menu-item:hover { opacity: 1; text-shadow: 0 0 8px rgba(255,255,255,0.3); }

/* 分类颜色类 */
.cat-logic { color: var(--accent-logic); }
.cat-spirit { color: var(--accent-spirit); }
.cat-senses { color: var(--accent-senses); }
.cat-life { color: var(--accent-life); }

/* 主容器 */
.container { max-width: 900px; margin: 0 auto; padding: 40px 20px; }

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
    display: inline-block; 
    padding: 2px 8px; 
    border-radius: 4px; 
    font-size: 0.75rem; 
    background: #333; 
    margin-right: 5px;
}

/* 文章详情 */
.post-content { background: #1f222e; padding: 40px; border-radius: 8px; }
.post-header { margin-bottom: 30px; border-bottom: 1px solid #333; padding-bottom: 20px; }
"""

# HTML 模板：基础骨架
layout_html = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} | 个人宇宙</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
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

    <footer style="text-align:center; padding: 40px; opacity: 0.5; font-size: 0.8rem;">
        <p class="tech-font">System.exit(0); // Constructed by You</p>
    </footer>
</body>
</html>
"""

# HTML 模板：首页
index_html = """
{% extends 'layout.html' %}

{% block content %}
<div style="text-align: center; margin-bottom: 60px;">
    <h1>万物归一</h1>
    <p style="opacity: 0.8;">“用 C++ 构筑逻辑，用玄术解构命运，用音乐抚慰灵魂。”</p>
</div>

<h2 class="tech-font">> 最新收录</h2>
<div class="grid">
    {% for post in posts %}
    <a href="{{ url_for('post_detail', post_id=post.id) }}" class="card">
        <span class="meta tech-font">{{ post.created_at.strftime('%Y-%m-%d') }} | {{ post.category }}</span>
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
{% endblock %}
"""

# HTML 模板：文章详情
post_html = """
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
    
    <div style="font-size: 1.1rem;">
        {{ post.content | safe }}
    </div>

    <div style="margin-top: 40px; padding-top: 20px; border-top: 1px dashed #444;">
        <a href="/" class="tech-font"><< 返回首页</a>
    </div>
</article>
{% endblock %}
"""

# Python 应用主程序
app_py_content = """
from flask import Flask, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///universe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-key-for-my-universe'

db = SQLAlchemy(app)

# --- 数据库模型 ---
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50)) # logic, spirit, senses, life
    content = db.Column(db.Text)
    summary = db.Column(db.String(200))
    tags = db.Column(db.String(100)) # 逗号分隔
    created_at = db.Column(db.DateTime, default=datetime.now)

    @property
    def css_class(self):
        mapping = {
            'logic': 'cat-logic',
            'spirit': 'cat-spirit',
            'senses': 'cat-senses',
            'life': 'cat-life'
        }
        return mapping.get(self.category, '')

# --- 初始化数据 (首次运行自动创建) ---
def init_db():
    with app.app_context():
        db.create_all()
        if Post.query.count() == 0:
            print("正在生成初始测试数据...")
            data = [
                Post(
                    title="C++ 内存管理与道的虚实",
                    category="logic",
                    summary="探讨指针的释放与道家'无'的境界，内存泄漏即是杂念。",
                    content="<p>在编写 C++ 析构函数时，我们常常思考资源的生命周期。这与修行的过程何其相似...</p><pre><code>delete ptr; // 回归虚无</code></pre>",
                    tags="C++,修行,哲学"
                ),
                Post(
                    title="论风水中的'气'与环境心理学",
                    category="spirit",
                    summary="卧室布局如何影响睡眠质量？古老的风水智慧其实是早期的心理暗示学。",
                    content="<p>青龙白虎，实则是对空间压迫感的一种形象化描述。当床头悬空，人的潜意识...</p>",
                    tags="风水,心理学,中医"
                ),
                Post(
                    title="Leica M10：捕捉光影下的少女",
                    category="senses",
                    summary="人像摄影不仅是记录，更是捕捉那一瞬间的情绪流动。",
                    content="<p>少女的回眸，配合 35mm 的人文视角，背景的虚化恰到好处...</p>",
                    tags="摄影,少女,美学"
                ),
                Post(
                    title="深夜代码后的钢琴独奏",
                    category="senses",
                    summary="Debug 结束，手指从键盘移向琴键。肖邦的夜曲是最好的抚慰。",
                    content="<p>（这里可以放置你的音频播放器）<br>当 C++ 的逻辑世界崩塌时，音乐重建了我的秩序。</p>",
                    tags="音乐,乐器,C++"
                ),
                Post(
                    title="给上帝的一封信：关于命运",
                    category="spirit",
                    summary="基督信仰与东方玄学的冲突与共融。",
                    content="<p>如果上帝掷骰子，那么易经是否就是那颗骰子的说明书？</p>",
                    tags="基督,玄术,写作"
                ),
            ]
            db.session.add_all(data)
            db.session.commit()
            print("测试数据生成完毕。")

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
    # 检查数据库是否存在，不存在则初始化
    if not os.path.exists('universe.db'):
        init_db()
    
    print("启动服务器... 请在浏览器访问 http://127.0.0.1:5000")
    app.run(debug=True)
"""

requirements_txt = """
Flask==2.3.2
Flask-SQLAlchemy==3.0.3
"""

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"[OK] 已创建: {path}")

def main():
    base_dir = "."
    
    # 1. 创建目录和文件
    create_file(os.path.join(base_dir, "app.py"), app_py_content)
    create_file(os.path.join(base_dir, "requirements.txt"), requirements_txt)
    create_file(os.path.join(base_dir, "static", "style.css"), css_content)
    create_file(os.path.join(base_dir, "templates", "layout.html"), layout_html)
    create_file(os.path.join(base_dir, "templates", "index.html"), index_html)
    create_file(os.path.join(base_dir, "templates", "post_html.html"), post_html)
    
    print("-" * 50)
    print("项目文件已全部生成！")
    print("-" * 50)
    print("请按照以下步骤运行：")
    print("1. 安装依赖: pip install -r requirements.txt")
    print("2. 运行网站: python app.py")
    print("-" * 50)

if __name__ == "__main__":
    main()