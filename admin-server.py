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
        if self.path == '/' or self.path == '/index.html':
            self.send_pwa_page()
        elif self.path == '/manifest.json':
            self.send_static_file('admin/manifest.json', 'application/json')
        elif self.path == '/sw.js':
            self.send_static_file('admin/sw.js', 'application/javascript')
        elif self.path == '/admin' or self.path == '/admin/':
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

    def send_static_file(self, rel_path, content_type):
        """Serve a static file from the blog directory"""
        abs_path = os.path.join(BLOG_DIR, rel_path)
        try:
            with open(abs_path, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def do_POST(self):
        if self.path == '/api/post':
            content_len = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_len).decode('utf-8')
            params = parse_qs(body, keep_blank_values=True)

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
        elif self.path == '/api/update':
            content_len = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_len).decode('utf-8')
            params = parse_qs(body, keep_blank_values=True)

            ctype = params.get('type', [''])[0]
            cid = params.get('id', [''])[0]
            title = params.get('title', [''])[0].strip()

            if not ctype:
                self.send_json({'error': '请选择类型'}, 400)
                return
            if not cid:
                self.send_json({'error': '缺少内容 ID'}, 400)
                return
            if ctype in ('post', 'project') and not title:
                self.send_json({'error': '标题不能为空'}, 400)
                return

            if ctype == 'post':
                result = self._update_post(cid, params)
            elif ctype == 'project':
                result = self._update_project(cid, params)
            elif ctype == 'photo':
                result = self._update_photo(cid, params)
            elif ctype == 'travel':
                result = self._update_travel(cid, params)
            elif ctype == 'zhai':
                result = self._update_zhai(cid, params)
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
        elif self.path == '/api/upload':
            result = self.handle_upload()
            self.send_json(result)
        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        if self.path.startswith('/api/content'):
            content_len = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_len).decode('utf-8')
            params = parse_qs(body, keep_blank_values=True)
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

    def handle_upload(self):
        """Handle file upload via multipart/form-data, save to static/img/"""
        content_type = self.headers.get('Content-Type', '')
        if not content_type.startswith('multipart/form-data'):
            return {'error': '请上传文件'}
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len)

        # Extract filename from multipart body
        import re
        m = re.search(rb'filename="([^"]+)"', body)
        if not m:
            return {'error': '未找到文件'}
        filename = m.group(1).decode('utf-8', errors='replace')

        # Only allow image files
        if not any(filename.lower().endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            return {'error': '仅支持 jpg、png、gif、webp 格式'}

        # Sanitize filename
        import os as os_mod
        basename = os_mod.path.basename(filename)
        name, ext = os_mod.path.splitext(basename)
        safe_name = ''.join(c for c in name if c.isalnum() or c in '-_ ') + ext.lower()
        if not safe_name or len(safe_name) < 2:
            safe_name = 'upload' + ext.lower()

        # Extract file data using proper multipart parsing
        from email.parser import BytesParser
        from email import policy
        # The body is a full RFC-2354 multipart message; prepend a synthetic header
        # so BytesParser can parse it
        full_message = b'Content-Type: ' + content_type.encode('utf-8') + b'\r\n\r\n' + body
        msg = BytesParser(policy=policy.default).parsebytes(full_message)
        file_part = None
        for part in msg.iter_parts():
            if part.get_content_disposition() == 'form-data' and part.get_param('name', header='content-disposition') == 'file':
                file_part = part
                break
        if not file_part:
            return {'error': '读取文件内容失败'}
        file_data = file_part.get_payload(decode=True)
        if not file_data or len(file_data) < 10:
            return {'error': '读取文件内容失败'}

        # Save to static/img/
        img_dir = os_mod.path.join(BLOG_DIR, 'static', 'img')
        os_mod.makedirs(img_dir, exist_ok=True)
        save_path = os_mod.path.join(img_dir, safe_name)
        if os_mod.path.exists(save_path):
            name, ext = os_mod.path.splitext(safe_name)
            save_path = os_mod.path.join(img_dir, name + '_' + ext)

        with open(save_path, 'wb') as f:
            f.write(file_data)

        web_path = 'img/' + os_mod.path.basename(save_path)
        return {'success': True, 'path': web_path, 'filename': os_mod.path.basename(save_path)}

    def _normalize_img_path(self, path):
        """Convert any path format to web path like img/filename.ext"""
        path = path.strip().strip('"').strip("'")
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
        cid = qs.get('id', [''])[0]
        if self.command == 'GET':
            if cid:
                return self.get_content(ctype, cid)
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

    # ── 获取单条内容 ──
    def get_content(self, ctype, cid):
        try:
            if ctype == 'post':
                return self._get_post(cid)
            elif ctype == 'photo':
                return self._get_photo(cid)
            elif ctype == 'travel':
                return self._get_travel(cid)
            elif ctype == 'project':
                return self._get_project(cid)
            elif ctype == 'zhai':
                return self._get_zhai(cid)
            else:
                return {'error': '未知类型'}
        except Exception as e:
            return {'error': str(e)}

    def _parse_frontmatter(self, filepath):
        """Parse Hugo frontmatter file, return (meta_dict, body_string)"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}, content
        _, frontmatter, body = parts
        meta = {}
        for line in frontmatter.strip().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ':' in line:
                key, val = line.split(':', 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if val.startswith('[') and val.endswith(']'):
                    try:
                        val = json.loads(val)
                        if isinstance(val, list):
                            val = ' '.join(str(v) for v in val)
                    except:
                        pass
                meta[key] = val
        return meta, body.strip()

    def _write_frontmatter(self, filepath, meta, body):
        """Write Hugo frontmatter file from meta dict and body string"""
        lines = ['---']
        for key in ['title', 'date', 'period', 'description', 'tags', 'link', 'image']:
            if key not in meta:
                continue
            val = meta[key]
            if key == 'description':
                lines.append(f'description: "{val}"')
            elif key == 'tags' and isinstance(val, str):
                tag_list = [t.strip() for t in val.replace(',', ' ').split() if t.strip()]
                val = json.dumps(tag_list, ensure_ascii=False)
                lines.append(f'{key}: {val}')
            elif val or key in ('title', 'date'):
                if isinstance(val, str) and key not in ('tags',):
                    lines.append(f'{key}: "{val}"')
                else:
                    lines.append(f'{key}: {val}')
        lines.append('---')
        lines.append('')
        lines.append(body)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def _get_post(self, cid):
        filepath = os.path.join(BLOG_DIR, 'content', 'blog', cid, 'index.zh-Hans.md')
        if not os.path.isfile(filepath):
            return {'error': f'文章「{cid}」不存在'}
        meta, body = self._parse_frontmatter(filepath)
        return {
            'id': cid, 'type': 'post',
            'title': meta.get('title', cid),
            'date': meta.get('date', ''),
            'period': meta.get('period', ''),
            'tags': meta.get('tags', ''),
            'content': body,
            'path': filepath,
        }

    def _get_project(self, cid):
        filepath = os.path.join(BLOG_DIR, 'content', 'projects', cid, 'index.zh-Hans.md')
        if not os.path.isfile(filepath):
            return {'error': f'项目「{cid}」不存在'}
        meta, body = self._parse_frontmatter(filepath)
        return {
            'id': cid, 'type': 'project',
            'title': meta.get('title', cid),
            'date': meta.get('date', ''),
            'period': meta.get('period', ''),
            'description': meta.get('description', ''),
            'image': meta.get('image', ''),
            'tags': meta.get('tags', ''),
            'link': meta.get('link', ''),
            'content': body,
            'path': filepath,
        }

    def _get_photo(self, cid):
        data = json.load(open(os.path.join(BLOG_DIR, 'data', 'yin.json'), encoding='utf-8'))
        idx = int(cid)
        if idx < 0 or idx >= len(data.get('items', [])):
            return {'error': '照片不存在'}
        item = data['items'][idx]
        return {'id': cid, 'type': 'photo', 'img': item.get('img', ''), 'caption': item.get('caption', ''), 'index': idx}

    def _get_travel(self, cid):
        data = json.load(open(os.path.join(BLOG_DIR, 'data', 'xing.json'), encoding='utf-8'))
        idx = int(cid)
        if idx < 0 or idx >= len(data.get('items', [])):
            return {'error': '旅行不存在'}
        item = data['items'][idx]
        return {'id': cid, 'type': 'travel', 'img': item.get('img', ''), 'place': item.get('place', ''), 'caption': item.get('caption', ''), 'index': idx}

    def _get_zhai(self, cid):
        data = json.load(open(os.path.join(BLOG_DIR, 'data', 'zhai.json'), encoding='utf-8'))
        idx = int(cid)
        if idx < 0 or idx >= len(data.get('items', [])):
            return {'error': '摘抄不存在'}
        item = data['items'][idx]
        return {'id': cid, 'type': 'zhai', 'quote': item.get('quote', ''), 'source': item.get('source', ''), 'note': item.get('note', ''), 'img': item.get('img', ''), 'index': idx}

    # ── 更新内容 ──
    def _update_post(self, cid, params):
        filepath = os.path.join(BLOG_DIR, 'content', 'blog', cid, 'index.zh-Hans.md')
        if not os.path.isfile(filepath):
            return {'error': f'文章「{cid}」不存在'}
        old_meta, body = self._parse_frontmatter(filepath)
        title = params.get('title', [''])[0].strip() or old_meta.get('title', cid)
        pub_date = params.get('pub_date', [''])[0].strip() or old_meta.get('date', date.today().isoformat())
        period = params.get('period', [''])[0].strip()
        tags = params.get('tags', [''])[0].strip()
        content = params.get('content', [''])[0].strip() or body
        meta = {
            'title': title,
            'date': pub_date,
            'period': period if period is not None else old_meta.get('period', ''),
            'tags': tags,
            'description': old_meta.get('description', ''),
        }
        # Only update period if user provided a value (allow empty to clear)
        if 'period' in params and params['period'][0].strip() != '':
            meta['period'] = period
        else:
            meta['period'] = old_meta.get('period', '')
        self._write_frontmatter(filepath, meta, content)
        return {'success': True, 'message': f'文章「{title}」已更新'}

    def _update_project(self, cid, params):
        filepath = os.path.join(BLOG_DIR, 'content', 'projects', cid, 'index.zh-Hans.md')
        if not os.path.isfile(filepath):
            return {'error': f'项目「{cid}」不存在'}
        old_meta, body = self._parse_frontmatter(filepath)
        title = params.get('title', [''])[0].strip() or old_meta.get('title', cid)
        pub_date = params.get('pub_date', [''])[0].strip() or old_meta.get('date', date.today().isoformat())
        period = params.get('period', [''])[0].strip()
        desc = params.get('desc', [''])[0].strip()
        tags = params.get('tags', [''])[0].strip()
        link = params.get('link', [''])[0].strip()
        content = params.get('content', [''])[0].strip() or body
        meta = {
            'title': title,
            'date': pub_date,
            'period': period if period != '' else old_meta.get('period', ''),
            'description': desc if desc != '' else old_meta.get('description', ''),
            'image': old_meta.get('image', ''),
            'tags': tags,
            'link': link if link != '' else old_meta.get('link', ''),
        }
        self._write_frontmatter(filepath, meta, content)
        return {'success': True, 'message': f'项目「{title}」已更新'}

    def _update_photo(self, cid, params):
        data = json.load(open(os.path.join(BLOG_DIR, 'data', 'yin.json'), encoding='utf-8'))
        idx = int(cid)
        if idx < 0 or idx >= len(data.get('items', [])):
            return {'error': '照片不存在'}
        img_path = params.get('img_path', [''])[0].strip()
        caption = params.get('caption', [''])[0].strip()
        if img_path:
            data['items'][idx]['img'] = self._normalize_img_path(img_path)
        if 'caption' in params:
            if caption:
                data['items'][idx]['caption'] = caption
            else:
                data['items'][idx].pop('caption', None)
        with open(os.path.join(BLOG_DIR, 'data', 'yin.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return {'success': True, 'message': '照片已更新'}

    def _update_travel(self, cid, params):
        data = json.load(open(os.path.join(BLOG_DIR, 'data', 'xing.json'), encoding='utf-8'))
        idx = int(cid)
        if idx < 0 or idx >= len(data.get('items', [])):
            return {'error': '旅行不存在'}
        img_path = params.get('img_path', [''])[0].strip()
        place = params.get('place', [''])[0].strip()
        caption = params.get('caption', [''])[0].strip()
        if img_path:
            data['items'][idx]['img'] = self._normalize_img_path(img_path)
        if 'place' in params:
            if place:
                data['items'][idx]['place'] = place
            else:
                data['items'][idx].pop('place', None)
        if 'caption' in params:
            if caption:
                data['items'][idx]['caption'] = caption
            else:
                data['items'][idx].pop('caption', None)
        with open(os.path.join(BLOG_DIR, 'data', 'xing.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return {'success': True, 'message': '旅行已更新'}

    def _update_zhai(self, cid, params):
        data = json.load(open(os.path.join(BLOG_DIR, 'data', 'zhai.json'), encoding='utf-8'))
        idx = int(cid)
        if idx < 0 or idx >= len(data.get('items', [])):
            return {'error': '摘抄不存在'}
        quote = params.get('quote', [''])[0].strip()
        source = params.get('source', [''])[0].strip()
        note = params.get('note', [''])[0].strip()
        img = params.get('img', [''])[0].strip()
        for key, val in [('quote', quote), ('source', source), ('note', note), ('img', img)]:
            if key in params:
                if val:
                    data['items'][idx][key] = val
                else:
                    data['items'][idx].pop(key, None)
        with open(os.path.join(BLOG_DIR, 'data', 'zhai.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return {'success': True, 'message': '摘抄已更新'}

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

    def send_pwa_page(self):
        """Serve the PWA wrapper page for mobile app experience"""
        html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#D4342F">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="写博客">
    <title>博客编辑器</title>
    <link rel="manifest" href="./manifest.json">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body { height: 100%; overflow: hidden; font-family: -apple-system, 'Microsoft YaHei', sans-serif; background: #f5f5f5; }
        #app { display: flex; flex-direction: column; height: 100%; }
        .top-bar {
            display: flex; align-items: center; justify-content: center; gap: 8px;
            padding: 10px 16px; background: linear-gradient(135deg, #D4342F, #E85D57);
            color: #fff; flex-shrink: 0; position: relative;
        }
        .top-bar h1 { font-size: 1rem; font-weight: 600; }
        .top-bar .install-hint {
            position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
            font-size: .72rem; opacity: .85; cursor: pointer;
            background: rgba(255,255,255,.2); padding: 4px 10px; border-radius: 100px;
            border: none; color: #fff;
        }
        iframe { flex: 1; width: 100%; border: none; background: #fff; }
        .loading {
            display: flex; align-items: center; justify-content: center; height: 100%;
            color: #8E8EA0; font-size: .95rem;
        }
    </style>
</head>
<body>
    <div id="app">
        <div class="top-bar">
            <h1>✿ 博客编辑器</h1>
            <button class="install-hint" id="installBtn" style="display:none" onclick="installApp()">安装应用</button>
        </div>
        <iframe id="adminFrame" src="./admin/" sandbox="allow-scripts allow-forms allow-same-origin allow-popups"></iframe>
        <div class="loading" id="loading">加载中...</div>
    </div>

    <script>
        const frame = document.getElementById('adminFrame');
        const loading = document.getElementById('loading');

        frame.addEventListener('load', function() {
            loading.style.display = 'none';
        });

        frame.addEventListener('error', function() {
            loading.textContent = '加载失败，请刷新重试';
        });

        // Hide loading after 5s timeout
        setTimeout(() => { loading.style.display = 'none'; }, 5000);

        // ── PWA Install Prompt ──
        let deferredPrompt = null;
        const installBtn = document.getElementById('installBtn');

        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            installBtn.style.display = 'block';
        });

        async function installApp() {
            if (!deferredPrompt) return;
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            if (outcome === 'accepted') {
                installBtn.style.display = 'none';
            }
            deferredPrompt = null;
        }

        // ── Service Worker Registration ──
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('./sw.js')
                .then(() => console.log('SW registered'))
                .catch(err => console.log('SW registration failed:', err));
        }
    </script>
</body>
</html>'''
        self.send_html(html)

    def send_admin_page(self):
        template_path = os.path.join(BLOG_DIR, 'admin', 'template.html')
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                html = f.read()
        except FileNotFoundError:
            html = '<html><body><h1>模板文件未找到: admin/template.html</h1></body></html>'
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
        print(f"  电脑访问: http://localhost:{port}/admin")

        # Try to detect local IP for mobile access
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            print(f"  手机访问: http://{local_ip}:{port}/admin （需同一 WiFi）")
        except Exception:
            print(f"  手机访问: http://<电脑IP>:{port}/admin （需同一 WiFi）")

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
