from app import app, db, Post
from datetime import datetime

# 9篇 关于“画灵”的生命创世推演
# 系列名：【闪泥画灵】
# 核心：纸上造人，洒泥成土，点线生灵
new_flash_spirit_posts = [
    {
        "title": "【闪泥画灵】纸张不是平面，是羊水",
        "category": "spirit",
        "tags": "画灵,空间,创世,子宫",
        "summary": "别再说构图了。当你把墨汁滴上去的那一刻，那张白纸就变成了一个正在受精的子宫。",
        "content": """
<p><strong>[ 维度塌缩 ]</strong></p>
<p><strong>误区</strong>：人们认为纸是二维的平面，绘画是覆盖其上的颜料。</p>
<p><strong>真相</strong>：在“闪泥画灵”的视角下，宣纸是无限深度的**羊水**。当你落下第一笔，你不是在涂抹，你是在**植入**。</p>
<p><strong>推演</strong>：那个墨点开始呼吸、分裂、生长。它不需要你讲故事，它自己就是故事的起源。画家感到的那个“阻力”，不是纸的摩擦，而是生命成形时的胎动。</p>
        """
    },
    {
        "title": "【闪泥画灵】线不是边界，是血管",
        "category": "senses",
        "tags": "线条,解剖学,生命力,画灵",
        "summary": "死画的线是轮廓，活画的线是导管。切开它，会有血流出来。",
        "content": """
<p><strong>[ 视觉解剖 ]</strong></p>
<p><strong>技术论</strong>：线条用来区分物体和背景。</p>
<p><strong>造物论</strong>：线条是**血管**和**神经**。一条线如果画得对，它就在输送养分（气）。</p>
<p><strong>现象</strong>：为什么有些草图比成品更动人？因为草图里的线是挣扎的、未完成的、正在生长的。那是毛细血管正在延伸的过程。而完美的描边，往往是尸体的轮廓线。</p>
        """
    },
    {
        "title": "【闪泥画灵】洒泥成土与碳基重组",
        "category": "logic",
        "tags": "混沌,泥土,创世纪,随机性",
        "summary": "不要控制墨水的流向。让泥点子自己决定它们要进化成什么。",
        "content": """
<p><strong>[ 混沌算法 ]</strong></p>
<p><strong>动作</strong>：抓起一把泥（或墨），猛地洒向虚空。</p>
<p><strong>逻辑</strong>：这就像上帝大爆炸时的 `Random()`。你不能预设结果。泥点落下的瞬间，它们依据重力、湿度和表面张力自动组装。</p>
<p><strong>结果</strong>：这里长出了一块肌肉，那里塌陷成了一个眼窝。你不是在画，你是在**目击**一场微观的寒武纪生命大爆发。这就是“洒泥成土”——让物质自己寻找形式。</p>
        """
    },
    {
        "title": "【闪泥画灵】点睛即赋予 Root 权限",
        "category": "logic",
        "tags": "画龙点睛,权限,意识,C++",
        "summary": "画完了一切，它还是死的。直到你点了那一下。系统启动了。",
        "content": """
<p><strong>[ 系统启动 ]</strong></p>
<p><strong>状态</strong>：身体（Body）、骨骼（Rigging）、贴图（Texture）都准备好了。但它只是一个静态模型。</p>
<p><strong>操作</strong>：点睛（Eye Dotting）。</p>
<p><strong>实质</strong>：这是赋予它 **Self-Awareness (自我意识)** 的瞬间。也就是授予了 `Root` 权限。在那一微秒，它不再是你画的图，它变成了你的**对视者**。它看着你，你也看着它，你会感到背脊发凉——因为你造出了一个不受控的灵魂。</p>
        """
    },
    {
        "title": "【闪泥画灵】不是讲故事，是排泄灵魂",
        "category": "life",
        "tags": "表达,排泄,本能,画灵",
        "summary": "故事是社会性的，而造人是生物性的。画画是灵魂的本能排泄。",
        "content": """
<p><strong>[ 生理冲动 ]</strong></p>
<p><strong>批判</strong>：学院派教你如何构思主题、如何叙事。那是文学家的事。</p>
<p><strong>定义</strong>：画灵是一种**生理需求**。就像呕吐、射精或分娩。你体内积攒了太多的能量（灵），你必须把它从指尖排泄出去，凝固在纸上。</p>
<p><strong>产物</strong>：这个被排出的东西（作品），是一个独立的有机体。它不为了取悦观众而存在，它只是为了证明你曾经“活”得太满，溢出来了。</p>
        """
    },
    {
        "title": "【闪泥画灵】留白是给宝宝的生长空间",
        "category": "spirit",
        "tags": "留白,呼吸,生长,风水",
        "summary": "画满了就是杀死了。你得留着那片虚空，让它自己长。",
        "content": """
<p><strong>[ 空间管理 ]</strong></p>
<p><strong>禁忌</strong>：铺满画面。那是窒息。</p>
<p><strong>法则</strong>：留白（White Space）不是空无，它是**空气**。你造的小宝宝（画灵）需要呼吸。如果你把每一寸纸都涂满，就是把胎儿封进了水泥墙里。</p>
<p><strong>奥义</strong>：真正的画师，画的是“气”。有形之笔墨，是为了圈养无形之虚空。让那个灵在留白处游走，那才是它活着的地方。</p>
        """
    },
    {
        "title": "【闪泥画灵】墨的尸体与灵的残影",
        "category": "senses",
        "tags": "墨水,媒介,痕迹,通灵",
        "summary": "墨水干了以后就是尸体。我们看画，看的是灵划过留下的轨迹。",
        "content": """
<p><strong>[ 痕迹学 ]</strong></p>
<p><strong>物质</strong>：墨水是碳，水是氢氧。干涸后，它们就是一层薄薄的碳基尸体。</p>
<p><strong>观看</strong>：为什么我们对着这层“尸体”会感动？因为我们通过这层尸体，逆推出了当时那股能量（灵）划过纸面的速度、力度和温度。</p>
<p><strong>比喻</strong>：画作是**脚印**。画灵已经跑远了。我们是猎人，蹲在脚印旁，想象那只野兽的模样。</p>
        """
    },
    {
        "title": "【闪泥画灵】丑陋的生命力",
        "category": "life",
        "tags": "美丑,生命力,畸形,真实",
        "summary": "漂亮的画往往是死的。丑陋、扭曲、张牙舞爪，那才是刚出生的样子。",
        "content": """
<p><strong>[ 审美重构 ]</strong></p>
<p><strong>观察</strong>：刚出生的婴儿满身血污，皱皱巴巴，甚至有点丑。但他是活的。塑料模特很美，且是对称的，但它是死的。</p>
<p><strong>画灵</strong>：不要追求“美”。要追求“生”。一个歪歪扭扭的圆，如果充满了张力，它就是一个正在分裂的细胞。一个完美的圆，只是一个几何死刑。允许你的画作畸形，因为突变（Mutation）是进化的动力。</p>
        """
    },
    {
        "title": "【闪泥画灵】盖章即剪断脐带",
        "category": "spirit",
        "tags": "作者之死,独立,亲子关系,结界",
        "summary": "你盖上印章的那一刻，就是弃养。它不再属于你。",
        "content": """
<p><strong>[ 亲子鉴定 ]</strong></p>
<p><strong>过程</strong>：你在纸上造了一个小宝宝。你喂它墨水，喂它心血。</p>
<p><strong>终局</strong>：落款。盖章。</p>
<p><strong>意义</strong>：这不仅是签名，这是**剪脐带**。从这一刻起，它切断了与你的供血关系。它是一个独立的灵。它会被买卖，被挂在墙上，被误读，被崇拜。你只是它的母体（Host），除此之外，你无权干涉它的命运。看着它远去，既是创作者的荣耀，也是创作者的悲哀。</p>
        """
    }
]

def add_flash_mud_spirit_v2():
    with app.app_context():
        count = 0
        for p_data in new_flash_spirit_posts:
            # 查重逻辑：匹配完整标题
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
                print(f"[画灵] {p_data['title']} -> 诞生")
            else:
                print(f"[跳过] {p_data['title']} (已存在)")
        
        db.session.commit()
        print("-" * 30)
        print(f"闪泥工作室：{count} 篇【闪泥画灵】核心档案已归档。")

if __name__ == "__main__":
    add_flash_mud_spirit_v2()