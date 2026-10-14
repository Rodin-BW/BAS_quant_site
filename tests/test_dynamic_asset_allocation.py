import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

ARTIFACT_DIR = Path("C:/Users/jbw06/.gemini/antigravity/brain/695d1c44-09fb-4b39-b4e6-b9c370839614")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

def test_dynamic_asset_allocation():
    html_path = Path("design/integrated_app.html").resolve()
    assert html_path.exists(), f"File not found: {html_path}"
    file_url = f"file:///{html_path.as_posix()}"

    print(f"[TEST] Opening {file_url} in Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 960})
        page.on("console", lambda msg: print(f"[CONSOLE] {msg.type}: {msg.text}"))
        
        # 1. 페이지 로드
        page.goto(file_url)
        page.wait_for_load_state("networkidle")
        print("[PASS] Page loaded successfully")

        # 2. 3-Way 전략 모드 전환: 동적 자산배분 (Dynamic DAA/VAA) 선택
        btn_dynamic = page.locator("#mode-dynamic")
        assert btn_dynamic.is_visible(), "#mode-dynamic button should be visible"
        btn_dynamic.click()
        page.wait_for_timeout(300)

        dynamic_panel = page.locator("#dynamic-panel")
        static_panel = page.locator("#static-panel")
        tripod_panel = page.locator("#tripod-panel")

        assert dynamic_panel.is_visible(), "Dynamic panel must be visible after click"
        assert not static_panel.is_visible(), "Static panel must be hidden"
        assert not tripod_panel.is_visible(), "Tripod panel must be hidden"
        print("[PASS] 3-Way Mode Switch to Dynamic verified")

        # 스크린샷 1: 동적 자산배분 패널 진입
        panel_screenshot = ARTIFACT_DIR / "dynamic_panel_opened.png"
        page.screenshot(path=str(panel_screenshot))
        print(f"[SCREENSHOT] Saved {panel_screenshot}")

        # 3. 프리셋 전환 테스트 (VAA 공격형 -> 듀얼 모멘텀 -> 나스닥 DAA -> DAA 균형형)
        page.click("#btn-preset-vaa")
        page.wait_for_timeout(200)
        vaa_off_count = page.locator("#dynamic-off-count").text_content()
        assert "10" in vaa_off_count, f"VAA should have 10 offensive assets, got {vaa_off_count}"

        page.click("#btn-preset-momentum")
        page.wait_for_timeout(200)
        canary_box = page.locator("#canary-container-box")
        assert "opacity-40" in (canary_box.get_attribute("class") or ""), "Canary box should be disabled in Momentum mode"

        page.click("#btn-preset-nasdaq-daa")
        page.wait_for_timeout(200)
        nasdaq_off = page.locator("#dynamic-offensive-tags").text_content()
        assert "QQQ" in nasdaq_off and "SOXX" in nasdaq_off, "Nasdaq DAA offensive tags missing"

        page.click("#btn-preset-daa")
        page.wait_for_timeout(200)
        daa_off_count = page.locator("#dynamic-off-count").text_content()
        assert "11" in daa_off_count, f"DAA should have 11 offensive assets, got {daa_off_count}"
        print("[PASS] Dynamic presets (DAA, VAA, Dual Momentum, Nasdaq DAA) switched and verified")

        # 4. 자산 태그 추가 & 삭제 인터랙션 테스트
        page.fill("#dynamic-offensive-input", "SOXL")
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)
        off_tags = page.locator("#dynamic-offensive-tags").text_content()
        assert "SOXL" in off_tags, "SOXL should be added to offensive tags"

        # 삭제 버튼 클릭
        page.locator("button[onclick*=\"removeDynamicAsset('offensive', 'SOXL')\"]").click()
        page.wait_for_timeout(200)
        off_tags_after = page.locator("#dynamic-offensive-tags").text_content()
        assert "SOXL" not in off_tags_after, "SOXL should be removed from offensive tags"
        print("[PASS] Dynamic asset tag add and remove verified")

        # 5. 백테스트 시뮬레이션 실행 (yfinance API 연동)
        print("[TEST] Running dynamic backtest simulation...")
        page.click("#btn-run-simulation")
        
        # 리포트 뷰 노출 및 동적 자산배분 렌더링 완료 대기 (최대 35초)
        page.wait_for_selector("#view-analytics:not(.hidden)", timeout=35000)
        page.wait_for_function("() => document.querySelector('#view-analytics h1')?.textContent.includes('동적 자산배분')", timeout=35000)
        page.wait_for_timeout(1000)
        print("[PASS] Analytics report view is active and dynamic banner rendered")

        # 6. 리포트 헤더 배너 및 KPI 검증
        banner_h1 = page.locator("#view-analytics h1").text_content()
        print(f"[REPORT] Banner Title: {banner_h1}")
        assert "동적 자산배분" in banner_h1 and "DAA" in banner_h1, f"Unexpected banner title: {banner_h1}"

        strat_id = page.locator("#report-strategy-id").text_content()
        print(f"[REPORT] Strategy ID Badge: {strat_id}")
        assert "DAA" in strat_id or "MOMENTUM" in strat_id, f"Strategy ID must reflect dynamic model: {strat_id}"

        legend_label = page.locator("#chart-legend-strategy-label").text_content()
        print(f"[REPORT] Chart Legend Label: {legend_label}")
        assert "동적 자산배분" in legend_label, f"Legend must reflect dynamic model: {legend_label}"

        heat_desc = page.locator("#monthly-heatmap-desc").text_content()
        print(f"[REPORT] Heatmap Desc: {heat_desc}")
        assert "동적" in heat_desc, f"Heatmap description must be dynamic: {heat_desc}"

        reb_desc = page.locator("#rebalance-history-desc").text_content()
        print(f"[REPORT] Rebalance Desc: {reb_desc}")
        assert "카나리아" in reb_desc or "모멘텀" in reb_desc, f"Rebalance description must be dynamic: {reb_desc}"

        kpi_cagr = page.locator("#kpi-cagr").text_content()
        kpi_mdd = page.locator("#kpi-mdd").text_content()
        kpi_sharpe = page.locator("#kpi-sharpe").text_content()
        print(f"[REPORT] KPI Results: CAGR={kpi_cagr}, MDD={kpi_mdd}, Sharpe={kpi_sharpe}")
        assert kpi_cagr != "" and kpi_cagr != "0.00%", "CAGR should be non-zero"
        assert kpi_mdd != "" and kpi_mdd != "0.00%", "MDD should be non-zero"

        # 차트 SVG 경로 검증
        curve_d = page.locator("#curve-bas-line").get_attribute("d")
        assert curve_d and len(curve_d) > 20, "Chart curve path 'd' must be drawn"
        print(f"[PASS] Chart curve rendered with {len(curve_d)} path characters")

        # 7. 차트 마우스 호버 액션 검증 (트라이포드 잔재 방지)
        chart_area = page.locator("#chart-hover-area")
        box = chart_area.bounding_box()
        page.mouse.move(box["x"] + box["width"] * 0.45, box["y"] + box["height"] * 0.5)
        page.wait_for_timeout(200)
        hover_title = page.locator("#tooltip-event-title").text_content()
        print(f"[REPORT] Chart Hover Tooltip Title: {hover_title}")
        assert "동적" in hover_title or "카나리아" in hover_title or "방어" in hover_title or "모멘텀" in hover_title, f"Tooltip should not show tripod in dynamic mode: {hover_title}"

        # 8. 리밸런싱 로그 검증
        log_rows = page.locator("#rebalance-log-tbody tr")
        row_count = log_rows.count()
        assert row_count > 0, "Rebalance log must contain records"
        tbody_text = page.locator("#rebalance-log-tbody").text_content()
        assert any(k in tbody_text for k in ["DAA", "공격", "카나리아", "세금", "비중"]), "Dynamic status or rebalance record not in log"

        # 스크린샷 2: 동적 자산배분 결과 리포트
        report_screenshot = ARTIFACT_DIR / "dynamic_backtest_report_verified.png"
        page.screenshot(path=str(report_screenshot))
        print(f"[SCREENSHOT] Saved {report_screenshot}")

        browser.close()
    print("[ALL TESTS PASSED] Dynamic Asset Allocation backtesting verified with 100% success!")

if __name__ == "__main__":
    test_dynamic_asset_allocation()
