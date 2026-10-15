import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

ARTIFACT_DIR = Path("C:/Users/jbw06/.gemini/antigravity/brain/695d1c44-09fb-4b39-b4e6-b9c370839614")

def verify_daily_bars_chart():
    html_path = Path("design/integrated_app.html").resolve()
    file_url = f"file:///{html_path.as_posix()}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 1. 데스크탑 뷰포트
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.goto(file_url)
        page.wait_for_load_state("networkidle")

        # 동적 자산배분 선택 후 백테스트 실행
        page.click("#mode-dynamic")
        page.wait_for_timeout(200)
        page.click("#btn-run-simulation")
        page.wait_for_selector("#view-analytics:not(.hidden)", timeout=15000)
        page.wait_for_timeout(1000)

        # 차트 카드 스크롤
        chart_card = page.locator("#main-chart-card")
        chart_card.scroll_into_view_if_needed()
        page.wait_for_timeout(300)

        # 1. 데스크탑 일봉 차트 캡처
        chart_card.screenshot(path=str(ARTIFACT_DIR / "daily_bars_desktop_chart.png"))
        print("[SCREENSHOT] Saved daily_bars_desktop_chart.png")

        # 2. 차트 마우스 호버 (일봉 툴팁 검증)
        hover_area = page.locator("#chart-hover-area")
        box = hover_area.bounding_box()
        if box:
            page.mouse.move(box["x"] + box["width"] * 0.7, box["y"] + box["height"] * 0.4)
            page.wait_for_timeout(400)
            chart_card.screenshot(path=str(ARTIFACT_DIR / "daily_bars_hover_tooltip.png"))
            print("[SCREENSHOT] Saved daily_bars_hover_tooltip.png")

        # 3. 트라이포드 모드에서도 백테스트 돌려서 차트 캡처
        page.click("#nav-builder-tab")
        page.wait_for_timeout(300)
        page.click("#mode-tripod")
        page.wait_for_timeout(200)
        page.click("#btn-run-simulation")
        page.wait_for_selector("#view-analytics:not(.hidden)", timeout=15000)
        page.wait_for_timeout(1000)
        chart_card.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        chart_card.screenshot(path=str(ARTIFACT_DIR / "daily_bars_tripod_chart.png"))
        print("[SCREENSHOT] Saved daily_bars_tripod_chart.png")

        # 4. 모바일 뷰포트에서도 차트 캡처
        mobile_page = browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        mobile_page.goto(file_url)
        mobile_page.wait_for_load_state("networkidle")
        mobile_page.click("#mode-dynamic")
        mobile_page.wait_for_timeout(200)
        mobile_page.click("#btn-run-simulation")
        mobile_page.wait_for_selector("#view-analytics:not(.hidden)", timeout=15000)
        mobile_page.wait_for_timeout(1000)
        mobile_chart = mobile_page.locator("#main-chart-card")
        mobile_chart.scroll_into_view_if_needed()
        mobile_page.wait_for_timeout(300)
        mobile_chart.screenshot(path=str(ARTIFACT_DIR / "mobile_daily_bars_chart.png"))
        print("[SCREENSHOT] Saved mobile_daily_bars_chart.png")

        browser.close()

if __name__ == '__main__':
    verify_daily_bars_chart()
