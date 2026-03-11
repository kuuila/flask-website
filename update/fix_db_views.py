import sqlite3

def add_views_column():
    db_path = 'universe.db'
    
    print(f"正在尝试连接数据库: {db_path} ...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查 views 列是否存在
        cursor.execute("PRAGMA table_info(post)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'views' not in columns:
            print(">>> 检测到缺少 'views' 字段，正在添加...")
            # 添加列，默认值为 0
            cursor.execute("ALTER TABLE post ADD COLUMN views INTEGER DEFAULT 0")
            conn.commit()
            print("✅ 数据库升级成功！已添加 'views' 统计字段。")
        else:
            print("✅ 'views' 字段已存在，无需操作。")
            
        conn.close()
    except Exception as e:
        print(f"❌ 数据库操作失败: {e}")

if __name__ == "__main__":
    add_views_column()