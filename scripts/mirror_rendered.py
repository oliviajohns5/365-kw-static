import json, urllib.request, ssl, re, pathlib, urllib.parse, html as htmlmod

ctx = ssl._create_unverified_context()
base = 'https://365-kw.com'
d = json.load(open('data/wp-export.json'))
urls = {base + '/'}
for p in d['posts']:
    slug = p['post_name'].strip('/')
    if slug:
        urls.add(f'{base}/{slug}/')
for c in d['categories']:
    if c['taxonomy'] == 'category' and c['slug'] != 'uncategorized':
        urls.add(f'{base}/category/{c["slug"]}/')
for n in range(2, 5):
    urls.add(f'{base}/page/{n}/')

public = pathlib.Path('public')
public.mkdir(exist_ok=True)
asset_paths = set()
page_results = []

def local_page_path(url):
    p = urllib.parse.urlparse(url).path
    if not p or p == '/':
        return public / 'index.html'
    if p.endswith('/'):
        return public / p.strip('/') / 'index.html'
    return public / p.lstrip('/')

def clean_url(u):
    u = htmlmod.unescape(u.strip())
    if not u or u.startswith(('data:', 'mailto:', 'tel:', 'javascript:', '#')):
        return u
    absu = urllib.parse.urljoin(base + '/', u)
    pu = urllib.parse.urlparse(absu)
    if pu.netloc in ('365-kw.com', 'www.365-kw.com'):
        path = urllib.parse.unquote(pu.path)
        if path.startswith(('/wp-content/', '/wp-includes/')) or re.search(r'\.(css|js|jpg|jpeg|png|webp|gif|svg|ico|woff2?|ttf|eot)$', path, re.I):
            asset_paths.add(path.lstrip('/'))
            return path
        return path or '/'
    return u

def rewrite_match(m):
    attr, quote, val = m.group(1), m.group(2), m.group(3)
    if attr.lower() == 'srcset':
        parts = []
        for part in val.split(','):
            bits = part.strip().split()
            if bits:
                bits[0] = clean_url(bits[0])
                parts.append(' '.join(bits))
        return f'{attr}={quote}{", ".join(parts)}{quote}'
    return f'{attr}={quote}{clean_url(val)}{quote}'

for url in sorted(urls):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 HermesStaticMigration/1.0'})
        r = urllib.request.urlopen(req, timeout=25, context=ctx)
        s = r.read().decode('utf-8', 'replace')
        s = re.sub(r'\b(src|href|data-src|data-lazy-src|srcset)=("|\')([^"\']+)(?:\2)', rewrite_match, s, flags=re.I)
        s = s.replace('https://365-kw.com', '').replace('http://365-kw.com', '')
        s = s.replace('https://www.365-kw.com', '').replace('http://www.365-kw.com', '')
        out = local_page_path(url)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(s, encoding='utf-8')
        page_results.append({'url': url, 'path': str(out), 'ok': True, 'bytes': len(s)})
    except Exception as e:
        page_results.append({'url': url, 'ok': False, 'error': str(e)})

pathlib.Path('data/page-results.json').write_text(json.dumps(page_results, indent=2, ensure_ascii=False))
pathlib.Path('data/asset-paths.txt').write_text('\n'.join(sorted(asset_paths)) + '\n')
print({'pages': len(page_results), 'ok': sum(1 for x in page_results if x.get('ok')), 'asset_paths': len(asset_paths)})
