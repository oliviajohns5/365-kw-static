from pathlib import Path

ROOT = Path('public')
REPLACEMENTS = {
    '/art.html': '/category/art/',
    '/contest.html': '/category/contest/',
    '/date-night.html': '/category/date-night/',
    '/exercise.html': '/category/exercise/',
    '/%d0%b1%d0%b5%d0%b7-%d1%80%d1%83%d0%b1%d1%80%d0%b8%d0%ba%d0%b8.html': '/category/family-fun/',
    '/%25d0%25b1%25d0%25b5%25d0%25b7-%25d1%2580%25d1%2583%25d0%25b1%25d1%2580%25d0%25b8%25d0%25ba%25d0%25b8.html': '/category/family-fun/',
}
changed_files = 0
changed_refs = 0
for file in ROOT.rglob('*.html'):
    s = file.read_text(errors='ignore')
    old_s = s
    for old, new in REPLACEMENTS.items():
        c = s.count(old)
        if c:
            changed_refs += c
            s = s.replace(old, new)
    if s != old_s:
        file.write_text(s)
        changed_files += 1
print({'changed_files': changed_files, 'changed_refs': changed_refs})
