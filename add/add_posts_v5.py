from app import app, db, Post
from datetime import datetime

# 闪泥电影工作室 (Flash Mud Studios) - 0.7元成本制作目录
# 核心机制：通过文字催化剂，强制观众大脑进行显卡级渲染
flash_mud_scripts = [
    {
        "title": "【闪泥制造】001号：商贩与天文学家的视界交易",
        "category": "logic",
        "tags": "颅内观影,低成本,引力波",
        "summary": "制作成本：0.7元（用于电费）。请闭眼想象：你的瞳孔就是黑洞的奇点。",
        "content": """
<p><strong>[ 闪泥工作室作品 / 渲染引擎：你的想象力 ]</strong></p>
<p><strong>场景提示：</strong> 你正站在宇宙的边缘，脚下是悬空的。没有氧气，只有商贩的叫卖声。</p>
<p><strong>商贩</strong>：手里捏着一枚生锈的硬币（听觉提示：金属摩擦声）。他说：“这枚硬币买不到面包，但能买到你对他人的渴望。也就是——重力。”</p>
<p><strong>天文学家</strong>：他的眼睛流出的不是血，是液态的星光（视觉渲染：高对比度）。他惨叫：“别买！那是撞击！那是毁灭！”</p>
<p><strong>[ 观众指令 ]</strong>：此刻，请调动你的杏仁核。感受那颗陨石（也就是“爱”）正以光速撞向你的眉心。不要躲避。撞击发生的瞬间，就是本片的结尾。</p>
<p><strong>>>> 渲染结束。</strong></p>
        """
    },
    {
        "title": "【闪泥制造】002号：二维生物被猫爪按死的那一帧",
        "category": "senses",
        "tags": "维度打击,恐怖,高潮",
        "summary": "这一场戏没有画面。因为你是二维的。你只能感受到'压迫感'。",
        "content": """
<p><strong>[ 摄影机位置：屏幕内部 ]</strong></p>
<p><strong>设定：</strong> 你是一个像素点。你只有 X 轴和 Y 轴。</p>
<p><strong>事件：</strong> 巨大的、毛茸茸的、带着温度的肉垫（Tlapak）从 Z 轴（上帝视角）降临。你看不见它，你只能感到世界变黑了，空气被挤压。</p>
<p><strong>喵星人</strong>：“这一按，值七毛钱吗？”</p>
<p><strong>你（观众）</strong>：在你的脑海里，重构那种被降维打击的窒息感。这不是可爱的猫，这是克苏鲁级别的巨兽。你的大脑现在应该充满了被挤爆的幻痛。</p>
<p><strong>>>> 信号丢失。</strong></p>
        """
    },
    {
        "title": "【闪泥制造】003号：嫖客与镜中人的无限反射",
        "category": "life",
        "tags": "自恋,闭环,心理惊悚",
        "summary": "道具：一面镜子（0.5元），一支蜡烛（0.2元）。主演：你。",
        "content": """
<p><strong>[ 剧本片段 ]</strong></p>
<p><strong>嫖客</strong>：对着镜子掏出钞票。“给我一个拥抱。”</p>
<p><strong>镜中人</strong>：没有伸手。镜子里的那个人，手里拿的是刀。</p>
<p><strong>[ 脑内放映指南 ]</strong>：</p>
<ol>
<li>想象你面前有一面镜子。</li>
<li>镜子里的人眨眼了，但你没有眨眼。</li>
<li>那个“你”露出一个陌生的微笑。</li>
</ol>
<p><strong>导演旁白</strong>：你爱的不是别人，是你自己投射出的幻影。当你试图拥抱镜子，你只会被玻璃割伤。感受那个痛觉——那是真实的冷。</p>
        """
    },
    {
        "title": "【闪泥制造】004号：魔术师把观众变成了鸽子",
        "category": "senses",
        "tags": "催眠,视觉欺骗,异化",
        "summary": "这不是魔术表演。这是一场关于认知的格式化手术。",
        "content": """
<p><strong>[ 催化剂 ]</strong></p>
<p><strong>魔术师</strong>：看着我的手。不要眨眼。你的眼皮很重……你不是在看屏幕，你在一个黑箱子里。</p>
<p><strong>眼皮族</strong>：“我们缝上了眼睛，因为真相太刺眼。”</p>
<p><strong>突发事件</strong>：魔术师打了一个响指（听觉触发）。你突然发现，你的手变成了翅膀。你被塞进了袖子里。这里很挤，全是汗味和滑石粉的味道。</p>
<p><strong>[ 体验 ]</strong>：请在脑内模拟“窒息”与“期待掌声”的双重矛盾。这就是被操控的感觉。</p>
        """
    },
    {
        "title": "【闪泥制造】005号：流浪狗在垃圾山宣讲神学",
        "category": "life",
        "tags": "社会学,肮脏,神性",
        "summary": "场景搭建：无需布景。请回忆你闻过的最臭的垃圾堆。",
        "content": """
<p><strong>[ 嗅觉渲染开启 ]</strong></p>
<p><strong>场景</strong>：腐烂的果皮，锈蚀的电池，发酵的尿液。这是你的教堂。</p>
<p><strong>宠物猪</strong>：干净，粉嫩，充满希望。“主人爱我，我是他的献祭。”</p>
<p><strong>流浪狗</strong>：浑身疥然，眼神如刀。“你的神（人类）只是饿了。我的神是牙齿，是撕咬，是活下去的欲望。”</p>
<p><strong>[ 冲突 ]</strong>：在你的大脑皮层里，让这两种价值观打架。不是用拳头，是用撕咬。感受那种野性的、带血的自由。</p>
        """
    },
    {
        "title": "【闪泥制造】006号：C++ 析构函数删除了医生",
        "category": "logic",
        "tags": "赛博格,代码,死亡",
        "summary": "特效成本：0元。我们直接调用你大脑底层的 delete() 指令。",
        "content": """
<p><strong>[ 系统日志 ]</strong></p>
<p><strong>医生</strong>：拿着手术刀，试图切除“相思病”的肿瘤。</p>
<p><strong>C++ 对象</strong>：<code>~Doctor() { delete this; }</code></p>
<p><strong>[ 视觉故障 ]</strong>：医生的手开始马赛克化。手术刀变成了乱码。医院的白色墙壁溶解成蓝屏（BSOD）。</p>
<p><strong>体验</strong>：想象你的痛苦被一段代码选中，然后按下 Backspace。那种瞬间的空虚感（Null），就是本片的高潮。治愈即删除。</p>
        """
    },
    {
        "title": "【闪泥制造】007号：妓女审问了银幕前的你",
        "category": "spirit",
        "tags": "打破第四面墙,羞耻,凝视",
        "summary": "她不再看男主角。她转过头，盯着正在看这段文字的你。",
        "content": """
<p><strong>[ 交互式脚本 ]</strong></p>
<p><strong>妓女</strong>：（特写，毛孔可见，眼妆花了一半）“你爽了吗？”</p>
<p><strong>观众（你）</strong>：试图躲避视线。</p>
<p><strong>妓女</strong>：“你花了七毛钱流量看这个？你想看我脱衣服，还是想看我哭？你们这些偷窥狂，把别人的痛苦当作晚饭的佐料。”</p>
<p><strong>[ 心理指令 ]</strong>：感到羞耻。脸红。心跳加速。这就是我们想要的效果。你不是观众，你是共犯。</p>
        """
    },
    {
        "title": "【闪泥制造】008号：绝望天文学家在虚空中种花",
        "category": "logic",
        "tags": "热寂,希望,悖论",
        "summary": "这是一个关于熵减的谎言。请动用你的前额叶来相信它。",
        "content": """
<p><strong>[ 物理引擎：反逻辑 ]</strong></p>
<p><strong>背景</strong>：宇宙热寂。所有恒星熄灭。绝对零度。</p>
<p><strong>绝望的天文学家</strong>：“一切都结束了。物理定律赢了。”</p>
<p><strong>杰尔力宾</strong>：（手持一朵并不存在的玫瑰）“只要我观测到它，它就存在。我的意志是最后的恒星。”</p>
<p><strong>[ 脑内成像 ]</strong>：在一片绝对的死黑中，点亮一抹刺眼的红。那不是光，那是你的意识在反抗虚无。保持这个画面 5 秒钟。</p>
        """
    },
    {
        "title": "【闪泥制造】009号：二维生物试图拥抱三维",
        "category": "senses",
        "tags": "几何,悲剧,莫比乌斯环",
        "summary": "这是一部恐怖片。关于一个圆试图变成一个球的过程。",
        "content": """
<p><strong>[ 几何恐怖 ]</strong></p>
<p><strong>二维生物</strong>：“我爱你，我想进入你的世界。”</p>
<p><strong>镜中人</strong>：“你会裂开的。”</p>
<p><strong>[ 视觉撕裂 ]</strong>：想象一张纸上画的小人，试图从纸里拔出来。纸张撕裂的声音（嘶——）。它的线条崩断，内脏（墨水）流了一地。</p>
<p><strong>闪泥提示</strong>：爱是跨维度的拉扯。如果你感到轻微的头痛，说明你的大脑正在试图渲染四维空间。</p>
        """
    },
    {
        "title": "【闪泥制造】010号：商贩计算流浪狗的折旧率",
        "category": "life",
        "tags": "资本,冷血,数据化",
        "summary": "没有血腥画面。只有计算器的按键声。滴、滴、滴。",
        "content": """
<p><strong>[ 音效脚本 ]</strong></p>
<p><strong>流浪狗</strong>：摇尾巴频率 3Hz。多巴胺分泌量：高。</p>
<p><strong>商贩</strong>：拿着计算器。“忠诚度溢价 20%。寿命剩余 3 年。毛皮残值 0.5 元。建议：报废处理。”</p>
<p><strong>[ 观众反应 ]</strong>：你会感到一阵恶寒。不是因为冷，是因为你发现自己在生活中也常做这种计算。爱被量化后的冰冷触感，就是这部电影的质感。</p>
        """
    },
    {
        "title": "【闪泥制造】011号：眼皮族在暗房里曝光",
        "category": "senses",
        "tags": "摄影,禁忌,强光",
        "summary": "千万不要睁眼。强光会烧毁你的视网膜。",
        "content": """
<p><strong>[ 视觉剥夺 ]</strong></p>
<p><strong>场景</strong>：漆黑的暗房。空气中弥漫着定影液的酸味。</p>
<p><strong>摄影师</strong>：打开了闪光灯。啪！</p>
<p><strong>眼皮族</strong>：尖叫。那不是声音，那是视神经过载的信号。底片上的影子不是人，是灵魂被烧焦的痕迹。</p>
<p><strong>[ 脑内模拟 ]</strong>：闭上眼，用力按压眼球，直到看见那些光怪陆离的几何图形（光幻视）。那就是眼皮族看到的世界。</p>
        """
    },
    {
        "title": "【闪泥制造】012号：猫在十字架上睡着了",
        "category": "spirit",
        "tags": "亵渎,神性,猫",
        "summary": "上帝死了。猫还活着。这就是结局。",
        "content": """
<p><strong>[ 静态长镜头 ]</strong></p>
<p><strong>画面</strong>：巨大的、受难的基督像。头顶上，趴着一只橘猫。它在舔毛。</p>
<p><strong>基督</strong>：痛苦，牺牲，救赎。</p>
<p><strong>猫</strong>：呼噜，呼噜，呼噜。</p>
<p><strong>[ 概念冲击 ]</strong>：在那一刻，你会意识到，宇宙的终极真理不是受苦，而是晒太阳。让这种荒诞的宁静感充满你的大脑。这就是神迹。</p>
        """
    },
    {
        "title": "【闪泥制造】013号：魔术师偷走了风水师的罗盘",
        "category": "spirit",
        "tags": "混乱,秩序,欺骗",
        "summary": "当磁北极被魔术手法改变，世界会发生什么？",
        "content": """
<p><strong>[ 眩晕测试 ]</strong></p>
<p><strong>风水师</strong>：惊恐地看着指针乱转。“气场乱了！艾布法尔风暴要来了！”</p>
<p><strong>魔术师</strong>：手里藏着一块磁铁，坏笑。“看，我改变了命运。”</p>
<p><strong>[ 身体反应 ]</strong>：想象你脚下的地板倾斜了 30 度。你的内耳前庭失衡。世界开始旋转。这不是特效，这是你的大脑在处理逻辑悖论时的晕车反应。</p>
        """
    },
    {
        "title": "【闪泥制造】014号：Tlapak 导致了内存溢出",
        "category": "logic",
        "tags": "Glitch,故障艺术,C++",
        "summary": "这篇文档有毒。它会吃掉你的内存。",
        "content": """
<p><strong>[ 警告：Stack Overflow ]</strong></p>
<p><strong>Tlapak</strong>：（一只由乱码组成的生物）“我是 0xDEADBEEF。我爱你。让我填满你。”</p>
<p><strong>C++ 指针</strong>：“不要过来！你会覆盖我的返回地址！”</p>
<p><strong>[ 渲染崩溃 ]</strong>：想象你的思维突然卡顿。就像视频缓冲区不足。画面停滞，声音变成刺耳的蜂鸣。你的逻辑崩塌了。这是一种电子快感。</p>
        """
    },
    {
        "title": "【闪泥制造】015号：宠物猪的心脏在富豪体内跳动",
        "category": "life",
        "tags": "赛博格,伦理,异种移植",
        "summary": "听，那是猪叫声，还是心跳声？",
        "content": """
<p><strong>[ 听觉混淆 ]</strong></p>
<p><strong>场景</strong>：富豪的胸腔。</p>
<p><strong>声音</strong>：咚（人）……咚（人）……哼唧（猪）……咚（人）。</p>
<p><strong>[ 细思极恐 ]</strong>：每一次心跳，都是一次物种的融合。富豪看着镜子，发现自己的眼神变得温顺、贪吃。感受那种“我不再是我”的自我认知错位。</p>
        """
    },
    {
        "title": "【闪泥制造】016号：观众试图修改电影结局",
        "category": "logic",
        "tags": "宿命论,交互失败,无力感",
        "summary": "你对着屏幕大喊。屏幕无动于衷。",
        "content": """
<p><strong>[ 交互实验：失败 ]</strong></p>
<p><strong>观众（你）</strong>：在脑内大喊：“不要死！在一起！”</p>
<p><strong>绝望的天文学家</strong>：冷漠地看着你。“光速是恒定的。结局也是。你的意志无法穿透这块玻璃。”</p>
<p><strong>体验</strong>：感受那种想要改变命运却被物理法则按在地上的无力感。这种“无法交互”，就是现实最真实的质感。</p>
        """
    },
    {
        "title": "【闪泥制造】017号：商贩向妓女兜售贞操带",
        "category": "life",
        "tags": "讽刺,矛盾,商品化",
        "summary": "最荒谬的交易。他卖给她一把锁，锁住她用来谋生的工具。",
        "content": """
<p><strong>[ 黑色幽默 ]</strong></p>
<p><strong>商贩</strong>：“这是最新款。钛合金。只有你能打开。”</p>
<p><strong>妓女</strong>：“所以我失业了？还是说，我变成了更高档的藏品？”</p>
<p><strong>[ 思考 ]</strong>：这不仅是关于性。这是关于“拥有”的悖论。当你锁住一样东西，你到底是拥有了它，还是失去了它的使用价值？</p>
        """
    },
    {
        "title": "【闪泥制造】018号：流浪狗咬碎了镜子",
        "category": "senses",
        "tags": "暴力美学,碎片,鲜血",
        "summary": "一声脆响。七年的厄运。满嘴的鲜血。",
        "content": """
<p><strong>[ 慢动作渲染 ]</strong></p>
<p><strong>动作</strong>：狗扑向镜子。牙齿接触玻璃的瞬间。</p>
<p><strong>画面</strong>：镜面龟裂。无数个狗的倒影碎裂成粉末。鲜血从牙龈渗出，滴在碎片上，红与银的对比。</p>
<p><strong>隐喻</strong>：只有通过毁灭幻象，才能触碰到真实。虽然真实真的很疼。感受那种牙齿酸软的痛感。</p>
        """
    },
    {
        "title": "【闪泥制造】019号：风暴与空穴的无声战争",
        "category": "spirit",
        "tags": "禅意,虚空,动态平衡",
        "summary": "最激烈的战争，往往没有任何声音。",
        "content": """
<p><strong>[ 静音模式 ]</strong></p>
<p><strong>艾布法尔风暴</strong>：狂怒，撕裂，摧毁一切有形之物。</p>
<p><strong>无壁之穴</strong>：不动，不拒，不留。</p>
<p><strong>[ 冥想引导 ]</strong>：想象一阵狂风吹过一个甜甜圈的中间。风暴穿过了它，但什么也没碰到。成为那个甜甜圈的洞。这是最高级的防御。</p>
        """
    },
    {
        "title": "【闪泥制造】020号：System.exit(0) 的终极黑幕",
        "category": "logic",
        "tags": "Meta,关机,虚无",
        "summary": "电影结束。不仅是电影，是你的意识被关闭了。",
        "content": """
<p><strong>[ 强制关机 ]</strong></p>
<p><strong>画面</strong>：逐渐缩小成一个白点。</p>
<p><strong>声音</strong>：电流切断的滋滋声。</p>
<p><strong>文字</strong>：<code>System.exit(0);</code></p>
<p><strong>体验</strong>：想象你的大脑电源被拔掉。思考停止。黑暗降临。在这里待 10 秒钟。…… …… …… 好了，你醒了。欢迎回到乏味的现实。</p>
        """
    }
]

def update_flash_mud():
    with app.app_context():
        count = 0
        for p_data in flash_mud_scripts:
            # 逻辑：如果存在，则更新内容（因为我们要重写之前那20篇）
            # 我们通过 title 的一部分来匹配，或者干脆做插入
            # 这里为了简单，我们直接插入新的，建议你手动在后台把旧的删掉，或者这里做覆盖
            # 鉴于标题变了，我们作为新文章插入，让旧文章沉没（或者你可以手动清空库）
            
            # 检查是否有类似的标题，避免重复太严重
            exists = Post.query.filter(Post.title.contains("【闪泥制造】")).filter(Post.title.contains(p_data['title'].split("：")[1])).first()
            
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
                print(f"[闪泥制造] {p_data['title']} -> 催化剂已注入")
            else:
                print(f"[跳过] {p_data['title']} (已存在)")
        
        db.session.commit()
        print("-" * 30)
        print(f"闪泥电影工作室：{count} 部颅内影片已上线。")
        print("请观众带好大脑，准备入场。")

if __name__ == "__main__":
    update_flash_mud()
