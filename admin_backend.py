from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from extensions import db, basic_auth
from models import Book, Chapter, ChapterComment, Post, Comment, VisitStats, RosaryData, DailyPrayer, UserDevice

def format_preview(view, context, model, name):
    value = getattr(model, name)
    if not value: return ""
    return str(value)[:30] + '...' if len(str(value)) > 30 else str(value)

# --- 基础安全视图 ---
class SecureModelView(ModelView):
    def is_accessible(self):
        return basic_auth.authenticate()
    def inaccessible_callback(self, name, **kwargs):
        return basic_auth.challenge()

class SecureIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not basic_auth.authenticate():
            return basic_auth.challenge()
        return super(SecureIndexView, self).index()

# --- 自定义管理视图 ---
class RosaryDataAdmin(SecureModelView):
    column_list = ('uid', 'updated_at', 'data')
    column_default_sort = ('updated_at', True)
    can_create = False
    column_formatters = {'data': format_preview}
    column_labels = {'data': 'Data Preview', 'uid': '用户ID', 'updated_at': '更新时间'}
    form_widget_args = {'data': {'rows': 10, 'style': 'font-family:monospace;'}, 'uid': {'readonly': True}}

class DailyPrayerAdmin(SecureModelView):
    column_list = ('created_at', 'name', 'content', 'uid')
    column_default_sort = ('created_at', True)
    column_searchable_list = ['name', 'content']
    can_create = False

class UserDeviceAdmin(SecureModelView):
    column_list = ('device_name', 'updated_at', 'last_ip', 'device_key', 'fingerprint')
    column_searchable_list = ['device_name', 'device_key', 'fingerprint', 'last_ip']
    column_default_sort = ('updated_at', True)
    
    # 3. 自定义表头
    column_labels = {
        'device_key': 'UUID', 
        'fingerprint': '指纹', 
        'device_name': '昵称', 
    }
    form_widget_args = {'data': {'rows': 10, 'style': 'font-family:monospace;'}, 'device_key': {'readonly': True}}

# --- 初始化函数 (由 app.py 调用) ---

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


class ChapterCommentAdmin(SecureModelView):
    column_list = ('chapter.title', 'nickname', 'content', 'created_at')
    column_searchable_list = ['content', 'nickname']
    # 修复：移除跨表过滤 'chapter.book.title'
    column_filters = ['nickname', 'content']
    column_labels = {'chapter.title':'章节', 'nickname':'书友', 'content':'内容', 'created_at':'时间'}
    can_create = False

def init_admin(app):
    admin = Admin(app, name='闪泥后台', index_view=SecureIndexView())
    
    # 主站管理
    admin.add_view(SecureModelView(Post, db.session, name='文章管理'))
    # 小说管理
    admin.add_view(BookAdmin(Book, db.session, name='小说书架', category='文学模块'))
    admin.add_view(ChapterAdmin(Chapter, db.session, name='章节管理', category='文学模块'))
    admin.add_view(ChapterCommentAdmin(ChapterComment, db.session, name='书评管理', category='文学模块'))

    admin.add_view(SecureModelView(Comment, db.session, name='评论监控'))
    admin.add_view(SecureModelView(VisitStats, db.session, name='流量统计'))
    
    # 玫瑰经/闪泥管理
    admin.add_view(DailyPrayerAdmin(DailyPrayer, db.session, name='今日祷告墙'))
    admin.add_view(UserDeviceAdmin(UserDevice, db.session, name='用户设备(新)'))
    admin.add_view(RosaryDataAdmin(RosaryData, db.session, name='旧·存档(待迁移)'))
    
    print("[System] 后台管理模块加载完成。")