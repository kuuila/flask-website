import random
from datetime import datetime, timedelta
from app import app, db, DailyPrayer

def generate_many_prayers():
    # 常用圣名库
    names = [
        "若望", "玛利亚", "彼得", "保禄", "德兰", "奥斯定", "方济各", "路加", 
        "玛尔大", "多默", "安德肋", "雅各伯", "斐理伯", "巴尔多禄茂", "玛窦", 
        "西满", "达陡", "玛弟亚", "斯德望", "巴尔纳伯", "依纳爵", "葛斯莫", 
        "达弥盎", "莫尼加", "则济利亚", "亚纳", "若瑟", "安多尼", "葛莱蒂"
    ]

    # 随机组合祷告词，让数据看起来不一样
    starts = ["求主", "感谢天主", "主啊", "愿", "为", "恳求", "仁慈的主", "献上"]
    middles = ["赐予", "保佑", "看顾", "宽恕", "指引", "坚固", "垂怜", "治愈", "圣化"]
    ends = ["我的家人", "这个世界", "教会合一", "受苦的人", "我的信德", "内心平安", "罪过的赦免", "每日的食粮", "迷途的羔羊", "炼灵", "生病的友邻"]
    suffixes = ["阿们。", "求主俯听。", "主，我信赖你。", "感谢主。", "。", "！"]

    print("正在生成 50 条测试数据...")
    
    new_records = []
    
    with app.app_context():
        # 可选：先清空旧数据，让列表看起来整洁（如果不需要清空，注释掉下面这行）
        # DailyPrayer.query.delete()
        
        for i in range(50):
            # 1. 随机生成内容
            name = random.choice(names)
            content = f"{random.choice(starts)}{random.choice(middles)}{random.choice(ends)}{random.choice(suffixes)}"
            
            # 2. 随机生成时间 (过去 24 小时内)
            # 为了保证排序测试效果，我们模拟每隔几分钟就有一个
            minutes_ago = i * 15 + random.randint(0, 10) 
            fake_time = datetime.now() - timedelta(minutes=minutes_ago)
            
            p = DailyPrayer(
                uid=f"test-bot-{i}",
                name=name,
                content=content,
                created_at=fake_time
            )
            new_records.append(p)
        
        # 批量提交
        db.session.add_all(new_records)
        db.session.commit()
        
        print("-" * 30)
        print(f"✅ 成功注入 {len(new_records)} 条祷告数据！")
        print("现在请刷新网页，进入【今日祷告】Tab。")
        print("列表应该有滚动条，向下滑动到底部会自动加载更多。")

if __name__ == "__main__":
    generate_many_prayers()