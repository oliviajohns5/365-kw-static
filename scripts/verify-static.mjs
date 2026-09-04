import fs from 'node:fs'
import path from 'node:path'

const publicDir = 'public'
const htmlFiles = []
function walk(dir) {
  for (const name of fs.readdirSync(dir)) {
    const p = path.join(dir, name)
    const st = fs.statSync(p)
    if (st.isDirectory()) walk(p)
    else if (p.endsWith('.html')) htmlFiles.push(p)
  }
}
walk(publicDir)
const missingAssets = []
const missingPages = []
const externalOld = []
for (const file of htmlFiles) {
  const html = fs.readFileSync(file, 'utf8')
  for (const m of html.matchAll(/\b(?:src|href|data-src|data-lazy-src)=["']([^"']+)["']/gi)) {
    const val = m[1]
    if (val.includes('365-kw.com')) externalOld.push({ file, val })
    if (!val.startsWith('/') || val.startsWith('//')) continue
    if (val.startsWith('/wp-content/') || val.startsWith('/wp-includes/')) {
      const local = path.join(publicDir, decodeURIComponent(val.slice(1)))
      if (!fs.existsSync(local)) missingAssets.push({ file, val })
    } else if (!/\.[a-z0-9]{2,5}$/i.test(val)) {
      const local = path.join(publicDir, decodeURIComponent(val.slice(1)), 'index.html')
      if (!fs.existsSync(local) && val !== '/') missingPages.push({ file, val })
    }
  }
}
const result = {
  htmlFiles: htmlFiles.length,
  missingAssets: missingAssets.length,
  missingPages: missingPages.length,
  externalOld: externalOld.length,
  sampleMissingAssets: missingAssets.slice(0, 20),
  sampleMissingPages: missingPages.slice(0, 20),
  sampleExternalOld: externalOld.slice(0, 10),
}
console.log(JSON.stringify(result, null, 2))
if (missingAssets.length > 50 || externalOld.length > 0) process.exit(1)
