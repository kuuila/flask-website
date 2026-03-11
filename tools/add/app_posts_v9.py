from app import app, db, Post
from datetime import datetime
import random

# 20篇 深度隐匿 (Stealth Mode) 的经典文本重构
# 核心：将神学原型 编译 为现代/赛博/二次元 符号
# 目的：懂的入，不懂的看个乐
new_hidden_posts = [
    {
        "title": "【闪泥制造】M-Code：石板上的硬编码协议",
        "category": "logic",
        "tags": "底层代码,协议,登山者,C++",
        "summary": "那个老程序员在山上待了40天，带回了两块加密硬盘。他说这是系统的核心约束。",
        "content": """
<p><strong>[ 档案编号：Exodus_v2 ]</strong></p>
<p><strong>角色</strong>：M-Code (初代架构师)</p>
<p><strong>剧情</strong>：山脚下的人群正在熔铸一只金色的牛（Crypto 货币/偶像）。M-Code 拿着两块石板走下来，看到满地的 Bug。</p>
<p><strong>台词</strong>：“<code>const int LAW = 10;</code> 这些是写死在 ROM 里的规则，不可变，不可重载。你们试图用动态类型（金牛）来绕过编译检查？那就准备好接受 <code>Segmentation Fault</code> 吧。”</p>
<p><strong>结局</strong>：他愤怒地摔碎了硬盘。因为硬件可以碎，但逻辑必须重写。</p>
        """
    },
    {
        "title": "【闪泥制造】牧羊少年的投石机：针对巨型主机的 DDOS",
        "category": "life",
        "tags": "格斗,弱点攻击,巨人,音乐",
        "summary": "对手是一台名为 G.O.L.I.A.T.H 的军用级防火墙。少年手里只有一颗数据包。",
        "content": """
<p><strong>[ 战斗回放 ]</strong></p>
<p><strong>巨人</strong>：全副武装，护甲值 9999。嘲笑面前这个拿琴的少年。</p>
<p><strong>少年 (D-String)</strong>：他没有穿戴厚重的铠甲（Saul's Armor），因为那会影响敏捷度。他从溪水里捡了五颗光滑的石头（Exploits）。</p>
<p><strong>动作</strong>：旋转，加速，释放。<code>ping -t -l 65500 target</code>。</p>
<p><strong>结果</strong>：并未击穿护甲，而是直接击中了眉心（CPU 散热孔）。系统瞬间宕机。有时候，低端物理攻击比魔法更有效。</p>
        """
    },
    {
        "title": "【闪泥制造】S-King 的空虚算法：当算力达到无穷大",
        "category": "logic",
        "tags": "AI,虚空,算法,后宫",
        "summary": "他拥有世界上最快的超算。但他最后打印出的结果是 Null。",
        "content": """
<p><strong>[ 实验室日志 ]</strong></p>
<p><strong>S-King (智慧之王)</strong>：我遍历了所有的享乐函数。我建造了巨大的虚拟园林，收集了 1000 个 waifu 模型。</p>
<p><strong>助手</strong>：结果如何？</p>
<p><strong>S-King</strong>：<code>return void;</code>。眼看，看不饱；耳听，听不足。日光之下的所有代码，都是复制粘贴。虚空的虚空。这一切都是捕风（Running after wind）。</p>
<p><strong>结论</strong>：算法的尽头是厌世。除非你找到了算法的编写者。</p>
        """
    },
    {
        "title": "【闪泥制造】帐棚制造者的防火墙：恩典补丁",
        "category": "logic",
        "tags": "网络安全,书信,逻辑,P-Logic",
        "summary": "他曾经是病毒制造者，后来变成了首席安全官。他写了一半的技术文档。",
        "content": """
<p><strong>[ 邮件归档 ]</strong></p>
<p><strong>发件人</strong>：P-Logic (原名 Saul)</p>
<p><strong>收件人</strong>：罗马节点, 加拉太节点, 以弗所节点...</p>
<p><strong>正文</strong>：不要再试图通过割礼（物理层修改）来获得 Root 权限了！系统内核已经更新了。现在是 <code>Faith_Based_Access</code>。只要你信任（Believe）那个超级管理员（Christ），你就会被自动赋予权限。这是恩典（Grace），不是工资（Works）！</p>
<p><strong>备注</strong>：我是个流产的胎儿，不配称为黑客。但系统的恩典临到了我。</p>
        """
    },
    {
        "title": "【闪泥制造】岛屿观察者的 Glitch 视觉：七个封印的解压缩",
        "category": "senses",
        "tags": "视觉艺术,末世,故障,J-Vision",
        "summary": "他被流放到拔摩岛（离线服务器）。他在那里看到了操作系统的最终蓝屏。",
        "content": """
<p><strong>[ 视觉渲染 ]</strong></p>
<p><strong>J-Vision</strong>：我看见天开了。有一个门。那是后门（Backdoor）。</p>
<p><strong>景象</strong>：四骑士正在格式化硬盘。星辰像坏点一样坠落。海变成了血（Hex Code #FF0000）。</p>
<p><strong>声音</strong>：七个雷声。那是服务器过载的轰鸣。但我被禁止记录那段 Log。</p>
<p><strong>结局</strong>：新天新地。也就是 System Restore 之后的纯净版 OS。没有眼泪（Error），没有死亡（Crash）。</p>
        """
    },
    {
        "title": "【闪泥制造】木匠的后门：Sudo 权限的获取",
        "category": "spirit",
        "tags": "木匠,Root,救赎,系统",
        "summary": "他没上过大学，没写过书。但他就是源代码本身。",
        "content": """
<p><strong>[ 核心揭秘 ]</strong></p>
<p><strong>身份</strong>：普通木匠的儿子。实质：<code>class Word extends God</code>。</p>
<p><strong>事件</strong>：他来到 Jordan River 初始化。系统发声：这是我的爱子。</p>
<p><strong>功能</strong>：他提供了一个 API。<code>Interface IWay, ITruth, ILife</code>。没人能绕过这个接口直接访问内核（Father）。</p>
<p><strong>Bug</strong>：系统杀了他。三天后，他重启了。并且带走了死亡的私钥（Keys of Hades）。</p>
        """
    },
    {
        "title": "【闪泥制造】磐石的三次拒绝：服务器日志造假",
        "category": "life",
        "tags": "运维,背叛,鸡叫,Peter",
        "summary": "那是凌晨三点。鸡叫之前，他删除了三次登录记录。",
        "content": """
<p><strong>[ 审计追踪 ]</strong></p>
<p><strong>场景</strong>：大祭司的院子（防火墙外围）。</p>
<p><strong>女仆（Bot）</strong>：检测到你的 IP 来自加利利。你和他是一伙的。</p>
<p><strong>Stone_Key (磐石)</strong>：<code>Deny. Deny. Deny.</code> 我不认识那个 User。我不懂那个协议。</p>
<p><strong>触发器</strong>：鸡叫了（Cron Job 执行）。</p>
<p><strong>反应</strong>：他出去痛哭。因为他发现主（Admin）转过身，隔着屏幕静静地看着他。</p>
        """
    },
    {
        "title": "【闪泥制造】逃跑的深潜员：三天三夜的离线模式",
        "category": "spirit",
        "tags": "潜水,深海,逃避,Jonah",
        "summary": "他买票去了反方向。于是系统派了一只大鱼（容器）来隔离他。",
        "content": """
<p><strong>[ 容器日志 ]</strong></p>
<p><strong>潜水员 (J-Fish)</strong>：我不想去尼尼微（敌对服务器）布道。我要休假。</p>
<p><strong>系统</strong>：抛出异常 <code>Great_Storm_Exception</code>。</p>
<p><strong>状态</strong>：被吞噬。在鱼腹（Docker Container）里隔离了 72 小时。只有海草缠绕，没有 Wifi。</p>
<p><strong>结果</strong>：除了祷告，还是祷告。最后被吐在了沙滩上。好吧，我去。</p>
        """
    },
    {
        "title": "【闪泥制造】花园里的非法访问：知识树的诱惑",
        "category": "logic",
        "tags": "创世纪,黑客,蛇,果实",
        "summary": "那不是苹果。那是一个名为 'Knowledge_of_Good_and_Evil' 的加密文件。",
        "content": """
<p><strong>[ 入侵检测 ]</strong></p>
<p><strong>蛇 (Social Engineer)</strong>：系统真的说不能访问这个目录吗？其实访问了也不会死（Crash），反而会获得 Admin 视野。</p>
<p><strong>用户 (Eve)</strong>：双击运行。</p>
<p><strong>后果</strong>：眼睛明亮了。但也发现了自己是裸奔的（No Firewall）。</p>
<p><strong>系统惩罚</strong>：<code>Access Denied</code>。被踢出伊甸园服务器。永久封号。</p>
        """
    },
    {
        "title": "【闪泥制造】通天塔项目：语言碎片化危机",
        "category": "logic",
        "tags": "巴别塔,语言学,项目管理,失败",
        "summary": "这是一个试图直通云端的大型单体应用（Monolith）。后来被拆分成了微服务。",
        "content": """
<p><strong>[ 项目复盘 ]</strong></p>
<p><strong>目标</strong>：我们要造一座塔，塔顶通天，为要传扬我们的名（Branding）。</p>
<p><strong>手段</strong>：全人类使用同一种编程语言。</p>
<p><strong>系统干预</strong>：<code>Confuse_Language()</code>。</p>
<p><strong>结果</strong>：前端听不懂后端，运维听不懂产品。项目烂尾。人们分散到各地。这就是为什么现在我们有 Java, Python, C++, Go 却依然无法互相理解。</p>
        """
    },
    {
        "title": "【闪泥制造】方舟号：冷数据备份",
        "category": "life",
        "tags": "洪水,备份,诺亚,动物",
        "summary": "所有的都在被格式化（洪水）。只有这一个硬盘（方舟）漂在水面上。",
        "content": """
<p><strong>[ 灾备演练 ]</strong></p>
<p><strong>预警</strong>：还有 120 年系统就要重装了。</p>
<p><strong>操作者 (Noah)</strong>：即使被嘲笑，依然在造船。<code>mkdir Ark</code>。</p>
<p><strong>数据迁移</strong>：每种数据（动物）保留一公一母（冗余备份）。</p>
<p><strong>执行</strong>：洪水（Flood）来了。所有未备份的数据全部丢失。当鸽子叼着橄榄叶（Ping Success）回来时，那就是 Reboot 完成的信号。</p>
        """
    },
    {
        "title": "【闪泥制造】燃烧的荆棘：低功耗高亮显示",
        "category": "spirit",
        "tags": "异象,呼召,摩西,火",
        "summary": "那丛荆棘在燃烧，但没有被烧毁。这是不符合热力学定律的。",
        "content": """
<p><strong>[ 视觉异常 ]</strong></p>
<p><strong>观察者</strong>：M-Code (当时还是个牧羊人)。</p>
<p><strong>现象</strong>：火光熊熊，但荆棘的材质（Mesh）没有损耗。这是一种永恒的能量源。</p>
<p><strong>声音</strong>：脱下你的鞋子。这地是圣的（Protected Memory）。</p>
<p><strong>名字</strong>：我是自有永有的（I AM WHO I AM）。你可以理解为 <code>while(true) { exist(); }</code>。</p>
        """
    },
    {
        "title": "【闪泥制造】空坟墓：404 Not Found",
        "category": "spirit",
        "tags": "复活,空坟墓,神迹,悬疑",
        "summary": "周日清晨。石头滚开了。里面只有裹尸布（Log Files）。",
        "content": """
<p><strong>[ 现场勘查 ]</strong></p>
<p><strong>对象</strong>：Jesus_Body.obj</p>
<p><strong>状态</strong>：Missing。</p>
<p><strong>目击者</strong>：几个妇女。还有那个跑得比彼得快的约翰。</p>
<p><strong>天使 (System Daemon)</strong>：为什么在死人中找活人？他已经重构了（Resurrected）。</p>
<p><strong>结论</strong>：这不是被盗号，这是系统升级。死亡的 Bug 被修复了。</p>
        """
    },
    {
        "title": "【闪泥制造】三十枚银币：私钥的泄露",
        "category": "life",
        "tags": "背叛,犹大,交易,自杀",
        "summary": "他吻了他。这是一个带有恶意载荷（Payload）的吻。",
        "content": """
<p><strong>[ 交易记录 ]</strong></p>
<p><strong>卖方</strong>：J-Iscariot。</p>
<p><strong>买方</strong>：宗教祭司集团。</p>
<p><strong>标的</strong>：The Master 的实时定位。</p>
<p><strong>价格</strong>：30 Silver Coins（奴隶的身价）。</p>
<p><strong>后果</strong>：交易成功。但卖方因为无法承受良心的溢出（Overflow），最终挂起（Hanged）了自己。那块田叫血田（Aceldama）。</p>
        """
    },
    {
        "title": "【闪泥制造】浪子回头：重新登录的 User",
        "category": "life",
        "tags": "亲情,浪子,猪,回归",
        "summary": "他挥霍了所有的带宽和存储。现在他只想回来当个 Guest 用户。",
        "content": """
<p><strong>[ 用户日志 ]</strong></p>
<p><strong>User_Prodigal</strong>：分了家产，去远方服务器挥霍。最后沦落到和猪抢豆荚（垃圾数据）。</p>
<p><strong>觉醒</strong>：我父亲的服务器里有无数资源，我为何在这里饿死？</p>
<p><strong>回归</strong>：离家还远，父亲（Admin）就跑过去抱住他。没有验证码，没有密码重置问题。</p>
<p><strong>指令</strong>：把那上好的袍子（Skin）给他穿上，宰了肥牛。因为这个儿子是死而复活，失而又得的。</p>
        """
    },
    {
        "title": "【闪泥制造】约伯的沙盒：压力测试",
        "category": "logic",
        "tags": "苦难,约伯,测试,撒旦",
        "summary": "这不是惩罚。这是一场获得许可的渗透测试。",
        "content": """
<p><strong>[ 测试环境 ]</strong></p>
<p><strong>目标</strong>：Job (VIP User)。</p>
<p><strong>攻击者</strong>：Satan (Penetration Tester)。</p>
<p><strong>授权</strong>：SysAdmin 说：“你可以动他的所有资产，但不许动他的内核（Life）。”</p>
<p><strong>过程</strong>：资产清零，防火墙全塌，浑身长毒疮。朋友们说：“你肯定有 Bug。”</p>
<p><strong>Job 的回应</strong>：我知道我的救赎主（Debugger）活着。即使我的硬盘被物理销毁，我仍要在代码之外见到他。</p>
        """
    },
    {
        "title": "【闪泥制造】好撒玛利亚人：未知的补丁贡献者",
        "category": "life",
        "tags": "善良,邻舍,种族,救援",
        "summary": "祭司绕道了。利未人绕道了。只有那个被歧视的人修复了 Bug。",
        "content": """
<p><strong>[ 事故现场 ]</strong></p>
<p><strong>受害者</strong>：被打个半死，丢在路边。</p>
<p><strong>路人 A/B (官方人员)</strong>：看见了，假装没看见（Ignore Error）。</p>
<p><strong>路人 C (Samaritan)</strong>：动了慈心。倒油和酒（消毒/修复）。扶他上牲口，带到客店。</p>
<p><strong>留言</strong>：“费用我包了。”</p>
<p><strong>问题</strong>：谁是那受伤之人的邻舍（Neighbor）？</p>
        """
    },
    {
        "title": "【闪泥制造】水面行走：无视物理引擎",
        "category": "senses",
        "tags": "神迹,彼得,水,信心",
        "summary": "在那一刻，重力参数被临时修改为 0。",
        "content": """
<p><strong>[ 物理异常 ]</strong></p>
<p><strong>场景</strong>：夜里的加利利海。风浪大作。</p>
<p><strong>现象</strong>：一个人在水面上走过来。Ghost?</p>
<p><strong>Stone_Key</strong>：“如果是你，叫我也走过去。”</p>
<p><strong>The Carpenter</strong>：“Come。”</p>
<p><strong>Glitch</strong>：彼得真的走了两步。但他一看风浪（环境参数），信心下降，立刻沉了下去。系统提示：<code>Low Faith Warning</code>。</p>
        """
    },
    {
        "title": "【闪泥制造】最后的晚餐：Fork 之前的 Commit",
        "category": "spirit",
        "tags": "圣餐,契约,酒,饼",
        "summary": "这是我的身体。这是我的血。这是新约（New Protocol）。",
        "content": """
<p><strong>[ 会议记录 ]</strong></p>
<p><strong>时间</strong>：被卖的那一夜。</p>
<p><strong>动作</strong>：拿起饼（Body），擘开。拿起杯（Blood），祝谢。</p>
<p><strong>声明</strong>：这是为了你们舍的。如此行，为的是纪念（Cache）我。</p>
<p><strong>预告</strong>：我不再喝这葡萄汁，直到我在父的国里喝新的那日子。系统即将分叉（Fork），旧约结束，新约开始。</p>
        """
    },
    {
        "title": "【闪泥制造】Alpha & Omega：闭环",
        "category": "logic",
        "tags": "终极,开始,结束,启示录",
        "summary": "我是 Start(); 我是 End();",
        "content": """
<p><strong>[ 系统广播 ]</strong></p>
<p><strong>The One</strong>：我是阿拉法，我是俄梅戛。我是初，我是终。</p>
<p><strong>时间线</strong>：从 Genesis 的 <code>Hello World</code> 到 Revelation 的 <code>System Halt</code>。</p>
<p><strong>承诺</strong>：看哪，我必快来。我的赏赐在我，要照各人所行的报应他。</p>
<p><strong>响应</strong>：<code>Amen. Come, Lord Jesus.</code></p>
        """
    }
]

def add_hidden_bible_posts():
    with app.app_context():
        count = 0
        for p_data in new_hidden_posts:
            # 查重
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
                print(f"[隐匿文本] {p_data['title']} -> 编译成功")
            else:
                print(f"[跳过] {p_data['title']}")
        
        db.session.commit()
        print("-" * 30)
        print(f"闪泥工作室：{count} 篇深度隐匿的元叙事已发布。")
        print("提示：只有拥有“听的耳”的人，才能解码这些文本。")

if __name__ == "__main__":
    add_hidden_bible_posts()