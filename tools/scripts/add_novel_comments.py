import os

def add_novel_comments():
    print("正在为【闪泥书架】添加评论系统...")

    # ========================================================
    # 1. 更新 models.py (添加 ChapterComment 模型)
    # ========================================================
    models_path = 'models.py'
    with open(models_path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_model_code = """
class ChapterComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    nickname = db.Column(db.String(50), default='书友')
    content = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
"""
    
    # 关联到 Chapter 模型
    # 我们需要找到 class Chapter... 并在里面添加 relationship
    if "class ChapterComment" not in content:
        # 1. 追加新模型定义
        content += new_model_code
        
        # 2. 在 Chapter 模型中添加反向关联
        if "class Chapter(db.Model):" in content:
            # 找到 Chapter 类的最后一行 (通常是 rank 定义)，在后面加一行
            target = "rank = db.Column(db.Integer, default=0)"
            injection = "    comments = db.relationship('ChapterComment', backref='chapter', lazy=True, cascade='all, delete-orphan')"
            content = content.replace(target, target + "\n" + injection)
            
        with open(models_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("[OK] models.py 已更新 (添加 ChapterComment)")
    else:
        print("[SKIP] models.py 已包含章节评论模型")

    # ========================================================
    # 2. 更新 novel_backend.py (添加评论处理逻辑)
    # ========================================================
    backend_path = 'novel_backend.py'
    
    # 我们直接重写 reader 路由部分，引入评论逻辑
    new_backend_code = """
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from extensions import db
from models import Book, Chapter, ChapterComment

novel_bp = Blueprint('novel', __name__, url_prefix='/novel')

# --- 辅助函数：评论清洗 (时间折叠) ---
def prune_chapter_comments(chapter_id):
    comments = ChapterComment.query.filter_by(chapter_id=chapter_id).order_by(ChapterComment.created_at.asc()).all()
    if len(comments) > 50:
        head_ids = [c.id for c in comments[:10]]
        tail_ids = [c.id for c in comments[-40:]]
        keep_ids = set(head_ids + tail_ids)
        for c in comments:
            if c.id not in keep_ids: db.session.delete(c)
        db.session.commit()

# 1. 书架首页
@novel_bp.route('/')
def shelf():
    books = Book.query.order_by(Book.created_at.desc()).all()
    return render_template('novel/shelf.html', books=books, title="闪泥书架")

# 2. 书籍目录页
@novel_bp.route('/book/<int:book_id>')
def toc(book_id):
    book = Book.query.get_or_404(book_id)
    chapters = Chapter.query.filter_by(book_id=book_id).order_by(Chapter.rank.asc(), Chapter.id.asc()).all()
    return render_template('novel/toc.html', book=book, chapters=chapters, title=book.title)

# 3. 章节阅读页 (含评论逻辑)
@novel_bp.route('/chapter/<int:chapter_id>', methods=['GET', 'POST'])
def reader(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    
    # POST: 提交评论
    if request.method == 'POST':
        nickname = request.form.get('nickname') or "书友"
        content = request.form.get('content')
        if content and content.strip():
            db.session.add(ChapterComment(chapter_id=chapter.id, nickname=nickname[:20], content=content[:500]))
            db.session.commit()
            prune_chapter_comments(chapter.id)
            # 防止表单重复提交，重定向回本页
            return redirect(url_for('novel.reader', chapter_id=chapter_id))

    # GET: 浏览
    if request.method == 'GET':
        chapter.views += 1
        db.session.commit()
    
    book = chapter.book
    prev_chap = Chapter.query.filter_by(book_id=book.id).filter(Chapter.id < chapter.id).order_by(Chapter.id.desc()).first()
    next_chap = Chapter.query.filter_by(book_id=book.id).filter(Chapter.id > chapter.id).order_by(Chapter.id.asc()).first()
    
    # 获取评论
    comments = ChapterComment.query.filter_by(chapter_id=chapter_id).order_by(ChapterComment.created_at.asc()).all()
    
    return render_template('novel/reader.html', 
                           chapter=chapter, 
                           book=book, 
                           prev_chap=prev_chap, 
                           next_chap=next_chap,
                           comments=comments,
                           title=chapter.title)
"""
    with open(backend_path, 'w', encoding='utf-8') as f:
        f.write(new_backend_code.strip())
    print("[OK] novel_backend.py 已更新 (增加评论逻辑)")

    # ========================================================
    # 3. 更新 admin_backend.py (后台管理)
    # ========================================================
    admin_path = 'admin_backend.py'
    with open(admin_path, 'r', encoding='utf-8') as f:
        admin_content = f.read()

    # 1. 导入模型
    if ", ChapterComment" not in admin_content:
        admin_content = admin_content.replace("from models import Book, Chapter, Post", "from models import Book, Chapter, ChapterComment, Post")

    # 2. 定义 Admin View
    new_admin_view = """
class ChapterCommentAdmin(SecureModelView):
    column_list = ('chapter.book.title', 'chapter.title', 'nickname', 'content', 'created_at')
    column_searchable_list = ['content', 'nickname']
    column_filters = ['chapter.book.title']
    column_labels = {'chapter.book.title':'书名', 'chapter.title':'章节', 'nickname':'书友', 'content':'内容'}
    can_create = False
"""
    # 3. 注册 View
    reg_code = "admin.add_view(ChapterCommentAdmin(ChapterComment, db.session, name='书评管理', category='文学模块'))"

    if "class ChapterCommentAdmin" not in admin_content:
        # 插入类定义
        target_loc = "def init_admin(app):"
        admin_content = admin_content.replace(target_loc, new_admin_view + "\n" + target_loc)
        
        # 插入注册
        target_reg = "name='章节管理', category='文学模块'))"
        admin_content = admin_content.replace(target_reg, target_reg + "\n    " + reg_code)
        
        with open(admin_path, 'w', encoding='utf-8') as f:
            f.write(admin_content)
        print("[OK] admin_backend.py 已更新 (添加书评管理)")

    # ========================================================
    # 4. 更新 templates/novel/reader.html (前端显示)
    # ========================================================
    # 我们直接重写 reader.html，加入评论区
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
        
        /* 评论区样式 */
        .comment-box { margin-top: 60px; border-top: 2px solid #333; padding-top: 30px; }
        .comment-title { font-family: 'Consolas', monospace; color: #ffcb6b; margin-bottom: 20px; font-size: 1rem; }
        .comment-list { margin-bottom: 30px; }
        .c-item { background: #1a1c25; padding: 15px; border-radius: 4px; margin-bottom: 10px; font-size: 0.95rem; }
        .c-meta { font-size: 0.8rem; color: #666; margin-bottom: 5px; display:flex; justify-content:space-between; }
        .c-user { color: #82aaff; font-weight:bold; }
        .c-content { color: #ddd; white-space: pre-wrap; }
        
        .c-form input, .c-form textarea {
            width: 100%; box-sizing: border-box; background: #0f111a; border: 1px solid #444; 
            color: white; padding: 10px; margin-bottom: 10px; font-family: inherit;
        }
        .c-form button {
            background: #ffcb6b; color: #000; border: none; padding: 10px 20px; 
            cursor: pointer; font-weight: bold; width: 100%;
        }

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

        <!-- 评论区 -->
        <div class="comment-box">
            <div class="comment-title">> 本章书评 (只保留 Top10 + 最新40)</div>
            
            <div class="comment-list">
                {% if comments %}
                    {% for c in comments %}
                        <div class="c-item">
                            <div class="c-meta"><span class="c-user">{{ c.nickname }}</span> <span>{{ c.created_at.strftime('%m-%d %H:%M') }}</span></div>
                            <div class="c-content">{{ c.content }}</div>
                        </div>
                        {% if loop.index == 10 and comments|length > 10 %}
                        <div style="text-align:center; color:#444; margin:10px 0; font-size:0.8rem;">[ ... 时空折叠区 ... ]</div>
                        {% endif %}
                    {% endfor %}
                {% else %}
                    <div style="text-align:center; color:#444; padding:20px;">暂无书评，来抢沙发...</div>
                {% endif %}
            </div>

            <form class="c-form" method="POST">
                <input type="text" name="nickname" placeholder="道友请留名 (默认: 书友)" maxlength="20">
                <textarea name="content" rows="3" placeholder="发表你的高见..." required maxlength="500"></textarea>
                <button type="submit">发布书评</button>
            </form>
        </div>
    </div>
</body>
</html>
"""
    with open('templates/novel/reader.html', 'w', encoding='utf-8') as f:
        f.write(reader_html)
    print("[OK] reader.html 已更新 (添加评论UI)")

    # ========================================================
    # 5. 数据库迁移脚本
    # ========================================================
    init_script = """
from app import app, db
with app.app_context():
    db.create_all()
    print("✅ 数据库表结构已更新 (新增 ChapterComment 表)")
"""
    with open('init_comment_db.py', 'w', encoding='utf-8') as f:
        f.write(init_script)

if __name__ == "__main__":
    add_novel_comments()
    print("-" * 30)
    print("升级完成！请执行以下步骤：")
    print("1. 运行数据库迁移: python3 init_comment_db.py")
    print("2. 重启服务: python3 app.py")
    print("3. 现在你的每章小说底部都有评论区了，且支持后台管理。")