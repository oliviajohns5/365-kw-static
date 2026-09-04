import pathlib, re, html

BRAND_FOOTER = '© 2026 365-kw.com. All rights reserved.'
CLEAN_STYLE = '''
<style id="static-cleanup-css">
.meta-author,.byline,.post-edit-link,.code-block{display:none!important}
.site-footer .copyright,.footer-b .copyright{font-size:14px;color:#f1f5f9;text-align:center}
.entry-meta{gap:10px}.entry-meta svg{display:none}.site-description{font-style:normal}.widget-title{letter-spacing:.01em}.back-to-top{border-radius:999px}
</style>
'''

def clean_classes(match):
    quote, val = match.group(1), match.group(2)
    drop_prefixes = ('wp-', 'post-', 'page-', 'single-', 'category-', 'tag-', 'hentry', 'status-', 'format-', 'type-', 'attachment-')
    keep=[]
    for token in val.split():
        low=token.lower()
        if low == 'wp-custom-logo' or low.startswith(drop_prefixes):
            continue
        keep.append(token)
    return 'class=' + quote + ' '.join(keep) + quote if keep else ''

for p in pathlib.Path('public').rglob('*.html'):
    s = p.read_text(errors='ignore')
    # Make lazy-loaded WP Rocket images normal static images.
    s = re.sub(r'\sdata-lazy-srcset=', ' srcset=', s, flags=re.I)
    s = re.sub(r'\sdata-lazy-src=', ' src=', s, flags=re.I)
    s = re.sub(r'\sdata-lazy-sizes=', ' sizes=', s, flags=re.I)
    s = re.sub(r'\sdata-rocket-[a-z-]+=("[^"]*"|\'[^\']*\')', '', s, flags=re.I)
    s = s.replace('type="rocketlazyloadscript"', 'type="text/javascript"')

    # Remove WordPress/plugin discovery and generator artifacts.
    s = re.sub(r'\n?\s*<!--\s*(?:All in One SEO|WP Rocket|Custom Logo).*?-->\s*', '\n', s, flags=re.I|re.S)
    s = re.sub(r'\n?\s*<meta[^>]+name=("|\')generator\1[^>]*>\s*', '\n', s, flags=re.I)
    s = re.sub(r'\n?\s*<meta[^>]+name=("|\')author\1[^>]*>\s*', '\n', s, flags=re.I)
    s = re.sub(r'\n?\s*<link[^>]+rel=("|\')profile\1[^>]*>\s*', '\n', s, flags=re.I)
    s = re.sub(r'\n?\s*<link[^>]+rel=("|\')shortlink\1[^>]*>\s*', '\n', s, flags=re.I)
    s = re.sub(r'\n?\s*<link[^>]+(?:wp-json|xmlrpc|oembed|/feed/|/comments/feed/)[^>]*>\s*', '\n', s, flags=re.I)
    s = re.sub(r'\n?\s*<script[^>]+(?:jquery|jquery-migrate|wp-embed|wp-emoji|comment-reply|email-decode|wp-content/plugins|rocket|lazyload)[^>]*></script>\s*', '\n', s, flags=re.I)
    s = re.sub(r'\n?\s*<script[^>]+/cdn-cgi/scripts/[^>]*></script>\s*', '\n', s, flags=re.I)
    s = s.replace('http://schema.org/WPHeader', 'https://schema.org/WebPageElement').replace('http://schema.org/WPSideBar', 'https://schema.org/WebPageElement').replace('http://schema.org/WPFooter', 'https://schema.org/WebPageElement')

    # Remove visible WordPress comments/widgets/forms.
    for start_token, end_tokens in [
        ('<div id="comments"', ['<aside id="secondary"', '<footer id="colophon"', '</main>']),
        ('<aside id="secondary"', ['<footer id="colophon"', '</main>']),
    ]:
        low = s.lower()
        start = low.find(start_token.lower())
        if start >= 0:
            candidates = [low.find(t.lower(), start + 1) for t in end_tokens]
            candidates = [x for x in candidates if x >= 0]
            if candidates:
                end = min(candidates)
                s = s[:start] + s[end:]
    s = re.sub(r'<div id="comments"\b.*?(?=<aside\b|<footer id="colophon"|<footer\b|</main>)', '', s, flags=re.I|re.S)
    s = re.sub(r'<aside id="secondary"\b.*?(?=<footer id="colophon"|<footer\b|</main>)', '', s, flags=re.I|re.S)
    s = re.sub(r'<div id="comments"\b.*?</div>\s*(?:<!--[^>]*-->)?\s*', '', s, flags=re.I|re.S)
    s = re.sub(r'<form[^>]+id=("|\')commentform\1.*?</form>', '', s, flags=re.I|re.S)
    s = re.sub(r'<span class=("|\')comment-box\1.*?</span>', '', s, flags=re.I|re.S)
    s = re.sub(r'<span class=("|\')byline\1.*?</span>', '', s, flags=re.I|re.S)
    s = re.sub(r'<a[^>]+/author/admin/[^>]*>\s*admin\s*</a>', '', s, flags=re.I)
    s = re.sub(r'Leave A Comment|Cancel reply|Your email address will not be published\.|Required fields are marked \*', '', s, flags=re.I)

    # Remove/replace old theme footer credit.
    s = re.sub(r'<div class=("|\')copyright-wrap\1>.*?</div>\s*Blossom Spa.*?Powered by\s*<a[^>]+>WordPress</a>\.?', f'<div class="copyright-wrap">{BRAND_FOOTER}</div>', s, flags=re.I|re.S)
    s = re.sub(r'Blossom Spa\s*\|\s*Developed By\s*<a[^>]*>\s*Blossom Themes\s*</a>\.\s*Powered by\s*<a[^>]*>WordPress</a>\.?', '', s, flags=re.I|re.S)
    s = s.replace('365-thingstodo.com. All Rights Reserved. All the best things to do in Kitchener-Waterloo!', '365-kw.com. All rights reserved.')

    # Remove old anti-scraping/WordPress comments if present.
    s = re.sub(r'<!--\s*/?wp:.*?-->', '', s, flags=re.I|re.S)

    # Clean schema references to /author/admin/ and explicit admin author names.
    s = s.replace('https:\/\/365-kw.com\/author\/admin\/#author', 'https:\/\/365-kw.com\/#organization')
    s = s.replace('/author/admin/', '/')
    s = re.sub(r'"name"\s*:\s*"admin"', '"name":"365-kw.com"', s)

    # Clean class attributes from obvious WordPress-only tokens.
    s = re.sub(r'class=("|\')([^"\']*)(?:wp-|post-|hentry|single-|page-id|category-)[^"\']*\1', clean_classes, s, flags=re.I)

    s = re.sub(r'<style id="static-cleanup-css">.*?</style>\s*', '', s, flags=re.I|re.S)
    s = re.sub(r'\bWordpress\b|\bWordPress\b', 'website', s)
    if '</head>' in s:
        s = s.replace('</head>', CLEAN_STYLE + '\n</head>', 1)
    p.write_text(s)
print('removed WordPress/theme/plugin visible artifacts and static-normalized lazy images')
