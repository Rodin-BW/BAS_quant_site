import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 1400})
        page = await context.new_page()

        print("[TEST] 1. Streamlit 접속 중...")
        await page.goto("http://localhost:8501", timeout=30000, wait_until="networkidle")
        await page.wait_for_timeout(2000)

        frame_el = await page.wait_for_selector("iframe", timeout=15000)
        frame = await frame_el.content_frame()
        assert frame is not None, "iframe content_frame을 찾을 수 없습니다."

        # 1. 초기 상태: 4종목 확인
        count_el = frame.locator("#donut-asset-count")
        initial_count = await count_el.text_content()
        curr_el = frame.locator("#donut-currency-exposure")
        initial_curr = await curr_el.text_content()
        print(f"[TEST] 1. 초기 도넛 카운트: {initial_count}, 통화: {initial_curr}")
        assert "4 종목" in initial_count, f"초기 종목 수 이상: {initial_count}"

        # 2. 3개 종목 순차 삭제 (사용자 상황 재현: QQQ만 남김)
        print("[TEST] 2. 종목 삭제 진행 (SPY, TLT, GLD 삭제)...")
        # 삭제 버튼 3번 클릭 (맨 위에서 2번째 항목부터 삭제)
        for _ in range(3):
            del_btns = frame.locator("#asset-list-container button:has-text('close')")
            count = await del_btns.count()
            if count > 1:
                await del_btns.nth(1).click()
                await page.wait_for_timeout(300)

        # QQQ 비중 100% 자동 맞춤
        await frame.locator("#btn-normalize-weights").click()
        await page.wait_for_timeout(500)

        one_count = await count_el.text_content()
        one_curr = await curr_el.text_content()
        print(f"[TEST] 3. 1종목(QQQ 100%) 삭제 후 도넛 카운트: {one_count}, 통화: {one_curr}")
        assert "1 종목" in one_count, f"1종목 삭제 후 도넛 카운트 불일치: {one_count}"

        # 4. 스크린샷 캡처: 1종목일 때 도넛 차트 연동 증빙
        artifact_dir = Path("C:/Users/jbw06/.gemini/antigravity/brain/695d1c44-09fb-4b39-b4e6-b9c370839614")
        shot_one = artifact_dir / "donut_single_asset_count_verified.png"
        await page.screenshot(path=str(shot_one))
        print(f"[TEST] 4. 1종목 도넛 차트 스크린샷 저장 완료: {shot_one}")

        # 5. 종목 1개 추가 (KRX 종목: 069500.KS)
        print("[TEST] 5. 한국 종목(069500.KS) 추가 테스트...")
        search_input = frame.locator("#ticker-search-input")
        await search_input.fill("069500.KS")
        await frame.locator("#btn-add-asset").click()
        await page.wait_for_timeout(1000)

        two_count = await count_el.text_content()
        two_curr = await curr_el.text_content()
        print(f"[TEST] 6. 2종목 추가 후 도넛 카운트: {two_count}, 통화: {two_curr}")
        assert "2 종목" in two_count, f"2종목 추가 후 도넛 카운트 불일치: {two_count}"
        assert "KRW" in two_curr, f"KRW 통화 노출 반영 불일치: {two_curr}"

        # 6. 프리셋(올웨더) 선택 시 5종목으로 자동 갱신 확인
        print("[TEST] 7. 올웨더 프리셋 클릭...")
        preset_allweather = frame.locator("button:has-text('올웨더 (All Weather)')").first
        await preset_allweather.click()
        await page.wait_for_timeout(500)

        preset_count = await count_el.text_content()
        print(f"[TEST] 8. 올웨더 프리셋 선택 후 도넛 카운트: {preset_count}")
        assert "5 종목" in preset_count, f"프리셋 종목 수 불일치: {preset_count}"

        await browser.close()
        print("\n✅ [SUCCESS] 도넛 차트 종목 수 및 통화 비중 실시간 연동 검증 100% 통과!")

if __name__ == "__main__":
    asyncio.run(run())
