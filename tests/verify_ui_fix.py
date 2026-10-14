import asyncio
from playwright.async_api import async_playwright

async def verify_ui_fix():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1366, "height": 768})
        await page.goto("http://localhost:8501", wait_until="networkidle")
        await asyncio.sleep(2)

        # 1. 키보드로 두 번째 옵션(트라이포드) 선택
        strat_box = page.locator('div[data-testid="stSelectbox"]').first
        await strat_box.click()
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("Enter")
        await asyncio.sleep(2)

        # 2. 빌더 최하단으로 스크롤하여 실행 버튼 클릭
        run_btn = page.locator('button:has-text("백테스팅 실행하기")')
        await run_btn.scroll_into_view_if_needed()
        await run_btn.click()

        # 결과 화면 로딩 대기
        await page.wait_for_selector("text=전략 구성 변경하러 가기", timeout=25000)
        await asyncio.sleep(1)

        # 3. 결과 화면 상단: 트라이포드 3대 축 카드 캡처
        summary_expander = page.locator('text=적용된 전략 구성 & 포트폴리오 배분 명세')
        await summary_expander.scroll_into_view_if_needed()
        await asyncio.sleep(0.5)
        await page.screenshot(path=r"C:\Users\jbw06\.gemini\antigravity\brain\695d1c44-09fb-4b39-b4e6-b9c370839614\fixed_ui_tripod_and_kpi.png")

        # 4. KPI 카드 집중 캡처
        kpi_sec = page.locator('text=백테스트 실질 성과 요약')
        await kpi_sec.scroll_into_view_if_needed()
        await asyncio.sleep(0.5)
        await page.screenshot(path=r"C:\Users\jbw06\.gemini\antigravity\brain\695d1c44-09fb-4b39-b4e6-b9c370839614\fixed_ui_kpi_cards_zoom.png")

        print("Captured UI fix screenshots successfully!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_ui_fix())
