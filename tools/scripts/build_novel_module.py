import os

def build_novel_module():
    print("正在构建【闪泥书架】模块...")

    # ========================================================
    # 1. 更新 models.py (添加书和章节模型)
    # ========================================================
    # 读取原文件
    if not os.path.exists('models.py'):
        print("❌ 错误：找不到 models.py")
        return
        
    with open('models.py', 'r', encoding='utf-8') as f:
        models_content = f.read()
    
    # 定义新模型
    new_models = """
# --- [新增] 小说模块模型 ---
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(50), default="闪泥")
    summary = db.Column(db.String(500))
    cover_color = db.Column(db.String(20), default="#4a0d0d") # 封面色调
    created_at = db.Column(db.DateTime, default=datetime.now)
    # 关联章节
    chapters = db.relationship('Chapter', backref='book', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return self.title

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    # 排序权重 (可选，默认按ID排序)
    rank = db.Column(db.Integer, default=0) 
"""
    
    if "class Book(db.Model)" not in models_content:
        with open('models.py', 'a', encoding='utf-8') as f:
            f.write(new_models)
        print("[OK] models.py 已更新 (添加 Book/Chapter)")
    else:
        print("[SKIP] models.py 已包含小说模型")

    # ========================================================
    # 2. 创建 novel_backend.py (后端逻辑)
    # ========================================================
    novel_backend_code = """
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from extensions import db
from models import Book, Chapter

novel_bp = Blueprint('novel', __name__, url_prefix='/novel')

# 1. 书架首页 (列出所有书)
@novel_bp.route('/')
def shelf():
    books = Book.query.order_by(Book.created_at.desc()).all()
    return render_template('novel/shelf.html', books=books, title="闪泥书架")

# 2. 书籍目录页
@novel_bp.route('/book/<int:book_id>')
def toc(book_id):
    book = Book.query.get_or_404(book_id)
    # 按 rank 排序，如果 rank 相同按 id 排序
    chapters = Chapter.query.filter_by(book_id=book_id).order_by(Chapter.rank.asc(), Chapter.id.asc()).all()
    return render_template('novel/toc.html', book=book, chapters=chapters, title=book.title)

# 3. 章节阅读页
@novel_bp.route('/chapter/<int:chapter_id>')
def reader(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    
    # 增加阅读量
    chapter.views += 1
    db.session.commit()
    
    book = chapter.book
    
    # 计算上一章/下一章
    # 逻辑：在同本书里，找比当前排序大/小的章节
    # 简单起见，这里假设按 ID 排序 (你也可以改为按 rank)
    prev_chap = Chapter.query.filter_by(book_id=book.id).filter(Chapter.id < chapter.id).order_by(Chapter.id.desc()).first()
    next_chap = Chapter.query.filter_by(book_id=book.id).filter(Chapter.id > chapter.id).order_by(Chapter.id.asc()).first()
    
    return render_template('novel/reader.html', 
                           chapter=chapter, 
                           book=book, 
                           prev_chap=prev_chap, 
                           next_chap=next_chap,
                           title=chapter.title)
"""
    with open('novel_backend.py', 'w', encoding='utf-8') as f:
        f.write(novel_backend_code.strip())
    print("[OK] novel_backend.py 已创建")

    # ========================================================
    # 3. 更新 admin_backend.py (后台管理)
    # ========================================================
    with open('admin_backend.py', 'r', encoding='utf-8') as f:
        admin_content = f.read()

    # 引入新模型
    if "from models import Post" in admin_content:
        admin_content = admin_content.replace(
            "from models import Post", 
            "from models import Book, Chapter, Post" # 确保引入
        )

    # 定义管理视图
    new_admin_views = """
class BookAdmin(SecureModelView):
    column_list = ('title', 'author', 'created_at')
    column_searchable_list = ['title']
    form_columns = ('title', 'author', 'summary', 'cover_color')

class ChapterAdmin(SecureModelView):
    column_list = ('book', 'title', 'views', 'created_at')
    column_searchable_list = ['title']
    column_filters = ['book.title']
    form_columns = ('book', 'title', 'content', 'rank')
    form_widget_args = {
        'content': {
            'rows': 20,
            'style': 'font-family: "Consolas", monospace; font-size: 14px; background:#f4f4f4;'
        }
    }
"""
    # 注册视图
    new_registrations = """
    # 小说管理
    admin.add_view(BookAdmin(Book, db.session, name='小说书架', category='文学模块'))
    admin.add_view(ChapterAdmin(Chapter, db.session, name='章节管理', category='文学模块'))
"""

    if "class BookAdmin" not in admin_content:
        # 插入类定义 (在 init_admin 之前)
        target_loc = "def init_admin(app):"
        admin_content = admin_content.replace(target_loc, new_admin_views + "\n" + target_loc)
        
        # 插入注册代码 (在函数内部)
        # 找一个现有的 add_view 作为锚点
        anchor = "admin.add_view(SecureModelView(Post, db.session, name='文章管理'))"
        admin_content = admin_content.replace(anchor, anchor + new_registrations)
        
        with open('admin_backend.py', 'w', encoding='utf-8') as f:
            f.write(admin_content)
        print("[OK] admin_backend.py 已更新")
    else:
        print("[SKIP] admin_backend.py 已包含小说管理")

    # ========================================================
    # 4. 更新 app.py (注册蓝图)
    # ========================================================
    # with open('app.py', 'r', encoding='utf-8') as f:
    #     app_content = f.read()
    
    # if "from novel_backend import novel_bp" not in app_content:
    #     # 导入
    #     app_content = app_content.replace("from rose_backend import rose_bp", "from rose_backend import rose_bp\nfrom novel_backend import novel_bp")
    #     # 注册
    #     app_content = app_content.replace("app.register_blueprint(rose_bp)", "app.register_blueprint(rose_bp)\napp.register_blueprint(novel_bp)")
        
    #     with open('app.py', 'w', encoding='utf-8') as f:
    #         f.write(app_content)
    #     print("[OK] app.py 已更新 (注册 novel_bp)")

    # ========================================================
    # 5. 创建前端模板 (Templates)
    # ========================================================
    os.makedirs('templates/novel', exist_ok=True)

    # 5.1 书架页 (shelf.html)
    shelf_html = """
{% extends 'layout.html' %}
{% block content %}
<div style="text-align: center; margin-bottom: 40px;">
    <h1 class="tech-font" style="color:var(--accent-life)">FLASH MUD SHELF</h1>
    <p style="opacity: 0.6;">“现实太无聊，不如读点爽文。”</p>
</div>

<div class="grid">
    {% for book in books %}
    <a href="{{ url_for('novel.toc', book_id=book.id) }}" class="card" style="border-left: 5px solid {{ book.cover_color }};">
        <h3 style="color:{{ book.cover_color }}">{{ book.title }}</h3>
        <div class="meta tech-font">Author: {{ book.author }} | {{ book.chapters|length }} Chapters</div>
        <p style="font-size: 0.9rem; opacity: 0.8; margin-top:10px;">{{ book.summary }}</p>
    </a>
    {% else %}
    <div style="text-align:center; width:100%; opacity:0.5;">书架空空如也...</div>
    {% endfor %}
</div>
{% endblock %}
"""
    with open('templates/novel/shelf.html', 'w', encoding='utf-8') as f: f.write(shelf_html)

    # 5.2 目录页 (toc.html)
    toc_html = """
{% extends 'layout.html' %}
{% block content %}
<div class="post-content">
    <div style="border-bottom:1px solid #333; padding-bottom:20px; margin-bottom:20px; text-align:center;">
        <h1 style="color:{{ book.cover_color }}; margin-bottom:5px;">{{ book.title }}</h1>
        <div class="meta tech-font">作者: {{ book.author }}</div>
        <p style="margin-top:15px; color:#ccc;">{{ book.summary }}</p>
    </div>

    <h3 class="tech-font">> 目录索引</h3>
    <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap:10px;">
        {% for chapter in chapters %}
        <a href="{{ url_for('novel.reader', chapter_id=chapter.id) }}" 
           style="background:rgba(255,255,255,0.05); padding:10px; border-radius:4px; display:flex; justify-content:space-between; transition:0.2s;"
           onmouseover="this.style.background='rgba(255,255,255,0.1)'" 
           onmouseout="this.style.background='rgba(255,255,255,0.05)'">
            <span>{{ chapter.title }}</span>
            <span style="font-size:0.7rem; opacity:0.5; align-self:center;">👁 {{ chapter.views }}</span>
        </a>
        {% endfor %}
    </div>
</div>
<div style="text-align:center; margin-top:20px;">
    <a href="{{ url_for('novel.shelf') }}" class="tech-font"><< 返回书架</a>
</div>
{% endblock %}
"""
    with open('templates/novel/toc.html', 'w', encoding='utf-8') as f: f.write(toc_html)

    # 5.3 阅读页 (reader.html)
    reader_html = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} | {{ book.title }}</title>
    <style>
        body { background: #111; color: #ccc; font-family: 'Georgia', serif; line-height: 1.8; margin: 0; padding: 0; }
        .reader-container { max-width: 800px; margin: 0 auto; padding: 20px 20px 60px 20px; font-size: 1.2rem; }
        h1 { color: #82aaff; font-size: 1.5rem; border-bottom: 1px dashed #333; padding-bottom: 15px; margin-bottom: 30px; }
        .nav-bar { display: flex; justify-content: space-between; margin: 40px 0; padding-top: 20px; border-top: 1px solid #333; }
        a { color: #ffcb6b; text-decoration: none; padding: 10px 20px; border: 1px solid #333; border-radius: 4px; transition: 0.3s; }
        a:hover { background: #222; border-color: #ffcb6b; }
        .disabled { opacity: 0.3; pointer-events: none; border-color: transparent; }
        .back-btn { position:fixed; top:20px; left:20px; opacity:0.5; font-size:0.8rem; }
        p { margin-bottom: 1.5em; text-align: justify; }
        
        /* 护眼模式微调 */
        @media (max-width: 768px) {
            .reader-container { font-size: 1.1rem; padding: 15px; }
            .back-btn { position: relative; top: 0; left: 0; display: block; margin-bottom: 20px; text-align: center; }
        }
    </style>
</head>
<body>
    <div class="reader-container">
        <a href="{{ url_for('novel.toc', book_id=book.id) }}" class="back-btn">📚 回目录</a>
        
        <h1>{{ chapter.title }}</h1>
        
        <div class="content">
            <!-- 自动处理换行 -->
            {% for para in chapter.content.split('\\n') %}
            <p>{{ para }}</p>
            {% endfor %}
        </div>

        <div class="nav-bar">
            {% if prev_chap %}
            <a href="{{ url_for('novel.reader', chapter_id=prev_chap.id) }}">← 上一章</a>
            {% else %}
            <a class="disabled">无上一章</a>
            {% endif %}

            <a href="{{ url_for('novel.toc', book_id=book.id) }}">目录</a>

            {% if next_chap %}
            <a href="{{ url_for('novel.reader', chapter_id=next_chap.id) }}">下一章 →</a>
            {% else %}
            <a class="disabled">无下一章</a>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""
    with open('templates/novel/reader.html', 'w', encoding='utf-8') as f: f.write(reader_html)
    print("[OK] 前端模板 (shelf/toc/reader) 已创建")

    # ========================================================
    # 6. 更新 layout.html (添加悬浮按钮)
    # ========================================================
    with open('templates/layout.html', 'r', encoding='utf-8') as f:
        layout = f.read()
    
    # 在 id="float-btns" 里面添加按钮
    # 寻找一个锚点，比如 donate-btn
    if "novel.shelf" not in layout:
        btn_html = """
        <a href="{{ url_for('novel.shelf') }}" class="float-btn" style="border-color:#ffcb6b; color:#ffcb6b; text-decoration:none;">📚 闪泥书架</a>"""
        
        target = '<div id="float-btns">'
        layout = layout.replace(target, target + btn_html)
        
        with open('templates/layout.html', 'w', encoding='utf-8') as f:
            f.write(layout)
        print("[OK] layout.html 已更新 (添加书架悬浮按钮)")

    # ========================================================
    # 7. 数据库迁移脚本
    # ========================================================
    db_script = """
from app import app, db
with app.app_context():
    db.create_all()
    print("✅ 数据库表结构已更新 (Book, Chapter)")
"""
    with open('init_novel_db.py', 'w', encoding='utf-8') as f:
        f.write(db_script)

if __name__ == "__main__":
    build_novel_module()
    print("-" * 30)
    print("构建完成！请执行以下步骤：")
    print("1. 初始化数据库: python3 init_novel_db.py")
    print("2. 重启服务: python3 app.py")
    print("3. 进入后台 /admin -> '文学模块' 添加你的爽文！")