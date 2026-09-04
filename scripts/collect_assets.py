import pathlib, re, html as htmlmod, urllib.parse
asset_paths=set()
# Parser for all quoted URL values
for p in pathlib.Path('public').rglob('*.html'):
    s=p.read_text(errors='ignore')
    for val in re.findall(r'\b(?:src|href|data-src|data-lazy-src|srcset)=["\']([^"\']+)["\']', s, re.I):
        for part in val.split(','):
            u=htmlmod.unescape(part.strip().split()[0]) if part.strip() else ''
            if u.startswith('/') and u.startswith(('/wp-content/','/wp-includes/','/cdn-cgi/')):
                asset_paths.add(urllib.parse.unquote(u.lstrip('/').split('?')[0]))
pathlib.Path('data/asset-paths-all.txt').write_text('\n'.join(sorted(asset_paths))+'\n')
print({'asset_paths':len(asset_paths)})
