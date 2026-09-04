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
@media (min-width:900px){
  body.blog #primary.content-area{max-width:1100px!important;margin-left:auto!important;margin-right:auto!important}
  body.blog .site-main article{display:grid!important;grid-template-columns:minmax(0,52%) minmax(0,48%)!important;align-items:stretch!important;overflow:hidden!important;background:#fff!important;border-radius:12px!important;margin-bottom:56px!important;box-shadow:0 14px 42px rgba(20,30,40,.10)!important}
  body.blog .site-main article>figure{grid-column:1!important;grid-row:1!important;width:100%!important;height:100%!important;min-height:360px!important;margin:0!important;position:relative!important;overflow:hidden!important;border-radius:12px 0 0 12px!important;background:#f3f4f6!important}
  body.blog .site-main article>figure a{display:block!important;width:100%!important;height:100%!important}
  body.blog .site-main article>figure img{width:100%!important;height:100%!important;object-fit:cover!important;display:block!important}
  body.blog .site-main article>figure .category{position:absolute!important;top:18px!important;left:18px!important;right:auto!important;z-index:2!important}
  body.blog .site-main article>.content-wrap{grid-column:2!important;grid-row:1!important;width:auto!important;min-height:360px!important;display:flex!important;flex-direction:column!important;justify-content:center!important;padding:44px 52px 52px!important;border:0!important;border-radius:0 12px 12px 0!important;background:#fff!important}
  body.blog .site-main article .entry-title{font-size:1.55em!important;line-height:1.25!important;margin-bottom:14px!important}
  body.blog .site-main article .entry-meta{margin-bottom:18px!important}
  body.blog .site-main article .entry-content{margin-top:0!important;font-size:17px!important;line-height:1.75!important;color:#4b5563!important}
  body.blog .site-main article .entry-content p{margin:0 0 22px!important}
  body.blog .site-main article .entry-footer{height:auto!important;margin-top:4px!important}
  body.blog .site-main article .btn-readmore{position:static!important;display:inline-flex!important;align-items:center!important;align-self:flex-start!important;width:auto!important;height:auto!important;padding:10px 18px!important;border-radius:999px!important;background:var(--primary-color)!important;color:#fff!important;font-size:12px!important;letter-spacing:.08em!important;text-transform:uppercase!important;line-height:1.2!important;text-indent:0!important;text-decoration:none!important;overflow:visible!important}
  body.blog .site-main article .btn-readmore:before,body.blog .site-main article .btn-readmore:after{display:none!important}
}
@media (max-width:899px){
  body.blog .site-main article>figure{margin:0!important;width:100%!important;overflow:hidden!important;border-radius:8px 8px 0 0!important}
  body.blog .site-main article>figure img{width:100%!important;height:auto!important;display:block!important}
}
@media (max-width:1024px){
  .responsive-nav{display:none!important;visibility:hidden!important;opacity:0!important;pointer-events:none!important;position:static!important;inset:auto!important;width:0!important;height:0!important;overflow:hidden!important;background:transparent!important;z-index:auto!important}
  body.showing-main-menu-modal{overflow:auto!important}
  .main-menu-modal,.primary-menu-list{visibility:hidden!important;opacity:0!important;pointer-events:none!important;position:static!important;transform:none!important;background:transparent!important;box-shadow:none!important;width:auto!important;height:auto!important;padding:0!important}
  header.site-header>.container{padding-left:15px!important;padding-right:15px!important;padding-bottom:0!important;position:relative!important}
  .header-main{display:flex!important;align-items:center!important;justify-content:space-between!important;gap:16px!important;position:relative!important;padding:16px 0!important}
  .site-branding{min-width:0!important;text-align:left!important;align-items:flex-start!important;display:flex!important;flex:auto!important}
  .site-branding .site-title,.site-branding .site-description{clip:rect(1px,1px,1px,1px)!important;position:absolute!important}
  .custom-logo-link{margin:0!important}.custom-logo-link img{max-width:72px!important;width:72px!important;height:auto!important}
  .nav-wrap{position:absolute!important;left:auto!important;right:15px!important;top:50%!important;transform:translateY(-50%)!important;display:block!important;width:50px!important;min-width:0!important;height:50px!important;background:transparent!important;padding:0!important;margin:0!important;box-shadow:none!important;border-radius:0!important;z-index:2000!important;flex:0 0 50px!important}
  .nav-wrap #site-navigation,.nav-wrap .main-navigation{display:none!important;width:0!important;height:0!important;overflow:hidden!important;visibility:hidden!important;pointer-events:none!important;background:transparent!important}
  .nav-wrap button.toggle-btn,.nav-wrap .toggle-btn,.main-navigation button.toggle-btn{display:none!important;visibility:hidden!important;opacity:0!important;width:0!important;height:0!important;padding:0!important;margin:0!important;border:0!important;background:transparent!important;box-shadow:none!important}
  .static-mobile-menu{display:block!important;position:relative!important;width:50px!important;height:50px!important;margin-left:0!important;z-index:2100!important}
  .static-mobile-menu summary{list-style:none;width:48px;height:48px;border-radius:999px;border:1px solid rgba(0,0,0,.12);background:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;box-shadow:0 6px 18px rgba(0,0,0,.12);cursor:pointer;padding:0}
  .static-mobile-menu summary::-webkit-details-marker{display:none}.static-mobile-menu summary span{width:22px;height:2px;background:#111827;border-radius:99px;display:block}
  .static-mobile-links{position:fixed;right:16px;top:96px;width:min(340px,calc(100vw - 32px));display:grid;padding:10px;background:#fff;border:1px solid #e5e7eb;border-radius:18px;box-shadow:0 22px 60px rgba(0,0,0,.18);z-index:2200}
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
    if '\x01' in s:
        s = s.replace('\x01', MENU + '\n<nav id="site-navigation" class="main-navigation" role="navigation" itemscope itemtype="http://schema.org/SiteNavigationElement">', 1)
    else:
        s = re.sub(r'(<nav id="site-navigation"[^>]*>)', lambda m: MENU + '\n' + m.group(1), s, count=1, flags=re.I)
    s = s.replace('</head>', CSS + '\n</head>', 1)
    if s != original:
        p.write_text(s)
        changed += 1
print({'changed_html_files': changed})
