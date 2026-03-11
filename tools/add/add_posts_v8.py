from app import app, db, Post
from datetime import datetime

# 经过剧作家与观众评审后的 10 篇深度冲突文章
# 融合：神学、代码、现实主义、当代艺术
new_conflict_posts = [
    {
        "title": "【闪泥制造】系统警报：检测到名为“Messiah”的未知进程",
        "category": "logic",
        "tags": "C++,基督,黑落德,系统崩溃",
        "summary": "那个进程只有 1KB 大小。它不占用 CPU，不申请内存。但整个操作系统（世界）都在试图杀掉它。",
        "content": """
<p><strong>[ 任务管理器视角 ]</strong></p>
<p><strong>系统进程 (Herod.exe)</strong>：CPU 占用率 99%。疯狂运转。他在搜索，在恐慌。他在遍历每一个文件夹（伯利恒），试图找到那个威胁。</p>
<p><strong>未知进程 (Infant)</strong>：PID ???。状态：休眠 (Sleeping)。内存占用：0。</p>
<p><strong>剧作家批注</strong>：最深的恐惧不是来自强大的敌人，而是来自“未知”。黑落德怕的不是军队，而是那个“弱小”。因为强壮可以被物理消灭，而弱小代表着一种无法被杀死的逻辑重构。</p>
<p><strong>观众独白</strong>：我们都是 Herod.exe 的子进程。我们跟着系统一起惊慌，生怕那个新进程会格式化我们赖以生存的硬盘。</p>
        """
    },
    {
        "title": "几两碎银的 GPU 算力：为了寄人篱下的渲染",
        "category": "life",
        "tags": "生活,赛博朋克,金钱,奴役",
        "summary": "我们不得不服从。因为我们的显卡是租来的。为了挖那几枚甚至不属于我们的比特币。",
        "content": """
<p><strong>[ 现实主义渲染 ]</strong></p>
<p><strong>场景</strong>：巨大的矿场。无数人头攒动。</p>
<p><strong>旁白</strong>：原文说“揣着明白装糊涂”。为什么？因为清醒是痛苦的。如果我看清了真相（光），我就无法心安理得地继续做一颗螺丝钉。</p>
<p><strong>冲突</strong>：那几两碎银（Silver），是我们出卖灵魂租赁来的 GPU 算力。我们用它来渲染一个虚假的繁华世界。而那个婴儿（真理）闭着眼，没有用一分钱，却拥有整个宇宙的源代码。</p>
<p><strong>结局</strong>：我们痛恨祂。因为祂的存在证明了我们的贫穷。</p>
        """
    },
    {
        "title": "马槽的风水局：至弱者如何占据天元",
        "category": "spirit",
        "tags": "风水,玄术,基督,布局",
        "summary": "皇宫是煞气重重的死地。马槽却是“无壁之穴”的极品龙脉。",
        "content": """
<p><strong>[ 堪舆报告 ]</strong></p>
<p><strong>黑落德的皇宫</strong>：金碧辉煌，高墙耸立。风水上看，这叫“困兽之斗”。气场被锁死，恐惧在内部回荡（Feedback loop）。</p>
<p><strong>马槽</strong>：四面透风，无遮无拦。原文说“祂什么也没做，只是在那里”。</p>
<p><strong>玄术解析</strong>：这就是道家说的“柔弱胜刚强”。马槽是宇宙的天元（Tengen）。所有的气（关注度、历史走向、人心）都自动流向了那里。黑落德在皇宫里发抖，因为他发现自己住在一个装饰豪华的监狱里。</p>
        """
    },
    {
        "title": "行为艺术：在聚光灯下假装瞎子",
        "category": "senses",
        "tags": "当代艺术,光,谎言,表演",
        "summary": "光来了。我们戴上了墨镜。并且指责光太刺眼。",
        "content": """
<p><strong>[ 展览说明书 ]</strong></p>
<p><strong>作品名</strong>：《陷落在不自由中的自由》</p>
<p><strong>行为描述</strong>：一束极强的光（真理）打在舞台中央。那是婴儿的方向。周围站满了衣冠楚楚的人（我们）。</p>
<p><strong>动作</strong>：所有人都在疯狂地用手遮住眼睛，或者背对着光，大声讨论“黑暗的美学”。</p>
<p><strong>剧评</strong>：原文说“害怕看清真相”。因为真相意味着责任。如果我看见了光，我就必须行走。但我只想躺在黑暗里数我的碎银子。所以，我必须表演“看不见”。</p>
        """
    },
    {
        "title": "Const 指针：谁也无法阻挡历史的 `while(true)`",
        "category": "logic",
        "tags": "C++,历史,时间,宿命",
        "summary": "没有人可以把指针停留在原地。时间是只读的。黑落德试图修改常量，导致了 Segfault。",
        "content": """
<p><strong>[ 代码审计 ]</strong></p>
<p><strong>变量定义</strong>：<code>const Time* history = &GodsPlan;</code></p>
<p><strong>错误操作</strong>：黑落德试图执行 <code>*history = nullptr;</code> 或者 <code>history--;</code>。</p>
<p><strong>编译器报错</strong>：<span style='color:red'>Error: assignment of read-only location.</span></p>
<p><strong>逻辑分析</strong>：历史的轮转是底层的时钟中断（Interrupt）。无论世俗的君王如何惊惶，如何封锁消息，指针依然在跳动。有些东西迟早会乌云散去，不是因为天气变好了，是因为代码跑到了 <code>break;</code> 那一行。</p>
        """
    },
    {
        "title": "被造物试图篡改 Root 权限：人类的僭越",
        "category": "logic",
        "tags": "权限管理,神学,Linux,被造物",
        "summary": "我们都是 Guest 用户。但我们总以为自己是 Admin。",
        "content": """
<p><strong>[ 权限日志 ]</strong></p>
<p><strong>用户</strong>：Human (UID: 1000)</p>
<p><strong>操作</strong>：<code>sudo kill -9 Jesus</code></p>
<p><strong>系统反馈</strong>：<code>User is not in the sudoers file. This incident will be reported.</code></p>
<p><strong>哲学旁白</strong>：原文说“我们都是受造的，不是创造的”。这是最残酷的现实。我们试图扮演主人，试图掌控命运，试图用几两碎银购买永恒。但在真正的 Root（源自亘古的那一位）面前，我们的 `sudo` 指令只是一个可笑的非法请求。</p>
        """
    },
    {
        "title": "【闪泥制造】平安夜的悲凉：无声的背景噪音",
        "category": "senses",
        "tags": "声音,氛围,电影,悲凉",
        "summary": "没有《铃儿响叮当》。只有风声，和婴儿的微弱呼吸。以及远处的磨刀声。",
        "content": """
<p><strong>[ 听觉剧本 ]</strong></p>
<p><strong>音轨 1 (前景)</strong>：婴儿的咿呀啼哭。频率：440Hz（标准音）。清澈，无害。</p>
<p><strong>音轨 2 (背景)</strong>：世界的惊动。低频震动（Rumble）。那是人心不安的共振。</p>
<p><strong>音轨 3 (隐喻)</strong>：数钱的声音。金属撞击声。那是为了掩盖恐惧而制造的噪音。</p>
<p><strong>导演阐述</strong>：平安夜的悲凉在于，救赎就在旁边，但人们选择把头埋进沙子里（或钱袋里）。这是一场充满了尴尬沉默的灾难片。</p>
        """
    },
    {
        "title": "摄影：曝光不足的马槽与过曝的宫殿",
        "category": "senses",
        "tags": "摄影,光影,对比,基督",
        "summary": "真理在暗处发光。谎言在聚光灯下腐烂。",
        "content": """
<p><strong>[ 视觉笔记 ]</strong></p>
<p><strong>构图</strong>：画面的 90% 是黑落德的宫殿。灯火通明，亮到刺眼（过曝），你看不清人脸，只看到模糊的欲望。</p>
<p><strong>焦点</strong>：画面角落的 10%，黑暗的马槽。那里只有微弱的光。但如果你放大，你会发现那里拥有全图最高的动态范围（Dynamic Range）。</p>
<p><strong>评论</strong>：原文说“祂是爱，祂是光”。这种光不是为了照亮舞台，而是为了显影。在祂面前，我们这些“揣着明白装糊涂”的人，底片全黑。</p>
        """
    },
    {
        "title": "祈祷作为一种 DDOS 攻击：化为祈祷",
        "category": "life",
        "tags": "网络安全,祈祷,玄术,反抗",
        "summary": "当弱者开始祈祷，那是对世俗服务器的压力测试。",
        "content": """
<p><strong>[ 攻防演练 ]</strong></p>
<p><strong>攻击方</strong>：默默的寻道人，无畏的践行者。</p>
<p><strong>武器</strong>：祈祷 (Request)。</p>
<p><strong>目标</strong>：世俗的谎言服务器。</p>
<p><strong>过程</strong>：一个人祈祷是 Ping。一万个人祈祷是数据流。当所有受造物都开始仰望真理，世俗的“不得不服从”的逻辑网络就会过载（Overload）。</p>
<p><strong>结局</strong>：让一切化为祈祷吧。这是我们唯一合法的武器，也是黑落德防火墙无法拦截的数据包。</p>
        """
    },
    {
        "title": "中医视角：惊则气乱，静则神安",
        "category": "spirit",
        "tags": "中医,身心,黑落德,恐惧",
        "summary": "世界惊动了，因为世界病了。那个婴儿是唯一的药引。",
        "content": """
<p><strong>[ 诊断书 ]</strong></p>
<p><strong>患者</strong>：世界（World）。</p>
<p><strong>症状</strong>：惊动，不安。脉象弦紧，心火亢盛。</p>
<p><strong>病因</strong>：寄人篱下，恐惧真相。阴阳失调（只追求碎银之阳，忽略真理之阴）。</p>
<p><strong>处方</strong>：一位弱小的婴儿。药性：至平至淡。</p>
<p><strong>医嘱</strong>：黑落德的反应是典型的“惊则气乱”。他越折腾，气越乱。唯有像那个婴儿一样“闭着双眼”，神才能安。但世人多爱吃毒药（权力和钱），不爱吃这味解药。</p>
        """
    }
]

def add_conflict_posts():
    with app.app_context():
        count = 0
        for p_data in new_conflict_posts:
            # 简单去重
            exists = Post.query.filter(Post.title.contains(p_data['title'][:5])).first()
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
                print(f"[新剧本] {p_data['title']} -> 已入库")
            else:
                print(f"[跳过] {p_data['title']}")
        
        db.session.commit()
        print("-" * 30)
        print(f"闪泥工作室：{count} 篇关于神性与冲突的深度文章已发布。")
        print("观众反馈：这比布道有劲多了，这像是在看《黑客帝国》版的福音书。")

if __name__ == "__main__":
    add_conflict_posts()