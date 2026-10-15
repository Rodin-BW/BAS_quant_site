import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

def test_offline_fallback():
    html_path = Path("design/integrated_app.html").resolve()
    assert html_path.exists(), f"File not found: {html_path}"
    file_url = f"file:///{html_path.as_posix()}"

    print(f"[TEST] Testing Standalone / Deployed Fallback (Blocking port 8502)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 960})
        
        # 8502 API 서버 요청을 인위적으로 모두 차단 (배포 환경 모의)
        page.route("**/api/**", lambda route: route.abort())

        page.goto(file_url)
        page.wait_for_load_state("networkidle")
        print("[PASS] Page loaded with API blocked")

        # 동적 자산배분 모드 선택
        page.click("#mode-dynamic")
        page.wait_for_timeout(300)

        # 백테스트 실행
        page.click("#btn-run-simulation")
        page.wait_for_selector("#view-analytics:not(.hidden)", timeout=10000)
        page.wait_for_timeout(500)

        # 1. 배너 검증
        banner_h1 = page.locator("#view-analytics h1").text_content()
        print(f"[REPORT] Banner Title: {banner_h1}")
        assert "동적 자산배분" in banner_h1 and "DAA" in banner_h1

        # 2. 전략 ID 배지
        strat_id = page.locator("#report-strategy-id").text_content()
        print(f"[REPORT] Strategy ID: {strat_id}")
        assert "DAA" in strat_id

        # 3. 차트 범례
        legend_label = page.locator("#chart-legend-strategy-label").text_content()
        print(f"[REPORT] Chart Legend: {legend_label}")
        assert "동적 자산배분" in legend_label and "Tripod" not in legend_label

        # 4. 월간 히트맵 설명
        heat_desc = page.locator("#monthly-heatmap-desc").text_content()
        print(f"[REPORT] Heatmap Desc: {heat_desc}")
        assert "동적" in heat_desc and "트라이포드" not in heat_desc

        # 5. 월간 히트맵 테이블 행 수
        matrix_rows = page.locator("#monthly-returns-tbody tr").count()
        print(f"[REPORT] Heatmap Rows: {matrix_rows}")
        assert matrix_rows > 3, "Heatmap rows must be generated"

        # 6. 리밸런싱 히스토리 설명
        reb_desc = page.locator("#rebalance-history-desc").text_content()
        print(f"[REPORT] Rebalance Desc: {reb_desc}")
        assert "카나리아" in reb_desc and "Tripod" not in reb_desc

        # 7. 리밸런싱 로그 행 검증
        reb_text = page.locator("#rebalance-log-tbody").text_content()
        print(f"[REPORT] First Rebalance Log Row: {page.locator('#rebalance-log-tbody tr').first.text_content().strip()[:60]}...")
        assert "DAA SAFE (공격)" in reb_text or "공격" in reb_text, f"Rebalance log should contain dynamic records: {reb_text[:100]}"
        assert "QQQ 40 / QLD 40" not in reb_text, "Tripod dummy holdings must not be present!"

        # 8. 차트 SVG 검증
        curve_d = page.locator("#curve-bas-line").get_attribute("d")
        print(f"[REPORT] Curve Path length: {len(curve_d)}")
        assert curve_d and len(curve_d) > 100, "Curve must be drawn in fallback"

        # 9. 스크린샷 저장
        screenshot_path = Path("C:/Users/jbw06/.gemini/antigravity/brain/695d1c44-09fb-4b39-b4e6-b9c370839614/dynamic_deployed_fallback_verified.png")
        page.screenshot(path=str(screenshot_path))
        print(f"[SCREENSHOT] Saved {screenshot_path}")

        browser.close()
    print("[ALL PASS] Deployed / Fallback Standalone Simulation verified with 100% success!")

if __name__ == '__main__':
    test_offline_fallback()
