import { chromium } from 'playwright'

const base = process.argv[2] || 'https://365-kw-static.vercel.app'
const paths = ['/', '/amazing-day-trips-from-san-sebastian/', '/business/the-walper-hotel/', '/privacy-policy/']
const browser = await chromium.launch({ headless: true })
const results = []
for (const path of paths) {
  const page = await browser.newPage({ viewport: { width: 576, height: 1024 }, deviceScaleFactor: 1, isMobile: true })
  const jsErrors = []
  page.on('pageerror', e => jsErrors.push(String(e)))
  await page.goto(base + path, { waitUntil: 'networkidle', timeout: 45000 })
  const metrics = await page.evaluate(() => {
    const vw = window.innerWidth
    const offenders = [...document.body.querySelectorAll('*')].map(el => {
      const r = el.getBoundingClientRect()
      return { tag: el.tagName, cls: String(el.className || '').slice(0,80), id: el.id || '', left: Math.round(r.left), right: Math.round(r.right), width: Math.round(r.width) }
    }).filter(x => x.width > 1 && (x.right > vw + 2 || x.left < -2)).slice(0, 10)
    const nav = document.querySelector('.responsive-nav')
    const navStyle = nav ? getComputedStyle(nav) : null
    const menu = document.querySelector('.static-mobile-menu')
    const menuStyle = menu ? getComputedStyle(menu) : null
    if (menu) menu.setAttribute('open', '')
    const openScrollWidth = Math.max(document.documentElement.scrollWidth, document.body.scrollWidth)
    return {
      viewport: vw,
      statusText: document.title,
      closedScrollWidth: Math.max(document.documentElement.scrollWidth, document.body.scrollWidth),
      openScrollWidth,
      responsiveNavDisplay: navStyle?.display || null,
      responsiveNavVisibility: navStyle?.visibility || null,
      mobileMenuDisplay: menuStyle?.display || null,
      mobileMenuVisible: !!menu && menuStyle.display !== 'none' && menuStyle.visibility !== 'hidden',
      offenders
    }
  })
  results.push({ path, jsErrors, ...metrics })
  await page.close()
}
await browser.close()
console.log(JSON.stringify(results, null, 2))
const bad = results.filter(r => r.closedScrollWidth > r.viewport || r.openScrollWidth > r.viewport || r.responsiveNavDisplay !== 'none' || !r.mobileMenuVisible || r.offenders.length)
if (bad.length) process.exit(1)
