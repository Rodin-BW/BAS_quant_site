import asyncio
from playwright.async_api import async_playwright

async def capture_live():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://localhost:8501", wait_until="networkidle")
        await asyncio.sleep(2)
        
        # 1. 빌더 화면
        await page.screenshot(path=r"C:\Users\jbw06\.gemini\antigravity\brain\695d1c44-09fb-4b39-b4e6-b9c370839614\current_app_builder.png")
        print("Captured builder")

        # 2. 백테스팅 실행 클릭
        run_btn = page.locator('button:has-text("백테스팅 실행하기")')
        await run_btn.scroll_into_view_if_needed()
        await run_btn.click()
        await page.wait_for_selector("text=전략 구성 변경하러 가기", timeout=40000)
        await asyncio.sleep(2.5)

        # 3. 결과 상단 KPI
        top_btn = page.locator('button:has-text("전략 구성 변경하러 가기")')
        await top_btn.scroll_into_view_if_needed()
        await asyncio.sleep(1)
        await page.screenshot(path=r"C:\Users\jbw06\.gemini\antigravity\brain\695d1c44-09fb-4b39-b4e6-b9c370839614\current_app_results_kpi.png")
        print("Captured results KPI")

        # 4. 결과 지표 비교표
        tbl = page.locator("text=종합 성과 및 위험조정 지표 비교표")
        await tbl.scroll_into_view_if_needed()
        await asyncio.sleep(1)
        await page.screenshot(path=r"C:\Users\jbw06\.gemini\antigravity\brain\695d1c44-09fb-4b39-b4e6-b9c370839614\current_app_results_table.png")
        print("Captured results Table")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_live())
