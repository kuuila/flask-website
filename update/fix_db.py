from app import app, db

# 这一步会扫描 app.py 里定义的所有模型
# 并自动在数据库中创建那些“还不存在”的表
# 已经存在的表（如 Post, Comment）不会受影响
def fix_database():
    if not os.path.exists('universe.db'):
        print("未找到数据库文件，将创建新的...")
    
    print("正在连接数据库并同步表结构...")
    with app.app_context():
        try:
            db.create_all()
            print("✅ 成功！'rosary_data' 表已创建。")
        except Exception as e:
            print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    import os
    fix_database()