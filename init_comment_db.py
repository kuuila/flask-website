
from app import app, db
with app.app_context():
    db.create_all()
    print("✅ 数据库表结构已更新 (新增 ChapterComment 表)")
