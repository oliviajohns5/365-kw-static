from pathlib import Path
from PIL import Image
import re, shutil, urllib.parse, hashlib
from collections import defaultdict

ROOT = Path('public')
TEXT_EXTS = {'.html', '.css', '.js'}
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
SKIP_DIRS = {'images', 'css', 'js', 'fonts'}

ATTR_URL_RE = re.compile(r"\b(?:href|src|data-src|data-lazy-src)=['\"]([^'\"]+)['\"]|url\(([^)]+)\)", re.I)
URL_RE = re.compile(r"(?:https?:)?//365-kw\.com(?P<abs>/(?:wp-content|wp-includes)/[^\s'\")<>]+)|(?P<rel>/(?:wp-content|wp-includes)/[^\s'\")<>]+)", re.I)
ARCHIVE_PREFIXES = ('/20', '/category/', '/author/', '/page/')
NON_ARTICLE = {'', 'privacy-policy', 'terms-and-conditions', '365-business'}


def clean_url_token(token: str) -> str:
    token = token.strip().strip('"\'')
    # Leave srcset descriptors out; caller uses URL_RE on whole file too.
    return token


def path_from_url(u: str):
    u = clean_url_token(u)
    if u.startswith('//'):
        u = 'https:' + u
    if u.startswith('http'):
        p = urllib.parse.urlsplit(u)
        if p.netloc and p.netloc.lower() not in ('365-kw.com', 'www.365-kw.com'):
            return None
        return urllib.parse.unquote(p.path)
    p = urllib.parse.urlsplit(u)
    return urllib.parse.unquote(p.path)


def slugify(s: str) -> str:
    s = urllib.parse.unquote(s)
    s = s.replace('·', '-')
    s = re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()
    s = re.sub(r'-+', '-', s)
    return s[:80].strip('-') or 'asset'


def page_slug(file: Path) -> str | None:
    rel = '/' + file.relative_to(ROOT).as_posix()
    if rel.endswith('/index.html'):
        rel = rel[:-len('/index.html')]
    elif rel.endswith('.html'):
        rel = rel[:-5]
    rel = rel.strip('/')
    if not rel or rel in NON_ARTICLE or rel.startswith(ARCHIVE_PREFIXES):
        return None
    return slugify(rel.split('/')[-1])


def logical_key(path: str) -> str:
    stem = Path(path).stem
    stem = re.sub(r'-\d+x\d+$', '', stem)
    stem = re.sub(r'-\d{6,8}$', '', stem)
    stem = re.sub(r'-\d+x\d+$', '', stem)
    return slugify(stem)


def size_score(file: Path) -> int:
    try:
        with Image.open(file) as im:
            return im.width * im.height
    except Exception:
        try:
            return file.stat().st_size
        except Exception:
            return 0

# Collect references and occurrence pages.
refs = defaultdict(list)  # url path -> text file occurrences
for f in ROOT.rglob('*'):
    if not f.is_file() or f.suffix.lower() not in TEXT_EXTS:
        continue
    if any(part in SKIP_DIRS for part in f.relative_to(ROOT).parts[:-1]):
        # still scan new dirs in future? currently not needed
        pass
    text = f.read_text(errors='ignore')
    for m in URL_RE.finditer(text):
        raw_path = m.group('abs') or m.group('rel')
        path = path_from_url(raw_path)
        if path:
            refs[path].append(f)

existing = {}
missing = []
for p in refs:
    fs_path = ROOT / p.lstrip('/')
    if fs_path.exists() and fs_path.is_file():
        existing[p] = fs_path
    else:
        # ignore old absolute paths already fixed by verify? keep visible
        missing.append(p)

# Build mapping.
mapping = {}
image_groups = defaultdict(list)
for p, fs_path in existing.items():
    if p.startswith('/wp-content/uploads/') and fs_path.suffix.lower() in IMAGE_EXTS:
        # choose best article slug from occurrences
        slugs = [page_slug(x) for x in refs[p]]
        slugs = [s for s in slugs if s]
        slug = slugs[0] if slugs else logical_key(p)
        image_groups[(slug, logical_key(p))].append((p, fs_path))

# Assign numbers per article slug.
article_counts = defaultdict(int)
for (slug, key), members in sorted(image_groups.items()):
    article_counts[slug] += 1
    dest = ROOT / 'images' / f'{slug}-{article_counts[slug]}.webp'
    # convert/copy the largest variant in each logical group.
    best_p, best_file = max(members, key=lambda x: size_score(x[1]))
    dest.parent.mkdir(exist_ok=True)
    try:
        if not dest.exists():
            with Image.open(best_file) as im:
                im = im.convert('RGB') if im.mode not in ('RGB',) else im
                im.save(dest, 'WEBP', quality=82, method=4)
    except Exception:
        # fallback: preserve ext if conversion fails
        dest = dest.with_suffix(best_file.suffix.lower())
        if not dest.exists():
            shutil.copy2(best_file, dest)
    for p, _ in members:
        mapping[p] = '/' + dest.relative_to(ROOT).as_posix()

