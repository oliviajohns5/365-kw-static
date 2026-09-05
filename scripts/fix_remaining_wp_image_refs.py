from pathlib import Path
from PIL import Image
import re, urllib.parse, shutil

ROOT=Path('public')
IMAGE_EXTS={'.jpg','.jpeg','.png','.webp'}
URL_RE=re.compile(r"/(wp-content/uploads/[^\s'\")<>]+)")
ARCHIVE_PREFIXES=('/20','/category/','/author/','/page/')

def slugify(s):
    s=urllib.parse.unquote(s).replace('·','-')
    s=re.sub(r'[^a-zA-Z0-9]+','-',s).strip('-').lower()
    s=re.sub(r'-+','-',s)
    return s[:80].strip('-') or 'image'

def page_slug(f):
    rel='/' + f.relative_to(ROOT).as_posix()
    if rel.endswith('/index.html'): rel=rel[:-len('/index.html')]
    rel=rel.strip('/')
    if not rel or rel.startswith(ARCHIVE_PREFIXES):
        return slugify(rel.replace('/','-') or 'archive')
    return slugify(rel.split('/')[-1])

def base_stem(path):
    stem=Path(path).stem
    stem=re.sub(r'-\d+x\d+$','',stem)
    stem=re.sub(r'-\d{6,8}$','',stem)
    stem=re.sub(r'-\d+x\d+$','',stem)
    return stem

def best_alt(old_path):
    p=ROOT/old_path.lstrip('/')
    if p.exists(): return p
    dirp=p.parent
    stem=base_stem(old_path)
    candidates=[]
    if dirp.exists():
        for x in dirp.iterdir():
            if x.is_file() and x.suffix.lower() in IMAGE_EXTS and base_stem(str(x))==slugify(stem):
                candidates.append(x)
        if not candidates:
            needle=slugify(stem)[:60]
            for x in dirp.iterdir():
                if x.is_file() and x.suffix.lower() in IMAGE_EXTS and slugify(x.stem).startswith(needle):
                    candidates.append(x)
    def score(x):
        try:
            with Image.open(x) as im: return im.width*im.height
        except Exception: return x.stat().st_size
    return max(candidates,key=score) if candidates else None

changed=0; converted=0; unresolved=[]
for f in ROOT.rglob('*.html'):
    s=f.read_text(errors='ignore')
    old=s
    def repl(m):
        nonlocal_path='/' + m.group(1)
        alt=best_alt(nonlocal_path)
        if not alt:
            unresolved.append((str(f), nonlocal_path)); return nonlocal_path
        slug=page_slug(f)
        dest=ROOT/'images'/f'{slug}-hero.webp'
        if not dest.exists():
            try:
                with Image.open(alt) as im:
                    im=im.convert('RGB') if im.mode!='RGB' else im
                    im.save(dest,'WEBP',quality=84,method=4)
            except Exception:
                dest=dest.with_suffix(alt.suffix.lower())
                shutil.copy2(alt,dest)
        return '/' + dest.relative_to(ROOT).as_posix()
    s=URL_RE.sub(repl,s)
    if s!=old:
        f.write_text(s); changed+=1
print({'changed_files':changed,'unresolved':len(unresolved),'unresolved_sample':unresolved[:5]})
