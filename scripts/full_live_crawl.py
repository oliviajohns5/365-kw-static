import urllib.request, urllib.parse, urllib.error, re, json, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict, Counter, deque

BASE = 'https://365-kw.com'
HOSTS = {'365-kw.com', 'www.365-kw.com'}
UA = 'Hermes hard QA crawler/1.0'
REDIRECTS = {301, 302, 303, 307, 308}
SKIP_SCHEMES = ('mailto:', 'tel:', 'javascript:', 'data:', '#')
ASSET_PREFIXES = ('/images/', '/css/', '/js/', '/fonts/', '/wp-content/', '/wp-includes/')
TEXT_ASSET_EXTS = {'.css', '.js'}

ATTR_RE = re.compile(r"\b(?:href|src|data-src|data-lazy-src|poster)=['\"]([^'\"]+)['\"]", re.I)
SRCSET_RE = re.compile(r"\bsrcset=['\"]([^'\"]+)['\"]", re.I)
CSS_URL_RE = re.compile(r"url\(\s*['\"]?([^)'\"]+)['\"]?\s*\)", re.I)
SCRIPT_RE = re.compile(r'<script\b[^>]*>.*?</script>', re.I | re.S)
STYLE_RE = re.compile(r'<style\b[^>]*>(.*?)</style>', re.I | re.S)


def quote_url(url):
    p = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(urllib.parse.unquote(p.path), safe='/%:@')
    query = urllib.parse.quote_plus(p.query, safe='=&:%/')
    return urllib.parse.urlunsplit((p.scheme, p.netloc, path, query, ''))


def normalize_url(raw, base_url):
    raw = (raw or '').strip().strip('"\'')
    if not raw or raw.lower().startswith(SKIP_SCHEMES):
        return None
    url = urllib.parse.urljoin(base_url, raw)
    p = urllib.parse.urlsplit(url)
    if p.scheme not in ('http', 'https'):
        return None
    # Strip fragments for HTTP status checks.
    return urllib.parse.urlunsplit((p.scheme, p.netloc.lower(), p.path or '/', p.query, ''))


def fetch_follow(url, timeout=25):
    req = urllib.request.Request(quote_url(url), headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.geturl(), r.headers, r.read()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

NOREDIR = urllib.request.build_opener(NoRedirect)


def fetch_chain(url, timeout=25, max_hops=10):
    cur = url
    chain = []
    for _ in range(max_hops):
        try:
            req = urllib.request.Request(quote_url(cur), headers={'User-Agent': UA})
            with NOREDIR.open(req, timeout=timeout) as r:
                chain.append({'url': cur, 'status': r.status, 'location': None})
                return chain, None
        except urllib.error.HTTPError as e:
            loc = e.headers.get('Location')
            chain.append({'url': cur, 'status': e.code, 'location': loc})
            if e.code in REDIRECTS and loc:
                cur = urllib.parse.urljoin(cur, loc)
                continue
            return chain, None
        except Exception as e:
            return chain, repr(e)
    return chain, 'too_many_redirects'


def extract_urls_from_html(html, page_url):
    urls = []
    no_scripts = SCRIPT_RE.sub('', html)
    for m in ATTR_RE.finditer(no_scripts):
        u = normalize_url(m.group(1), page_url)
        if u:
            urls.append(u)
    for m in SRCSET_RE.finditer(no_scripts):
        for part in m.group(1).split(','):
            token = part.strip().split()[0] if part.strip() else ''
            u = normalize_url(token, page_url)
            if u:
                urls.append(u)
    for m in CSS_URL_RE.finditer(no_scripts):
        u = normalize_url(m.group(1), page_url)
        if u:
            urls.append(u)
    return urls


def extract_urls_from_css(css_text, css_url):
    out = []
    for m in CSS_URL_RE.finditer(css_text):
        u = normalize_url(m.group(1), css_url)
        if u:
            out.append(u)
    return out


def is_internal(url):
    return urllib.parse.urlsplit(url).netloc.lower() in HOSTS


def is_asset_path(path):
    return path.startswith(ASSET_PREFIXES) or bool(re.search(r'\.(webp|png|jpe?g|gif|svg|ico|css|js|woff2?|ttf|eot|otf|mp4|webm|pdf)$', path, re.I))

# Baseline endpoints.
endpoint_checks = ['https://365-kw.com/', 'https://www.365-kw.com/', 'http://365-kw.com/', 'http://www.365-kw.com/', BASE + '/robots.txt', BASE + '/sitemap.xml', BASE + '/llms.txt']
endpoints = {}
for u in endpoint_checks:
    ch, err = fetch_chain(u)
    endpoints[u] = {'chain': ch, 'err': err}

# Sitemap.
sitemap_status, sitemap_final, sitemap_headers, sitemap_body = fetch_follow(BASE + '/sitemap.xml')
sitemap_xml = sitemap_body.decode('utf-8', 'ignore')
sitemap_urls = re.findall(r'<loc>(https?://[^<]+)</loc>', sitemap_xml)
sitemap_internal = [u for u in sitemap_urls if urllib.parse.urlsplit(u).netloc.lower() == '365-kw.com']

# Crawl all sitemap pages and discovered internal pages until stable.
pages_to_visit = deque(sitemap_internal)
seen_pages = set()
page_results = {}
occurrences = defaultdict(list)
asset_urls = set()
external_urls = set()
old_ref_hits = []

while pages_to_visit:
    batch = []
    while pages_to_visit and len(batch) < 40:
        u = pages_to_visit.popleft()
        if u in seen_pages:
            continue
        seen_pages.add(u)
        batch.append(u)
    if not batch:
        continue

    def page_job(url):
        try:
            st, final, headers, body = fetch_follow(url)
            html = body.decode('utf-8', 'ignore')
            urls = extract_urls_from_html(html, url)
            return url, {'status': st, 'final': final, 'bytes': len(body), 'title': (re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.S).group(1).strip() if re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.S) else ''), 'urls': urls, 'old_refs': ('/wp-content/' in html or '/wp-includes/' in html)}, None
        except Exception as e:
            return url, None, repr(e)

    with ThreadPoolExecutor(max_workers=20) as ex:
        for fut in as_completed([ex.submit(page_job, u) for u in batch]):
            url, result, err = fut.result()
            if err:
                page_results[url] = {'error': err}
                continue
            page_results[url] = {k: v for k, v in result.items() if k != 'urls'}
            if result['old_refs']:
                old_ref_hits.append(url)
            for target in result['urls']:
                p = urllib.parse.urlsplit(target)
                if is_internal(target):
                    if p.path.startswith(('/wp-content/', '/wp-includes/')):
                        old_ref_hits.append(url + ' -> ' + target)
                    if is_asset_path(p.path):
                        asset_urls.add(target)
                    else:
                        occurrences[target].append(url)
                        if target not in seen_pages:
                            pages_to_visit.append(target)
                else:
                    external_urls.add(target)

