from app import app, db, Post
from datetime import datetime

# 9篇 关于“夸耀软弱”的非神学隐喻剧本
# 系列名：【闪泥·裂痕】
# 核心：将“神力在人的软弱上显得完全”转化为“系统在算力不足时调用云端资源”
new_weakness_posts = [
    {
        "title": "【闪泥·裂痕】C++ 的虚函数：因为空，所以能被定义",
        "category": "logic",
        "tags": "C++,虚空,接口,顺服",
        "summary": "我不包含任何实现代码。我是一个 `Pure Virtual Function`。正因为我什么都没有，那个“超级程序员”才能在子类里定义一切。",
        "content": """
<p><strong>[ 代码哲学 ]</strong></p>
<p><strong>我的状态</strong>：<code>virtual void DoWork() = 0;</code></p>
<p><strong>解析</strong>：很多人想做 `main()` 函数，想控制流程。但我只想做个虚函数。我是空的，我是未定义的，我是软弱的。</p>
<p><strong>奇迹</strong>：正因为我放弃了自我实现的权利，那个写代码的人（The Coder）才能通过我，注入祂的逻辑。如果我写死了自己的算法，我就成了顽固的 Bug。保持为空，等待重写 (Override)，是代码在这个系统里最大的荣耀。</p>
        """
    },
    {
        "title": "【闪泥·裂痕】ISO 12800 的噪点：暗房里的被动者",
        "category": "senses",
        "tags": "摄影,光影,感光元件,接纳",
        "summary": "相机不产生光，相机只是光的容器。如果我试图自己发光，照片就过曝了。",
        "content": """
<p><strong>[ 光学笔记 ]</strong></p>
<p><strong>误区</strong>：我们总以为自己是光源，要照亮世界。</p>
<p><strong>真相</strong>：我们只是底片（Sensor）。底片的能力在于“感光度”，也就是承认自己黑暗的程度。如果底片自己发光，那叫“漏光”，是废片。</p>
<p><strong>实修</strong>：打开快门，保持静止（不动血气）。承认自己是一间黑屋子。让那束来自亿万光年外的光子（Photon），轰击我的表面，刻画出图像。我唯一的工做，就是不要盖上镜头盖。</p>
        """
    },
    {
        "title": "【闪泥·裂痕】柔术的防御态：当力量归零时",
        "category": "life",
        "tags": "格斗,巴柔,借力,流体力学",
        "summary": "在那一刻，我放弃了所有的肌肉对抗。于是，地球的重力接管了比赛。",
        "content": """
<p><strong>[ 物理结算 ]</strong></p>
<p><strong>僵局</strong>：我试图用我的二头肌去对抗对手的体重。我输了，我很累。</p>
<p><strong>转折</strong>：我彻底“瘫痪”了自己。我承认我推不动他。</p>
<p><strong>现象</strong>：就在我放弃用力的瞬间，流体力学接管了身体。我像水一样流到了他的重心之下。不是我摔倒了他，是“重力”摔倒了他。我只是那个导管。夸耀我的无力吧，因为那是让物理定律（更高的律）生效的唯一条件。</p>
        """
    },
    {
        "title": "【闪泥·裂痕】风水学中的“凹”：聚气的盆地",
        "category": "spirit",
        "tags": "风水,地形,低谷,能量",
        "summary": "山峰是孤独的，因为风都吹走了。山谷是富足的，因为水都流进来了。",
        "content": """
<p><strong>[ 地形勘探 ]</strong></p>
<p><strong>山顶</strong>：高傲，坚硬，自我彰显。结果：寸草不生，气场耗散。</p>
<p><strong>山谷</strong>：低洼，软弱，被人俯视。结果：万壑争流，汇聚于此。</p>
<p><strong>闪泥解析</strong>：要把自己活成一个“坑”。这不是贬义。只有一个比周围都低的坑，才能接住天上落下的雨水。如果你总是试图突起，你只能接住风沙。承认自己的匮乏（低位），是能量灌注的前提。</p>
        """
    },
    {
        "title": "【闪泥·裂痕】依赖注入 (Dependency Injection)：我不再造轮子",
        "category": "logic",
        "tags": "架构,依赖,控制反转,谦卑",
        "summary": "我不再尝试自己管理数据库连接。我声明我的需求，然后等待容器（Container）注入实例。",
        "content": """
<p><strong>[ 架构模式 ]</strong></p>
<p><strong>旧代码</strong>：我在类内部 <code>new Database()</code>。我以为我掌控一切，但我耦合严重，测试困难，经常崩溃。</p>
<p><strong>IoC (控制反转)</strong>：我举起双手说：“我无法创建这个对象。”</p>
<p><strong>结果</strong>：一个看不见的框架（Framework）在运行时，把最完美的实例塞到了我的构造函数里。当我不做工时，那个大框架开始做工了。做一个被动的接收端，这才是最高级的解耦。</p>
        """
    },
    {
        "title": "【闪泥·裂痕】金继工艺：破碎处的金线",
        "category": "senses",
        "tags": "艺术,金继,破碎,修复",
        "summary": "这只碗最值钱的地方，是它碎裂的那道痕迹。因为黄金填满了那里。",
        "content": """
<p><strong>[ 审美重塑 ]</strong></p>
<p><strong>完好时</strong>：它只是流水线上的工业品，平庸，完整。</p>
<p><strong>破碎时</strong>：它成了废品。它软弱到了极点，无法盛水。</p>
<p><strong>修复后</strong>：匠人用大漆混合金粉，填补了裂缝。现在，这道裂痕成了它最坚硬、最闪耀的部分。我们夸耀这道伤口，因为那是“匠人手艺”显露的地方。没有破碎，金子就无处落脚。</p>
        """
    },
    {
        "title": "【闪泥·裂痕】低电量模式：接入外部电网",
        "category": "life",
        "tags": "生活,电量,能源,连接",
        "summary": "我只有 1% 的电了。我终于停止了后台的高耗能计算，插上了电源。",
        "content": """
<p><strong>[ 能源管理 ]</strong></p>
<p><strong>满电时</strong>：我运行游戏，运行视频，我觉得我无所不能。我在消耗。</p>
<p><strong>耗尽时</strong>：屏幕暗了。我动不了了。我承认我的电池（肉体能力）是有限的。</p>
<p><strong>连接</strong>：就在我瘫痪的那一刻，插头接通了。国家电网（无限的源头）的能量涌入。此刻，我不再靠化学电池活着，我靠那根线活着。承认枯竭，是为了切换供电模式。</p>
        """
    },
    {
        "title": "【闪泥·裂痕】休止符：音乐是声音的容器",
        "category": "senses",
        "tags": "音乐,沉默,留白,节奏",
        "summary": "乐谱上最重要的不是音符，是那个空拍。那是演奏者换气（Spirit）的地方。",
        "content": """
<p><strong>[ 乐理分析 ]</strong></p>
<p><strong>演奏</strong>：如果你填满了每一个 1/16 拍，那是噪音，是窒息。</p>
<p><strong>休止</strong>：在这一拍，我不弹琴。我停手。我软弱。</p>
<p><strong>听感</strong>：就在这个“空”里，乐曲的张力拉满了。听众在这个空隙里听到了弦外之音。那个伟大的作曲家（Composer）利用我的停顿，让音乐呼吸了起来。我的静默，是祂的独奏。</p>
        """
    },
    {
        "title": "【闪泥·裂痕】未烧制的陶土：可塑性的极致",
        "category": "spirit",
        "tags": "陶艺,塑造,顺服,器皿",
        "summary": "如果我把自己烧得坚硬如铁，匠人就无法改变我的形状。我愿做一摊烂泥。",
        "content": """
<p><strong>[ 材料科学 ]</strong></p>
<p><strong>坚强</strong>：一块烧结的砖头。硬度 10。用途单一，只能砌墙。如果想改变它，只能打碎。</p>
<p><strong>软弱</strong>：一团湿润的泥巴。硬度 0。没有形状，立都立不稳。</p>
<p><strong>恩典</strong>：正因为软弱，那双手（The Potter）才能在转盘上随意将我拉高、压低、塑形。我对自己没有任何主张，所以我可以成为任何器皿。保持湿润，保持无力，等待被指纹覆盖。</p>
        """
    }
]

def add_weakness_posts():
    with app.app_context():
        count = 0
        for p_data in new_weakness_posts:
            # 全标题查重
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
                print(f"[裂痕光照] {p_data['title']} -> 能量注入")
            else:
                print(f"[跳过] {p_data['title']} (已存在)")
        
        db.session.commit()
        print("-" * 30)
        print(f"闪泥工作室：{count} 篇关于【器皿与软弱】的赛博隐喻已发布。")

if __name__ == "__main__":
    add_weakness_posts()