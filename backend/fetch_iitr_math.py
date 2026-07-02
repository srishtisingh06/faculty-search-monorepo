import asyncio
from playwright.async_api import async_playwright

async def fetch():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=['--ignore-certificate-errors']
        )

        context = await browser.new_context(
            ignore_https_errors=True,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        page = await context.new_page()

        await page.goto(
            'https://iitr.ac.in/Departments/Mathematics%20Department/People/Faculty/index.html',
            wait_until='domcontentloaded',
            timeout=45000
        )

        await page.wait_for_timeout(8000)

        html = await page.content()

        with open('data/raw/iitr_math.html', 'w', encoding='utf-8') as f:
            f.write(html)

        print(f'Saved! Size: {len(html)}')

        await browser.close()

asyncio.run(fetch())