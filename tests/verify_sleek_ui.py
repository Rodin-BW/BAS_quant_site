import asyncio
from playwright.async_api import async_playwright

async def verify_new_ui():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        await page.goto("http://localhost:8501", wait_until="networkidle")
        await asyncio.sleep(2)

        # 1. 깔끔해진 빌더 화면 (정적 자산배분) 상단 캡처
        await page.screenshot(path=r"C:\Users\jbw06\.gemini\antigravity\brain\695d1c44-09fb-4b39-b4e6-b9c370839614\sleek_builder_static.png")
        print("Captured sleek static builder")

        # 2. 트라이포드 전략 버튼 클릭 전환
        tp_btn = page.locator('button:has-text("나스닥 레버리지 트라이포드")')
        await tp_btn.click()
        await asyncio.sleep(1.5)
        await page.screenshot(path=r"C:\Users\jbw06\.gemini\antigravity\brain\695d1c44-09fb-4b39-b4e6-b9c370839614\sleek_builder_tripod.png")
        print("Captured sleek tripod builder")

        # 3. 최하단으로 스크롤하여 백테스팅 실행
        run_btn = page.locator('button:has-text("백테스팅 실행하기")')
        await run_btn.scroll_into_view_if_needed()
        await asyncio.sleep(0.5)
        await run_btn.click()
        print("Clicked run button")

        # 결과 화면 로딩 대기
        await page.wait_for_selector("text=전략 구성 변경하러 가기", timeout=40000)
        # 탭 또는 플롯 렌더 대기
        await page.wait_for_selector("text=자산 성장 차트", timeout=40000)
        await asyncio.sleep(3)

        # 4. 결과 화면 상단 KPI 및 차트 캡처
        top_btn = page.locator('button:has-text("전략 구성 변경하러 가기")')
        await top_btn.scroll_into_view_if_needed()
        await asyncio.sleep(1.0)
        await page.screenshot(path=r"C:\Users\jbw06\.gemini\antigravity\brain\695d1c44-09fb-4b39-b4e6-b9c370839614\sleek_result_kpi_charts.png")
        print("Captured sleek result view successfully")

        # 5. 종합 성과 및 위험조정 지표 비교표 캡처
        tbl_header = page.locator('text=종합 성과 및 위험조정 지표 비교표')
        await tbl_header.scroll_into_view_if_needed()
        await asyncio.sleep(1.0)
        await page.screenshot(path=r"C:\Users\jbw06\.gemini\antigravity\brain\695d1c44-09fb-4b39-b4e6-b9c370839614\sleek_result_comparison_table.png")
        print("Captured sleek result comparison table successfully")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_new_ui())
