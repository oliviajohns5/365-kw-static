import pathlib, re, json

id_to_slug = {}
try:
    data = json.load(open('data/wp-export.json'))
    for post in data.get('posts', []):
        if post.get('post_name'):
            id_to_slug[str(post.get('ID'))] = '/' + post['post_name'].strip('/') + '/'
except Exception:
    pass

for p in pathlib.Path('public').rglob('*.html'):
    s = p.read_text(errors='ignore')
    s = re.sub(r'\n?\s*<link[^>]+(?:/feed/|/comments/feed/|wp-json|xmlrpc\.php|oembed)[^>]*>\s*', '\n', s, flags=re.I)
    s = re.sub(r'\n?\s*<script[^>]+/wp-includes/js/wp-embed[^>]*></script>\s*', '\n', s, flags=re.I)
    s = re.sub(r'href=("|\')([^"\']*)#(?:respond|comments)("|\')', lambda m: f'href={m.group(1)}{m.group(2) or "/"}{m.group(3)}', s, flags=re.I)
    s = re.sub(r'href=("|\')/cdn-cgi/l/email-protection("|\')', r'href=\1/contact-us/\2', s, flags=re.I)
    s = re.sub(r'href=("|\')/signup("|\')', r'href=\1/contact-us/\2', s, flags=re.I)
    s = s.replace('/%d0%b1%d0%b5%d0%b7-%d1%80%d1%83%d0%b1%d1%80%d0%b8%d0%ba%d0%b8.html/page/2/', '/category/family-fun/page/2/')
    def repl_pid(m):
        return 'href=' + m.group(1) + id_to_slug.get(m.group(2), '/') + m.group(3)
    s = re.sub(r'href=("|\')/\?p=(\d+)("|\')', repl_pid, s)
    p.write_text(s)
print('cleaned static-only WordPress artifacts and legacy dynamic links')