# Include CSS nested assets.
css_urls = {u for u in asset_urls if urllib.parse.urlsplit(u).path.lower().endswith('.css')}
for css_url in list(css_urls):
    try:
        st, final, headers, body = fetch_follow(css_url)
        for u in extract_urls_from_css(body.decode('utf-8', 'ignore'), css_url):
            if is_internal(u):
                asset_urls.add(u)
            else:
                external_urls.add(u)
    except Exception:
        pass

# Status/redirect checks for unique internal pages and assets.
def check_url_set(urls, workers=32):
    bad = []
    redirects = []
    statuses = Counter()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for fut in as_completed([ex.submit(fetch_chain, u) for u in sorted(urls)]):
            chain, err = fut.result()
            # need original; first chain url or unknown unavailable, wrap differently next
    return bad, redirects, statuses


def one_check(u):
    ch, err = fetch_chain(u)
    final_status = ch[-1]['status'] if ch else None
    return u, ch, err, final_status


def classify(urls, workers=32):
    bad, redirects = [], []
    statuses = Counter()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for fut in as_completed([ex.submit(one_check, u) for u in sorted(urls)]):
            u, ch, err, final = fut.result()
            statuses[str(final if final is not None else 'ERR')] += 1
            if err or final != 200:
                bad.append({'url': u, 'chain': ch, 'err': err, 'occurrences': occurrences.get(u, [])[:5]})
            if any(step['status'] in REDIRECTS for step in ch):
                redirects.append({'url': u, 'chain': ch, 'occurrences': occurrences.get(u, [])[:5]})
    return bad, redirects, statuses

page_bad, page_redirects, page_statuses = classify(seen_pages, 32)
asset_bad, asset_redirects, asset_statuses = classify(asset_urls, 40)

report = {
    'base': BASE,
    'generated_at_epoch': int(time.time()),
    'endpoints': endpoints,
    'sitemap_urls': len(sitemap_urls),
    'sitemap_internal_urls': len(sitemap_internal),
    'sitemap_duplicates': len(sitemap_urls) - len(set(sitemap_urls)),
    'pages_discovered_and_checked': len(seen_pages),
    'sitemap_pages_missing_from_discovery': sorted(set(sitemap_internal) - set(seen_pages))[:20],
    'page_statuses': dict(page_statuses),
    'page_bad_count': len(page_bad),
    'page_redirect_count': len(page_redirects),
    'asset_urls_checked': len(asset_urls),
    'asset_statuses': dict(asset_statuses),
    'asset_bad_count': len(asset_bad),
    'asset_redirect_count': len(asset_redirects),
    'old_wp_reference_hits': len(old_ref_hits),
    'old_wp_reference_samples': old_ref_hits[:20],
    'external_urls_discovered_not_status_checked': len(external_urls),
    'bad_page_samples': page_bad[:20],
    'bad_asset_samples': asset_bad[:20],
    'page_redirect_samples': page_redirects[:20],
    'asset_redirect_samples': asset_redirects[:20],
}
print(json.dumps(report, ensure_ascii=False, indent=2))
