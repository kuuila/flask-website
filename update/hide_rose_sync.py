import os

def hide_sync_buttons():
    html_path = 'templates/rose.html'
    
    if not os.path.exists(html_path):
        print(f"❌ 错误：找不到 {html_path}")
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # ==========================================
    # 1. 修改 HTML 结构
    # ==========================================
    
    # 我们要找的旧代码块（按钮容器的开头）
    # 之前的脚本生成的代码是这样的：
    # <div style="display:flex; gap:10px; margin-top:10px;">
    
    old_div_start = '<div style="display:flex; gap:10px; margin-top:10px;">'
    
    # 新的代码块：
    # 1. 加一个 ID="sync-area"
    # 2. 改为 display:none (默认隐藏)
    # 3. 在上面加一个开关按钮
    new_div_block = """
        <!-- 云端同步开关 -->
        <div style="text-align:center; margin-top:8px;">
             <span onclick="App.toggleSync()" style="font-size:0.75rem; color:#666; cursor:pointer; border-bottom:1px dashed #555; transition:0.3s;" onmouseover="this.style.color='#aaa'" onmouseout="this.style.color='#666'">
                [ ☁️ 管理云端存档 ]
             </span>
        </div>

        <!-- 云端同步按钮组 (默认隐藏) -->
        <div id="sync-area" style="display:none; gap:10px; margin-top:10px;">"""

    if old_div_start in content:
        content = content.replace(old_div_start, new_div_block)
        print("[OK] HTML 结构已修改：按钮已隐藏，添加了开关链接。")
    else:
        # 容错：如果找不到完全匹配的字符串（可能因为空格），尝试模糊查找
        print("⚠️ 尝试模糊匹配 HTML...")
        alt_old = 'gap:10px; margin-top:10px;">'
        if alt_old in content:
            # 我们只替换样式部分
            content = content.replace('style="display:flex; gap:10px; margin-top:10px;"', 'id="sync-area" style="display:none; gap:10px; margin-top:10px;"')
            # 并在前面插入开关
            insert_marker = '<!-- 新增：云端同步按钮组 -->'
            toggle_html = """
        <!-- 云端同步开关 -->
        <div style="text-align:center; margin-top:8px;">
             <span onclick="App.toggleSync()" style="font-size:0.75rem; color:#666; cursor:pointer; border-bottom:1px dashed #555;">[ ☁️ 管理云端存档 ]</span>
        </div>
            """
            if insert_marker in content:
                content = content.replace(insert_marker, insert_marker + toggle_html)
            print("[OK] HTML 已通过模糊匹配修改。")
        else:
            print("❌ 无法定位按钮容器，请检查 rose.html")
            return

    # ==========================================
    # 2. 注入 JS Toggle 函数
    # ==========================================
    
    toggle_js = """
            toggleSync() {
                const el = document.getElementById('sync-area');
                if (el.style.display === 'none') {
                    el.style.display = 'flex';
                    // 自动滚动到底部
                    setTimeout(() => {
                         el.scrollIntoView({ behavior: 'smooth', block: 'end' });
                    }, 100);
                } else {
                    el.style.display = 'none';
                }
            },
    """

    # 插入到 App 对象里，比如 downloadData 之前
    if "toggleSync" not in content:
        target_js = "async downloadData() {"
        content = content.replace(target_js, toggle_js + "\n            " + target_js)
        print("[OK] JS Toggle 逻辑已注入。")
    
    # 写入文件
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    hide_sync_buttons()
    print("-" * 30)
    print("更新完成！")
    print("现在底部的上传/下载按钮平时是隐藏的。")
    print("点击 [ ☁️ 管理云端存档 ] 才会显示。")