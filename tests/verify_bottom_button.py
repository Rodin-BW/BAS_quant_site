import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        await page.goto("http://localhost:8501", wait_until="networkidle")
        await asyncio.sleep(2)

        # 1. 빌더 화면 최하단 버튼으로 직접 스크롤
        run_btn = page.locator('button:has-text("백테스팅 실행하기")')
        await run_btn.scroll_into_view_if_needed()
        await asyncio.sleep(1)
        await page.screenshot(path=r"C:\Users\jbw06\.gemini\antigravity\brain\695d1c44-09fb-4b39-b4e6-b9c370839614\builder_bottom_action_card.png")
        print("Captured builder bottom card!")

        # 2. 최하단 백테스팅 실행 버튼 클릭
        await run_btn.click()
        print("Clicked run button")

        # 결과 화면 로딩 완료 대기
        await page.wait_for_selector("text=전략 구성 변경하러 가기", timeout=20000)
        print("Found results view!")

        # 3. 결과 화면 상단으로 스크롤하여 결과 요약/차트 영역 캡처
        header_el = page.locator('text=전략 구성 변경하러 가기')
        await header_el.scroll_into_view_if_needed()
        await asyncio.sleep(1)
        await page.screenshot(path=r"C:\Users\jbw06\.gemini\antigravity\brain\695d1c44-09fb-4b39-b4e6-b9c370839614\results_navigated_top_screen.png")
        print("Captured results top view!")

        # 4. 결과 화면 최하단으로 스크롤하여 돌아가기 버튼 캡처
        back_btn = page.locator('button:has-text("전략 구성(빌더) 화면으로 돌아가기")')
        await back_btn.scroll_into_view_if_needed()
        await asyncio.sleep(1)
        await page.screenshot(path=r"C:\Users\jbw06\.gemini\antigravity\brain\695d1c44-09fb-4b39-b4e6-b9c370839614\results_bottom_return_button.png")
        print("Captured results bottom return button!")

        # 5. 최하단 돌아가기 버튼 클릭 테스트
        await back_btn.click()
        print("Clicked back to builder button")

        await page.wait_for_selector("text=Step 1. 운용할 전략 아키텍처 선택", timeout=20000)
        print("Back to builder screen confirmed!")
        top_step1 = page.locator('text=Step 1. 운용할 전략 아키텍처 선택')
        await top_step1.scroll_into_view_if_needed()
        await asyncio.sleep(1)
        await page.screenshot(path=r"C:\Users\jbw06\.gemini\antigravity\brain\695d1c44-09fb-4b39-b4e6-b9c370839614\back_to_builder_top_verified.png")
        print("Captured return to builder screen!")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
