import asyncio
from playwright.async_api import async_playwright

async def verify_comma_formatting():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://localhost:8501", wait_until="networkidle")
        await asyncio.sleep(2)

        # 초기 자본금 입력창 스크롤 및 캡처
        cap_input = page.locator('text=Step 3. 시뮬레이션 환경')
        await cap_input.scroll_into_view_if_needed()
        await asyncio.sleep(1)
        await page.screenshot(path=r"C:\Users\jbw06\.gemini\antigravity\brain\695d1c44-09fb-4b39-b4e6-b9c370839614\step3_comma_formatted_input.png")
        print("Captured comma formatted input successfully")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_comma_formatting())
