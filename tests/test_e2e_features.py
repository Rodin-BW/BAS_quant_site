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
        
        screenshot_path = os.path.join(artifact_dir, "recent_date_yfinance_verified.png")
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"Verified screenshot saved to {screenshot_path}", flush=True)
        
        browser.close()
        print("All Recent Date & yfinance Verification Passed Successfully!", flush=True)

if __name__ == "__main__":
    test_e2e_features()
