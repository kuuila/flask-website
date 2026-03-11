from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from sqlalchemy import or_
from extensions import db
from models import Post, Comment

# 创建主站蓝图
main_bp = Blueprint('main', __name__)

# --- 辅助函数 ---
def prune_comments(post_id):
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    if len(comments) > 50:
        head = [c.id for c in comments[:10]]
        tail = [c.id for c in comments[-40:]]
        keep_ids = set(head + tail)
        for c in comments:
            if c.id not in keep_ids: db.session.delete(c)
        db.session.commit()

# --- 路由 ---
@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    tab = request.args.get('tab', 'latest')
    per_page = 9
    query = Post.query

    if tab == 'popular': query = query.order_by(Post.views.desc())
    elif tab == 'recommend': query = query.filter(Post.title.contains('闪泥')).order_by(Post.created_at.desc())
    else: query = query.order_by(Post.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('index.html', pagination=pagination, current_tab=tab, title="首页")

@main_bp.route('/category/<category_name>')
def category(category_name):
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(category=category_name).order_by(Post.created_at.desc()).paginate(page=page, per_page=12, error_out=False)
    return render_template('index.html', pagination=pagination, current_tab='category', title=category_name.upper())

@main_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    
    # 增加阅读量
    if request.method == 'GET':
        post.views = (post.views or 0) + 1
        db.session.commit()

    if request.method == 'POST':
        nickname = request.form.get('nickname') or "匿名访客"
        content = request.form.get('content')
        if content and content.strip():
            db.session.add(Comment(post_id=post.id, nickname=nickname[:20], content=content[:500]))
            db.session.commit()
            prune_comments(post.id)
            return redirect(url_for('main.post_detail', post_id=post_id))
            
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.asc()).all()
    return render_template('post_html.html', post=post, comments=comments, title=post.title)

@main_bp.route('/s/<sub_web>')
def subweb(sub_web):
    # 如果玫瑰经需要文章列表数据，可以在这里传递，或者玫瑰经页面改为纯静态+API
    return render_template(sub_web+'.html')

@main_bp.route('/api/search')
def search_api():
    query = request.args.get('q', '')
    if not query: return jsonify([])
    results = Post.query.filter(or_(Post.title.contains(query),Post.summary.contains(query),Post.tags.contains(query))).order_by(Post.created_at.desc()).limit(10).all()
    return jsonify([{'id': p.id, 'title': p.title, 'summary': p.summary, 'date': p.created_at.strftime('%Y-%m-%d'), 'category': p.category} for p in results])