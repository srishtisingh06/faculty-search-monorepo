"""
Fetch IIT Bhubaneswar faculty pages: SECS (CSE/ECE/EE), unified table (for ME), Math
Run this on your local machine.
"""
import asyncio
from playwright.async_api import async_playwright
 
PAGES = {
    'iitbbs_secs': 'https://secs.iitbbs.ac.in/index.php/faculty-members/',
    'iitbbs_all': 'https://www.iitbbs.ac.in/index.php/faculty-members/',
    'iitbbs_math': 'https://sbs.iitbbs.ac.in/index.php/mathematics/mathematics-faculty-members/',
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
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=45000)
                await page.wait_for_timeout(8000)
                html = await page.content()
                out_path = f'data/raw/{key}.html'
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f'  Saved! Size: {len(html)} -> {out_path}')
            except Exception as e:
                print(f'  FAILED: {key} -> {e}')
 
        await browser.close()
 
asyncio.run(fetch())