import pathlib
import re

ROOT = pathlib.Path('public')

MENU = '''
<details class="static-mobile-menu">
  <summary aria-label="Open menu"><span></span><span></span><span></span></summary>
  <nav class="static-mobile-links" aria-label="Mobile menu">
    <a href="/">Home</a>
    <a href="/category/travel/">Travel</a>
    <a href="/privacy-policy/">Privacy Policy</a>
    <a href="/contact-us/">Contact Us</a>
    <a href="/dmca/">DMCA</a>
    <a href="/terms-and-conditions/">Terms And Conditions</a>
  </nav>
</details>
'''.strip()

CSS = '''
<style id="static-hard-qa-css">
html,body{max-width:100%;overflow-x:hidden}
img,svg,video,iframe{max-width:100%;height:auto}
figure,figure[style],.wp-caption,.wp-caption[style]{max-width:100%!important}
.pure_content img,.entry-content img,.post img{max-width:100%;height:auto}
.site-header,.site-header .container,.header-main,.nav-wrap{overflow:visible!important}
.static-mobile-menu{display:none}
@media (max-width:1024px){
  .responsive-nav{display:none!important;visibility:hidden!important;opacity:0!important;pointer-events:none!important;position:static!important;inset:auto!important;width:0!important;height:0!important;overflow:hidden!important;background:transparent!important;z-index:auto!important}
  body.showing-main-menu-modal{overflow:auto!important}
  .main-menu-modal,.primary-menu-list{visibility:hidden!important;opacity:0!important;pointer-events:none!important;position:static!important;transform:none!important;background:transparent!important;box-shadow:none!important;width:auto!important;height:auto!important;padding:0!important}
  header.site-header>.container{padding-left:15px!important;padding-right:15px!important;padding-bottom:0!important}
  .header-main{display:flex!important;align-items:center!important;justify-content:space-between!important;gap:16px!important;position:relative!important;padding:16px 0!important}
  .site-branding{min-width:0!important;text-align:left!important;align-items:flex-start!important;display:flex!important;flex:auto!important}
  .site-branding .site-title,.site-branding .site-description{clip:rect(1px,1px,1px,1px)!important;position:absolute!important}
  .custom-logo-link{margin:0!important}.custom-logo-link img{max-width:72px!important;width:72px!important;height:auto!important}
  .nav-wrap{position:static!important;display:flex!important;justify-content:flex-end!important;align-items:center!important;background:transparent!important;padding:0!important;margin:0!important;box-shadow:none!important;border-radius:0!important;z-index:20!important;flex:0 0 auto!important}
  .nav-wrap #site-navigation{display:block!important}.nav-wrap #site-navigation .nav-menu,.nav-wrap #site-navigation .menu-menu-1-container,.nav-wrap #site-navigation .toggle-btn{display:none!important}
  .static-mobile-menu{display:block!important;position:relative!important;margin-left:auto!important;z-index:1000!important}
  .static-mobile-menu summary{list-style:none;width:48px;height:48px;border-radius:999px;border:1px solid rgba(0,0,0,.12);background:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;box-shadow:0 6px 18px rgba(0,0,0,.12);cursor:pointer;padding:0}
  .static-mobile-menu summary::-webkit-details-marker{display:none}.static-mobile-menu summary span{width:22px;height:2px;background:#111827;border-radius:99px;display:block}
  .static-mobile-links{position:absolute;right:0;top:calc(100% + 10px);width:min(82vw,310px);display:grid;padding:10px;background:#fff;border:1px solid #e5e7eb;border-radius:18px;box-shadow:0 22px 60px rgba(0,0,0,.18);z-index:1001}
  .static-mobile-links a{display:block;padding:14px 14px;border-radius:12px;color:#111827!important;text-decoration:none!important;font-weight:700;text-transform:none!important;border:0!important;background:transparent!important}.static-mobile-links a:hover{background:#f3f4f6!important}
  header.page-header{padding-top:54px!important;padding-bottom:42px!important;margin-bottom:40px!important}
}
@media (max-width:767px){.container{width:auto!important;max-width:100%!important;margin-left:15px!important;margin-right:15px!important}.site-content>.container{margin-left:15px!important;margin-right:15px!important}.content-area,#primary,#secondary{width:100%!important;float:none!important;padding-left:0!important;padding-right:0!important}.post figure{width:100%!important}}
</style>
'''.strip()

changed = 0
for p in ROOT.rglob('*.html'):
    s = p.read_text(errors='ignore')
    original = s
    s = re.sub(r'<script id="static-mobile-menu-js">.*?</script>\s*', '', s, flags=re.S|re.I)
    s = re.sub(r'<style id="static-mobile-menu-css">.*?</style>\s*', '', s, flags=re.S|re.I)
    s = re.sub(r'<style id="static-hard-qa-css">.*?</style>\s*', '', s, flags=re.S|re.I)
    s = re.sub(r'<details class="static-mobile-menu">.*?</details>\s*', '', s, flags=re.S|re.I)
    # Remove accidental Gmail/email text pasted into the Custom CSS block, preserving the actual grid CSS that follows.
    s = re.sub(r'(id=["\']wp-custom-css["\'][^>]*>.*?)(?:Conversation opened\..*?)(?=\.grid_container,)', r'\1', s, flags=re.S|re.I)
    s = re.sub(r'(<nav id="site-navigation"[^>]*>)', MENU + '\n\1', s, count=1, flags=re.I)
    s = s.replace('</head>', CSS + '\n</head>', 1)
    if s != original:
        p.write_text(s)
        changed += 1
print({'changed_html_files': changed})
