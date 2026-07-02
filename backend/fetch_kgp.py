import asyncio
from playwright.async_api import async_playwright

async def fetch():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://cse.iitkgp.ac.in/?faculty.html=')
        await page.wait_for_timeout(8000)
        html = await page.content()
        with open('data/raw/iitkgp_cse.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'Saved! Size: {len(html)}')
        await browser.close()

asyncio.run(fetch())