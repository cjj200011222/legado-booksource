import asyncio, json, urllib.request, urllib.parse, re

BASE = "http://192.168.5.10:1122"
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

def save_tmp(url_tag, src):
    tmp = src.copy()
    tmp['bookSourceName'] = f'ZZ测试-{url_tag}'
    tmp['bookSourceUrl'] = f'https://temp-t27-{url_tag}.local'
    tmp['enabled'] = True
    req = urllib.request.Request(BASE + "/saveBookSource", data=json.dumps(tmp).encode(), headers={'Content-Type': 'application/json'})
    return opener.open(req, timeout=30).read().decode()

def get_remote_src(url):
    enc = urllib.parse.quote(url, safe='')
    d = json.loads(opener.open(BASE + f"/getBookSource?url={enc}", timeout=15).read().decode())
    return d.get('data')

async def ws_debug(tag, key="诡秘之主", timeout=60):
    import websockets
    uri = "ws://192.168.5.10:1123/bookSourceDebug"
    msg = json.dumps({"key": key, "tag": tag})
    try:
        async with websockets.connect(uri, open_timeout=8) as ws:
            await ws.send(msg)
            st = {'search_done': False, 'booklist_n': 0, 'toc_done': False, 'toc_n': 0, 'content_done': False, 'err': '', 'page_got': False}
            while True:
                try:
                    r = await asyncio.wait_for(ws.recv(), timeout=timeout)
                except asyncio.TimeoutError: break
                except Exception: break
                txt = r if isinstance(r, str) else r.decode('utf-8','replace')
                if '≡获取成功' in txt: st['page_got'] = True
                if '搜索页解析完成' in txt: st['search_done'] = True
                if '列表大小:' in txt:
                    try: st['booklist_n'] = int(txt.split('列表大小:')[1].strip())
                    except: pass
                if '目录列表解析完成' in txt: st['toc_done'] = True
                if '目录总数' in txt:
                    m = re.search(r'目录总数:(\d+)', txt)
                    if m: st['toc_n'] = int(m.group(1))
                if '正文页解析完成' in txt: st['content_done'] = True
                if 'Exception' in txt and not st['err']: st['err'] = txt[txt.find('Exception'):][:90]
            return st
    except Exception as e:
        return {'search_done': False, 'booklist_n': 0, 'toc_done': False, 'toc_n': 0, 'content_done': False, 'err': f'连接:{str(e)[:40]}', 'page_got': False}

def first_explore_url(s):
    e = s.get('exploreUrl','')
    if not e: return None
    if e.strip().startswith('['):
        ee = re.sub(r',\s*]', ']', e)
        try:
            arr = json.loads(ee)
            for x in arr:
                u = x.get('url','')
                if u:
                    u = u.replace('{{page}}','1').replace('{{key}}','诡秘之主')
                    # 相对路径补全
                    if u.startswith('//'): u = 'https:' + u
                    elif u.startswith('/'): 
                        base = s.get('bookSourceUrl','https://www.qidian.com')
                        root = re.match(r'(https?://[^/]+)', base)
                        u = root.group(1) + u if root else 'https://www.qidian.com' + u
                    return u
            return None
        except: return None
    else:
        m = re.search(r'::([^:\n]+)', e)
        if m:
            u = m.group(1).strip().replace('{{page}}','1')
            if u.startswith('@js'): return None
            if u.startswith('//'): u = 'https:' + u
            elif u.startswith('/') and not u.startswith('https'):
                u = 'https://www.qidian.com' + u
            return u
    return None

async def main():
    j = json.load(open('9b55c33bd0291fd9dfd8e63ab908f9b7.json', encoding='utf-8'))
    qd = [s for s in j if 'qidian' in s.get('bookSourceUrl','').lower() and 'qidiantu' not in s.get('bookSourceUrl','')]
    
    results = []
    for i, s in enumerate(qd):
        name = s['bookSourceName'][:24]
        url = s['bookSourceUrl']
        # 1. 搜索/目录/正文 (真机已有该源? 先写入真机再调试)
        remote = get_remote_src(url)
        if not remote:
            # 不在真机上 → 写入
            r = save_tmp(f"s{i}", s)
            remote_tag = f"https://temp-t27-s{i}.local"
        else:
            remote_tag = url
        st = await ws_debug(remote_tag)
        # 2. 发现 (临时源: searchUrl 指向发现第一个URL, 用源自己的规则)
        exp_url = first_explore_url(s)
        exp_st = None
        if exp_url:
            tmp = s.copy()
            tmp['bookSourceUrl'] = f'https://temp-t27-e{i}.local'
            tmp['bookSourceName'] = f'ZZ测试-e{i}'
            tmp['searchUrl'] = exp_url
            save = save_tmp(f"e{i}", tmp)
            exp_st = await ws_debug(f"https://temp-t27-e{i}.local", timeout=45)
        
        results.append({'name': s['bookSourceName'], 'url': url, 'search': st, 'explore': exp_st, 'exp_url': exp_url})
        s_ok = '✓' if st['search_done'] else '✗'
        t_ok = '✓' if st['toc_done'] else '✗'
        c_ok = '✓' if st['content_done'] else '✗'
        e_ok = ('✓'+str(exp_st['booklist_n']) if exp_st and exp_st['booklist_n']>0 else ('△'+str(exp_st['booklist_n']) if exp_st else '—'))
        print(f"{i+1:2}. {name:26} 搜{s_ok}({st['booklist_n']}) 目{t_ok} 正{c_ok} 发{e_ok}")
        # 清理临时源
        if remote_tag.startswith('https://temp'):
            body = [{"bookSourceUrl": remote_tag}]
        else: body = []
        if exp_url:
            body.append({"bookSourceUrl": f"https://temp-t27-e{i}.local"})
        if body:
            req = urllib.request.Request(BASE + "/deleteBookSources", data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
            try: opener.open(req, timeout=20).read()
            except: pass

    with open('test27_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print('\n结果已存 test27_results.json')

asyncio.run(main())
