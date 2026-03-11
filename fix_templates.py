import os
import re

def fix_templates_v2():
    print("正在修复模板路由 (V2版)...")
    
    # 需要检查的文件
    targets = [
        'templates/index.html',
        'templates/post_html.html',
        'templates/layout.html'
    ]
    
    # 需要添加 'main.' 前缀的路由函数名
    endpoints = ['index', 'category', 'post_detail', 'subweb']
    
    for path in targets:
        if not os.path.exists(path):
            print(f"⚠️ 跳过 {path}")
            continue
            
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = content
        count = 0
        
        for ep in endpoints:
            # 正则解释：
            # url_for\(\s*  -> 匹配 url_for( 和可能的空格
            # (['"])        -> 捕获组1：匹配单引号或双引号
            # (?!main\.)    -> 负向预查：确保后面没有跟着 "main." (防止重复添加)
            # ep            -> 匹配函数名 (如 index)
            # \1            -> 匹配与组1相同的引号 (确保引号闭合)
            pattern = re.compile(r"(url_for\(\s*)(['\"])(?!main\.)" + re.escape(ep) + r"(\1)")
            
            # 查找有多少处匹配
            matches = pattern.findall(new_content)
            if matches:
                # 替换为： url_for( ' main.index '
                # \g<1> 保留 url_for(
                # \g<2> 保留引号
                # main. 加上前缀
                # ep 函数名
                # \g<2> 闭合引号
                new_content = pattern.sub(r"\g<1>\g<2>main." + ep + r"\g<2>", new_content)
                count += len(matches)
                print(f"  - 在 {path} 中修复了 {len(matches)} 处 '{ep}' 路由")

        if count > 0:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ {path} 保存成功！")
        else:
            print(f"✔️ {path} 无需修改")

if __name__ == "__main__":
    fix_templates_v2()
    print("-" * 30)
    print("修复完成！请重启服务并刷新网页。")