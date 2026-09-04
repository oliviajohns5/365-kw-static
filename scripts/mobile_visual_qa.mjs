import { chromium } from 'playwright'
import fs from 'node:fs'

const base = 'http://127.0.0.1:4173'
const paths = ['/', '/amazing-day-trips-from-san-sebastian/', '/business/the-walper-hotel/', '/privacy-policy/']
const browser = await chromium.launch({ headless: true })
const results = []
for (const path of paths) {
  const page = await browser.newPage({ viewport: { width: 576, height: 1024 }, deviceScaleFactor: 1, isMobile: true })
  const errors = []
  page.on('pageerror', e => errors.push(String(e)))
  page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()) })
  await page.goto(base + path, { waitUntil: 'networkidle', timeout: 30000 })
  const metrics = await page.evaluate(() => {
    const vw = window.innerWidth
    const offenders = [...document.body.querySelectorAll('*')].map(el => {
      const r = el.getBoundingClientRect()
      return { tag: el.tagName, cls: el.className || '', id: el.id || '', left: r.left, right: r.right, width: r.width }
    }).filter(x => x.width > 1 && (x.right > vw + 2 || x.left < -2)).slice(0, 20)
    const nav = document.querySelector('.responsive-nav')
    const navStyle = nav ? getComputedStyle(nav) : null
    const menu = document.querySelector('.static-mobile-menu')
    const menuStyle = menu ? getComputedStyle(menu) : null
    return {
      title: document.title,
      viewport: vw,
      scrollWidth: document.documentElement.scrollWidth,
      bodyScrollWidth: document.body.scrollWidth,
      overflowX: Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) - vw,
      responsiveNavDisplay: navStyle?.display || null,
      responsiveNavVisibility: navStyle?.visibility || null,
      mobileMenuDisplay: menuStyle?.display || null,
      mobileMenuVisible: !!menu && menuStyle.display !== 'none' && menuStyle.visibility !== 'hidden',
      offenders
    }
  })
  await page.screenshot({ path: `qa-mobile-${path.replaceAll('/','_') || 'home'}.png`, fullPage: false })
  results.push({ path, errors, ...metrics })
  await page.close()
}
await browser.close()
fs.writeFileSync('qa-mobile-results.json', JSON.stringify(results, null, 2))
console.log(JSON.stringify(results, null, 2))
