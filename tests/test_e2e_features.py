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
        
        # iframe이 로드될 때까지 대기
        page.wait_for_selector("iframe", timeout=30000)
        time.sleep(2)
        
        # 자식 iframe 중 우리 앱 컨텐츠를 가진 프레임 탐색
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
            # fallback
            target_frame = page.frames[1] if len(page.frames) > 1 else page.main_frame

        print(f"Target frame found: {target_frame.url}", flush=True)

        # 1. 1/N 버튼 확인 및 클릭
        print("2. Testing 1/N equal weight button...", flush=True)
        btn_equal = target_frame.locator("#btn-equal-weight")
        btn_equal.wait_for(state="visible", timeout=15000)
        btn_equal.click()
        time.sleep(1)
        
        # 합계 100% 확인
        total_badge = target_frame.locator("#total-weight-pill").text_content()
        print(f"Total weight pill after 1/N: {total_badge.strip()}", flush=True)
        assert "100.0%" in total_badge
        
        # 2. 날짜 피커 확인
        print("3. Checking date picker range...", flush=True)
        end_date_input = target_frame.locator("#sim-end-date")
        max_attr = end_date_input.get_attribute("max")
        val_attr = end_date_input.input_value()
        print(f"End date value: {val_attr}, max: {max_attr}", flush=True)
        assert max_attr and int(max_attr[:4]) >= 2026, f"Max date is not 2026+: {max_attr}"
        
        # 3. 백테스트 실행 버튼 클릭
        print("4. Clicking Run Simulation button...", flush=True)
        run_btn = target_frame.locator("#btn-run-simulation")
        run_btn.click()
        
        # 4. 백테스트 결과 및 배당 지표 대기
        print("5. Waiting for backtest results with dividend yield...", flush=True)
        target_frame.locator("#kpi-cagr").wait_for(state="visible", timeout=35000)
        time.sleep(2)
        
        cagr_text = target_frame.locator("#kpi-cagr").text_content().strip()
        div_yield_text = target_frame.locator("#report-div-yield").text_content().strip()
        cum_div_text = target_frame.locator("#report-cum-div").text_content().strip()
        mdd_text = target_frame.locator("#kpi-mdd").text_content().strip()
        final_wealth = target_frame.locator("#kpi-final-wealth").text_content().strip()
        
        print("=== E2E HARNESS VERIFICATION REPORT ===", flush=True)
        print(f"CAGR: {cagr_text}", flush=True)
        print(f"Portfolio Dividend Yield: {div_yield_text}", flush=True)
        print(f"Cumulative Dividends: {cum_div_text}", flush=True)
        print(f"MDD: {mdd_text}", flush=True)
        print(f"Final Wealth: {final_wealth}", flush=True)
        
        assert div_yield_text != "-" and "%" in div_yield_text, f"Invalid dividend yield: {div_yield_text}"
        assert cum_div_text != "-" and "₩" in cum_div_text, f"Invalid cumulative dividends: {cum_div_text}"
        
        # 리포트 스크롤 및 전체화면 스크린샷 캡처
        screenshot_path = os.path.join(artifact_dir, "e2e_features_verified.png")
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"Verified screenshot saved to {screenshot_path}", flush=True)
        
        browser.close()
        print("E2E Test Passed Successfully!", flush=True)

if __name__ == "__main__":
    test_e2e_features()
