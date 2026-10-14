import asyncio
from playwright.async_api import async_playwright

async def verify_bottom_returns():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://localhost:8501", wait_until="networkidle")
        await asyncio.sleep(2)

        # 백테스팅 실행
        run_btn = page.locator('button:has-text("백테스팅 실행하기")')
        await run_btn.scroll_into_view_if_needed()
        await run_btn.click()
        await page.wait_for_selector("text=전략 구성 변경하러 가기", timeout=40000)
        await asyncio.sleep(2.5)

        # 보고서 하단 연도별 및 월별 수익률 매트릭스 영역으로 스크롤
        returns_section = page.locator("text=연도별 및 월별 수익률 매트릭스")
        await returns_section.scroll_into_view_if_needed()
        await asyncio.sleep(1)
        await page.screenshot(path=r"C:\Users\jbw06\.gemini\antigravity\brain\695d1c44-09fb-4b39-b4e6-b9c370839614\report_bottom_returns_matrix.png")
        print("Captured bottom returns matrix successfully")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_bottom_returns())
