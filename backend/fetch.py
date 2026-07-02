import asyncio
from playwright.async_api import async_playwright

# ==========================================
# CHANGE ONLY THESE TWO VALUES
# ==========================================

URL = "https://cae.iiti.ac.in/main/faculty"
OUTPUT = "data/raw/iiti_cae.html"

# ==========================================


async def fetch():
    async with async_playwright() as pw:

        browser = await pw.chromium.launch(
            headless=True,
            args=["--ignore-certificate-errors"]
        )

        context = await browser.new_context(
            ignore_https_errors=True,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )

        page = await context.new_page()

        try:
            print("Opening:", URL)

            await page.goto(
                URL,
                wait_until="networkidle",
                timeout=60000
            )

            await page.wait_for_timeout(5000)

            html = await page.content()

            with open(OUTPUT, "w", encoding="utf-8") as f:
                f.write(html)

            print("\n✅ Saved Successfully")
            print("File :", OUTPUT)
            print("HTML Size :", len(html))

        except Exception as e:
            print("\n❌ Error:", e)

        finally:
            await browser.close()


asyncio.run(fetch())