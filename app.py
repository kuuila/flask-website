import os
from flask import Flask, render_template, request, redirect, url_for, flash, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from sqlalchemy import func, or_
from datetime import datetime, timedelta
import threading
from extensions import app,db,socketio,basic_auth
# --- 后台管理模块 ---
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_basicauth import BasicAuth
from models import Post, Comment, VisitStats, RosaryData, DailyPrayer, UserDevice
from admin_backend import init_admin
from rose_backend import rose_bp
from novel_backend import novel_bp

# rose api
app.register_blueprint(rose_bp) 
app.register_blueprint(novel_bp) 

init_admin(app)

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

@app.route('/api/search')
def search_api():
    query = request.args.get('q', '')
    if not query: return jsonify([])
    results = Post.query.filter(or_(Post.title.contains(query),Post.summary.contains(query),Post.tags.contains(query))).order_by(Post.created_at.desc()).limit(10).all()
    data = []
    for p in results:
        data.append({'id': p.id, 'title': p.title, 'summary': p.summary, 'date': p.created_at.strftime('%Y-%m-%d'), 'category': p.category})
    return jsonify(data)

# --- 首页路由 (核心修改：分页与分栏) ---
@app.route('/')
def index():
    # 获取参数，默认第1页，默认 'latest' 标签
    page = request.args.get('page', 1, type=int)
    tab = request.args.get('tab', 'latest')
    per_page = 9 # 每页显示9篇

    query = Post.query

    # 根据标签筛选/排序
    if tab == 'popular':
        # 人气最高：按 views 倒序
        query = query.order_by(Post.views.desc())
    elif tab == 'recommend':
        # 闪泥推荐：筛选标题含"闪泥"的文章
        query = query.filter(Post.title.contains('闪泥')).order_by(Post.created_at.desc())
    else: # latest
        # 最新发布
        query = query.order_by(Post.created_at.desc())

    # 执行分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('index.html', pagination=pagination, current_tab=tab, title="首页")

@app.route('/s/<sub_web>')
def subweb(sub_web):
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template(sub_web+'.html', posts=posts)

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    
    # 增加阅读量 (简单防刷：仅GET请求且非后台)
    if request.method == 'GET':
        post.views = (post.views or 0) + 1
        db.session.commit()

    if request.method == 'POST':
        nickname = request.form.get('nickname')
        content = request.form.get('content')
        if not nickname or nickname.strip() == "": nickname = "匿名访客"
        if content and content.strip() != "":
            new_comment = Comment(post_id=post.id, nickname=nickname[:20], content=content[:500])
            db.session.add(new_comment)
            db.session.commit()
            comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.asc()).all()
            if len(comments) > 50:
                head = [c.id for c in comments[:10]]
                tail = [c.id for c in comments[-40:]]
                for c in comments:
                    if c.id not in set(head+tail): db.session.delete(c)
                db.session.commit()
            return redirect(url_for('post_detail', post_id=post_id))
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.asc()).all()
    return render_template('post_html.html', post=post, comments=comments, title=post.title)

@app.route('/category/<category_name>')
def category(category_name):
    # 分类页面也加上简单的分页
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(category=category_name).order_by(Post.created_at.desc()).paginate(page=page, per_page=12, error_out=False)
    # 复用 index.html，但需要传 current_tab 为 None 或特定值避免显示首页 Tab
    return render_template('index.html', pagination=pagination, current_tab='category', title=category_name.upper())

# @app.route('/api/rose/sync', methods=['POST'])
# def rose_sync_upload():
#     try:
#         uid = request.json.get('uid'); data_str = request.json.get('data')
#         if not uid or not data_str: return jsonify({'status': 'error', 'msg': '缺少参数'}), 400
#         record = RosaryData.query.get(uid)
#         if not record:
#             record = RosaryData(uid=uid, data=data_str)
#             db.session.add(record)
#         else: record.data = data_str
#         db.session.commit()
#         return jsonify({'status': 'success', 'msg': '云端存档已更新'})
#     except Exception as e: return jsonify({'status': 'error', 'msg': str(e)}), 500

# @app.route('/api/rose/sync/<uid>', methods=['GET'])
# def rose_sync_download(uid):
#     record = RosaryData.query.get(uid)
#     if record: return jsonify({'status': 'success', 'data': record.data, 'time': record.updated_at})
#     else: return jsonify({'status': 'error', 'msg': '未找到云端存档'}), 404

# --- SocketIO ---
@socketio.on('send_message')
def handle_message(data):
    msg = data.get('message')
    nickname = data.get('nickname', '***')
    if len(nickname) < 1: nickname = "***"
    if len(nickname) > 16: nickname = nickname[:16]
    if msg: emit('receive_message', {'user': nickname, 'msg': msg}, broadcast=True)

# --- HTTPS Redirect ---
def run_http_redirect():
    from flask import Flask, redirect, request
    redirect_app = Flask(__name__)
    @redirect_app.route('/', defaults={'path': ''})
    @redirect_app.route('/<path:path>')
    def https_redirect(path):
        return redirect(request.url.replace('http://', 'https://'), code=301)
    redirect_app.run(host='0.0.0.0', port=80)

def run_http_server():
    socketio.run(app,host='0.0.0.0', port=80, debug=False)


# --- 今日祷告 API ---
# @app.route('/api/rose/prayers', methods=['GET'])
# def get_prayers():
#     # 1. 清理 2 天前的数据
#     try:
#         two_days_ago = datetime.now() - timedelta(days=2)
#         DailyPrayer.query.filter(DailyPrayer.created_at < two_days_ago).delete()
#         db.session.commit()
#     except:
#         db.session.rollback()

#     # 2. 获取分页数据
#     offset = request.args.get('offset', 0, type=int)
#     limit = 10
    
#     # 按时间倒序
#     query = DailyPrayer.query.order_by(DailyPrayer.created_at.desc())
#     total = query.count()
#     prayers = query.offset(offset).limit(limit).all()
    
#     data = []
#     for p in prayers:
#         data.append({
#             'time': p.created_at.strftime('%H:%M'),
#             'name': p.name,
#             'content': p.content
#         })
        
#     return jsonify({'status': 'success', 'data': data, 'has_more': (offset + limit) < total})

# @app.route('/api/rose/prayer', methods=['POST'])
# def submit_prayer():
#     uid = request.json.get('uid')
#     name = request.json.get('name')
#     content = request.json.get('content')
    
#     if not content or len(content) < 5: # 简单校验
#         return jsonify({'status': 'error', 'msg': '祷告词太短'}), 400
        
#     new_p = DailyPrayer(uid=uid, name=name, content=content)
#     db.session.add(new_p)
#     db.session.commit()
#     return jsonify({'status': 'success'})

if __name__ == '__main__':
    if not os.path.exists('universe.db'):
        with app.app_context(): db.create_all()
    
    import threading
    t = threading.Thread(target=run_http_server, daemon=True)
    t.start()
    print(">>> 闪泥工作室 HTTP 主服务启动 (Port 3006)...")
    
    # 不使用 SSL，直接运行
    socketio.run(app, host='0.0.0.0', port=3006, debug=True)