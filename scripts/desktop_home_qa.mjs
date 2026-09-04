import { chromium } from 'playwright'
const base = process.argv[2] || 'https://365-kw-static.vercel.app'
const browser = await chromium.launch({ headless: true })
const page = await browser.newPage({ viewport: { width: 1365, height: 900 }, deviceScaleFactor: 1 })
await page.goto(base + '/', { waitUntil: 'networkidle', timeout: 45000 })
const data = await page.evaluate(() => {
  const q = sel => [...document.querySelectorAll(sel)].slice(0,6).map(el => {
    const r = el.getBoundingClientRect(), cs = getComputedStyle(el)
    return {tag:el.tagName, cls:String(el.className).slice(0,80), x:Math.round(r.x), y:Math.round(r.y), w:Math.round(r.width), h:Math.round(r.height), display:cs.display, float:cs.float, position:cs.position, margin:cs.margin, padding:cs.padding, bg:cs.backgroundColor}
  })
  return {
    viewport: window.innerWidth,
    bodyW: document.body.scrollWidth,
    primary: q('#primary'),
    articles: q('main article'),
    figures: q('main article figure'),
    contentWraps: q('main article .content-wrap'),
    entryHeaders: q('main article .entry-header'),
    entryContents: q('main article .entry-content'),
    readmore: q('main article .entry-footer')
  }
})
console.log(JSON.stringify(data,null,2))
await page.screenshot({path:'desktop-home-before.png', fullPage:false})
await browser.close()
