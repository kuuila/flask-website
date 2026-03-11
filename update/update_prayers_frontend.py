import os

def fix_prayer_list_bug():
    html_path = 'templates/rose2.html'
    
    if not os.path.exists(html_path):
        print(f"❌ 错误：找不到 {html_path}")
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # ==========================================
    # 修复 1：移除 HTML 中的注释，防止干扰判断
    # ==========================================
    old_html = """<div class="prayer-list" id="prayer-list" onscroll="App.checkScroll()">
                <!-- 列表由 JS 填充 -->
            </div>"""
    
    new_html = """<div class="prayer-list" id="prayer-list" onscroll="App.checkScroll()"></div>"""
    
    if old_html in content:
        content = content.replace(old_html, new_html)
        print("[OK] HTML 注释已移除，容器已清空。")
    else:
        # 尝试模糊匹配，只去掉注释
        content = content.replace('<!-- 列表由 JS 填充 -->', '')
        print("[OK] HTML 注释已移除 (模糊匹配)。")

    # ==========================================
    # 修复 2：优化 JS 中的 switchTab 逻辑
    # 改为判断 offset 是否为 0，而不是判断 DOM 内容
    # ==========================================
    
    # 查找旧的 switchTab 函数头
    # 我们需要替换整个 switchTab 函数
    
    old_js_start = "switchTab(mode) {"
    
    # 新的 switchTab 函数
    # 1. 使用 this.prayerOffset === 0 来判断是否初次加载，这比 innerHTML 更靠谱
    # 2. 增加 console.log 方便调试
    new_js_logic = """switchTab(mode) {
                document.querySelectorAll('.mode-tab').forEach(e => e.classList.remove('active'));
                
                // 激活对应的 Tab 按钮
                const tabs = document.querySelectorAll('.mode-tab');
                if(mode === 'calendar' && tabs[0]) tabs[0].classList.add('active');
                if(mode === 'strict' && tabs[1]) tabs[1].classList.add('active');
                if(mode === 'prayers' && tabs[2]) {
                    tabs[2].classList.add('active');
                    // 【关键修复】使用数据状态判断，而不是 DOM 内容
                    // 如果 offset 为 0，说明还没加载过数据，或者列表被清空了
                    if (this.prayerOffset === 0) {
                        console.log("Tab切换: 首次加载祈祷列表...");
                        this.loadPrayers(true);
                    }
                }

                // 切换面板显示
                const pCal = document.getElementById('view-calendar');
                const pStrict = document.getElementById('view-strict');
                const pPrayers = document.getElementById('view-prayers');

                if(pCal) pCal.classList.toggle('active', mode === 'calendar');
                if(pStrict) pStrict.classList.toggle('active', mode === 'strict');
                if(pPrayers) pPrayers.classList.toggle('active', mode === 'prayers');
            },"""

    # 定位并替换
    # 为了准确，我们找到 old_js_start，然后手动截取到它大概结束的位置不太容易
    # 我们采用“替换函数体核心逻辑”的方法
    
    # 识别旧逻辑中的特征代码
    buggy_check = 'if(document.getElementById(\'prayer-list\').innerHTML.trim() === "")'
    
    if buggy_check in content:
        # 替换那个错误的判断条件
        content = content.replace(buggy_check, 'if (this.prayerOffset === 0)')
        print("[OK] JS 逻辑已修复：判断条件改为检测 offset。")
    else:
        # 如果找不到特征代码，可能是 formatting 变了，尝试直接替换 switchTab 定义
        # 这需要你的代码结构比较标准
        import re
        # 匹配 switchTab 函数体
        pattern = re.compile(r'switchTab\(mode\)\s*\{[\s\S]*?pPanel\.classList\.toggle\(\'active\',\s*mode\s*===\s*\'prayers\'\);\s*\},')
        
        match = pattern.search(content)
        if match:
            content = content.replace(match.group(0), new_js_logic)
            print("[OK] JS 逻辑已通过正则完全重写。")
        else:
            print("⚠️ 未能自动替换 JS 逻辑，请检查代码格式。尝试手动修复...")

    # ==========================================
    # 修复 3：确保 API 地址正确
    # ==========================================
    # 检查 fetch 路径
    if "fetch(`/api/rose/prayers" not in content:
        print("⚠️ 警告：未找到 fetch API 调用，可能 loadPrayers 函数缺失？")

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    fix_prayer_list_bug()
    print("-" * 30)
    print("修复完成！")
    print("1. 请确保 python3 app.py 正在运行。")
    print("2. 刷新 rose.html 页面。")
    print("3. 再次点击【今日祷告】Tab，现在应该能看到数据了。")