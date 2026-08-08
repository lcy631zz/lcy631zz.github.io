#!/usr/bin/env python3
"""
博客内容管理面板 - 本地Web服务器
运行后在浏览器打开 http://localhost:8080/admin 即可使用
"""

import http.server
import json
import os
import subprocess
import sys
from datetime import date, datetime
from urllib.parse import parse_qs, urlparse

PORT = 8082
BLOG_DIR = os.path.dirname(os.path.abspath(__file__))

class AdminHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/admin' or self.path == '/admin/':
            self.send_admin_page()
        elif self.path == '/api/data':
            self.send_json(self.get_data())
        elif self.path == '/api/git/status':
            self.send_json(self.git_status())
        elif self.path == '/api/git/log':
            self.send_json(self.git_log())
        elif self.path.startswith('/api/content'):
            self.send_json(self.handle_content())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/post':
            content_len = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_len).decode('utf-8')
            params = parse_qs(body)

            title = params.get('title', [''])[0].strip()
            content_type = params.get('type', [''])[0]

            if not content_type:
                self.send_json({'error': '请选择发布类型'}, 400)
                return

            if content_type in ('post', 'project') and not title:
                self.send_json({'error': '标题不能为空'}, 400)
                return

            if content_type == 'post':
                result = self.create_post(title, params)
            elif content_type == 'photo':
                result = self.add_photo(params)
            elif content_type == 'travel':
                result = self.add_travel(params)
            elif content_type == 'project':
                result = self.create_project(title, params)
            elif content_type == 'zhai':
                result = self.add_zhai(params)
            else:
                result = {'error': '未知类型'}

            if 'error' in result:
                self.send_json(result, 400)
            else:
                self.send_json(result)
        elif self.path == '/api/git/publish':
            self.send_json(self.git_publish())
        elif self.path == '/api/git/rollback':
            self.send_json(self.git_rollback())
        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        if self.path.startswith('/api/content'):
            content_len = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_len).decode('utf-8')
            params = parse_qs(body)
            self.send_json(self.delete_content(params))
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
        data = {'posts': [], 'photos': 0, 'travels': 0, 'projects': 0, 'excerpts': 0}

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

        zhai_file = os.path.join(BLOG_DIR, 'data', 'zhai.json')
        if os.path.isfile(zhai_file):
            with open(zhai_file, 'r', encoding='utf-8') as f:
                zhai = json.load(f)
                data['excerpts'] = len(zhai.get('items', []))

        return data

    def create_post(self, title, params):
        safe_title = title.strip()
        dir_path = os.path.join(BLOG_DIR, 'content', 'blog', safe_title)

        if os.path.exists(dir_path):
            return {'error': f'文章「{safe_title}」已存在'}

        os.makedirs(dir_path, exist_ok=True)

        pub_date = params.get('pub_date', [''])[0].strip()
        if pub_date:
            date_value = pub_date
        else:
            from datetime import date
            date_value = date.today().isoformat()
        period = params.get('period', [''])[0].strip()
        period_yaml = f'period: "{period}"' if period else ''
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
{period_yaml}
description: ""
tags: {tags_yaml}
---

