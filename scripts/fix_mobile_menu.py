import pathlib, re

SCRIPT = '''
<script id="static-mobile-menu-js">
document.addEventListener('DOMContentLoaded', function () {
  var body = document.body;
  function closeMenu() {
    body.classList.remove('showing-main-menu-modal');
    document.querySelectorAll('[data-toggle-target=".main-menu-modal"]').forEach(function (btn) { btn.setAttribute('aria-expanded', 'false'); });
  }
  function openMenu() {
    body.classList.add('showing-main-menu-modal');
    document.querySelectorAll('[data-toggle-target=".main-menu-modal"]').forEach(function (btn) { btn.setAttribute('aria-expanded', 'true'); });
  }
  document.querySelectorAll('[data-toggle-target=".main-menu-modal"]').forEach(function (btn) {
    btn.addEventListener('click', function (event) {
      event.preventDefault();
      body.classList.contains('showing-main-menu-modal') ? closeMenu() : openMenu();
    });
  });
  document.querySelectorAll('.main-menu-modal a').forEach(function (link) { link.addEventListener('click', closeMenu); });
  document.addEventListener('keyup', function (event) { if (event.key === 'Escape') closeMenu(); });
});
</script>
'''
CSS = '''
<style id="static-mobile-menu-css">
@media (max-width: 1024px){
  .responsive-nav{display:block}.site-header .main-navigation .nav-menu{display:none}
  .main-menu-modal{visibility:hidden;opacity:0;pointer-events:none;transition:opacity .18s ease,visibility .18s ease}
  body.showing-main-menu-modal .main-menu-modal{visibility:visible;opacity:1;pointer-events:auto}
  body.showing-main-menu-modal .responsive-nav{position:fixed;inset:0;z-index:99999;background:rgba(0,0,0,.5)}
  body.showing-main-menu-modal .primary-menu-list{position:absolute;top:0;right:0;width:min(86vw,360px);height:100%;overflow:auto;background:#fff;box-shadow:-20px 0 60px rgba(0,0,0,.22);padding:72px 28px 28px;display:block}
  body.showing-main-menu-modal .primary-menu-list .mobile-menu ul{display:grid;gap:0;margin:0;padding:0;list-style:none}
  body.showing-main-menu-modal .primary-menu-list .mobile-menu a{display:block;padding:15px 0;border-bottom:1px solid #eef2f7;color:#1f2937;font-weight:700;text-decoration:none}
  .close-main-nav-toggle{position:absolute;top:22px;right:22px;width:42px;height:42px;border:0;border-radius:999px;background:#eef2f7;cursor:pointer;z-index:2}
  .close-main-nav-toggle:before{content:'×';font-size:30px;line-height:40px;color:#111827}
  .toggle-btn{display:inline-flex;align-items:center;justify-content:center;flex-direction:column;gap:5px;width:46px;height:46px;border:1px solid #e5e7eb;border-radius:999px;background:#fff;cursor:pointer}
  .toggle-btn .toggle-bar{display:block;width:20px;height:2px;background:#111827;border-radius:99px}
}
</style>
'''
for p in pathlib.Path('public').rglob('*.html'):
    s=p.read_text(errors='ignore')
    s=re.sub(r'<script id="static-mobile-menu-js">.*?</script>\s*','',s,flags=re.S|re.I)
    s=re.sub(r'<style id="static-mobile-menu-css">.*?</style>\s*','',s,flags=re.S|re.I)
    if '</head>' in s:
        s=s.replace('</head>', CSS+'\n</head>', 1)
    if '</body>' in s:
        s=s.replace('</body>', SCRIPT+'\n</body>', 1)
    else:
        s += SCRIPT
    p.write_text(s)
print('added static mobile menu css/js')
