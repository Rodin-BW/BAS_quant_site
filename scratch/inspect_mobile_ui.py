import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

ARTIFACT_DIR = Path("C:/Users/jbw06/.gemini/antigravity/brain/695d1c44-09fb-4b39-b4e6-b9c370839614")

def capture_mobile_full():
    html_path = Path("design/integrated_app.html").resolve()
    file_url = f"file:///{html_path.as_posix()}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        page.goto(file_url)
        page.wait_for_load_state("networkidle")

        # 0. 빌더 최상단 캡처 (헤더 겹침 및 세그먼트 버튼 확인)
        page.screenshot(path=str(ARTIFACT_DIR / "mobile_builder_top.png"))
        print("[SCREENSHOT] Saved mobile_builder_top.png")

        # 1. 동적 자산배분 패널로 전환 및 스크롤
        page.click("#mode-dynamic")
        page.wait_for_timeout(300)
        
        # 동적 패널 위치로 스크롤
        dyn_panel = page.locator("#dynamic-panel")
        dyn_panel.scroll_into_view_if_needed()
        page.wait_for_timeout(200)
        page.screenshot(path=str(ARTIFACT_DIR / "mobile_dynamic_panel_scrolled.png"))
        print("[SCREENSHOT] Saved mobile_dynamic_panel_scrolled.png")

        # 2. 백테스트 실행 버튼 위치로 스크롤
        run_btn = page.locator("#btn-run-simulation")
        run_btn.scroll_into_view_if_needed()
        page.wait_for_timeout(200)
        page.screenshot(path=str(ARTIFACT_DIR / "mobile_run_button_scrolled.png"))
        print("[SCREENSHOT] Saved mobile_run_button_scrolled.png")

        # 3. 백테스트 실행 (클릭)
        run_btn.click()
        page.wait_for_selector("#view-analytics:not(.hidden)", timeout=15000)
        page.wait_for_timeout(1000)
        
        # 리포트 상단
        page.screenshot(path=str(ARTIFACT_DIR / "mobile_report_top.png"))
        print("[SCREENSHOT] Saved mobile_report_top.png")

        # 리포트 차트
        page.locator("#main-chart-card").scroll_into_view_if_needed()
        page.wait_for_timeout(200)
        page.screenshot(path=str(ARTIFACT_DIR / "mobile_report_chart.png"))
        print("[SCREENSHOT] Saved mobile_report_chart.png")

        # 리포트 테이블 (히트맵, 리밸런싱 로그)
        page.locator("#monthly-heatmap-desc").scroll_into_view_if_needed()
        page.evaluate("window.scrollBy(0, 80)")
        page.wait_for_timeout(200)
        page.screenshot(path=str(ARTIFACT_DIR / "mobile_report_tables.png"))
        print("[SCREENSHOT] Saved mobile_report_tables.png")

        browser.close()

if __name__ == '__main__':
    capture_mobile_full()
