import os
import re

def merge_header_profile():
    html_path = 'templates/rose2.html'
    
    if not os.path.exists(html_path):
        print(f"❌ 错误：找不到 {html_path}")
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # ==========================================
    # 1. 定义新的 CSS (灵修铭牌样式)
    # ==========================================
    new_css = """
        /* === 合并后的灵修铭牌 (Profile Card) === */
        .profile-card {
            position: relative;
            margin: 10px auto 5px auto;
            background: linear-gradient(180deg, rgba(20, 30, 50, 0.9) 0%, rgba(8, 12, 20, 0.95) 100%);
            border: 1px solid var(--gold-dim);
            border-radius: 6px;
            padding: 0; /* 内部布局自己控制 */
            width: fit-content;
            min-width: 140px;
            max-width: 80%;
            box-shadow: 0 4px 15px rgba(0,0,0,0.6);
            display: flex;
            flex-direction: column;
            align-items: center;
            overflow: hidden; /* 保证进度条不溢出圆角 */
            z-index: 30;
        }

        /* 上半部分：圣名 (点击改名) */
        .pc-name-row {
            width: 100%;
            padding: 8px 15px 4px 15px;
            text-align: center;
            font-size: 0.95rem;
            color: var(--text-main);
            cursor: pointer;
            border-bottom: 1px solid rgba(212, 175, 55, 0.1);
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 5px;
        }
        .pc-name-row:active { background: rgba(255,255,255,0.05); }

        /* 下半部分：中文位阶 (点击看详情) */
        .pc-rank-row {
            width: 100%;
            padding: 4px 15px 8px 15px;
            text-align: center;
            font-family: 'Cinzel', serif;
            font-size: 0.75rem; /* 小字号 */
            color: var(--gold-primary);
            cursor: help;
            letter-spacing: 2px;
            font-weight: bold;
            text-shadow: 0 0 5px rgba(212,175,55,0.3);
        }
        .pc-rank-row:active { background: rgba(212, 175, 55, 0.1); }

        /* 底部进度条 */
        .pc-progress-bg {
            width: 100%;
            height: 3px;
            background: rgba(0,0,0,0.5);
            position: relative;
        }
        .pc-progress-bar {
            height: 100%;
            background: linear-gradient(90deg, var(--gold-dim), var(--gold-primary));
            width: 0%;
            box-shadow: 0 0 8px var(--gold-primary);
            transition: width 1s ease-out;
        }

        /* 隐藏旧元素干扰 */
        .user-profile, .rank-badge-container { display: none !important; }
        
        /* 调整 Header 间距 */
        .app-title { margin-top: 15px !important; font-size: 1.1rem !important; opacity: 0.8; }
        .stats-bar { margin-top: 5px !important; }
    """

    # ==========================================
    # 2. 定义新的 HTML 结构
    # ==========================================
    new_header_html = """
    <div class="header">
        <!-- 合并后的灵修铭牌 -->
        <div class="profile-card">
            <!-- 1. 圣名区域 -->
            <div class="pc-name-row" onclick="App.editName()">
                <span id="name-display">设置圣名</span> 
                <span style="font-size:0.7em; opacity:0.5; color:var(--gold-dim);">✎</span>
            </div>
            
            <!-- 2. 位阶区域 (无英文) -->
            <div class="pc-rank-row" onclick="App.showRankInfo()">
                <span id="rank-cn">旅人</span>
                <!-- 隐藏的英文ID，防止JS报错 -->
                <span id="rank-lat" style="display:none"></span>
            </div>

            <!-- 3. 底部进度条 -->
            <div class="pc-progress-bg">
                <div class="pc-progress-bar" id="rank-bar"></div>
            </div>
        </div>

        <div class="app-title">Sanctum Rosarium</div>
        
        <div class="stats-bar">
            <div class="stat-item"><span class="stat-icon">📿</span><span>总灵修: <span class="stat-val" id="stat-total-days">0</span> 天</span></div>
            <div class="stat-item"><span class="stat-icon">👑</span><span>40天圆满: <span class="stat-val" id="stat-rounds">0</span> 轮</span><span class="stat-val" id="stat-rounds-cnt" style="font-size:0.7rem; margin-left:2px; opacity:0.8">(0/40)</span></div>
        </div>
        <div class="date-info" id="date-display">loading...</div>
    </div>
    """

    # ==========================================
    # 3. 执行替换
    # ==========================================
    
    # 1. 注入 CSS
    if ".profile-card" not in content:
        content = content.replace("</style>", new_css + "\n    </style>")
        print("[OK] 新的 CSS 样式已注入")

    # 2. 替换 Header HTML
    # 我们使用正则找到整个 <div class="header">...</div> 块并替换
    # 注意：re.DOTALL 让 . 匹配换行符
    pattern = re.compile(r'<div class="header">[\s\S]*?</div>', re.DOTALL)
    
    if pattern.search(content):
        content = pattern.sub(new_header_html, content)
        print("[OK] Header HTML 结构已重构 (合并铭牌)")
    else:
        print("❌ 错误：无法定位 header 区域，替换失败。")
        return

    # 3. 清理旧的 JS 渲染逻辑中的干扰 (可选，但为了保险)
    # 之前的 renderRank 可能会找 .rank-badge-container，现在它被 CSS 隐藏了，没关系
    # 只要 id="rank-cn" 和 id="rank-bar" 还在，JS 就能正常工作。
    # 我们在 HTML 里保留了隐藏的 id="rank-lat"，防止 JS 报错。

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("-" * 30)
    print("✅ 升级完成！")
    print("头像和位阶已合并为一个精致的铭牌。")
    print("英文头衔已隐藏，界面更清爽。")
    print("请刷新 rose.html 查看效果。")

if __name__ == "__main__":
    merge_header_profile()