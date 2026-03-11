import os
import uuid

# ==========================================
# 1. 更新 app.py (增加数据模型 + 同步接口)
# ==========================================
def update_app_py():
    app_path = 'app.py'
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否已经添加过，防止重复
    if 'class RosaryData(db.Model):' in content:
        print("[SKIP] app.py 似乎已经包含了 RosaryData 模型。")
    else:
        # 1. 插入数据库模型
        model_code = """
# --- 新增：玫瑰经用户数据存储 ---
class RosaryData(db.Model):
    uid = db.Column(db.String(36), primary_key=True) # 客户端生成的 UUID
    data = db.Column(db.Text, nullable=False)        # 完整的 JSON 字符串
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

"""
        # 找到 db = SQLAlchemy(app) 之后插入模型
        insert_point = "db = SQLAlchemy(app)"
        if insert_point in content:
            content = content.replace(insert_point, insert_point + "\n" + model_code)

        # 2. 插入 API 路由
        api_code = """
# --- 玫瑰经数据同步 API ---
@app.route('/api/rose/sync', methods=['POST'])
def rose_sync_upload():
    try:
        uid = request.json.get('uid')
        data_str = request.json.get('data')
        
        if not uid or not data_str:
            return jsonify({'status': 'error', 'msg': '缺少参数'}), 400
            
        # 查找或创建
        record = RosaryData.query.get(uid)
        if not record:
            record = RosaryData(uid=uid, data=data_str)
            db.session.add(record)
        else:
            record.data = data_str
            
        db.session.commit()
        return jsonify({'status': 'success', 'msg': '云端存档已更新'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/api/rose/sync/<uid>', methods=['GET'])
def rose_sync_download(uid):
    record = RosaryData.query.get(uid)
    if record:
        return jsonify({'status': 'success', 'data': record.data, 'time': record.updated_at})
    else:
        return jsonify({'status': 'error', 'msg': '未找到云端存档'}), 404
"""
        # 添加到文件末尾 (在 socketio.run 之前)
        if "if __name__ == '__main__':" in content:
            parts = content.split("if __name__ == '__main__':")
            content = parts[0] + api_code + "\nif __name__ == '__main__':" + parts[1]
        
        # 写入文件
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("[OK] app.py 已更新 (增加 RosaryData 模型与 API)")

