from app import app, db, Post
from datetime import datetime

# 10篇 重构后的《围脖寻踪》
# 新增元素：队友离合（聚散）、路人善意（恩典）、老板凶恶（阻力）
# 核心标签：爱（Top Tag）
new_revised_scarf_posts = [
    {
        "title": "【闪泥制造】饺子馆老板的咆哮：拒绝访问的防火墙",
        "category": "logic",
        "tags": "爱,冷漠,饺子馆,冲突",
        "summary": "老板挥舞着漏勺，像驱赶苍蝇一样驱赶我们。'没看见！别耽误我做生意！滚出去！'",
        "content": """
<p><strong>[ 阻断攻击 ]</strong></p>
<p><strong>角色</strong>：饺子馆老板 (NPC_Villain)。油腻，暴躁，眼神如刀。</p>
<p><strong>动作</strong>：我们试图查看监控。他猛地拍桌子，震得醋碟乱跳。</p>
<p><strong>台词</strong>：“丢了活该！这里不是失物招领处！再不点菜就滚！”</p>
<p><strong>闪泥解析</strong>：他不是一个人，他是一堵墙。他代表了世界对他人的绝对冷漠。在他的逻辑里，一条承载回忆的围脖（Data），价值低于一盘 15 块钱的韭菜鸡蛋水饺。这是资本主义最底层的凶恶——对“无利可图之物”的蔑视。</p>
        """
    },
    {
        "title": "【闪泥制造】路人的手电筒：随机的恩典注入",
        "category": "senses",
        "tags": "爱,路人,光,温暖",
        "summary": "车厢暗处。一个陌生人打开了手机闪光灯。'是这个吗？'",
        "content": """
<p><strong>[ 光影渲染 ]</strong></p>
<p><strong>环境</strong>：昏暗的座位底下。灰尘飞舞。</p>
<p><strong>事件</strong>：我们正绝望时，一束强光打入黑暗。一个疲惫的上班族（Passerby）趴在地上，帮我们寻找。</p>
<p><strong>台词</strong>：“我看你们找半天了。别急，再仔细看看缝隙。”</p>
<p><strong>隐喻</strong>：他与我们无亲无故。他的善意是系统溢出的 Bug，是不求回报的算力支持。在老板的咆哮声之后，这束光显得如此刺眼。爱，往往来自匿名用户。</p>
        """
    },
    {
        "title": "【闪泥制造】队友的离去：线程的分叉",
        "category": "life",
        "tags": "爱,离合,队友,疲惫",
        "summary": "走到第三个路口。队友停下了。'只是一条围脖而已，值得吗？'",
        "content": """
<p><strong>[ 剧情分支 ]</strong></p>
<p><strong>队友 A</strong>：陪跑了三公里。累了。看不到希望。</p>
<p><strong>冲突</strong>：“我还有事，先撤了。买条新的吧。”他转过身，融入人海。</p>
<p><strong>心理活动</strong>：看着他的背影，我感到了比丢东西更深的失落。寻找的过程是一台离心机，它甩掉了那些不够坚定的连接。聚散是常态，陪你走到终点的人，比终点更稀有。</p>
        """
    },
    {
        "title": "【闪泥制造】圣安东尼前的控诉：为何恶人横行",
        "category": "spirit",
        "tags": "爱,祷告,善恶,圣安东尼",
        "summary": "我们在教堂跪下。不是为了求围脖，是为了求安慰。那个老板的脸太凶了。",
        "content": """
<p><strong>[ 神学辩论 ]</strong></p>
<p><strong>祷告词</strong>：“圣安东尼啊，为什么？我们只是想找回心爱之物，为什么要遭遇那样的羞辱？”</p>
<p><strong>回应</strong>：圣像沉默。但在沉默中，我们想起了那个帮我们打手电筒的路人。</p>
<p><strong>领悟</strong>：世界是平衡的。魔鬼（凶恶老板）负责制造障碍，天使（路人）负责提供梯子。而圣安东尼负责看着我们，看我们在善恶夹缝中，是否依然选择继续寻找。</p>
        """
    },
    {
        "title": "【闪泥制造】画展里的重逢与告别：新的队友加入",
        "category": "senses",
        "tags": "爱,画展,路人,循环",
        "summary": "旧的队友走了。一个看画的女孩听到了我们的对话，加入了队伍。",
        "content": """
<p><strong>[ 动态组队 ]</strong></p>
<p><strong>场景</strong>：安静的画廊。</p>
<p><strong>女孩 (New_Member)</strong>：“我也丢过东西。我懂那种感觉。我帮你们问问策展人。”</p>
<p><strong>闪泥解析</strong>：这就是爱的流动性（Fluidity）。当你因为执着（Loop）而发出信号，总会吸引同频的信号。旧的线程结束（Terminated），新的线程启动（Spawned）。寻找围脖的队伍，变成了一个流动的社区。</p>
        """
    },
    {
        "title": "【闪泥制造】垃圾桶翻找实录：尊严的抛售",
        "category": "life",
        "tags": "爱,老板,垃圾,尊严",
        "summary": "老板指着门口的泔水桶：'要找自己翻去！' 我们真的翻了。",
        "content": """
<p><strong>[ 极端特写 ]</strong></p>
<p><strong>画面</strong>：手伸进泔水。油污。恶臭。老板在旁边冷笑。</p>
<p><strong>姐妹</strong>：没有哭。眼神坚定。一点点翻找。</p>
<p><strong>核心标签</strong>：<code>&lt;LOVE&gt;</code></p>
<p><strong>旁白</strong>：爱是什么？爱就是为了对方，可以把尊严踩在脚下。那一刻，老板的凶恶显得如此渺小，而沾满油污的手显得如此圣洁。我们在垃圾里，确认了彼此的羁绊。</p>
        """
    },
    {
        "title": "【闪泥制造】车厢内的陌生回音：全车广播",
        "category": "senses",
        "tags": "爱,路人,广播,希望",
        "summary": "列车员听到了我们的恳求。'各位乘客，刚才有人丢了一条红色围脖……'",
        "content": """
<p><strong>[ 广播通知 ]</strong></p>
<p><strong>声音</strong>：电流麦。穿透了嘈杂的车厢。</p>
<p><strong>反应</strong>：低头玩手机的人们抬起了头。有人翻看自己的包，有人询问邻座。冷漠的车厢瞬间变成了一个协作网络（P2P Network）。</p>
<p><strong>结果</strong>：虽然没找到。但那一刻，几百个陌生人的注意力汇聚在一条不存在的围脖上。这种集体性的善意，是对那个凶恶老板最有力的反击。</p>
        """
    },
    {
        "title": "【闪泥制造】分道扬镳的路口：理智与情感的 Bug",
        "category": "logic",
        "tags": "爱,离合,逻辑,分歧",
        "summary": "队友 B：'根据概率论，找回的可能性为 0.01%。我止损了。' 他是对的，但他错了。",
        "content": """
<p><strong>[ 逻辑错误 ]</strong></p>
<p><strong>队友 B (理性派)</strong>：试图用 ROI（投资回报率）来计算这场寻找。时间成本 > 围脖价值。</p>
<p><strong>我们 (感性派)</strong>：继续寻找。</p>
<p><strong>解析</strong>：队友 B 没有错，他遵循的是经济学算法。但爱是 Bug。爱是明知概率为 0，依然执行 <code>try...catch</code>。他的离去，是因为他的 CPU 无法处理“非理性”的数据。</p>
        """
    },
    {
        "title": "【闪泥制造】老板的诅咒与路人的糖果：世界的两极",
        "category": "spirit",
        "tags": "爱,善恶,对比,慰藉",
        "summary": "被赶出饺子馆时，一个小女孩递给我们一颗糖。'姐姐别哭。'",
        "content": """
<p><strong>[ 蒙太奇 ]</strong></p>
<p><strong>镜头 A</strong>：老板狰狞的脸。“滚！”（地狱的火）</p>
<p><strong>镜头 B</strong>：小女孩稚嫩的手。大白兔奶糖。（天堂的光）</p>
<p><strong>独白</strong>：世界就是这样撕裂。左手是恶意，右手是治愈。我们在这一天之内，经历了人性的极夜与极昼。这颗糖，融化了刚才所有的委屈。</p>
        """
    },
    {
        "title": "【闪泥制造】终局：作为源头的爱（修正版）",
        "category": "life",
        "tags": "爱,结局,源头,所有",
        "summary": "围脖丢了。队友散了。但我们看清了谁是恶魔，谁是天使。",
        "content": """
<p><strong>[ 演职员表 ]</strong></p>
<p><strong>主演</strong>：我，姐妹。</p>
<p><strong>反派</strong>：饺子馆老板（感谢你教会我世界的残酷）。</p>
<p><strong>客串</strong>：路人甲乙丙（感谢你们证明了神的存在）。</p>
<p><strong>离场</strong>：前队友（感谢陪伴，祝好）。</p>
<p><strong>总结</strong>：这是一场关于“筛选”的旅途。围脖的丢失，是为了让我们筛选出真正重要的人。物体是虚空的，但我们在对抗冷漠、接受离别时产生的那股力量，名为爱。它是痛的，但它是活的。</p>
        """
    }
]

def add_revised_scarf_posts():
    with app.app_context():
        count = 0
        for p_data in new_revised_scarf_posts:
            exists = Post.query.filter(Post.title.contains(p_data['title'][:15])).first()
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
                print(f"[围脖寻踪·修正] {p_data['title']} -> 录入胶卷")
            else:
                print(f"[跳过] {p_data['title']}")
        
        db.session.commit()
        print("-" * 30)
        print(f"闪泥工作室：{count} 篇包含众生相（离合/善意/凶恶）的剧本已发布。")
        print("提示：这不仅仅是找东西，这是社会的横切面。")

if __name__ == "__main__":
    add_revised_scarf_posts()
