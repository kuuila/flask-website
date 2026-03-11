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