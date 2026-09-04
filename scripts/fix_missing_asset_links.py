from pathlib import Path
import re

ROOT = Path('public')

# Old WordPress original-image URLs -> existing local migrated images.
REPLACEMENTS = {
    '/wp-content/uploads/2011/10/biz_leavebehind_back.jpg': '/wp-content/uploads/2020/11/biz_leavebehind_back-2605800.jpg',
    '/wp-content/uploads/2011/10/Amanda-Business-Photos-2011-No-2.jpg': '/wp-content/uploads/2020/11/Amanda-Business-Photos-2011-No-2-235x300-8522562.jpg',
    '/wp-content/uploads/2012/01/Screen-Shot-2012-01-18-at-11.40.16-AM.png': '/wp-content/uploads/2020/11/Screen-Shot-2012-01-18-at-11.40.16-AM-150x150-6631534.png',
    '/wp-content/uploads/2012/03/Screen-Shot-2012-03-25-at-9.39.19-AM.png': '/wp-content/uploads/2020/11/Waterloo-Wellington-Science-and-Engineering-Fair-1574657-640x446.jpg',
    '/wp-content/uploads/2012/03/Keith-Marshall8.png': '',
    '/wp-content/uploads/2012/04/Screen-Shot-2012-04-13-at-7.52.09-PM.png': '/wp-content/uploads/2020/11/Screen-Shot-2012-04-13-at-7.52.09-PM-150x150-3168715.png',
    '/wp-content/uploads/2012/04/Keith-Marshall5.png': '',
    '/wp-content/uploads/2012/04/Screen-Shot-2012-04-21-at-8.15.40-PM.png': '/wp-content/uploads/2020/11/Screen-Shot-2012-04-21-at-8.15.40-PM-150x150-9538368.png',
    '/wp-content/uploads/2012/05/Walper-2.jpg': '/wp-content/uploads/2020/11/Walper-2-300x224-9165504.jpg',
    '/wp-content/uploads/2012/05/Walper-3.jpg': '/wp-content/uploads/2020/11/Walper-3-300x169-6017830.jpg',
    '/wp-content/uploads/2012/05/Walper5.jpg': '/wp-content/uploads/2020/11/Walper5-300x168-9903395.jpg',
    '/wp-content/uploads/2012/06/RR-bar.jpg': '/wp-content/uploads/2020/11/RR-bar-1089669.jpg',
    '/wp-content/uploads/2012/06/RR-bar-2.jpg': '/wp-content/uploads/2020/11/RR-bar-2-3629166.jpg',
    '/wp-content/uploads/2012/06/rr-yuk-yuks.jpg': '/wp-content/uploads/2020/11/rr-yuk-yuks-283x300-4207481.jpg',
    '/wp-content/uploads/2012/06/rr-bar-3.jpg': '/wp-content/uploads/2020/11/rr-bar-3-1409488.jpg',
    '/wp-content/uploads/2012/06/Screen-Shot-2012-06-17-at-9.19.20-AM.png': '/wp-content/uploads/2020/11/THEMUSEUM-Remembers-Goudies-6116535-640x480.jpg',
    '/wp-content/uploads/2012/07/taya2.jpg': '/wp-content/uploads/2020/11/taya2-300x190-5671654.jpg',
    '/wp-content/uploads/2012/07/taya3.jpg': '/wp-content/uploads/2020/11/taya3-300x214-5510632.jpg',
    '/wp-content/uploads/2012/07/taya4.jpg': '/wp-content/uploads/2020/11/taya4-300x196-2583854.jpg',
    '/wp-content/uploads/2012/07/taya-fundraiser.jpg': '/wp-content/uploads/2020/11/taya-fundraiser-300x200-6779636.jpg',
}

# Replace a whole linked image block with nothing where the migrated file is a 1x1 tracking/empty image
# and no meaningful migrated asset exists.
def remove_empty_linked_image(html: str, old_url: str) -> str:
    pattern = re.compile(r'<a\s+[^>]*href=["\']' + re.escape(old_url) + r'["\'][^>]*>\s*<img\s+[^>]*>\s*(?:<noscript>.*?</noscript>)?\s*</a>', re.I | re.S)
    return pattern.sub('', html)

changed_files = 0
changed_refs = 0
for file in ROOT.rglob('*.html'):
    html = file.read_text(errors='ignore')
    original = html
    for old, new in REPLACEMENTS.items():
        before = html
        if new:
            html = html.replace(old, new)
        else:
            html = remove_empty_linked_image(html, old)
            html = html.replace(old, '')
        changed_refs += before.count(old)
    if html != original:
        file.write_text(html)
        changed_files += 1

print({'changed_files': changed_files, 'old_refs_replaced_or_removed': changed_refs})
