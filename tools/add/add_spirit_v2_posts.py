from app import app, db, Post
from datetime import datetime

# 10篇 基于《雅歌》变奏的【闪泥制造】二期工程
# 核心：将古典神学诗句 编译 为赛博朋克/硬核生活/逻辑代码
new_spirit_posts_v2 = [
    {
        "title": "【闪泥制造】没药的波形：模拟信号中的苦味",
        "category": "senses",
        "tags": "音乐,没药,声音,失真",
        "summary": "没药是苦的。我在合成器上加了一个 Bitcrusher 效果器，为了模拟这种苦。",
        "content": """
<p><strong>[ 音频工程 ]</strong></p>
<p><strong>素材</strong>：一段名为“恩宠”的采样 (Sample)。</p>
<p><strong>处理</strong>：良人的恩宠，如没药入怀。没药是防腐的，也是苦涩的。我将采样率降低到 8-bit，增加了一层底噪（Hiss）。</p>
<p><strong>听感</strong>：那声音不再平滑，变得粗糙、颗粒感十足，像沙砾沁入心田。这才是真实的恩宠——它不是甜腻的糖水，它是带有痛感的防腐剂，让灵魂在流连中不至腐烂。</p>
        """
    },
    {
        "title": "【闪泥制造】A* 寻路算法：凭爱指引",
        "category": "logic",
        "tags": "C++,算法,指引,游戏开发",
        "summary": "在迷宫中，启发式函数 H(n) = 爱。",
        "content": """
<p><strong>[ 寻路逻辑 ]</strong></p>
<p><strong>起点</strong>：寻觅（Start_Node）。</p>
<p><strong>终点</strong>：你面前（Target_Node）。</p>
<p><strong>障碍</strong>：荆棘（Collision Box），深渊（NavMesh Gap）。</p>
<p><strong>算法</strong>：普通的 BFS（广度优先）会超时。我重写了 A* 算法。即使前路未知，但有一个名为 <code>Love_Pointer</code> 的启发式函数，始终指向你的坐标。无论绕多少弯路（试炼），最优路径最终都会收敛到你的面前。</p>
        """
    },
    {
        "title": "【闪泥制造】百合花的渲染层：Z-Buffer 的深度测试",
        "category": "logic",
        "tags": "图形学,渲染,百合,神迹",
        "summary": "深渊是黑色的背景。百合花是唯一的发光材质。",
        "content": """
<p><strong>[ 渲染管线 ]</strong></p>
<p><strong>背景</strong>：跨过深渊。Pixel Color = #000000 (Pure Void)。</p>
<p><strong>前景</strong>：百合花。Shader 设置为自发光（Emissive），强度 1000%。</p>
<p><strong>冲突</strong>：按理说，深渊会吞噬光线。但在 Z-Buffer（深度缓冲）中，我强制让百合花的层级高于深渊。即使在最黑暗的低谷，那白色的花瓣也处处盛开，覆盖了绝望的贴图。这就是“恩宠”的渲染优先级。</p>
        """
    },
    {
        "title": "【闪泥制造】中医视角的荆棘：痛则不通",
        "category": "spirit",
        "tags": "中医,经络,荆棘,治愈",
        "summary": "历经荆棘，就是经络里布满了结节。良人是唯一的针。",
        "content": """
<p><strong>[ 经络探查 ]</strong></p>
<p><strong>症状</strong>：气滞血瘀。因为曾寻觅，尝尽试炼。心包经被“荆棘”（情绪郁结）堵死。</p>
<p><strong>治疗</strong>：良人恩宠。这是一种高能量的阳气（Qi）。</p>
<p><strong>反应</strong>：当这股气沁入心田，就像没药走窜。你会感到剧痛，然后是疏通后的极度酸爽。百合花盛开，就是气血终于通达末梢时的红润。唯有深情者（信赖医生的人），能忍受这种破冰的痛。</p>
        """
    },
    {
        "title": "【闪泥制造】香草山的取景框：胶片的宽容度",
        "category": "senses",
        "tags": "摄影,香草山,胶片,光影",
        "summary": "那是极高光和极暗部的对撞。唯有电影卷能记录这种爱。",
        "content": """
<p><strong>[ 曝光参数 ]</strong></p>
<p><strong>场景</strong>：香草山。充满了神性的光辉。</p>
<p><strong>挑战</strong>：普通数码相机会过曝，变成一片死白。但我用的是 Kodak Vision3 电影卷。</p>
<p><strong>成片</strong>：在高光的“佳偶之爱”和阴影的“深渊试炼”之间，胶片保留了丰富的层次。唯有深情者（懂摄影的人），能在一张照片里读出那种“流连”的颗粒感。爱不是清晰度，爱是宽容度。</p>
        """
    },
    {
        "title": "【闪泥制造】格斗场上的拥抱：终到你面前",
        "category": "life",
        "tags": "MMA,格斗,拥抱,结局",
        "summary": "我们打了 5 个回合。最后我们抱在了一起。",
        "content": """
<p><strong>[ 比赛记录 ]</strong></p>
<p><strong>回合 1-4</strong>：历经荆棘。你的刺拳，我的低扫。血混着汗，尝尽试炼。</p>
<p><strong>回合 5</strong>：体力耗尽。跨过体能的深渊。</p>
<p><strong>结局</strong>：铃声响起。没有输赢。我们互相拥抱（Clinch），头靠在对方满是伤口的肩膀上。那汗水的味道，此刻竟如没药般芬芳。在暴力的尽头，我们终到彼此面前。这是战士的香草山。</p>
        """
    },
    {
        "title": "【闪泥制造】罗盘在深渊失效：凭你爱指引",
        "category": "spirit",
        "tags": "风水,磁场,玄术,指引",
        "summary": "这里磁场紊乱，罗盘指针疯狂旋转。我闭上了眼。",
        "content": """
<p><strong>[ 堪舆困局 ]</strong></p>
<p><strong>地点</strong>：人生的深渊。空亡线。罗盘失效。</p>
<p><strong>破局</strong>：风水师收起了工具。当物理磁场乱了，心流（Heart Flow）就成了唯一的导航。</p>
<p><strong>口诀</strong>：“凭爱指引”。这不是技术，这是感应。我感知到“良人”在香草山（吉位）发出的信号。不需要罗盘，我的直觉（深情）会自动修正方向，避开所有的煞气（荆棘）。</p>
        """
    },
    {
        "title": "【闪泥制造】少女与香草山：Cosplay 还是神学？",
        "category": "senses",
        "tags": "二次元,少女,Cosplay,雅歌",
        "summary": "她穿着充满了蕾丝（荆棘隐喻）的裙子，站在布景的山顶。",
        "content": """
<p><strong>[ 漫展现场 ]</strong></p>
<p><strong>角色</strong>：Shulamite (书拉密女)。</p>
<p><strong>服装</strong>：洁白如百合，但裙摆上绣满了黑色的荆棘纹样。</p>
<p><strong>台词</strong>：“带我跑，我们便快跑跟随你。”</p>
<p><strong>评论</strong>：死宅们在拍裙底，而唯有深情者（懂神学的人）看懂了她的眼神。那是一种穿越了二次元障壁的渴望。她不是在扮演角色，她是在等待那个跨越深渊而来的良人。</p>
        """
    },
    {
        "title": "【闪泥制造】递归函数的堆栈溢出：爱意流连",
        "category": "logic",
        "tags": "C++,递归,溢出,流连",
        "summary": "函数不断调用自己，直到填满整个内存。",
        "content": """
<p><strong>[ 代码片段 ]</strong></p>
<pre><code>void Love() {
    Enter_Heart(); // 沁入心田
    Love(); // 流连，再次调用
}</code></pre>
<p><strong>运行结果</strong>：Stack Overflow。系统崩溃。</p>
<p><strong>解析</strong>：这种“流连”是危险的。没药入怀，就没有打算离开。它不断递归，占满你的每一寸 RAM（心田）。直到你无法再处理任何其他任务（试炼）。这是一种甜蜜的死机。</p>
        """
    },
    {
        "title": "【闪泥制造】播客里的静默 10 秒：深情者的一窥",
        "category": "senses",
        "tags": "播客,声音,静默,留白",
        "summary": "我讲了 50 分钟的苦难。然后我停顿了。",
        "content": """
<p><strong>[ 音轨分析 ]</strong></p>
<p><strong>00:00 - 50:00</strong>：讲述荆棘，讲述深渊，讲述寻找的艰辛。</p>
<p><strong>50:01 - 50:10</strong>：完全的静音（Silence）。</p>
<p><strong>意图</strong>：在那 10 秒里，我不想说话。因为语言是墙壁，静默是无壁之穴。在那片死寂中，百合花正在开放。唯有戴着耳机、调大音量的深情听众，能在那段底噪中，听到良人隐秘的呼吸声。那是一窥其颜的时刻。</p>
        """
    }
]

def add_spirit_v2_posts():
    with app.app_context():
        count = 0
        for p_data in new_spirit_posts_v2:
            exists = Post.query.filter(Post.title.contains(p_data['title'][:10])).first()
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
                print(f"[雅歌变奏] {p_data['title']} -> 编译通过")
            else:
                print(f"[跳过] {p_data['title']}")
        
        db.session.commit()
        print("-" * 30)
        print(f"闪泥工作室二期：{count} 篇关于荆棘与没药的深度文案已发布。")

if __name__ == "__main__":
    add_spirit_v2_posts()