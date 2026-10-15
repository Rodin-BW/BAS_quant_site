import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

ARTIFACT_DIR = Path("C:/Users/jbw06/.gemini/antigravity/brain/695d1c44-09fb-4b39-b4e6-b9c370839614")

def verify_attribution_suite():
    html_path = Path("design/integrated_app.html").resolve()
    file_url = f"file:///{html_path.as_posix()}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.goto(file_url)
        page.wait_for_load_state("networkidle")

        # 1. 정적 모드 백테스트 실행
        run_btn = page.locator("#btn-run-simulation")
        run_btn.click()
        page.wait_for_selector("#view-analytics:not(.hidden)", timeout=15000)
        page.wait_for_timeout(1000)

        # Attribution 섹션으로 스크롤
        attr_sec = page.locator("#attribution-section")
        attr_sec.scroll_into_view_if_needed()
        page.wait_for_timeout(300)

        # Tab 1: 전체 누적 수익 기여도 캡처
        page.screenshot(path=str(ARTIFACT_DIR / "attr_tab_return.png"))
        print("[SCREENSHOT] Saved attr_tab_return.png")

        # Tab 2: 최대 낙폭(MDD) 손실 기여도 캡처
        page.click("#attr-tab-mdd")
        page.wait_for_timeout(300)
        attr_sec.screenshot(path=str(ARTIFACT_DIR / "attr_tab_mdd.png"))
        print("[SCREENSHOT] Saved attr_tab_mdd.png")

        # Tab 3: 2022년 금리인상기 손익 기여도 캡처
        page.click("#attr-tab-2022")
        page.wait_for_timeout(300)
        attr_sec.screenshot(path=str(ARTIFACT_DIR / "attr_tab_2022.png"))
        print("[SCREENSHOT] Saved attr_tab_2022.png")

        # Tab 4: 벤치마크 브릿지 & 알파 워터폴 캡처 (기본 SPY)
        page.click("#attr-tab-factor")
        page.wait_for_timeout(400)
        attr_sec.screenshot(path=str(ARTIFACT_DIR / "attr_tab_factor_spy.png"))
        print("[SCREENSHOT] Saved attr_tab_factor_spy.png")

        # 벤치마크를 QQQ(나스닥 100)로 변경 후 다시 캡처
        page.select_option("#attr-benchmark-select", "QQQ")
        page.wait_for_timeout(400)
        attr_sec.screenshot(path=str(ARTIFACT_DIR / "attr_tab_factor_qqq.png"))
        print("[SCREENSHOT] Saved attr_tab_factor_qqq.png")

        # 모바일 환경에서도 확인
        mobile_page = browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        mobile_page.goto(file_url)
        mobile_page.wait_for_load_state("networkidle")
        mobile_page.click("#btn-run-simulation")
        mobile_page.wait_for_selector("#view-analytics:not(.hidden)", timeout=15000)
        mobile_page.wait_for_timeout(1000)
        m_attr = mobile_page.locator("#attribution-section")
        m_attr.scroll_into_view_if_needed()
        mobile_page.wait_for_timeout(300)
        m_attr.screenshot(path=str(ARTIFACT_DIR / "mobile_attr_suite.png"))
        print("[SCREENSHOT] Saved mobile_attr_suite.png")

        browser.close()

if __name__ == '__main__':
    verify_attribution_suite()
