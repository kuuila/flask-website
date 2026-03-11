from app import app, db, Post
from datetime import datetime

# 10篇 基于“天蛾之茧”寓言的【闪泥甘泉】系列
# 核心精髓：挣扎是必要的流变。人为的捷径导致了存在的萎缩。
new_moth_posts = [
    {
        "title": "【闪泥甘泉】强制通过的 Unit Test：臃肿的上线",
        "category": "logic",
        "tags": "C++,测试,上线,崩溃",
        "summary": "我注释掉了所有的报错代码（剪开了茧）。程序跑起来了，但它是个怪物。",
        "content": """
<p><strong>[ 编译日志 ]</strong></p>
<p><strong>现状</strong>：代码在第 404 行卡住了。那是关于“苦难校验”的逻辑。它过不去。</p>
<p><strong>我的慈悲</strong>：我觉得编译器太残忍。于是我手动 <code>// 注释</code> 了那个校验函数，甚至用 <code>return true;</code> 伪造了通过。</p>
<p><strong>后果</strong>：上线成功。但这是一个反常的进程。它占用了 100% 的内存（臃肿），却无法处理任何并发请求（翅膀萎缩）。在生产环境的阳光下，它崩馈了。原来，那个校验过程，是为了把数据压缩进核心逻辑里。</p>
        """
    },
    {
        "title": "【闪泥甘泉】MMA 降服技：别急着拍地",
        "category": "life",
        "tags": "格斗,绞技,挣扎,体液",
        "summary": "那个细管就是裸绞。你必须在窒息中学会呼吸。",
        "content": """
<p><strong>[ 笼中对 ]</strong></p>
<p><strong>处境</strong>：对手的手臂像那条细管一样，勒住了我的颈动脉。天蛾的茧变成了八角笼。</p>
<p><strong>诱惑</strong>：裁判看着我，想终止比赛（剪刀）。我想拍地认输。</p>
<p><strong>顿悟</strong>：不。正是在这缺氧的几秒钟里，血液被挤压，求生欲被泵入四肢百骸。如果此刻有人帮我解开，我就永远练不出“抗压的脖子”。只有挤过去，我才能飞。</p>
        """
    },
    {
        "title": "【闪泥甘泉】圣神的流变学：狭窄的恩典",
        "category": "spirit",
        "tags": "神学,流变学,窄门,恩典",
        "summary": "恩典不是宽阔的大门。恩典是高压水枪。",
        "content": """
<p><strong>[ 灵性物理 ]</strong></p>
<p><strong>原理解析</strong>：为什么天蛾必须挤过细管？为了把体液从肥大的腹部压入翅膀。</p>
<p><strong>神学映射</strong>：我们就像那个肥大的虫子，充满了世俗的脂肪（欲望）。“苦难”不是为了杀死我们，而是为了充当那个高压喷嘴。只有经过极度狭窄的挤压，我们的生命力才能流向灵性的翅膀。剪开茧，就是剥夺了我们“起飞”的资格。</p>
        """
    },
    {
        "title": "【闪泥甘泉】作弊码 (Cheat Code)：被毁掉的游戏体验",
        "category": "logic",
        "tags": "游戏,作弊,虚无,反常",
        "summary": "我输入了 'whosyourdaddy'。我无敌了。我也死了。",
        "content": """
<p><strong>[ 玩家独白 ]</strong></p>
<p><strong>操作</strong>：Boss 太难打了。那个茧太厚了。我打开控制台，开启了上帝模式（剪刀）。</p>
<p><strong>结局</strong>：我一刀秒了 Boss。然后呢？我站在空荡荡的地图里，身体反常地臃肿（满级数据），翅膀反常地萎缩（毫无操作技巧）。游戏瞬间失去了意义。我赢了，但我的“玩家之魂”痛苦地爬了一会，就删号了。</p>
        """
    },
    {
        "title": "【闪泥甘泉】胶片的显影：不要打开暗房的门",
        "category": "senses",
        "tags": "摄影,暗房,耐心,光",
        "summary": "我看它在药水里挣扎得太慢，于是我开了灯。",
        "content": """
<p><strong>[ 暗房事故 ]</strong></p>
<p><strong>过程</strong>：底片在显影液（细管）里浸泡。影像在黑暗中缓慢浮现，那是一种化学的挣扎。</p>
<p><strong>干预</strong>：我失去了耐心。我想帮它快点见光。我打开了红灯之外的白炽灯（剪刀）。</p>
<p><strong>毁坏</strong>：那一瞬间，所有的层次、所有的灰度、所有细巧精致的彩纹，全部曝光过度，变成了一片死白。没有经过黑暗的挤压，光就成了杀手。</p>
        """
    },
    {
        "title": "【闪泥甘泉】廉价的慈悲：0.7 元的剪刀",
        "category": "life",
        "tags": "慈悲,伪善,代价,审判",
        "summary": "我以为我是救世主。其实我是刽子手。",
        "content": """
<p><strong>[ 道德审判 ]</strong></p>
<p><strong>道具</strong>：一把并不锋利的剪刀。成本 0.7 元。</p>
<p><strong>动机</strong>：我看不得受苦。或者说，我看不得“我看它受苦”。是为了帮它，还是为了安抚我的焦虑？</p>
<p><strong>判词</strong>：这是一种廉价的慈悲。真正的慈悲是陪伴它流血，是守在细管旁边祷告，而不是动手破坏规则。我的“好心”，是对造物主精密算法的傲慢干涉。</p>
        """
    },
    {
        "title": "【闪泥甘泉】被催熟的 AI：没有经过拟合的模型",
        "category": "logic",
        "tags": "AI,训练,过拟合,智障",
        "summary": "我跳过了数万次的迭代训练。直接把参数调到了最大。",
        "content": """
<p><strong>[ 模型训练 ]</strong></p>
<p><strong>Epoch</strong>：本该进行 10000 次的 Loss Function 挣扎。</p>
<p><strong>干预</strong>：我手动修改了权重，试图让它直接“顿悟”（剪开茧）。</p>
<p><strong>产物</strong>：一个只会复读、逻辑混乱的 AI。它的词汇量很肥大（臃肿），但它的推理能力为零（翅膀萎缩）。没有经过梯度的下降与回传，智能就无法涌现。</p>
        """
    },
    {
        "title": "【闪泥甘泉】风水中的“穿堂煞”：气需要回旋",
        "category": "spirit",
        "tags": "风水,气场,阻碍,直冲",
        "summary": "不管是房子还是虫子，太直的路都是死路。",
        "content": """
<p><strong>[ 堪舆原理 ]</strong></p>
<p><strong>细管</strong>：这就是风水里的“玄关”或“影壁”。它的作用是阻挡直冲的气流，迫使气流回旋、压缩、凝聚。</p>
<p><strong>剪刀</strong>：把玄关拆了。让大门直通阳台。</p>
<p><strong>结果</strong>：气散了。蛾子体内的“气”没有经过压缩，无法冲入翅膀的经络。那个球形的囊（积聚）一旦失去了细管（转化），就成了死水一潭。</p>
        """
    },
    {
        "title": "【闪泥甘泉】拔苗助长的神学版：不想背十字架的信徒",
        "category": "spirit",
        "tags": "十字架,捷径,成功神学,苦难",
        "summary": "我们想要复活的荣耀，却不想经过骷髅地的细管。",
        "content": """
<p><strong>[ 信仰偏差 ]</strong></p>
<p><strong>愿望</strong>：主啊，剪开这个茧吧。拿走我的贫穷，拿走我的病痛，让我直接飞。</p>
<p><strong>回应</strong>：上帝放下了剪刀。祂指着那条极细的管儿——那是十字架的道路。</p>
<p><strong>真相</strong>：如果我们不经过那个“死荫的幽谷”，我们的灵性就会像那只蛾子一样，肥大而软弱。只有被钉死过的生命，才能展开复活的翅膀。</p>
        """
    },
    {
        "title": "【闪泥甘泉】蝴蝶效应的终局：一次微小的善意毁灭",
        "category": "logic",
        "tags": "混沌,蝴蝶效应,善意,毁灭",
        "summary": "我在这个早晨剪开了一个茧。导致了遥远未来的某种灭绝。",
        "content": """
<p><strong>[ 系统推演 ]</strong></p>
<p><strong>输入</strong>：一次微小的“帮助”。剪断两根丝。</p>
<p><strong>输出</strong>：一只不寿而终的蛾子。</p>
<p><strong>宏观影响</strong>：这只蛾子本该在今晚授粉一朵夜开的百合。百合枯萎了。某种生态链断裂了。我以为我比造物主更智慧，但我只是向精密的宇宙代码里，注入了一个名为“溺爱”的病毒。</p>
        """
    }
]

def add_moth_spring_posts():
    with app.app_context():
        count = 0
        for p_data in new_moth_posts:
            # 查重：如果有相同标题的，跳过
            exists = Post.query.filter(Post.title.contains(p_data['title'])).first()
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
                print(f"[甘泉注入] {p_data['title']} -> 发布成功")
            else:
                print(f"[跳过] {p_data['title']} (已存在)")
        
        db.session.commit()
        print("-" * 30)
        print(f"闪泥工作室：{count} 篇【闪泥甘泉】系列文章已上线。")
        print("请观众细细品尝这份来自苦难的甘甜。")

if __name__ == "__main__":
    add_moth_spring_posts()