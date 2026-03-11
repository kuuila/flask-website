import os

def add_prayer_to_admin():
    app_path = 'app.py'
    
    if not os.path.exists(app_path):
        print("❌ 错误：找不到 app.py")
        return

    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否已添加
    if "DailyPrayerAdmin" in content:
        print("⚠️ 后台似乎已包含【今日祷告】管理，跳过更新。")
        return

    # ==========================================
    # 1. 定义 Admin 类代码
    # ==========================================
    # 我们配置：按时间倒序、可搜索名字和内容、禁止后台手动创建（只允许前台提交）
    admin_class_code = """
# --- 今日祷告后台配置 ---
class DailyPrayerAdmin(SecureModelView):
    column_list = ('created_at', 'name', 'content', 'uid')
    column_default_sort = ('created_at', True) # 默认倒序
    column_searchable_list = ['name', 'content', 'uid'] # 搜索框支持的字段
    column_labels = {
        'created_at': '提交时间',
        'name': '圣名',
        'content': '祷告内容',
        'uid': '设备ID'
    }
    can_create = False # 仅限前台提交
    can_edit = True
    can_delete = True
"""

    # ==========================================
    # 2. 插入 Admin 类定义
    # ==========================================
    # 找一个插入点，比如 RosaryDataAdmin 之后，或者 SecureIndexView 之前
    # 为了稳妥，我们插在 `class SecureIndexView` 之前
    target_class_loc = "class SecureIndexView(AdminIndexView):"
    
    if target_class_loc in content:
        content = content.replace(target_class_loc, admin_class_code + "\n" + target_class_loc)
    else:
        print("❌ 无法定位代码插入点 (SecureIndexView)，请检查 app.py 结构。")
        return

    # ==========================================
    # 3. 注册到 Admin 实例
    # ==========================================
    # 寻找 `admin = Admin(...)` 之后的添加视图代码
    # 我们找 `admin.add_view(SecureModelView(VisitStats...))` 这一行
    
    target_register = "admin.add_view(SecureModelView(VisitStats, db.session, name='流量统计'))"
    new_register = "admin.add_view(DailyPrayerAdmin(DailyPrayer, db.session, name='今日祷告墙'))"
    
    if target_register in content:
        content = content.replace(target_register, target_register + "\n" + new_register)
    else:
        # 备选方案：尝试找 RosaryDataAdmin 的注册
        alt_target = "name='玫瑰经存档'))"
        if alt_target in content:
            content = content.replace(alt_target, alt_target + "\n" + new_register)
        else:
            print("❌ 无法定位注册点，请手动添加 admin.add_view 代码。")
            return

    # ==========================================
    # 4. 写入文件
    # ==========================================
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 成功！后台已添加【今日祷告墙】管理模块。")
    print("-" * 30)
    print("请重启 Flask 服务: python3 app.py")
    print("访问 /admin 查看效果。")

if __name__ == "__main__":
    add_prayer_to_admin()