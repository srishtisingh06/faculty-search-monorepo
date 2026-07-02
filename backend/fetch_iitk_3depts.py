"""
Fetch IIT Kanpur faculty pages: ME, EE, Mathematics & Statistics
Run this on your local machine where Playwright + venv is set up.
"""
import asyncio
from playwright.async_api import async_playwright
 
PAGES = {
    'iitk_me': 'https://www.iitk.ac.in/me/people/faculty',
    'iitk_ee': 'https://www.iitk.ac.in/ee/faculty',
    'iitk_math': 'https://www.iitk.ac.in/math/index.php/faculty',
}
 
async def fetch():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=['--ignore-certificate-errors'])
        context = await browser.new_context(
            ignore_https_errors=True,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
 
        for key, url in PAGES.items():
            print(f'Fetching {key}: {url}')
            await page.goto(url)
            await page.wait_for_timeout(6000)
            html = await page.content()
            out_path = f'data/raw/{key}.html'
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f'  Saved! Size: {len(html)} -> {out_path}')
 
        await browser.close()
 
asyncio.run(fetch())