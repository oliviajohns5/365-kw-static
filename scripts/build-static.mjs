import fs from 'node:fs'
import path from 'node:path'

const publicDir = 'public'
const domain = 'https://365-kw.com'
const pages = []
function walk(dir) {
  for (const name of fs.readdirSync(dir)) {
    const p = path.join(dir, name)
    const st = fs.statSync(p)
    if (st.isDirectory()) walk(p)
    else if (name === 'index.html') pages.push(p)
  }
}
walk(publicDir)
const urls = pages.map(p => {
  let rel = '/' + path.relative(publicDir, path.dirname(p)).replaceAll(path.sep, '/')
  if (rel === '/.') rel = '/'
  if (!rel.endsWith('/')) rel += '/'
  return domain + rel
}).sort()
const sitemap = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.map(u => `  <url><loc>${u}</loc></url>`).join('\n')}\n</urlset>\n`
fs.writeFileSync(path.join(publicDir, 'sitemap.xml'), sitemap)
fs.writeFileSync(path.join(publicDir, 'robots.txt'), `User-agent: *\nAllow: /\nSitemap: ${domain}/sitemap.xml\n`)
console.log(JSON.stringify({ pages: pages.length, sitemapUrls: urls.length }))
