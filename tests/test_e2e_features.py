import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

def test_e2e_features():
    artifact_dir = r"C:\Users\jbw06\.gemini\antigravity\brain\695d1c44-09fb-4b39-b4e6-b9c370839614"
    os.makedirs(artifact_dir, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        
        print("1. Opening Streamlit app (http://localhost:8501)...", flush=True)
        page.goto("http://localhost:8501", timeout=60000)
        
        page.wait_for_selector("iframe", state="attached", timeout=40000)
        time.sleep(2)
        
        target_frame = None
        for frame in page.frames:
            if frame != page.main_frame:
                try:
                    if frame.locator("#btn-equal-weight").count() > 0 or frame.locator("#sim-end-date").count() > 0:
                        target_frame = frame
                        break
                except Exception:
                    pass
                    
        if target_frame is None:
            target_frame = page.frames[1] if len(page.frames) > 1 else page.main_frame

        print(f"Target frame found: {target_frame.url}", flush=True)

        # 1. 1/N 버튼 확인 및 클릭
        print("2. Testing 1/N equal weight button...", flush=True)
        btn_equal = target_frame.locator("#btn-equal-weight")
        btn_equal.wait_for(state="visible", timeout=15000)
        btn_equal.click()
        time.sleep(1)
        
        total_badge = target_frame.locator("#total-weight-pill").text_content()
        print(f"Total weight pill after 1/N: {total_badge.strip()}", flush=True)
        assert "100.0%" in total_badge
        
        # 2. 날짜 피커 제한 해제 확인 (max 속성이 제거되어 최신 날짜 제한 없음)
        print("3. Checking date picker range (max attribute unlocked)...", flush=True)
        end_date_input = target_frame.locator("#sim-end-date")
        max_attr = end_date_input.get_attribute("max")
        val_attr = end_date_input.input_value()
        print(f"End date value: {val_attr}, max attribute: {max_attr}", flush=True)
        assert max_attr is None or max_attr == "", f"Max attribute should be unlocked: {max_attr}"
        assert val_attr.startswith("2026"), f"Default end date should be today 2026: {val_attr}"
        
        # 3. 백테스트 실행 버튼 클릭
        print("4. Clicking Run Simulation button...", flush=True)
        run_btn = target_frame.locator("#btn-run-simulation")
        run_btn.click()
        
        # 4. 백테스트 결과 및 최신 2026 날짜 렌더링 검증
        print("5. Waiting for live backtest results...", flush=True)
        target_frame.locator("#kpi-cagr").wait_for(state="visible", timeout=35000)
        time.sleep(2)
        
        cagr_text = target_frame.locator("#kpi-cagr").text_content().strip()
        div_yield_text = target_frame.locator("#report-div-yield").text_content().strip()
        cum_div_text = target_frame.locator("#report-cum-div").text_content().strip()
        mdd_text = target_frame.locator("#kpi-mdd").text_content().strip()
        final_wealth = target_frame.locator("#kpi-final-wealth").text_content().strip()
        chart_end_label = target_frame.locator("#chart-end-label").text_content().strip()
        
        # 최근 월간 수익률 테이블 확인
        first_row_year = target_frame.locator("#monthly-returns-tbody tr:first-child td:first-child").text_content().strip()
        # 최근 리밸런싱 로그 확인
        first_reb_date = target_frame.locator("#rebalance-log-tbody tr:first-child span.font-bold").text_content().strip()
        
        print("=== E2E HARNESS VERIFICATION REPORT ===", flush=True)
        print(f"CAGR: {cagr_text}", flush=True)
        print(f"Portfolio Dividend Yield: {div_yield_text}", flush=True)
        print(f"Cumulative Dividends: {cum_div_text}", flush=True)
        print(f"MDD: {mdd_text}", flush=True)
        print(f"Final Wealth: {final_wealth}", flush=True)
        print(f"Chart End Label: {chart_end_label}", flush=True)
        print(f"Monthly Returns Top Year: {first_row_year}", flush=True)
        print(f"Recent Rebalance Log Date: {first_reb_date}", flush=True)
        
        assert div_yield_text != "-" and "%" in div_yield_text, f"Invalid dividend yield: {div_yield_text}"
        assert cum_div_text != "-" and "₩" in cum_div_text, f"Invalid cumulative dividends: {cum_div_text}"
        assert chart_end_label.startswith("2026"), f"Chart end date not up to date: {chart_end_label}"
        assert first_row_year == "2026", f"Monthly returns matrix top year should be 2026: {first_row_year}"
        assert first_reb_date.startswith("2026"), f"Rebalance log should show 2026: {first_reb_date}"
        
        # 5. 차트 인터랙티브 호버 검증 (마우스 놓았을 때 액션 표시)
        print("6. Verifying interactive chart hover action...", flush=True)
        chart_area = target_frame.locator("#chart-hover-area")
        tooltip = target_frame.locator("#chart-interactive-tooltip")
        
        # 호버 전에는 opacity-0 클래스 확인
        assert "opacity-0" in tooltip.get_attribute("class"), "Tooltip should be hidden before hover"
        
        # 차트 70% 위치 (2022년 금리인상 방어 구간)로 마우스 이동
        chart_box = chart_area.bounding_box()
        hover_x = chart_box["x"] + chart_box["width"] * 0.72
        hover_y = chart_box["y"] + chart_box["height"] * 0.45
        page.mouse.move(hover_x, hover_y)
        time.sleep(1)
        
        # 호버 후 툴팁 활성화 검증
        tooltip_classes = tooltip.get_attribute("class")
        assert "opacity-0" not in tooltip_classes, f"Tooltip should be visible on hover: {tooltip_classes}"
        hover_date = target_frame.locator("#tooltip-date-header").text_content().strip()
        hover_event = target_frame.locator("#tooltip-event-title").text_content().strip()
        hover_bas = target_frame.locator("#tooltip-bas-val").text_content().strip()
        print(f"Chart Hover Active -> Date: {hover_date}, Event: {hover_event}, Return: {hover_bas}", flush=True)
        assert hover_date != "" and hover_bas != "", "Tooltip contents should be populated on hover"
        
        # 호버 상태 스크린샷 캡처
        hover_screenshot_path = os.path.join(artifact_dir, "chart_hover_action_verified.png")
        page.screenshot(path=hover_screenshot_path, full_page=True)
        print(f"Hover action screenshot saved to {hover_screenshot_path}", flush=True)

        # 6. 리포트 차트 스케일 버튼 (Log vs Linear) 동작 검증
        print("7. Verifying Chart Scale Toggle (Log <-> Linear)...", flush=True)
        btn_linear = target_frame.locator("#scale-btn-linear")
        btn_log = target_frame.locator("#scale-btn-log")
        curve_line = target_frame.locator("#curve-bas-line")

        d_before = curve_line.get_attribute("d")
        btn_linear.click()
        time.sleep(0.5)
        d_linear = curve_line.get_attribute("d")
        assert d_before != d_linear, "Linear scale should change chart curve path d attribute"
        print("Linear scale curve verified successfully!", flush=True)

        btn_log.click()
        time.sleep(0.5)
        d_log = curve_line.get_attribute("d")
        assert d_log != d_linear, "Log scale should change chart curve path d attribute back"
        print("Log scale curve verified successfully!", flush=True)

        # 7. 리포트 타임프레임 기간 필터 버튼 (1Y, 5Y, ALL) 동작 검증
        print("8. Verifying Chart Timeframe (1Y, 5Y, ALL)...", flush=True)
        btn_1y = target_frame.locator("#tf-btn-1y")
        btn_all = target_frame.locator("#tf-btn-all")
        x_labels = target_frame.locator("#chart-x-labels")

        btn_1y.click()
        time.sleep(0.5)
        labels_1y = x_labels.text_content().strip()
        print(f"1Y Timeframe X-Labels: {labels_1y}", flush=True)
        assert "2025" in labels_1y or "2026" in labels_1y, f"1Y labels should reflect recent 1 year: {labels_1y}"

        btn_all.click()
        time.sleep(0.5)
        labels_all = x_labels.text_content().strip()
        print(f"ALL Timeframe X-Labels: {labels_all}", flush=True)
        assert "2010" in labels_all, f"ALL labels should start with 2010: {labels_all}"

        # 8. 최근 리밸런싱 히스토리 '전체 로그' 모달 팝업 및 전체 이력 검증
        print("9. Verifying Full Rebalance Log Modal...", flush=True)
        btn_full_log = target_frame.locator("#btn-open-rebalance-modal")
        modal = target_frame.locator("#rebalance-modal")
        tbody_modal = target_frame.locator("#reb-modal-tbody")

        assert "hidden" in modal.get_attribute("class"), "Rebalance modal should be hidden initially"
        btn_full_log.click()
        time.sleep(0.5)
        assert "hidden" not in modal.get_attribute("class"), "Rebalance modal should be visible after click"
        
        row_count = tbody_modal.locator("tr").count()
        print(f"Rebalance modal total rows rendered: {row_count}", flush=True)
        assert row_count > 10, f"Rebalance modal should render complete history: got {row_count} rows"

        # 모달 팝업 상태 스크린샷 캡처
        modal_screenshot = os.path.join(artifact_dir, "rebalance_history_modal_verified.png")
        page.screenshot(path=modal_screenshot, full_page=True)
        print(f"Rebalance modal screenshot saved to {modal_screenshot}", flush=True)

        # 모달 닫기
        modal_close_btn = target_frame.locator("#btn-close-rebalance-modal")
        modal_close_btn.dispatch_event("click")
        time.sleep(0.5)
        assert "hidden" in modal.get_attribute("class"), "Rebalance modal should close after clicking close button"
        print("Rebalance modal open/close verified successfully!", flush=True)

        # 9. 8대 KPI 카드 info 툴팁 title 속성 검증
        print("10. Verifying KPI tooltips...", flush=True)
        kpi_info_icons = target_frame.locator("#view-analytics .cursor-help")
        info_count = kpi_info_icons.count()
        assert info_count >= 8, f"Should have at least 8 KPI info icons, found {info_count}"
        first_title = kpi_info_icons.first.get_attribute("title")
        assert first_title and len(first_title) > 10, f"KPI info should have informative tooltip title: {first_title}"
        print(f"Verified KPI Tooltip Sample: {first_title[:45]}...", flush=True)

        # 최종 리포트 전체 스크린샷 캡처
        final_screenshot = os.path.join(artifact_dir, "report_interactive_buttons_verified.png")
        page.screenshot(path=final_screenshot, full_page=True)
        print(f"Final report verified screenshot saved to {final_screenshot}", flush=True)

        browser.close()
        print("All Report Interactive Buttons and Features Passed Successfully!", flush=True)

if __name__ == "__main__":
    test_e2e_features()
