from pathlib import Path

ROOT = Path('public')
STYLE_ID = 'static-adsense-layout-guard-css'
SCRIPT_ID = 'static-adsense-layout-guard-js'
STYLE = f'''<style id="{STYLE_ID}">
/* static-adsense-layout-guard */
.static-auto-ad-moved {{
  max-width: 1170px !important;
  width: calc(100% - 60px) !important;
  margin: 28px auto 34px !important;
  padding: 0 !important;
  clear: both !important;
  text-align: center !important;
  position: relative !important;
  z-index: 1 !important;
}}
.static-auto-ad-moved ins.adsbygoogle {{
  max-width: 100% !important;
  margin-left: auto !important;
  margin-right: auto !important;
}}
.site-header .google-auto-placed.static-auto-ad-moving,
.site-header ins.adsbygoogle.static-auto-ad-moving {{
  max-height: 0 !important;
  overflow: hidden !important;
  margin: 0 !important;
}}
@media (max-width: 767px) {{
  .static-auto-ad-moved {{
    width: 100% !important;
    max-width: 100% !important;
    margin: 18px auto 22px !important;
  }}
}}
</style>'''
SCRIPT = f'''<script id="{SCRIPT_ID}">
(function() {{
  function targetContainer() {{
    var content = document.getElementById('content') || document.querySelector('.site-content');
    var pageHeader = content && content.querySelector('.page-header');
    if (content && pageHeader && pageHeader.parentNode) {{
      return {{ parent: pageHeader.parentNode, before: pageHeader.nextSibling }};
    }}
    if (content && content.parentNode) return {{ parent: content.parentNode, before: content }};
    return null;
  }}
  function moveHeaderAutoAds() {{
    var target = targetContainer();
    if (!target) return;
    var nodes = document.querySelectorAll('.site-header .google-auto-placed, .site-header ins.adsbygoogle');
    nodes.forEach(function(node) {{
      var wrap = node.classList && node.classList.contains('google-auto-placed') ? node : (node.closest && node.closest('.google-auto-placed')) || node;
      if (!wrap || wrap.dataset.staticAdMoved === '1') return;
      wrap.dataset.staticAdMoved = '1';
      wrap.classList.add('static-auto-ad-moved');
      wrap.classList.remove('static-auto-ad-moving');
      target.parent.insertBefore(wrap, target.before);
    }});
  }}
  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', moveHeaderAutoAds);
  }} else {{
    moveHeaderAutoAds();
  }}
  var observer = new MutationObserver(function() {{ moveHeaderAutoAds(); }});
  observer.observe(document.documentElement, {{ childList: true, subtree: true }});
  setTimeout(moveHeaderAutoAds, 500);
  setTimeout(moveHeaderAutoAds, 1500);
  setTimeout(moveHeaderAutoAds, 4000);
}})();
</script>'''
changed = 0
for file in ROOT.rglob('*.html'):
    s = file.read_text(errors='ignore')
    old = s
    # Remove previous versions if rerun.
    import re
    s = re.sub(r'<style id="static-adsense-layout-guard-css">[\s\S]*?</style>\s*', '', s)
    s = re.sub(r'<script id="static-adsense-layout-guard-js">[\s\S]*?</script>\s*', '', s)
    if '</head>' in s:
        s = s.replace('</head>', STYLE + '\n' + SCRIPT + '\n</head>', 1)
    else:
        s = STYLE + '\n' + SCRIPT + '\n' + s
    if s != old:
        file.write_text(s)
        changed += 1
print({'changed_files': changed})
