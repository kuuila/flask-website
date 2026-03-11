import os

def update_rose_rank():
    html_path = 'templates/rose2.html'
    
    if not os.path.exists(html_path):
        print(f"❌ 错误：找不到 {html_path}")
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # ==========================================
    # 1. 插入 CSS 样式 (徽章样式)
    # ==========================================
    css_insert = """
        /* === 灵修位阶徽章 === */
        .rank-badge-container {
            text-align: center;
            margin-top: 15px;
            margin-bottom: 5px;
            animation: fadeIn 1s ease-in;
        }
        
        .rank-badge {
            display: inline-flex;
            flex-direction: column;
            align-items: center;
            padding: 8px 20px;
            background: linear-gradient(180deg, rgba(30,40,60,0.8) 0%, rgba(10,15,25,0.9) 100%);
            border: 1px solid var(--gold-dim);
            border-radius: 4px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            position: relative;
            cursor: help; /* 提示可点击/查看 */
        }
        
        .rank-badge::before, .rank-badge::after {
            content: '☩';
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            color: var(--gold-dim);
            font-size: 0.8rem;
        }
        .rank-badge::before { left: 8px; }
        .rank-badge::after { right: 8px; }

        .rank-title-lat {
            font-family: 'Cinzel', serif;
            font-size: 0.9rem;
            color: var(--gold-primary);
            letter-spacing: 1px;
            text-transform: uppercase;
            font-weight: bold;
            text-shadow: 0 0 5px rgba(212,175,55,0.3);
        }
        
        .rank-title-cn {
            font-family: 'Noto Serif SC', serif;
            font-size: 0.75rem;
            color: #8B9BB4;
            margin-top: 2px;
        }

        /* 进度条容器 */
        .rank-progress-bg {
            width: 100%;
            height: 2px;
            background: rgba(255,255,255,0.1);
            margin-top: 6px;
            border-radius: 1px;
            position: relative;
        }
        .rank-progress-bar {
            height: 100%;
            background: var(--gold-primary);
            width: 0%;
            box-shadow: 0 0 5px var(--gold-primary);
            transition: width 1s ease-out;
        }
    """
    
    if ".rank-badge" not in content:
        # 插在 </style> 之前
        content = content.replace("</style>", css_insert + "\n    </style>")
        print("[OK] CSS 样式已添加")

    # ==========================================
    # 2. 插入 HTML 结构 (位阶显示区域)
    # ==========================================
    html_insert = """
        <div class="rank-badge-container" onclick="App.showRankInfo()">
            <div class="rank-badge">
                <div class="rank-title-lat" id="rank-lat">VIATOR</div>
                <div class="rank-title-cn" id="rank-cn">旅人</div>
                <div class="rank-progress-bg">
                    <div class="rank-progress-bar" id="rank-bar"></div>
                </div>
            </div>
        </div>
    """
    
    # 插在 stats-bar 之后，date-info 之前
    # 定位点: <div class="date-info"
    if "rank-badge-container" not in content:
        target = '<div class="date-info"'
        content = content.replace(target, html_insert + "\n        " + target)
        print("[OK] HTML 结构已添加")

    # ==========================================
    # 3. 注入 JS 逻辑 (位阶计算算法)
    # ==========================================
    
    # 这是核心算法代码
    js_logic = """
            // ================= 灵修位阶系统 =================
            // 逻辑：得分 = 总天数 + (完成轮次 * 50)
            // 轮次权重高，鼓励完成40天严修
            calculateRank() {
                const days = this.data.calendar.length;
                const rounds = this.data.strict.rounds || 0;
                
                // 计算灵修分数 (Score)
                // 每一轮严修(40天)相当于额外的加成，体现"质"的飞跃
                const score = days + (rounds * 50);

                const ranks = [
                    { s: 0,    l: "Viator",           c: "旅人",       desc: "初踏灵修之旅，步履蹒跚但心向光明。" },
                    { s: 30,   l: "Catechumenus",     c: "慕道者",     desc: "已聆听圣言，徘徊于门槛，预备心灵。" },
                    { s: 100,  l: "Novitius",         c: "初学修士",   desc: "穿上修道初衣，开始习练克己与日课。" },
                    { s: 250,  l: "Fidelis",          c: "坚贞信徒",   desc: "信德扎根，如树栽溪水旁，按时结果。" },
                    { s: 500,  l: "Miles Christi",    c: "基督精兵",   desc: "佩戴玫瑰念珠为剑，在属灵战场上得胜。" },
                    { s: 1000, l: "Eques Rosarii",    c: "玫瑰骑士",   desc: "以玫瑰经为荣耀勋章，誓死守护圣教会。" },
                    { s: 2000, l: "Custos Fidei",     c: "信仰守护者", desc: "成为信德的堡垒，为他人遮风挡雨。" },
                    { s: 3500, l: "Contemplativus",   c: "默观者",     desc: "超越语言的祈祷，在静默中注视真理之光。" },
                    { s: 6000, l: "Amicus Dei",       c: "天主之友",   desc: "如亚巴郎般，与主亲密同行，无话不谈。" },
                    { s: 9999, l: "Sanctus Bellator", c: "成圣战士",   desc: "凡在世上打过美好的仗，必获正义的冠冕。" }
                ];

                let currentRank = ranks[0];
                let nextRank = ranks[1];
                let progress = 0;

                for (let i = 0; i < ranks.length; i++) {
                    if (score >= ranks[i].s) {
                        currentRank = ranks[i];
                        nextRank = ranks[i + 1] || { s: score * 1.2 }; // 最高级后虚拟一个上限
                    } else {
                        break;
                    }
                }

                // 计算当前等级内的进度百分比
                const range = nextRank.s - currentRank.s;
                const currentVal = score - currentRank.s;
                progress = Math.min(100, Math.max(0, (currentVal / range) * 100));

                return { current: currentRank, next: nextRank, progress: progress, score: score };
            },

            renderRank() {
                const rankData = this.calculateRank();
                
                document.getElementById('rank-lat').innerText = rankData.current.l;
                document.getElementById('rank-cn').innerText = rankData.current.c;
                document.getElementById('rank-bar').style.width = rankData.progress + "%";
            },

            showRankInfo() {
                const r = this.calculateRank();
                const days = this.data.calendar.length;
                const rounds = this.data.strict.rounds || 0;
                
                let info = `⚜️ **灵修位阶：${r.current.c}** (${r.current.l})\\n\\n`;
                info += `📜 **位阶描述**：\\n${r.current.desc}\\n\\n`;
                info += `📊 **灵修积分**：${r.score}\\n`;
                info += `   • 累积天数：${days} (x1)\\n`;
                info += `   • 圆满轮次：${rounds} (x50)\\n\\n`;
                info += `⚔️ **下一位阶**：${r.next.c || '圆满'}\\n`;
                if(r.next.c) {
                    info += `   • 距离升级还需：${r.next.s - r.score} 分\\n`;
                }
                
                alert(info);
            },
    """

    # 插入到 renderStats 方法之前
    if "calculateRank" not in content:
        target_js = "renderStats() {"
        content = content.replace(target_js, js_logic + "\n            " + target_js)
        
        # 还要在 renderStats 内部调用 renderRank
        # 我们在 renderStats 函数的最后（在 innerHTML 赋值之后）加一行
        # 找到 document.getElementById('strict-grid').innerHTML = sHTML;
        last_stat_line = "document.getElementById('strict-grid').innerHTML = sHTML;"
        content = content.replace(last_stat_line, last_stat_line + "\n                this.renderRank();")
        
        print("[OK] JS 逻辑已注入")

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    update_rose_rank()
    print("-" * 30)
    print("更新完成！")
    print("玫瑰经页面现已包含【灵修位阶系统】。")
    print("请重启 Flask 服务并刷新页面查看。")