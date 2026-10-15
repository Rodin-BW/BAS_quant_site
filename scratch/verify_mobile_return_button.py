import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

ARTIFACT_DIR = Path("C:/Users/jbw06/.gemini/antigravity/brain/695d1c44-09fb-4b39-b4e6-b9c370839614")

def verify_mobile_return_to_builder():
    html_path = Path("design/integrated_app.html").resolve()
    file_url = f"file:///{html_path.as_posix()}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 모바일 뷰포트 (iPhone 14 / 갤럭시급: 390x844)
        page = browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        page.goto(file_url)
        page.wait_for_load_state("networkidle")

        # 1. 빌더 상단 모바일 네비게이션 캡처
        page.screenshot(path=str(ARTIFACT_DIR / "mobile_top_nav_builder.png"))
        print("[SCREENSHOT] Saved mobile_top_nav_builder.png")

        # 2. 백테스트 실행
        run_btn = page.locator("#btn-run-simulation")
        run_btn.scroll_into_view_if_needed()
        page.wait_for_timeout(200)
        run_btn.click()
        page.wait_for_selector("#view-analytics:not(.hidden)", timeout=15000)
        page.wait_for_timeout(1000)

        # 3. 리포트 상단 캡처 (모바일 헤더 탭 상태 확인)
        page.screenshot(path=str(ARTIFACT_DIR / "mobile_report_header_nav.png"))
        print("[SCREENSHOT] Saved mobile_report_header_nav.png")

        # 4. 리포트 맨 밑으로 스크롤하여 "전략 설정으로 돌아가기" CTA 카드 확인 및 캡처
        bottom_card = page.locator("#bottom-return-builder-card")
        bottom_card.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        page.screenshot(path=str(ARTIFACT_DIR / "mobile_report_bottom_return_card.png"))
        print("[SCREENSHOT] Saved mobile_report_bottom_return_card.png")

        # 5. 하단 "전략 설정으로 돌아가기" 버튼 클릭
        return_btn = page.locator("#btn-bottom-return-builder")
        return_btn.click()
        page.wait_for_timeout(500)

        # 6. 빌더 화면으로 성공적으로 복귀했는지 캡처
        page.screenshot(path=str(ARTIFACT_DIR / "mobile_returned_to_builder.png"))
        print("[SCREENSHOT] Saved mobile_returned_to_builder.png")

        browser.close()

if __name__ == '__main__':
    verify_mobile_return_to_builder()