# CSS/JS/fonts/theme/plugin images.
for p, fs_path in sorted(existing.items()):
    if p in mapping:
        continue
    parts = Path(p).parts
    ext = fs_path.suffix.lower()
    if ext == '.css':
        name = slugify(fs_path.stem) + '.css'
        dest = ROOT / 'css' / name
    elif ext == '.js':
        name = fs_path.name.split('?')[0]
        dest = ROOT / 'js' / name
    elif ext in IMAGE_EXTS:
        name = slugify(fs_path.stem) + ('.webp' if ext != '.gif' else '.gif')
        dest = ROOT / 'images' / name
    elif ext in {'.woff', '.woff2', '.ttf', '.eot', '.svg', '.otf'}:
        name = fs_path.name
        dest = ROOT / 'fonts' / name
    else:
        # Put miscellaneous referenced assets in /assets would be clearer, but user asked css/js/images.
        name = fs_path.name
        dest = ROOT / 'js' / name if '/js/' in p else ROOT / 'css' / name
    dest.parent.mkdir(exist_ok=True)
    if ext in IMAGE_EXTS and ext not in {'.webp', '.gif'}:
        try:
            if not dest.with_suffix('.webp').exists():
                with Image.open(fs_path) as im:
                    im = im.convert('RGB') if im.mode not in ('RGB',) else im
                    dest = dest.with_suffix('.webp')
                    im.save(dest, 'WEBP', quality=82, method=4)
            else:
                dest = dest.with_suffix('.webp')
        except Exception:
            if not dest.exists():
                shutil.copy2(fs_path, dest)
    else:
        shutil.copy2(fs_path, dest)
    mapping[p] = '/' + dest.relative_to(ROOT).as_posix()

# Rewrite references in text files, preserving query strings by dropping cachebuster/ver.
for f in ROOT.rglob('*'):
    if not f.is_file() or f.suffix.lower() not in TEXT_EXTS:
        continue
    text = f.read_text(errors='ignore')
    old = text
    # Replace exact URL/path matches including URL-encoded variants.
    def repl(m):
        path = path_from_url(m.group(0))
        return mapping.get(path, m.group(0))
    text = URL_RE.sub(repl, text)
    if text != old:
        f.write_text(text)

# Rewrite copied CSS files too because they may contain relative wp paths or old absolute paths.
for f in list((ROOT/'css').glob('*.css')):
    text = f.read_text(errors='ignore')
    old = text
    text = URL_RE.sub(lambda m: mapping.get(path_from_url(m.group(0)), m.group(0)), text)
    if text != old:
        f.write_text(text)

# Add image sizing CSS that avoids stretching small article images to full desktop width.
css_marker = '/* static-image-size-normalization */'
css_block = f'''\n{css_marker}\n@media (min-width: 900px) {{\n  body.single .entry-content img,\n  body.page .entry-content img {{\n    width: auto !important;\n    max-width: min(100%, 760px) !important;\n    height: auto !important;\n    object-fit: contain !important;\n    display: block !important;\n    margin-left: auto !important;\n    margin-right: auto !important;\n  }}\n  body.single .entry-content figure,\n  body.page .entry-content figure {{\n    max-width: 760px !important;\n    margin-left: auto !important;\n    margin-right: auto !important;\n  }}\n  body.single .entry-content .wp-block-image.alignwide img,\n  body.single .entry-content .wp-block-image.alignfull img {{\n    max-width: min(100%, 960px) !important;\n  }}\n}}\n'''
for f in ROOT.rglob('*.html'):
    text = f.read_text(errors='ignore')
    if css_marker not in text:
        text = text.replace('</head>', '<style id="static-image-size-normalization">' + css_block + '</style>\n</head>')
        f.write_text(text)

# Remove old referenced asset directories only after rewrite? Keep files for now for rollback/direct old URL compatibility.
# We leave old files on disk but no site HTML should reference them.
print({
    'referenced_paths': len(refs),
    'existing_referenced_paths': len(existing),
    'missing_referenced_paths': len(set(missing)),
    'image_groups': len(image_groups),
    'mappings': len(mapping),
    'new_images': len(list((ROOT/'images').glob('*'))) if (ROOT/'images').exists() else 0,
    'new_css': len(list((ROOT/'css').glob('*'))) if (ROOT/'css').exists() else 0,
    'new_js': len(list((ROOT/'js').glob('*'))) if (ROOT/'js').exists() else 0,
    'new_fonts': len(list((ROOT/'fonts').glob('*'))) if (ROOT/'fonts').exists() else 0,
})
