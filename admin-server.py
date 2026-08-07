#!/usr/bin/env python3
"""
博客内容管理面板 - 本地Web服务器
运行后在浏览器打开 http://localhost:8080/admin 即可使用
"""

import http.server
import json
import os
import sys
from datetime import date
from urllib.parse import parse_qs, urlparse

PORT = 8082
BLOG_DIR = os.path.dirname(os.path.abspath(__file__))

class AdminHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/admin' or self.path == '/admin/':
            self.send_admin_page()
        elif self.path == '/api/data':
            self.send_json(self.get_data())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/post':
            content_len = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_len).decode('utf-8')
            params = parse_qs(body)

            title = params.get('title', [''])[0].strip()
            content_type = params.get('type', [''])[0]

            if not title or not content_type:
                self.send_json({'error': '标题和类型不能为空'}, 400)
                return

            if content_type == 'post':
                result = self.create_post(title, params)
            elif content_type == 'photo':
                result = self.add_photo(params)
            elif content_type == 'travel':
                result = self.add_travel(params)
            elif content_type == 'project':
                result = self.create_project(title, params)
            else:
                result = {'error': '未知类型'}

            if 'error' in result:
                self.send_json(result, 400)
            else:
                self.send_json(result)
        else:
            self.send_response(404)
            self.end_headers()

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def send_html(self, html):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def get_data(self):
        data = {'posts': [], 'photos': 0, 'travels': 0, 'projects': 0}

        blog_dir = os.path.join(BLOG_DIR, 'content', 'blog')
        if os.path.isdir(blog_dir):
            for d in sorted(os.listdir(blog_dir), reverse=True):
                idx = os.path.join(blog_dir, d, 'index.zh-Hans.md')
                if os.path.isfile(idx):
                    data['posts'].append(d)

        yin_file = os.path.join(BLOG_DIR, 'data', 'yin.json')
        if os.path.isfile(yin_file):
            with open(yin_file, 'r', encoding='utf-8') as f:
                yin = json.load(f)
                data['photos'] = len(yin.get('items', []))

        xing_file = os.path.join(BLOG_DIR, 'data', 'xing.json')
        if os.path.isfile(xing_file):
            with open(xing_file, 'r', encoding='utf-8') as f:
                xing = json.load(f)
                data['travels'] = len(xing.get('items', []))

        proj_dir = os.path.join(BLOG_DIR, 'content', 'projects')
        if os.path.isdir(proj_dir):
            data['projects'] = len([d for d in os.listdir(proj_dir) if os.path.isdir(os.path.join(proj_dir, d))])

        return data

    def create_post(self, title, params):
        safe_title = title.strip()
        dir_path = os.path.join(BLOG_DIR, 'content', 'blog', safe_title)

        if os.path.exists(dir_path):
            return {'error': f'文章「{safe_title}」已存在'}

        os.makedirs(dir_path, exist_ok=True)

        pub_date = params.get('pub_date', [''])[0].strip()
        if pub_date:
            date_value = pub_date.replace('T', ' ') + ':00'
        else:
            from datetime import datetime
            date_value = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        tags = params.get('tags', [''])[0].strip()
        tags_yaml = '[]'
        if tags:
            tag_list = [t.strip() for t in tags.replace(',', ' ').split() if t.strip()]
            tags_yaml = json.dumps(tag_list, ensure_ascii=False)

        content = params.get('content', [''])[0].strip()
        if not content:
            content = '在这里写下你的内容吧！'

        md = f'''---
title: "{safe_title}"
date: {date_value}
description: ""
tags: {tags_yaml}
---

{content}
'''

        filepath = os.path.join(dir_path, 'index.zh-Hans.md')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md)

        return {'success': True, 'file': filepath, 'title': safe_title}

    def add_photo(self, params):
        img_path = params.get('img_path', [''])[0].strip()
        caption = params.get('caption', [''])[0].strip()

        if not img_path:
            return {'error': '图片路径不能为空'}

        data_file = os.path.join(BLOG_DIR, 'data', 'yin.json')
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        item = {'img': img_path}
        if caption:
            item['caption'] = caption
        data['items'].append(item)

        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return {'success': True, 'count': len(data['items'])}

    def add_travel(self, params):
        img_path = params.get('img_path', [''])[0].strip()
        place = params.get('place', [''])[0].strip()
        caption = params.get('caption', [''])[0].strip()

        if not img_path:
            return {'error': '图片路径不能为空'}

        data_file = os.path.join(BLOG_DIR, 'data', 'xing.json')
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        item = {'img': img_path}
        if place:
            item['place'] = place
        if caption:
            item['caption'] = caption
        data['items'].append(item)

        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return {'success': True, 'count': len(data['items'])}

    def create_project(self, title, params):
        safe_title = title.strip()
        dir_path = os.path.join(BLOG_DIR, 'content', 'projects', safe_title)

        if os.path.exists(dir_path):
            return {'error': f'项目「{safe_title}」已存在'}

        os.makedirs(dir_path, exist_ok=True)

        pub_date = params.get('pub_date', [''])[0].strip()
        if pub_date:
            date_value = pub_date.replace('T', ' ') + ':00'
        else:
            from datetime import datetime
            date_value = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        desc = params.get('desc', [''])[0].strip()
        tags = params.get('tags', [''])[0].strip()
        tags_yaml = '[]'
        if tags:
            tag_list = [t.strip() for t in tags.replace(',', ' ').split() if t.strip()]
            tags_yaml = json.dumps(tag_list, ensure_ascii=False)
        link = params.get('link', [''])[0].strip()

        content = params.get('content', [''])[0].strip()
        if not content:
            content = '在这里介绍你的项目...'

        md = f'''---
title: "{safe_title}"
date: {date_value}
description: "{desc}"
image: "img/project-cover.jpg"
tags: {tags_yaml}
link: "{link}"
---

{content}
'''

        filepath = os.path.join(dir_path, 'index.zh-Hans.md')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md)

        return {'success': True, 'file': filepath, 'title': safe_title}

    def send_admin_page(self):
        html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>博客管理面板</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, 'Microsoft YaHei', sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        .header {
            background: linear-gradient(135deg, #D4342F, #E85D57);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 1.8rem; margin-bottom: 8px; }
        .header p { opacity: 0.9; font-size: 0.95rem; }

        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 30px 20px;
        }

        .tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }
        .tab-btn {
            padding: 10px 24px;
            border: 2px solid #e0e0e0;
            background: white;
            border-radius: 100px;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 500;
            transition: all 0.3s;
            color: #666;
        }
        .tab-btn:hover { border-color: #D4342F; color: #D4342F; }
        .tab-btn.active {
            background: #D4342F;
            color: white;
            border-color: #D4342F;
        }

        .form-card {
            background: white;
            border-radius: 16px;
            padding: 32px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            display: none;
        }
        .form-card.active { display: block; }

        .form-card h2 {
            font-size: 1.3rem;
            margin-bottom: 8px;
            color: #1A1A2E;
        }
        .form-card .desc {
            color: #8E8EA0;
            font-size: 0.9rem;
            margin-bottom: 24px;
        }

        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            font-weight: 600;
            margin-bottom: 6px;
            color: #5A5A72;
            font-size: 0.9rem;
        }
        .form-group label .required { color: #D4342F; }
        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e8e8e8;
            border-radius: 10px;
            font-size: 1rem;
            font-family: inherit;
            transition: border-color 0.3s;
            background: #fafafa;
        }
        .form-group input:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #D4342F;
            background: white;
        }
        .form-group textarea {
            min-height: 200px;
            resize: vertical;
            line-height: 1.8;
        }
        .form-group .hint {
            font-size: 0.82rem;
            color: #8E8EA0;
            margin-top: 4px;
        }

        .btn-submit {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 14px 36px;
            background: linear-gradient(135deg, #D4342F, #E85D57);
            color: white;
            border: none;
            border-radius: 100px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 16px rgba(212,52,47,0.3);
        }
        .btn-submit:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 24px rgba(212,52,47,0.4);
        }
        .btn-submit:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }
        .stat-card .num {
            font-size: 2rem;
            font-weight: 700;
            color: #D4342F;
        }
        .stat-card .label {
            font-size: 0.85rem;
            color: #8E8EA0;
            margin-top: 4px;
        }

        .msg {
            padding: 12px 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: none;
            font-size: 0.95rem;
        }
        .msg.success {
            display: block;
            background: #E8F5EE;
            color: #3D8B6E;
            border: 1px solid #A8D5BA;
        }
        .msg.error {
            display: block;
            background: #FFF0EF;
            color: #B22F2A;
            border: 1px solid #FFD5D3;
        }

        .help-text {
            background: #FFF5EC;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
            border: 1px solid #FFE0C0;
        }
        .help-text h3 {
            color: #E8780A;
            font-size: 1rem;
            margin-bottom: 8px;
        }
        .help-text p, .help-text li {
            font-size: 0.9rem;
            color: #7A5C3E;
        }
        .help-text ul {
            padding-left: 20px;
            margin-top: 8px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>✿ 博客管理面板</h1>
        <p>简单填表，轻松发布内容</p>
    </div>

    <div class="container">
        <!-- 统计 -->
        <div class="stats" id="stats">
            <div class="stat-card">
                <div class="num" id="statPosts">-</div>
                <div class="label">文章</div>
            </div>
            <div class="stat-card">
                <div class="num" id="statPhotos">-</div>
                <div class="label">照片</div>
            </div>
            <div class="stat-card">
                <div class="num" id="statTravels">-</div>
                <div class="label">旅行</div>
            </div>
            <div class="stat-card">
                <div class="num" id="statProjects">-</div>
                <div class="label">项目</div>
            </div>
        </div>

        <!-- 消息提示 -->
        <div class="msg" id="msg"></div>

        <!-- 标签切换 -->
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('post')">📝 写文章</button>
            <button class="tab-btn" onclick="switchTab('photo')">🖼️ 加照片</button>
            <button class="tab-btn" onclick="switchTab('travel')">✈️ 加旅行</button>
            <button class="tab-btn" onclick="switchTab('project')">📁 加项目</button>
        </div>

        <!-- 写文章 -->
        <div class="form-card active" id="form-post">
            <h2>写新文章</h2>
            <p class="desc">写一篇散文、诗歌、随笔... 任何你想写的都可以。</p>
            <form onsubmit="return submitForm(event, 'post')">
                <div class="form-group">
                    <label>发布日期</label>
                    <input type="datetime-local" name="pub_date" id="pub_date">
                    <p class="hint">留空则使用当前时间</p>
                </div>
                <div class="form-group">
                    <label>文章标题 <span class="required">*</span></label>
                    <input type="text" name="title" placeholder="例如：秋天的第一片落叶" required>
                </div>
                <div class="form-group">
                    <label>标签</label>
                    <input type="text" name="tags" placeholder="例如：散文 秋天（用空格分隔）">
                    <p class="hint">留空表示不添加标签</p>
                </div>
                <div class="form-group">
                    <label>正文 <span class="required">*</span></label>
                    <textarea name="content" placeholder="在这里写下你的文章内容...

支持 Markdown 格式：
## 标题
**加粗** *斜体*
> 引用
- 列表" required></textarea>
                </div>
                <button type="submit" class="btn-submit" id="btn-post">发布文章</button>
            </form>
        </div>

        <!-- 加照片 -->
        <div class="form-card" id="form-photo">
            <h2>添加二次元照片</h2>
            <p class="desc">添加你喜欢的角色插画或截图到「荫」板块。</p>
            <div class="help-text">
                <h3>第一步：准备图片</h3>
                <p>把图片文件放到博客的 <code>static/img/</code> 目录下。</p>
                <ul>
                    <li>支持格式：jpg、png、gif、webp</li>
                    <li>建议大小：不超过 2MB</li>
                    <li>你可以用文件管理器直接复制粘贴到这里</li>
                </ul>
            </div>
            <form onsubmit="return submitForm(event, 'photo')">
                <div class="form-group">
                    <label>图片路径 <span class="required">*</span></label>
                    <input type="text" name="img_path" placeholder="例如：static/img/anime-character.jpg" required>
                    <p class="hint">相对于博客根目录的路径</p>
                </div>
                <div class="form-group">
                    <label>图片说明</label>
                    <input type="text" name="caption" placeholder="例如：宫园薰 - 四月是你的谎言">
                    <p class="hint">鼠标悬停时会显示这段文字</p>
                </div>
                <button type="submit" class="btn-submit" id="btn-photo">添加照片</button>
            </form>
        </div>

        <!-- 加旅行 -->
        <div class="form-card" id="form-travel">
            <h2>添加旅行影像</h2>
            <p class="desc">记录你去过的地方，看过的风景。</p>
            <div class="help-text">
                <h3>第一步：准备图片</h3>
                <p>把图片文件放到博客的 <code>static/img/</code> 目录下。</p>
                <ul>
                    <li>支持格式：jpg、png、gif、webp</li>
                    <li>建议用横版图片（16:10 比例效果最好）</li>
                </ul>
            </div>
            <form onsubmit="return submitForm(event, 'travel')">
                <div class="form-group">
                    <label>图片路径 <span class="required">*</span></label>
                    <input type="text" name="img_path" placeholder="例如：static/img/tokyo-tower.jpg" required>
                </div>
                <div class="form-group">
                    <label>地点</label>
                    <input type="text" name="place" placeholder="例如：东京塔">
                    <p class="hint">会在图片左上角显示地点标签</p>
                </div>
                <div class="form-group">
                    <label>图片说明</label>
                    <input type="text" name="caption" placeholder="例如：2024年冬天">
                </div>
                <button type="submit" class="btn-submit" id="btn-travel">添加旅行</button>
            </form>
        </div>

        <!-- 加项目 -->
        <div class="form-card" id="form-project">
            <h2>添加新项目</h2>
            <p class="desc">展示你的技术项目或作品。</p>
            <form onsubmit="return submitForm(event, 'project')">
                <div class="form-group">
                    <label>发布日期</label>
                    <input type="datetime-local" name="pub_date" id="pub_date_project">
                    <p class="hint">留空则使用当前时间</p>
                </div>
                <div class="form-group">
                    <label>项目名称 <span class="required">*</span></label>
                    <input type="text" name="title" placeholder="例如：个人博客系统" required>
                </div>
                <div class="form-group">
                    <label>简短描述</label>
                    <input type="text" name="desc" placeholder="一句话描述你的项目">
                </div>
                <div class="form-group">
                    <label>标签</label>
                    <input type="text" name="tags" placeholder="例如：Python Django（用空格分隔）">
                </div>
                <div class="form-group">
                    <label>项目链接</label>
                    <input type="text" name="link" placeholder="https://github.com/lcy631zz/项目名">
                </div>
                <div class="form-group">
                    <label>详细介绍</label>
                    <textarea name="content" placeholder="介绍你的项目：
- 做了什么
- 用了什么技术
- 遇到了什么挑战
- 有什么收获"></textarea>
                </div>
                <button type="submit" class="btn-submit" id="btn-project">添加项目</button>
            </form>
        </div>
    </div>

    <script>
        // 加载统计数据
        function loadStats() {
            fetch('/api/data')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('statPosts').textContent = data.posts.length;
                    document.getElementById('statPhotos').textContent = data.photos;
                    document.getElementById('statTravels').textContent = data.travels;
                    document.getElementById('statProjects').textContent = data.projects;
                })
                .catch(() => {});
        }
        loadStats();

        // 设置默认发布时间为当前时间
        function setDefaultDate() {
            const now = new Date();
            const offset = now.getTimezoneOffset();
            const local = new Date(now.getTime() - offset * 60000);
            const iso = local.toISOString().slice(0, 16);
            const d1 = document.getElementById('pub_date');
            const d2 = document.getElementById('pub_date_project');
            if (d1 && !d1.value) d1.value = iso;
            if (d2 && !d2.value) d2.value = iso;
        }
        setDefaultDate();

        // 标签切换
        function switchTab(type) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.form-card').forEach(f => f.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('form-' + type).classList.add('active');
        }

        // 提交表单
        function submitForm(e, type) {
            e.preventDefault();
            const form = e.target;
            const btn = document.getElementById('btn-' + type);
            const msg = document.getElementById('msg');

            const formData = new FormData(form);
            const params = new URLSearchParams();
            params.append('type', type);

            for (const [key, value] of formData.entries()) {
                params.append(key, value);
            }

            btn.disabled = true;
            btn.textContent = '提交中...';
            msg.className = 'msg';
            msg.style.display = 'none';

            fetch('/api/' + type, {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: params.toString()
            })
            .then(r => r.json())
            .then(data => {
                if (data.error) {
                    msg.className = 'msg error';
                    msg.textContent = data.error;
                } else {
                    msg.className = 'msg success';
                    const titles = {post: '文章', photo: '照片', travel: '旅行', project: '项目'};
                    msg.textContent = data.success ? '添加成功！' : (data.error || '完成');
                    form.reset();
                    loadStats();
                }
            })
            .catch(err => {
                msg.className = 'msg error';
                msg.textContent = '出错了：' + err.message;
            })
            .finally(() => {
                btn.disabled = false;
                const labels = {post: '发布文章', photo: '添加照片', travel: '添加旅行', project: '添加项目'};
                btn.textContent = labels[type];
            });

            return false;
        }
    </script>
</body>
</html>'''
        self.send_html(html)

    def log_message(self, format, *args):
        pass  # 静默日志


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT

    # 检查数据目录是否存在
    os.makedirs(os.path.join(BLOG_DIR, 'data'), exist_ok=True)
    for f in ['yin.json', 'xing.json']:
        path = os.path.join(BLOG_DIR, 'data', f)
        if not os.path.exists(path):
            with open(path, 'w', encoding='utf-8') as fp:
                json.dump({'items': []}, fp, ensure_ascii=False, indent=2)

    handler = AdminHandler
    with http.server.HTTPServer(("", port), handler) as httpd:
        print("")
        print("  ✿ 博客管理面板已启动")
        print("")
        print(f"  在浏览器打开: http://localhost:{port}/admin")
        print("")
        print("  按 Ctrl+C 停止服务")
        print("")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  已停止。")
            sys.exit(0)


if __name__ == '__main__':
    main()
