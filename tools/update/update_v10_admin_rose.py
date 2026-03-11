import os

def update_admin_for_rose():
    app_path = 'app.py'
    
    if not os.path.exists(app_path):
        print("❌ 错误：找不到 app.py")
        return

    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否已经添加过
    if "RosaryDataAdmin" in content:
        print("⚠️ 后台似乎已经包含玫瑰经存档管理，跳过更新。")
        return

    # 我们需要定义一个自定义的 Admin View 类，让数据显示更友好
    # 并将其注册到 admin 中
    
    # 1. 定义新的 Admin View 类代码
    # 我们把它插入到 admin 初始化之前
    admin_view_code = """
# --- 玫瑰经后台管理视图配置 ---
class RosaryDataAdmin(SecureModelView):
    # 列表页显示的字段
    column_list = ('uid', 'updated_at', 'data_preview')
    # 默认按更新时间倒序排列
    column_default_sort = ('updated_at', True)
    # 禁止创建（数据应由用户上传），允许编辑和删除
    can_create = False
    can_edit = True
    can_delete = True
    
    # 编辑页：让 data 字段显示为大文本框，字体设为等宽方便看 JSON
    form_widget_args = {
        'data': {
            'rows': 15,
            'style': 'font-family: "Consolas", monospace; font-size: 12px;'
        },
        'uid': {
            'readonly': True
        }
    }
    
    # 列表页预览逻辑：只显示前 100 个字符
    def data_preview(self, context, model, name):
        if not model.data: return ""
        return model.data[:100] + '...' if len(model.data) > 100 else model.data
    
    # 自定义标签名
    column_labels = {
        'uid': '设备ID (UUID)',
        'data': 'JSON 数据包',
        'updated_at': '最后同步时间',
        'data_preview': '数据预览'
    }

"""

    # 2. 注册语句
    # 找到 VisitStats 注册的地方，在其后添加
    register_code = "admin.add_view(RosaryDataAdmin(RosaryData, db.session, name='玫瑰经存档'))"

    # --- 执行插入操作 ---
    
    # A. 插入类定义 (找 SecureModelView 定义的地方，或者直接在 admin = Admin... 之前)
    # 我们可以找 `class VisitStats(db.Model):` 的结束位置，或者找 `class SecureIndexView`
    target_class_loc = "class SecureIndexView(AdminIndexView):"
    
    if target_class_loc in content:
        content = content.replace(target_class_loc, admin_view_code + "\n" + target_class_loc)
    else:
        print("❌ 无法定位插入点，请确保 app.py 结构正确。")
        return

    # B. 插入注册语句
    # 寻找 VisitStats 的注册语句
    target_register = "admin.add_view(SecureModelView(VisitStats, db.session, name='流量统计'))"
    
    if target_register in content:
        content = content.replace(target_register, target_register + "\n" + register_code)
        
        # 写入文件
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ 成功！玫瑰经数据管理已集成到后台。")
    else:
        print("❌ 无法找到 VisitStats 注册语句，无法自动添加。")

if __name__ == "__main__":
    update_admin_for_rose()
    print("-" * 30)
    print("请重启 Flask 服务: python3 app.py")
    print("访问 http://IP/admin 即可看到【玫瑰经存档】菜单。")