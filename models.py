from datetime import datetime
from extensions import db

# --- 主站模型 (文章/评论/统计) ---
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    content = db.Column(db.Text)
    summary = db.Column(db.String(500))
    tags = db.Column(db.String(100))
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")

    @property
    def css_class(self):
        mapping = {'logic': 'cat-logic', 'spirit': 'cat-spirit', 'senses': 'cat-senses', 'life': 'cat-life'}
        return mapping.get(self.category, '')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    nickname = db.Column(db.String(50), default='Anonymous')
    content = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

class VisitStats(db.Model):
    date = db.Column(db.String(20), primary_key=True)
    count = db.Column(db.Integer, default=0)

# --- 玫瑰经/身份模型 ---

# [修复] 补上 UserDevice 模型
class UserDevice(db.Model):
    device_key = db.Column(db.String(36), primary_key=True)  # UUID
    fingerprint = db.Column(db.String(64), index=True)       # 指纹
    device_name = db.Column(db.String(50))                   # 昵称
    data = db.Column(db.Text)                                # 存档数据
    last_ip = db.Column(db.String(50))                       # IP
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class RosaryData(db.Model):
    uid = db.Column(db.String(36), primary_key=True)
    data = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class DailyPrayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(36))
    name = db.Column(db.String(50))
    content = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)
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
    comments = db.relationship('ChapterComment', backref='chapter', lazy=True, cascade='all, delete-orphan') 

class ChapterComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    nickname = db.Column(db.String(50), default='书友')
    content = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
