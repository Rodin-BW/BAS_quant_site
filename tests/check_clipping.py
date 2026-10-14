import asyncio
from playwright.async_api import async_playwright

VIEWPORTS = [
    {"name": "desktop_1920", "width": 1920, "height": 1080},
    {"name": "laptop_1366", "width": 1366, "height": 768},
    {"name": "tablet_1024", "width": 1024, "height": 768},
    {"name": "mobile_390", "width": 390, "height": 844}
]

async def check_clipping():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        report = []

        for vp in VIEWPORTS:
            page = await browser.new_page(viewport={"width": vp["width"], "height": vp["height"]})
            await page.goto("http://localhost:8501", wait_until="networkidle")
            await asyncio.sleep(2)

            # 1. 빌더 화면 검사 (상단 및 최하단)
            body_scroll_w = await page.evaluate("document.body.scrollWidth")
            win_inner_w = await page.evaluate("window.innerWidth")
            has_h_overflow_builder = body_scroll_w > win_inner_w + 5

            # 최하단 버튼 가시성 검사
            run_btn = page.locator('button:has-text("백테스팅 실행하기")')
            await run_btn.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            is_run_btn_visible = await run_btn.is_visible()
            
            # 빌더 하단 캡처
            shot_builder = f"C:\\Users\\jbw06\\.gemini\\antigravity\\brain\\695d1c44-09fb-4b39-b4e6-b9c370839614\\check_builder_{vp['name']}.png"
            await page.screenshot(path=shot_builder)

            # 2. 백테스팅 버튼 클릭하여 결과 화면 검사
            await run_btn.click()
            await page.wait_for_selector("text=전략 구성 변경하러 가기", timeout=20000)
            await asyncio.sleep(1)

            # 결과 화면 상단 확인
            header_el = page.locator('text=전략 구성 변경하러 가기')
            await header_el.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            is_header_visible = await header_el.is_visible()

            # 결과 화면 최하단 돌아가기 버튼 확인
            back_btn = page.locator('button:has-text("전략 구성(빌더) 화면으로 돌아가기")')
            await back_btn.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            is_back_btn_visible = await back_btn.is_visible()

            # 수평 오버플로우 검사
            res_scroll_w = await page.evaluate("document.body.scrollWidth")
            has_h_overflow_res = res_scroll_w > win_inner_w + 5

            shot_res = f"C:\\Users\\jbw06\\.gemini\\antigravity\\brain\\695d1c44-09fb-4b39-b4e6-b9c370839614\\check_result_{vp['name']}.png"
            await page.screenshot(path=shot_res)

            report.append({
                "viewport": vp["name"],
                "width": vp["width"],
                "height": vp["height"],
                "h_overflow_builder": has_h_overflow_builder,
                "is_run_btn_visible": is_run_btn_visible,
                "is_header_visible": is_header_visible,
                "is_back_btn_visible": is_back_btn_visible,
                "h_overflow_res": has_h_overflow_res
            })
            await page.close()

        await browser.close()
        
        print("=== CLIPPING CHECK REPORT ===")
        for r in report:
            print(r)

if __name__ == "__main__":
    asyncio.run(check_clipping())
