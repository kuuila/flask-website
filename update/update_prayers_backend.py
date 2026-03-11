import os

def update_backend():
    app_path = 'app.py'
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if "class DailyPrayer(db.Model):" in content:
        print("⚠️ 后端似乎已包含 DailyPrayer 模型，跳过模型注入。")
    else:
        # 1. 注入模型
        model_code = """
# --- 新增：今日祷告墙 ---
class DailyPrayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(36))       # 设备ID
    name = db.Column(db.String(50))      # 圣名
    content = db.Column(db.String(50))   # 祷告词
    created_at = db.Column(db.DateTime, default=datetime.now)
"""
        content = content.replace("db = SQLAlchemy(app)", "db = SQLAlchemy(app)\n" + model_code)

        # 2. 注入 API (包含2天清理逻辑)
        # 需引入 timedelta
        if "from datetime import datetime" in content and "timedelta" not in content:
            content = content.replace("from datetime import datetime", "from datetime import datetime, timedelta")

        api_code = """
# --- 今日祷告 API ---
@app.route('/api/rose/prayers', methods=['GET'])
def get_prayers():
    # 1. 清理 2 天前的数据
    try:
        two_days_ago = datetime.now() - timedelta(days=2)
        DailyPrayer.query.filter(DailyPrayer.created_at < two_days_ago).delete()
        db.session.commit()
    except:
        db.session.rollback()

    # 2. 获取分页数据
    offset = request.args.get('offset', 0, type=int)
    limit = 10
    
    # 按时间倒序
    query = DailyPrayer.query.order_by(DailyPrayer.created_at.desc())
    total = query.count()
    prayers = query.offset(offset).limit(limit).all()
    
    data = []
    for p in prayers:
        data.append({
            'time': p.created_at.strftime('%H:%M'),
            'name': p.name,
            'content': p.content
        })
        
    return jsonify({'status': 'success', 'data': data, 'has_more': (offset + limit) < total})

@app.route('/api/rose/prayer', methods=['POST'])
def submit_prayer():
    uid = request.json.get('uid')
    name = request.json.get('name')
    content = request.json.get('content')
    
    if not content or len(content) < 5: # 简单校验
        return jsonify({'status': 'error', 'msg': '祷告词太短'}), 400
        
    new_p = DailyPrayer(uid=uid, name=name, content=content)
    db.session.add(new_p)
    db.session.commit()
    return jsonify({'status': 'success'})
"""
        # 插入到 main 之前
        if "if __name__ == '__main__':" in content:
            parts = content.split("if __name__ == '__main__':")
            content = parts[0] + api_code + "\nif __name__ == '__main__':" + parts[1]

        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ 后端更新成功！(模型 + API)")

    # 3. 自动更新数据库结构
    # 我们生成一个临时脚本来建表
    import sqlite3
    try:
        # 直接利用 Flask context 建表更稳妥，但这里简单起见，我们生成一个 fix_db 脚本让用户跑，或者直接在这里跑
        # 既然上面已经改了 app.py，我们可以在这里调用一个子进程来建表
        pass 
    except Exception:
        pass

if __name__ == "__main__":
    update_backend()
    
    # 自动创建新表
    print("正在更新数据库表结构...")
    from app import app, db
    with app.app_context():
        db.create_all()
        print("✅ 数据库表 'daily_prayer' 创建成功！")