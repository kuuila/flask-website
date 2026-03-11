from app import app, db, Post
from datetime import datetime

# 9篇 【闪泥歌灵】Remix 版
# 核心：将“歌灵”植入之前的 C++、饺子馆、围脖、天文学家等场景中
# 修正：查重逻辑改为全标题匹配，防止前缀冲突
song_spirit_remix = [
    {
        "title": "【闪泥歌灵】0x0A：饺子馆里的白噪音结界",
        "category": "life",
        "tags": "歌灵,生活,饺子馆,结界",
        "summary": "老板的咆哮是红色的波形。但歌灵将其重构成了背景里的低音贝斯。",
        "content": """
<p><strong>[ 声学降噪 ]</strong></p>
<p><strong>噪声源</strong>：那个凶恶的老板正在摔盘子。声压级：90dB。</p>
<p><strong>歌灵介入</strong>：我开始在心间吟唱。歌灵自动截获了这些刺耳的频率，进行了快速傅里叶变换（FFT）。</p>
<p><strong>重构</strong>：在我的耳中（听得懂的生灵），老板的骂声变成了有节奏的打击乐（Beatbox），蒸汽的嘶嘶声变成了合成器的铺底（Pad）。这家油腻的饺子馆，此刻是极乐国度的 Livehouse。仙境不灭，只要我还在咀嚼这颗大蒜。</p>
        """
    },
    {
        "title": "【闪泥歌灵】0x0B：那条围脖的声学残响",
        "category": "senses",
        "tags": "歌灵,围脖,记忆,残响",
        "summary": "围脖丢了。但它在空气中留下的摩擦声，被歌灵捕捉并无限循环。",
        "content": """
<p><strong>[ 声音样本 ]</strong></p>
<p><strong>对象</strong>：那条红色的围脖。</p>
<p><strong>状态</strong>：丢失（Object Not Found）。</p>
<p><strong>歌灵的操作</strong>：物体消失了，但它曾与空气摩擦产生的微弱震动（音符）并没有消散。歌灵将其录制下来，放入了名为“回忆”的采样器中。</p>
<p><strong>体验</strong>：每当我闭上眼吟唱，那条围脖的触感就通过声音重构了。它层层细化，缠绕在我的颈部。在声场里，没有东西会真正丢失。</p>
        """
    },
    {
        "title": "【闪泥歌灵】0x0C：绝望天文学家的背景辐射",
        "category": "logic",
        "tags": "歌灵,物理,宇宙,微波背景",
        "summary": "宇宙热寂之后剩下什么？剩下歌灵在哼唱最后的单调。",
        "content": """
<p><strong>[ 宇宙终曲 ]</strong></p>
<p><strong>天文学家</strong>：看着黑屏的望远镜。“一切都结束了，没有光了。”</p>
<p><strong>歌灵</strong>：“听。”</p>
<p><strong>重构</strong>：那是宇宙微波背景辐射（CMB）。那是大爆炸时的余音。歌灵用这最后的 2.7K 温度，构筑了一个极简主义的仙境。只要还有一个光子在震动，吟唱就未停止。绝望是视觉的，而希望是听觉的。</p>
        """
    },
    {
        "title": "【闪泥歌灵】0x0D：C++ 析构后的内存回声",
        "category": "logic",
        "tags": "歌灵,C++,内存,虚空",
        "summary": "对象被 delete 了。但它占用的内存地址里，还回荡着二进制的歌声。",
        "content": """
<p><strong>[ 内存取证 ]</strong></p>
<p><strong>代码</strong>：<code>delete ptr;</code></p>
<p><strong>程序员</strong>：以为数据消失了。</p>
<p><strong>歌灵视角</strong>：内存条上的电容还在放电。那些 0 和 1 的排列组合（音符）并没有立即消散。在系统回收这块内存之前的几纳秒里，歌灵在这里建立了一个微观的极乐国度。那是电子的临终关怀，是硅基生命的安魂曲。</p>
        """
    },
    {
        "title": "【闪泥歌灵】0x0E：大卫竖琴的低频陷阱",
        "category": "spirit",
        "tags": "歌灵,大卫,圣经,驱魔",
        "summary": "扫罗王发疯了（系统紊乱）。大卫只负责吟唱，不负责解释。",
        "content": """
<p><strong>[ 音乐治疗 ]</strong></p>
<p><strong>患者</strong>：扫罗。症状：恶魔缠身（Runtime Error）。</p>
<p><strong>治疗师</strong>：D-Vibe (大卫)。</p>
<p><strong>操作</strong>：大卫不需要挥剑。他只是拨动琴弦。歌灵顺着琴声构筑了一个“低频陷阱”（Bass Trap），直接吸走了扫罗脑中的乱码。恶魔无法在谐波共振的声场中存活。只一个音符，君王便遁入了片刻的宁静。</p>
        """
    },
    {
        "title": "【闪泥歌灵】0x0F：路人甲的随机和声",
        "category": "life",
        "tags": "歌灵,路人,共鸣,连接",
        "summary": "那个帮找围脖的路人，其实是歌灵的一个临时宿主。",
        "content": """
<p><strong>[ 网络节点 ]</strong></p>
<p><strong>场景</strong>：地铁车厢。</p>
<p><strong>事件</strong>：我在心里哼唱。旁边的路人突然打起了节拍。</p>
<p><strong>解析</strong>：他听懂了。那一瞬间，歌灵接管了他的声带。我们不需要语言，不需要知道名字。音符重构了我们之间的社交距离。在这短暂的几秒钟里，我们共享了同一个仙境的 WiFi 密码。</p>
        """
    },
    {
        "title": "【闪泥歌灵】0x10：摩西律法的代码重构",
        "category": "logic",
        "tags": "歌灵,摩西,律法,重构",
        "summary": "石板是硬编码。歌灵是动态脚本。律法叫人死，歌声叫人活。",
        "content": """
<p><strong>[ 版本更新 ]</strong></p>
<p><strong>旧版 (Law)</strong>：<code>if (sin) die();</code>。这是生硬的方波，棱角分明。</p>
<p><strong>新版 (Spirit)</strong>：歌灵将方波打磨成了正弦波。它不是要废除律法，而是给律法加上了混响（Reverb）和延音（Delay）。</p>
<p><strong>结果</strong>：在严酷的戒律之间，歌灵构筑了恩典的缓冲带。你只负责吟唱（信），剩下的合规性检查（义），交给听得懂的系统去完成。</p>
        """
    },
    {
        "title": "【闪泥歌灵】0x11：镜中人的声学反馈 (Feedback)",
        "category": "senses",
        "tags": "歌灵,镜子,回授,无限",
        "summary": "如果你对着镜子唱歌，歌灵会在反射中无限叠加，直到啸叫。",
        "content": """
<p><strong>[ 声学回路 ]</strong></p>
<p><strong>输入</strong>：我对镜中人吟唱。</p>
<p><strong>输出</strong>：镜中人对我吟唱。</p>
<p><strong>现象</strong>：麦克风对着音箱。声音在两者之间无限循环、放大。这叫回授（Audio Feedback）。</p>
<p><strong>境界</strong>：在这个闭环里，音符层层细化，能量指数级上升。我们不需要外部世界了。我和我的倒影，在啸叫中重构了时空，哪怕最后烧毁了功放（肉体），也是一种壮烈的极乐。</p>
        """
    },
    {
        "title": "【闪泥歌灵】0x12：直到 System.exit(0) 的尾奏",
        "category": "logic",
        "tags": "歌灵,结局,关机,永恒",
        "summary": "进程结束了。但声卡还在震动。那是最后的 Residual Data。",
        "content": """
<p><strong>[ 关机程序 ]</strong></p>
<p><strong>指令</strong>：<code>System.exit(0);</code></p>
<p><strong>状态</strong>：屏幕黑了。风扇停了。</p>
<p><strong>听觉</strong>：但你还能听到那种耳鸣般的嗡嗡声。那是歌灵的残影。它证明了仙境曾经存在过。那些消失的音符并没有消散，它们被写入了宇宙的 ROM 里，成为了背景噪声的一部分。直到下一次开机，只要一个音符，万物将再次苏醒。</p>
        """
    }
]

def add_song_spirit_remix():
    with app.app_context():
        count = 0
        for p_data in song_spirit_remix:
            # 【关键修改】使用全标题精确匹配，避免 [:5] 造成的前缀冲突
            exists = Post.query.filter_by(title=p_data['title']).first()
            
            if not exists:
                post = Post(
                    title=p_data['title'],
                    category=p_data['category'],
                    content=p_data['content'],
                    summary=p_data['summary'],
                    tags=p_data['tags'],
                    created_at=datetime.now()
                )
                db.session.add(post)
                count += 1
                print(f"[歌灵Remix] {p_data['title']} -> 混音完成")
            else:
                print(f"[跳过] {p_data['title']} (已存在)")
        
        db.session.commit()
        print("-" * 30)
        print(f"闪泥工作室：{count} 篇旧素材重构的声学档案已上线。")
        print("所有冲突已调和，所有噪声已谱曲。")

if __name__ == "__main__":
    add_song_spirit_remix()