# ==========================================
# 2. 更新 rose.html (增加按钮 + JS逻辑)
# ==========================================
def update_rose_html():
    html_path = 'templates/rose.html'
    if not os.path.exists(html_path):
        print(f"[ERROR] 找不到 {html_path}")
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 插入按钮 HTML (放在 Footer 的 mode-tabs 下面)
    # 定位点: <div class="mode-tabs">...</div>
    # 我们在 mode-tabs 闭合标签后插入
    btn_html = """
        <!-- 新增：云端同步按钮组 -->
        <div style="display:flex; gap:10px; margin-top:10px;">
            <button class="btn btn-stop" onclick="App.uploadData()" style="flex:1; border-color:var(--gold-primary); color:var(--gold-primary); font-size:0.8rem; padding:8px;">
                ☁️ 上传存档 (Upload)
            </button>
            <button class="btn btn-stop" onclick="App.downloadData()" style="flex:1; border-color:#888; color:#ccc; font-size:0.8rem; padding:8px;">
                📥 下载覆盖 (Download)
            </button>
        </div>
    """
    
    if "☁️ 上传存档" not in content:
        # 寻找 mode-tabs 结束位置的特征
        target_str = '<div class="mode-tab" onclick="App.switchTab(\'strict\')">40天严修 (Strict)</div>\n        </div>'
        if target_str in content:
            content = content.replace(target_str, target_str + btn_html)
        else:
            # 备用方案：插在 footer 开头
            content = content.replace('<div class="footer">', '<div class="footer">' + btn_html)
        print("[OK] rose.html 按钮已添加")

    # 2. 插入 JS 逻辑 (UUID生成 + 上传 + 下载)
    # 我们把新方法注入到 App 对象中。
    # 寻找 `updateNameDisplay() {` 作为一个插入点（因为它肯定存在）
    js_logic = """
            // --- 云端同步功能 ---
            getOrCreateUUID() {
                let uid = localStorage.getItem('rosary_uid');
                if (!uid) {
                    // 生成简单的 UUID
                    uid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
                        return v.toString(16);
                    });
                    localStorage.setItem('rosary_uid', uid);
                }
                return uid;
            },

            async uploadData() {
                if(!confirm("确定要将本地记录上传到云端吗？\\n这将覆盖云端旧数据。")) return;
                
                const uid = this.getOrCreateUUID();
                // 确保数据是最新的
                this.saveData(); 
                const payload = {
                    uid: uid,
                    data: JSON.stringify(this.data)
                };

                try {
                    const res = await fetch('/api/rose/sync', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(payload)
                    });
                    const json = await res.json();
                    if(json.status === 'success') {
                        alert("✅ 上传成功！\\n您的唯一ID是: " + uid + "\\n(换设备时需手动填入此ID才能找回数据)");
                    } else {
                        alert("❌ 上传失败: " + json.msg);
                    }
                } catch(e) {
                    alert("❌ 网络错误: " + e);
                }
            },

            async downloadData() {
                let uid = this.getOrCreateUUID();
                // 允许用户输入 ID 以恢复其他设备的数据
                const inputUid = prompt("请输入您的设备ID进行恢复 (默认使用本机ID):", uid);
                if(inputUid) uid = inputUid.trim();
                else return;

                if(!confirm("⚠️ 警告：下载将【覆盖】当前本地的所有记录！\\n确定要继续吗？")) return;

                try {
                    const res = await fetch('/api/rose/sync/' + uid);
                    if(res.status === 404) {
                        alert("❌ 未找到该ID的云端存档。");
                        return;
                    }
                    const json = await res.json();
                    if(json.status === 'success') {
                        // 覆盖本地数据
                        this.data = JSON.parse(json.data);
                        this.saveData();
                        // 刷新界面
                        this.updateNameDisplay();
                        this.renderStats();
                        this.renderUI(); // 刷新名字等
                        // 如果 ID 变了，保存新 ID
                        if(uid !== localStorage.getItem('rosary_uid')) {
                            localStorage.setItem('rosary_uid', uid);
                        }
                        alert("✅ 同步成功！数据已更新。");
                    } else {
                        alert("❌ 下载失败: " + json.msg);
                    }
                } catch(e) {
                    alert("❌ 网络错误: " + e);
                }
            },
    """

    if "getOrCreateUUID" not in content:
        # 插入到 updateNameDisplay 之前
        target_js = "updateNameDisplay() {"
        content = content.replace(target_js, js_logic + "\n            " + target_js)
        print("[OK] rose.html JS逻辑已注入")

    # 3. 在 user-profile 旁边显示一个小小的 ID 提示，或者在点击名字时显示 ID
    # 修改 editName 方法，增加显示 ID 的功能
    new_edit_name = """
            editName() {
                const uid = this.getOrCreateUUID();
                const defaultValue = this.data.userName === "设置圣名" ? "" : this.data.userName;
                const newName = prompt("请输入您的圣名 (Confirmation Name):\\n\\n[本机ID]: " + uid, defaultValue);
                if(newName !== null && newName.trim() !== "") {
                    this.data.userName = newName.trim();
                    this.saveData();
                    this.updateNameDisplay();
                }
            },
    """
    # 替换旧的 editName
    # 正则太麻烦，直接寻找特征字符串替换
    old_edit_name_start = 'editName() {'
    old_edit_name_end = 'this.updateNameDisplay();\n                }\n            },'
    
    # 简单查找替换 editName 函数体比较困难，这里我们在 init 里加个 log 提示 ID 即可，或者利用上面的 prompt 修改
    # 这里采用替换整个 editName 函数的方式（需要匹配够准）
    # 为了稳妥，我们用字符串 split 替换
    import re
    pattern = re.compile(r'editName\(\)\s*\{[\s\S]*?\},')
    match = pattern.search(content)
    if match and "本机ID" not in match.group(0):
        content = content.replace(match.group(0), new_edit_name)
        print("[OK] rose.html 修改了 editName 以显示 ID")

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)

# ==========================================
# 主程序
# ==========================================
if __name__ == "__main__":
    print("开始更新玫瑰经同步功能...")
    update_app_py()
    update_rose_html()
    print("-" * 30)
    print("更新完成！")
    print("请重启 Flask 服务: python3 app.py")
    print("访问 /s/rose 即可看到底部的【上传/下载】按钮。")