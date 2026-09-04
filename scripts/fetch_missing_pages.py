import pathlib, re, urllib.parse, json, urllib.request, ssl
ctx=ssl._create_unverified_context(); base='https://365-kw.com'; public=pathlib.Path('public')
def local_page_path_from_path(v):
    if v == '/': return public/'index.html'
    clean=v.split('#',1)[0].split('?',1)[0]
    if not clean.endswith('/'): clean+='/'
    return public/clean.strip('/')/'index.html'
def fetch_url(url):
    r=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 HermesStaticMigration/1.0'}),timeout=20,context=ctx)
    if 'text/html' not in r.headers.get('content-type',''): return False
    s=r.read().decode('utf-8','replace')
    s=s.replace('https://365-kw.com','').replace('http://365-kw.com','').replace('https://www.365-kw.com','').replace('http://www.365-kw.com','')
    out=local_page_path_from_path(urllib.parse.urlparse(url).path)
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(s,encoding='utf-8')
    return True
for round_no in range(4):
    missing=[]
    for p in public.rglob('*.html'):
        s=p.read_text(errors='ignore')
        for val in re.findall(r'\b(?:href|src)=["\']([^"\']+)["\']',s,re.I):
            if not val.startswith('/') or val.startswith(('/wp-content/','/wp-includes/','/cdn-cgi/')): continue
            if any(x in val for x in ['/feed/','/comments/feed/','/wp-json/','xmlrpc.php']): continue
            if re.search(r'\.[a-z0-9]{2,5}(?:[?#]|$)', val, re.I): continue
            local=local_page_path_from_path(val)
            if not local.exists(): missing.append(val.split('#',1)[0].split('?',1)[0])
    missing=sorted(set(missing))[:80]
    print({'round':round_no,'missing_to_fetch':len(missing),'sample':missing[:10]})
    if not missing: break
    ok=0
    for v in missing:
        try:
            if fetch_url(base+v): ok+=1
        except Exception:
            pass
    print({'round':round_no,'fetched':ok})