{content}
'''

        filepath = os.path.join(dir_path, 'index.zh-Hans.md')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md)

        return {'success': True, 'file': filepath, 'title': safe_title}

    def _normalize_img_path(self, path):
        """Convert any path format to web path like img/filename.ext"""
        # Already a clean web path
        if path.startswith('img/') or path.startswith('/img/'):
            return path.lstrip('/')
        # WSL path: \\wsl.localhost\Ubuntu\home\fanze\my-website\static\img\xxx.jpg
        if 'wsl.localhost' in path or 'static' in path:
            import re
            m = re.search(r'img[/\\]([^\"\\]+)', path)
            if m:
                return 'img/' + m.group(1)
        # Windows absolute path: C:\Users\...\static\img\xxx.jpg
        if re.match(r'^[A-Za-z]:\\', path):
            import re
            m = re.search(r'img[/\\]([^\"\\]+)', path)
            if m:
                return 'img/' + m.group(1)
        # If it starts with static/, strip it
        if path.startswith('static/'):
            return path[7:]
        # If it starts with static\, strip it
        if path.startswith('static\\'):
            return path[7:]
        return path

    def add_photo(self, params):
        img_path = params.get('img_path', [''])[0].strip()
        caption = params.get('caption', [''])[0].strip()

        if not img_path:
            return {'error': '图片路径不能为空'}

        img_path = self._normalize_img_path(img_path)

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

        img_path = self._normalize_img_path(img_path)

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

    def add_zhai(self, params):
        quote = params.get('quote', [''])[0].strip()
        source = params.get('source', [''])[0].strip()
        note = params.get('note', [''])[0].strip()
        img = params.get('img', [''])[0].strip()

        if not quote:
            return {'error': '摘抄内容不能为空'}

        data_file = os.path.join(BLOG_DIR, 'data', 'zhai.json')
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        item = {'quote': quote}
        if source:
            item['source'] = source
        if note:
            item['note'] = note
        if img:
            item['img'] = img
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
            date_value = pub_date
        else:
            from datetime import date
            date_value = date.today().isoformat()
        period = params.get('period', [''])[0].strip()
        period_yaml = f'period: "{period}"' if period else ''
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
{period_yaml}
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

    def _git(self, args, timeout=30):
        result = subprocess.run(
            ['git'] + args, cwd=BLOG_DIR, capture_output=True, text=True, timeout=timeout
        )
        out = result.stdout.strip()
        err = result.stderr.strip()
        rc = result.returncode
        return {'rc': rc, 'stdout': out, 'stderr': err}

    def git_status(self):
        r = self._git(['status', '--short', '--branch'])
        if r['rc'] != 0:
            return {'error': r['stderr'] or 'git status failed'}
        lines = r['stdout'].splitlines() if r['stdout'] else []
        changed = [l for l in lines if l.strip()]
        branch = ''
        for l in lines:
            if l.startswith('##'):
                branch = l
                break
        return {
            'branch': branch or 'unknown',
            'hasChanges': len(changed) > 0,
            'count': len(changed),
            'files': changed[:20],
        }

    def git_log(self, n=5):
        r = self._git(['log', f'--oneline', f'-n', str(n)])
        if r['rc'] != 0:
            return {'error': r['stderr'] or 'git log failed'}
        entries = []
        for line in r['stdout'].splitlines():
            parts = line.split(' ', 1)
            entries.append({'hash': parts[0], 'msg': parts[1] if len(parts) > 1 else ''})
        return {'entries': entries}

    def git_publish(self):
        steps = []
        r = self._git(['add', '-A'])
        if r['rc'] != 0:
            return {'error': 'git add 失败: ' + r['stderr'], 'steps': steps}
        steps.append('已添加所有文件到暂存区')

        r = self._git(['diff', '--cached', '--quiet'])
        if r['rc'] == 0:
            return {'success': True, 'message': '没有需要提交的修改', 'skipped': True, 'steps': steps + ['没有检测到修改']}

        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        msg = f'update from admin panel {now}'
        r = self._git(['commit', '-m', msg])
        if r['rc'] != 0:
            return {'error': 'git commit 失败: ' + r['stderr'], 'steps': steps}
        steps.append(f'已提交: {msg}')

        r = self._git(['push', 'origin', 'master'])
        if r['rc'] != 0:
            return {'error': 'git push 失败: ' + r['stderr'], 'committed': True, 'steps': steps}
        steps.append('已推送到 GitHub')
        return {'success': True, 'message': '发布成功！', 'committed': True, 'pushed': True, 'steps': steps}

    def git_rollback(self):
        r = self._git(['reset', '--hard', 'HEAD'])
        if r['rc'] != 0:
            return {'error': 'git reset 失败: ' + r['stderr']}
        r = self._git(['clean', '-fd'])
        if r['rc'] != 0:
            return {'error': 'git clean 失败: ' + r['stderr']}
        return {'success': True, 'message': '已回滚到上一次提交的状态'}

    def handle_content(self):
        qs = parse_qs(urlparse(self.path).query)
        ctype = qs.get('type', [''])[0]
        if self.command == 'GET':
            return self.list_content(ctype)
        self.send_json({'error': '不支持的请求方法'}, 405)

    def list_content(self, ctype):
        try:
            if ctype == 'post':
                return self._list_posts()
            elif ctype == 'photo':
                return self._list_photos()
            elif ctype == 'travel':
                return self._list_travels()
            elif ctype == 'project':
                return self._list_projects()
            elif ctype == 'zhai':
                return self._list_zhaies()
            else:
                return {'error': '未知类型'}
        except Exception as e:
            return {'error': str(e)}

    def _list_posts(self):
        items = []
        blog_dir = os.path.join(BLOG_DIR, 'content', 'blog')
        if os.path.isdir(blog_dir):
            for d in sorted(os.listdir(blog_dir), reverse=True):
                idx = os.path.join(blog_dir, d, 'index.zh-Hans.md')
                if os.path.isfile(idx):
                    items.append({'id': d, 'title': d, 'path': idx, 'type': 'dir'})
        return {'items': items}

    def _list_photos(self):
        data = json.load(open(os.path.join(BLOG_DIR, 'data', 'yin.json'), encoding='utf-8'))
        items = []
        for i, item in enumerate(data.get('items', [])):
            items.append({'id': str(i), 'title': item.get('caption', item.get('img', '')), 'img': item.get('img', ''), 'caption': item.get('caption', ''), 'index': i})
        return {'items': items}

    def _list_travels(self):
        data = json.load(open(os.path.join(BLOG_DIR, 'data', 'xing.json'), encoding='utf-8'))
        items = []
        for i, item in enumerate(data.get('items', [])):
            items.append({'id': str(i), 'title': item.get('place', item.get('caption', '')), 'img': item.get('img', ''), 'place': item.get('place', ''), 'caption': item.get('caption', ''), 'index': i})
        return {'items': items}

    def _list_projects(self):
        items = []
        proj_dir = os.path.join(BLOG_DIR, 'content', 'projects')
        if os.path.isdir(proj_dir):
            for d in sorted(os.listdir(proj_dir), reverse=True):
                idx = os.path.join(proj_dir, d, 'index.zh-Hans.md')
                if os.path.isfile(idx):
                    items.append({'id': d, 'title': d, 'path': idx, 'type': 'dir'})
        return {'items': items}

    def _list_zhaies(self):
        data = json.load(open(os.path.join(BLOG_DIR, 'data', 'zhai.json'), encoding='utf-8'))
        items = []
        for i, item in enumerate(data.get('items', [])):
            items.append({'id': str(i), 'title': item.get('source', item.get('quote', '')[:30]), 'quote': item.get('quote', ''), 'source': item.get('source', ''), 'note': item.get('note', ''), 'index': i})
        return {'items': items}

    def delete_content(self, params):
        qs = parse_qs(urlparse(self.path).query)
        ctype = qs.get('type', [''])[0] or params.get('type', [''])[0]
        cid = params.get('id', [''])[0]
        try:
            if ctype == 'post':
                return self._delete_post(cid)
            elif ctype == 'photo':
                return self._delete_photo(cid)
            elif ctype == 'travel':
                return self._delete_travel(cid)
            elif ctype == 'project':
                return self._delete_project(cid)
            elif ctype == 'zhai':
                return self._delete_zhai(cid)
            else:
                return {'error': '未知类型'}
        except Exception as e:
            return {'error': str(e)}

    def _delete_post(self, cid):
        import shutil
        dir_path = os.path.join(BLOG_DIR, 'content', 'blog', cid)
        if not os.path.isdir(dir_path):
            return {'error': f'文章「{cid}」不存在'}
        shutil.rmtree(dir_path)
        return {'success': True, 'message': f'已删除文章「{cid}」'}

    def _delete_project(self, cid):
        import shutil
        dir_path = os.path.join(BLOG_DIR, 'content', 'projects', cid)
        if not os.path.isdir(dir_path):
            return {'error': f'项目「{cid}」不存在'}
        shutil.rmtree(dir_path)
        return {'success': True, 'message': f'已删除项目「{cid}」'}

    def _delete_photo(self, cid):
        data_file = os.path.join(BLOG_DIR, 'data', 'yin.json')
        data = json.load(open(data_file, encoding='utf-8'))
        idx = int(cid)
        if idx < 0 or idx >= len(data.get('items', [])):
            return {'error': '照片不存在'}
        data['items'].pop(idx)
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return {'success': True, 'message': '已删除照片'}

    def _delete_travel(self, cid):
        data_file = os.path.join(BLOG_DIR, 'data', 'xing.json')
        data = json.load(open(data_file, encoding='utf-8'))
        idx = int(cid)
        if idx < 0 or idx >= len(data.get('items', [])):
            return {'error': '旅行不存在'}
        data['items'].pop(idx)
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return {'success': True, 'message': '已删除旅行'}

    def _delete_zhai(self, cid):
        data_file = os.path.join(BLOG_DIR, 'data', 'zhai.json')
        data = json.load(open(data_file, encoding='utf-8'))
        idx = int(cid)
        if idx < 0 or idx >= len(data.get('items', [])):
            return {'error': '摘抄不存在'}
        data['items'].pop(idx)
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return {'success': True, 'message': '已删除摘抄'}

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

        .git-bar {
            background: white;
            border-radius: 12px;
            padding: 16px 24px;
            margin-bottom: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            display: flex;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
        }
        .git-bar .git-info {
            flex: 1;
            min-width: 200px;
        }
        .git-bar .git-branch {
            font-weight: 600;
            color: #5A5A72;
            font-size: 0.9rem;
        }
        .git-bar .git-status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 6px;
        }
        .git-bar .git-status-dot.clean { background: #3D8B6E; }
        .git-bar .git-status-dot.dirty { background: #E85D57; }
        .git-bar .git-status-text {
            font-size: 0.85rem;
            color: #8E8EA0;
        }
        .git-bar .git-btns {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .btn-publish {
            padding: 10px 28px;
            background: linear-gradient(135deg, #D4342F, #E85D57);
            color: white;
            border: none;
            border-radius: 100px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 16px rgba(212,52,47,0.3);
        }
        .btn-publish:hover { transform: translateY(-2px); box-shadow: 0 6px 24px rgba(212,52,47,0.4); }
        .btn-publish:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .btn-rollback {
            padding: 10px 28px;
            background: white;
            color: #B22F2A;
            border: 2px solid #FFD5D3;
            border-radius: 100px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-rollback:hover { background: #FFF0EF; border-color: #E85D57; }
        .btn-rollback:disabled { opacity: 0.5; cursor: not-allowed; }

        .git-detail {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
            margin-top: 0;
        }
        .git-detail.open {
            max-height: 400px;
            margin-top: 12px;
        }
        .git-detail-inner {
            background: #f8f8f8;
            border-radius: 10px;
            padding: 16px;
            border: 1px solid #e8e8e8;
        }
        .git-detail-inner h4 {
            font-size: 0.85rem;
            color: #8E8EA0;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .git-file-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .git-file-list li {
            padding: 6px 12px;
            font-size: 0.85rem;
            font-family: 'Courier New', monospace;
            border-bottom: 1px solid #eee;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .git-file-list li:last-child { border-bottom: none; }
        .git-file-status {
            font-weight: 700;
            font-size: 0.8rem;
            min-width: 20px;
        }
        .git-file-status.modified { color: #E85D57; }
        .git-file-status.added { color: #3D8B6E; }
        .git-file-status.deleted { color: #888; }
        .git-file-path { color: #333; word-break: break-all; }

        .git-progress {
            margin-top: 12px;
            padding: 12px 16px;
            background: #f0f7ff;
            border-radius: 10px;
            border: 1px solid #d0e0f0;
            display: none;
        }
        .git-progress.active { display: block; }
        .git-progress .step {
            font-size: 0.9rem;
            color: #5A5A72;
            padding: 4px 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .git-progress .step.done { color: #3D8B6E; }
        .git-progress .step.active { color: #D4342F; font-weight: 600; }
        .git-progress .step-icon {
            font-size: 1rem;
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
            <div class="stat-card">
                <div class="num" id="statExcerpts">-</div>
                <div class="label">摘抄</div>
            </div>
        </div>

        <!-- 消息提示 -->
        <div class="msg" id="msg"></div>

        <!-- Git 操作栏 -->
        <div class="git-bar" id="gitBar">
            <div class="git-info">
                <span class="git-branch" id="gitBranch">分支: 加载中...</span><br>
                <span class="git-status-text" id="gitStatusText" style="cursor:pointer" onclick="toggleGitDetail()"></span>
            </div>
            <div class="git-btns">
                <button class="btn-publish" id="btnPublish" onclick="gitPublish()">🚀 一键发布</button>
                <button class="btn-rollback" id="btnRollback" onclick="gitRollback()">↩️ 一键回滚</button>
            </div>
        </div>
        <!-- 未提交文件详情 -->
        <div class="git-detail" id="gitDetail">
            <div class="git-detail-inner">
                <h4>未提交的文件</h4>
                <ul class="git-file-list" id="gitFileList"></ul>
            </div>
        </div>
        <!-- 发布进度 -->
        <div class="git-progress" id="gitProgress">
            <div id="gitProgressSteps"></div>
        </div>

        <!-- 标签切换 -->
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('post')">📝 写文章</button>
            <button class="tab-btn" onclick="switchTab('photo')">🖼️ 加照片</button>
            <button class="tab-btn" onclick="switchTab('travel')">✈️ 加旅行</button>
            <button class="tab-btn" onclick="switchTab('project')">📁 加项目</button>
            <button class="tab-btn" onclick="switchTab('zhai')">📖 加摘抄</button>
            <button class="tab-btn" onclick="switchTab('manage')" style="background:#f0f0f0">📋 内容管理</button>
        </div>

        <!-- 写文章 -->
        <div class="form-card active" id="form-post">
            <h2>写新文章</h2>
            <p class="desc">写一篇散文、诗歌、随笔... 任何你想写的都可以。</p>
            <form onsubmit="return submitForm(event, 'post')">
                <div class="form-group">
                    <label>日期</label>
                    <input type="date" name="pub_date" id="pub_date">
                    <p class="hint">留空则使用今天</p>
                </div>
                <div class="form-group">
                    <label>时期</label>
                    <input type="text" name="period" placeholder="例如：小学、2024年夏天、大学时期（可留空）">
                    <p class="hint">用文字描述这篇文章的时间背景</p>
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
                    <label>日期</label>
                    <input type="date" name="pub_date" id="pub_date_project">
                    <p class="hint">留空则使用今天</p>
                </div>
                <div class="form-group">
                    <label>时期</label>
                    <input type="text" name="period" placeholder="例如：大学时期、2024年夏天（可留空）">
                    <p class="hint">用文字描述这个项目的时间背景</p>
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

        <!-- 加摘抄 -->
        <div class="form-card" id="form-zhai">
            <h2>添加读书摘抄</h2>
            <p class="desc">记录书中打动你的文字。</p>
            <form onsubmit="return submitForm(event, 'zhai')">
                <div class="form-group">
                    <label>摘抄内容 <span class="required">*</span></label>
                    <textarea name="quote" placeholder="例如：人间有味是清欢。" required></textarea>
                </div>
                <div class="form-group">
                    <label>出处</label>
                    <input type="text" name="source" placeholder="例如：苏轼《浣溪沙》">
                </div>
                <div class="form-group">
                    <label>备注</label>
                    <input type="text" name="note" placeholder="例如：最喜欢的诗句">
                </div>
                <div class="form-group">
                    <label>配图路径</label>
                    <input type="text" name="img" placeholder="例如：static/img/zhai-cover.jpg（可选）">
                </div>
                <button type="submit" class="btn-submit" id="btn-zhai">添加摘抄</button>
            </form>
        </div>

        <!-- 内容管理 -->
        <div class="form-card" id="form-manage">
            <h2>管理已发布内容</h2>
            <p class="desc">查看、编辑或删除你已经发布的内容。</p>
            <div class="tabs" style="margin-bottom:16px">
                <button class="tab-btn active" onclick="manageTab='post';loadManageList()">📝 文章</button>
                <button class="tab-btn" onclick="manageTab='photo';loadManageList()">🖼️ 照片</button>
                <button class="tab-btn" onclick="manageTab='travel';loadManageList()">✈️ 旅行</button>
                <button class="tab-btn" onclick="manageTab='project';loadManageList()">📁 项目</button>
                <button class="tab-btn" onclick="manageTab='zhai';loadManageList()">📖 摘抄</button>
            </div>
            <div id="manageList" style="min-height:100px">
                <p style="color:#8E8EA0;text-align:center;padding:40px">加载中...</p>
            </div>
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
                    document.getElementById('statExcerpts').textContent = data.excerpts;
                })
                .catch(() => {});
        }
        loadStats();

        // 设置默认日期为今天
        function setDefaultDate() {
            const now = new Date();
            const today = now.getFullYear() + '-' + String(now.getMonth()+1).padStart(2,'0') + '-' + String(now.getDate()).padStart(2,'0');
            const d1 = document.getElementById('pub_date');
            const d2 = document.getElementById('pub_date_project');
            if (d1 && d1.type === 'date' && !d1.value) d1.value = today;
            if (d2 && d2.type === 'date' && !d2.value) d2.value = today;
        }
        setDefaultDate();

        // 内容管理
        let manageTab = 'post';
        const manageTypeNames = {post: '文章', photo: '照片', travel: '旅行', project: '项目', zhai: '摘抄'};

        function loadManageList() {
            const listEl = document.getElementById('manageList');
            listEl.innerHTML = '<p style="color:#8E8EA0;text-align:center;padding:40px">加载中...</p>';
            fetch('/api/content?type=' + manageTab)
                .then(r => r.json())
                .then(data => {
                    if (data.error) {
                        listEl.innerHTML = '<p style="color:#B22F2A;text-align:center;padding:40px">' + data.error + '</p>';
                        return;
                    }
                    const items = data.items || [];
                    if (!items.length) {
                        listEl.innerHTML = '<p style="color:#8E8EA0;text-align:center;padding:40px">暂无内容</p>';
                        return;
                    }
                    listEl.innerHTML = '<div style="display:grid;gap:12px">' + items.map(item => {
                        const title = item.title || item.quote?.substring(0, 50) || '未命名';
                        const subtitle = item.source || item.place || item.caption || item.path || '';
                        const imgPreview = item.img ? `<div style="width:60px;height:60px;border-radius:8px;overflow:hidden;flex-shrink:0"><img src="/${item.img}" style="width:100%;height:100%;object-fit:cover" onerror="this.style.display='none'"></div>` : '';
                        return `<div class="manage-item">
                            <div style="display:flex;align-items:center;gap:12px;padding:12px 16px;background:#fafafa;border-radius:10px;border:1px solid #eee">
                                ${imgPreview}
                                <div style="flex:1;min-width:0">
                                    <div style="font-weight:600;color:#1A1A2E">${title}</div>
                                    ${subtitle ? `<div style="font-size:0.85rem;color:#8E8EA0;margin-top:2px">${subtitle}</div>` : ''}
                                </div>
                                <div style="display:flex;gap:6px;flex-shrink:0">
                                    <button onclick="editItem('${item.id}')" style="padding:6px 16px;border:1px solid #ddd;background:white;border-radius:8px;cursor:pointer;font-size:0.85rem">编辑</button>
                                    <button onclick="deleteItem('${item.id}')" style="padding:6px 16px;border:1px solid #FFD5D3;background:white;color:#B22F2A;border-radius:8px;cursor:pointer;font-size:0.85rem">删除</button>
                                </div>
                            </div>
                        </div>`;
                    }).join('') + '</div>';
                })
                .catch(err => {
                    listEl.innerHTML = '<p style="color:#B22F2A;text-align:center;padding:40px">加载失败: ' + err.message + '</p>';
                });
        }

        function editItem(id) {
            // 根据当前类型切换到对应标签页
            const tabMap = {post: 'post', photo: 'photo', travel: 'travel', project: 'project', zhai: 'zhai'};
            switchTab(tabMap[manageTab] || 'post');
            showMsg('请手动修改内容后重新提交（编辑功能开发中...）', 'success');
        }

        function deleteItem(id) {
            const typeName = manageTypeNames[manageTab] || manageTab;
            if (!confirm(`确定删除这条${typeName}吗？此操作不可恢复。`)) return;
            const btn = event.target;
            btn.disabled = true;
            btn.textContent = '删除中...';
            fetch('/api/content?type=' + manageTab, {
                method: 'DELETE',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'id=' + encodeURIComponent(id)
            })
            .then(r => r.json())
            .then(data => {
                if (data.error) {
                    showMsg(data.error, 'error');
                } else {
                    showMsg(data.message || '已删除', 'success');
                    loadManageList();
                    loadStats();
                }
            })
            .catch(err => showMsg('删除失败: ' + err.message, 'error'))
            .finally(() => { btn.disabled = false; btn.textContent = '删除'; });
        }

        // Git 状态
        function loadGitStatus() {
            fetch('/api/git/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('gitBranch').textContent = data.branch || '未知分支';
                    const dot = document.querySelector('.git-status-dot');
                    const text = document.getElementById('gitStatusText');
                    if (dot) {
                        dot.className = 'git-status-dot ' + (data.hasChanges ? 'dirty' : 'clean');
                    }
                    if (text) {
                        if (data.hasChanges) {
                            text.textContent = `${data.count} 个未提交修改（点击查看）`;
                            text.style.cursor = 'pointer';
                            text.style.color = '#D4342F';
                        } else {
                            text.textContent = '已同步到最新';
                            text.style.cursor = 'default';
                            text.style.color = '#8E8EA0';
                        }
                    }
                    // 文件列表
                    const listEl = document.getElementById('gitFileList');
                    if (listEl) {
                        listEl.innerHTML = '';
                        if (data.files && data.files.length) {
                            data.files.forEach(f => {
                                const li = document.createElement('li');
                                const parts = f.trim().split(/\\s+/, 2);
                                if (parts.length >= 2) {
                                    const status = parts[0];
                                    const path = parts[1];
                                    let cls = 'modified', label = 'M';
                                    if (status === 'A') { cls = 'added'; label = '+'; }
                                    else if (status === 'D') { cls = 'deleted'; label = '−'; }
                                    else if (status === '??') { cls = 'added'; label = '?'; }
                                    li.innerHTML = `<span class="git-file-status ${cls}">${label}</span><span class="git-file-path">${path}</span>`;
                                } else {
                                    li.textContent = f;
                                }
                                listEl.appendChild(li);
                            });
                        }
                        if (!data.hasChanges) {
                            listEl.innerHTML = '<li style="color:#8E8EA0">暂无修改</li>';
                        }
                    }
                })
                .catch(() => {});
        }
        loadGitStatus();
        setInterval(loadGitStatus, 10000);

        function toggleGitDetail() {
            const el = document.getElementById('gitDetail');
            if (el) el.classList.toggle('open');
        }

        function showProgress(steps) {
            const container = document.getElementById('gitProgress');
            const stepsEl = document.getElementById('gitProgressSteps');
            container.classList.add('active');
            stepsEl.innerHTML = steps.map(s =>
                `<div class="step ${s.done ? 'done' : (s.active ? 'active' : '')}"><span class="step-icon">${s.done ? '✅' : (s.active ? '⏳' : '⬜')}</span>${s.text}</div>`
            ).join('');
        }

        function hideProgress() {
            const container = document.getElementById('gitProgress');
            if (container) container.classList.remove('active');
        }

        // 一键发布
        function gitPublish() {
            const btn = document.getElementById('btnPublish');
            btn.disabled = true;
            showProgress([
                {text: '添加文件到暂存区...', active: true, done: false},
                {text: '提交变更...', active: false, done: false},
                {text: '推送到 GitHub...', active: false, done: false}
            ]);
            fetch('/api/git/publish', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    if (data.error) {
                        showMsg(data.error, 'error');
                        hideProgress();
                    } else {
                        const steps = data.steps || [];
                        showProgress(steps.map((s, i) => ({
                            text: s,
                            done: i < steps.length,
                            active: i === steps.length
                        })));
                        if (!data.skipped) {
                            setTimeout(() => {
                                hideProgress();
                                showMsg(data.message || '发布完成！', 'success');
                            }, 1200);
                        } else {
                            hideProgress();
                            showMsg(data.message || '没有需要提交的修改', 'success');
                        }
                        loadGitStatus();
                    }
                })
                .catch(err => {
                    showMsg('发布失败: ' + err.message, 'error');
                    hideProgress();
                })
                .finally(() => { btn.disabled = false; btn.textContent = '🚀 一键发布'; });
        }

        // 一键回滚
        function gitRollback() {
            if (!confirm('确定要回滚吗？这将丢弃所有未提交的修改，恢复到上一次发布的版本。')) return;
            const btn = document.getElementById('btnRollback');
            btn.disabled = true;
            btn.textContent = '回滚中...';
            fetch('/api/git/rollback', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    if (data.error) {
                        showMsg(data.error, 'error');
                    } else {
                        showMsg(data.message || '已回滚', 'success');
                        loadGitStatus();
                        loadStats();
                    }
                })
                .catch(err => showMsg('回滚失败: ' + err.message, 'error'))
                .finally(() => { btn.disabled = false; btn.textContent = '↩️ 一键回滚'; });
        }

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

            fetch('/api/post', {
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
