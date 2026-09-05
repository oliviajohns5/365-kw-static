from pathlib import Path
import re, urllib.parse, json

ROOT = Path('public')
TEXT_EXTS = {'.html', '.css', '.js'}
ASSET_PREFIXES = ('/images/', '/css/', '/js/', '/fonts/')
OLD_PREFIXES = ('/wp-content/', '/wp-includes/')
URL_ATTR_RE = re.compile(r"\b(?:href|src|data-src|data-lazy-src)=['\"]([^'\"]+)['\"]|url\(([^)]+)\)", re.I)
SRCSET_RE = re.compile(r"\bsrcset=['\"]([^'\"]+)['\"]", re.I)

old_hits = []
asset_refs = []
missing = []

for f in ROOT.rglob('*'):
    if not f.is_file() or f.suffix.lower() not in TEXT_EXTS:
        continue
    text = f.read_text(errors='ignore')
    for pref in OLD_PREFIXES:
        if pref in text:
            for m in re.finditer(re.escape(pref), text):
                old_hits.append({'file': str(f), 'prefix': pref, 'offset': m.start()})
    raw_urls = []
    for m in URL_ATTR_RE.finditer(text):
        raw_urls.append((m.group(1) or m.group(2) or '').strip().strip('"\''))
    for m in SRCSET_RE.finditer(text):
        for part in m.group(1).split(','):
            raw_urls.append(part.strip().split()[0] if part.strip() else '')
    for raw in raw_urls:
        if not raw or raw.startswith(('data:', 'mailto:', 'tel:', 'javascript:', '#')):
            continue
        u = urllib.parse.urljoin('/' + f.relative_to(ROOT).as_posix(), raw)
        p = urllib.parse.urlsplit(u)
        if p.netloc and p.netloc.lower() not in ('365-kw.com', 'www.365-kw.com'):
            continue
        path = urllib.parse.unquote(p.path)
        if path.startswith(ASSET_PREFIXES):
            asset_refs.append({'file': str(f), 'raw': raw, 'path': path})
            if not (ROOT / path.lstrip('/')).is_file():
                missing.append({'file': str(f), 'raw': raw, 'path': path})

counts = {}
for d in ['images', 'css', 'js', 'fonts']:
    p = ROOT / d
    counts[d] = len([x for x in p.iterdir() if x.is_file()]) if p.exists() else 0

print(json.dumps({
    'new_file_counts': counts,
    'old_wp_reference_hits': len(old_hits),
    'old_wp_reference_samples': old_hits[:10],
    'clean_asset_references': len(asset_refs),
    'unique_clean_asset_references': len({x['path'] for x in asset_refs}),
    'missing_clean_asset_references': len(missing),
    'missing_clean_asset_samples': missing[:20],
}, ensure_ascii=False, indent=2))
