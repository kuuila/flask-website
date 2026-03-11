from app import app, db, Post
from datetime import datetime

# 9篇 关于“慈悲”的跨界剧本
# 系列名：【闪泥之磁】
# 修正：查重逻辑改为全标题匹配，防止因前缀相同导致误判
new_magnetic_posts = [
    {
        "title": "【闪泥之磁】C++ 的析构函数：唯一的负熵流",
        "category": "logic",
        "tags": "C++,物理学,熵增,慈悲",
        "summary": "宇宙的本质是熵增（混乱）。而慈悲是唯一的负熵（有序）。我们在代码中寻找那个逆转热力学定律的算法。",
        "content": """
<p><strong>[ 系统底层逻辑 ]</strong></p>
<p><strong>现状</strong>：社会系统正在经历高强度的熵增（Entropy）。冲突、仇恨、内卷，这些都是系统过热产生的废热。</p>
<p><strong>操作</strong>：调用 <code>Compassion()</code> 函数。</p>
<p><strong>解析</strong>：慈悲不是一种情绪，它是一种物理学现象。它是一个“耗散结构”的冷却剂。当你选择宽恕（Forgiveness），你实际上是在切断一个正反馈的混乱回路（Loop），并注入了一股“负熵流”。</p>
<p><strong>结局</strong>：该函数不返回任何值（Void），但它重置了系统的有序性。慈悲，就是用你的 CPU 算力，去抵消宇宙的混乱。</p>
        """
    },
    {
        "title": "【闪泥之磁】镜像神经元：无需光缆的悲伤传输",
        "category": "senses",
        "tags": "摄影,神经科学,少女,镜像",
        "summary": "为什么看她的照片你会流泪？因为你的大脑正在运行模拟程序。",
        "content": """
<p><strong>[ 神经美学 ]</strong></p>
<p><strong>场景</strong>：取景器里的少女在哭泣。光圈 f/1.2。</p>
<p><strong>生理反应</strong>：摄影师并未触碰她，但他的前扣带皮层（ACC）亮了。这是“镜像神经元”（Mirror Neurons）在放电。</p>
<p><strong>闪泥旁白</strong>：摄影不是捕捉光线，而是通过视觉信号，远程激活观众脑内的痛苦回路。当我们说“这张照片有灵魂”，其实是说“我的镜像神经元正在高频共振”。慈悲，就是一种生物学上的无线传输协议。</p>
        """
    },
    {
        "title": "【闪泥之磁】博弈论最优解：街头霸王的宽恕连招",
        "category": "logic",
        "tags": "游戏,博弈论,格斗,算法",
        "summary": "在街霸（Street Fighter）的无限局中，最优解不是连招，而是宽恕。",
        "content": """
<p><strong>[ 算法模拟 ]</strong></p>
<p><strong>游戏</strong>：囚徒困境（The Prisoner's Dilemma），重复 10000 轮。</p>
<p><strong>策略 A</strong>：总是背叛（恶）。收益：短期高，长期归零（被系统隔离）。</p>
<p><strong>策略 B</strong>：总是合作（圣母）。收益：被吃干抹净。</p>
<p><strong>策略 C (Tit-for-tat with Forgiveness)</strong>：你打我，我反击；但如果你停手，我立刻原谅你。这是慈悲的算法化。</p>
<p><strong>结论</strong>：慈悲不是软弱，它是数学证明后的纳什均衡。在长期的格斗中，给对手留一个“重启键”，是胜率最高的打法。</p>
        """
    },
    {
        "title": "【闪泥之磁】催产素风水局：屋内的生物磁场重构",
        "category": "spirit",
        "tags": "风水,中医,生物学,催产素",
        "summary": "不需要改大门朝向。只需要你分泌一点催产素。",
        "content": """
<p><strong>[ 环境内分泌学 ]</strong></p>
<p><strong>风水师</strong>：“这屋子煞气太重。”</p>
<p><strong>生物黑客</strong>：“那是因为居住者的皮质醇（压力荷尔蒙）超标了。”</p>
<p><strong>改造方案</strong>：不是摆放水晶，而是进行一次拥抱，或者一次慈心的布施。这会刺激大脑分泌催产素（Oxytocin）。</p>
<p><strong>原理</strong>：催产素能降低杏仁核的活跃度。当居住者的生物场（Bio-field）变得柔和，所谓的“风水”自然就顺了。慈悲，就是人体自带的镇宅之宝。</p>
        """
    },
    {
        "title": "【闪泥之磁】量子纠缠：非洲草原上的波函数坍缩",
        "category": "spirit",
        "tags": "非洲哲学,物理学,量子,玄术",
        "summary": "在非洲的草原上，量子物理学家听懂了部落长老的话。",
        "content": """
<p><strong>[ 跨文化对谈 ]</strong></p>
<p><strong>长老</strong>：“Ubuntu（乌班图）。我存在，因为我们存在。”</p>
<p><strong>物理学家</strong>：“这叫量子纠缠（Quantum Entanglement）。两个粒子一旦发生作用，它们就不再是独立的个体，而是一个波函数。”</p>
<p><strong>闪泥解析</strong>：伤害他人为什么会反噬？因为在波函数的层面，并没有“他人”。慈悲不是一种道德要求，它是对物理实相（Reality）的客观描述。自私，是一种视力缺陷。</p>
        """
    },
    {
        "title": "【闪泥之磁】格斗家的 0.3 秒：杏仁核劫持前的慈悲",
        "category": "life",
        "tags": "格斗,正念,修行,神经可塑性",
        "summary": "拳头飞过来。在杏仁核尖叫之前，他插入了 3 秒钟的慈悲。",
        "content": """
<p><strong>[ 慢动作渲染 ]</strong></p>
<p><strong>刺激</strong>：路人的辱骂。
<strong>本能反应</strong>：杏仁核劫持（Amygdala Hijack）。战斗模式开启。</p>
<p><strong>高手操作</strong>：在刺激与反应之间，强行撕开一个“正念缝隙”（The Gap）。深呼吸。迷走神经张力恢复。</p>
<p><strong>内心独白</strong>：“他也是个受苦的灵魂。”</p>
<p><strong>结果</strong>：拳头放下了。这比击倒对手更难。这是对自己大脑神经回路的现场重塑。</p>
        """
    },
    {
        "title": "【闪泥之磁】骷髅地的去标签化：看穿罗马盔甲的恐惧",
        "category": "spirit",
        "tags": "基督,心理学,去标签,救赎",
        "summary": "他看着钉死他的人，剥离了“罗马士兵”这个标签。",
        "content": """
<p><strong>[ 认知重构 ]</strong></p>
<p><strong>场景</strong>：骷髅地。</p>
<p><strong>常规认知</strong>：这是一群恶徒，刽子手，敌人。</p>
<p><strong>神之视角</strong>：De-labeling（去标签化）。他看到的不是“恶人”，而是“恐惧的人”、“无知的人”、“被体制裹挟的生物体”。</p>
<p><strong>台词</strong>：“父啊，赦免他们，因为他们所做的，他们不晓得。”</p>
<p><strong>解析</strong>：慈悲的最高境界，是透过厚厚的社会面具，看到那个赤裸、颤抖、充满匮乏的生命内核。</p>
        """
    },
    {
        "title": "【闪泥之磁】悲智双运：拒绝做烂好人的防火墙策略",
        "category": "logic",
        "tags": "网络安全,边界,智慧,慈悲",
        "summary": "没有防火墙的服务器不是慈悲，是裸奔。",
        "content": """
<p><strong>[ 安全策略 ]</strong></p>
<p><strong>误区</strong>：傻瓜慈悲（Idiot Compassion）。为了不让黑客（索取者）不高兴，而开放所有端口。</p>
<p><strong>真相</strong>：真正的慈悲需要智慧（Prajna）。就像配置 <code>iptables</code>。</p>
<p><strong>操作</strong>：<code>DROP</code> 那些恶意的请求。这不是冷酷，这是为了保护系统的核心服务（Core Service），以便能持续为更多人提供价值。当你拒绝勒索软件时，你是在教它规则。这也是一种慈悲。</p>
        """
    },
    {
        "title": "【闪泥之磁】巴赫的审美替代：大提琴里的同体大悲",
        "category": "senses",
        "tags": "音乐,声音,美学,同体大悲",
        "summary": "戴上耳机。巴赫的大提琴是全人类的哭声。",
        "content": """
<p><strong>[ 听觉实验 ]</strong></p>
<p><strong>素材</strong>：巴赫《G大调第一大提琴组曲》。</p>
<p><strong>体验</strong>：为什么你会哭？因为艺术提供了一种“审美替代”。在那一瞬间，你的自我（Ego）边界溶解了。</p>
<p><strong>闪泥解析</strong>：你不再是你。你变成了那个拉琴的人，变成了那个作曲的人，甚至变成了那棵做成琴的树。这种“无我”的震颤，就是慈悲的声学表现。音乐是让人类体验“同体大悲”的模拟器。</p>
        """
    }
]

def add_magnetic_posts():
    with app.app_context():
        count = 0
        for p_data in new_magnetic_posts:
            # 修正：使用完整标题查重，避免 "【闪泥之磁】" 前缀导致误判
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
                print(f"[磁场生成] {p_data['title']} -> 入库")
            else:
                print(f"[跳过] {p_data['title']} (已存在)")
        
        db.session.commit()
        print("-" * 30)
        print(f"闪泥之磁：{count} 篇跨学科慈悲剧本已上线。")

if __name__ == "__main__":
    add_magnetic_posts()