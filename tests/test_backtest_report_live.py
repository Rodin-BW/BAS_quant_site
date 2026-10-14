import asyncio
import re
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
        context = await browser.new_context(viewport={"width": 1440, "height": 1800})
        page = await context.new_page()

        print("[TEST] 1. Streamlit 웹 페이지 접속 중...")
        await page.goto("http://localhost:8501", timeout=45000, wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # iframe 찾기
        frame_el = await page.wait_for_selector("iframe", timeout=15000)
        frame = await frame_el.content_frame()
        assert frame is not None, "iframe content_frame을 찾을 수 없습니다."
        print("[TEST] 2. 메인 iframe 로드 완료.")

        # 시작/종료일자 설정 (2020-01-01 ~ 2023-01-01 빠른 실데이터 백테스트)
        await frame.fill("#sim-start-date", "2020-01-01")
        await frame.fill("#sim-end-date", "2023-01-01")
        print("[TEST] 3. 백테스트 기간 설정 완료: 2020-01-01 ~ 2023-01-01")

        # 정적 자산배분 시뮬레이션 실행 버튼 클릭
        run_btn = frame.locator("#btn-run-simulation")
        await run_btn.click()
        print("[TEST] 4. 정적 자산배분 시뮬레이션 실행 버튼 클릭 (yfinance API 실시간 연산 요청 중)...")

        # 분석 탭 노출 대기 (네트워크 및 연산 대기)
        await frame.wait_for_selector("#view-analytics:not(.hidden)", timeout=35000)
        await page.wait_for_timeout(2000)
        print("[TEST] 5. 분석 리포트 화면 view-analytics 렌더링 완료!")

        # 6. KPI 지표 검증
        cagr_text = await frame.locator("#kpi-cagr").text_content()
        mdd_text = await frame.locator("#kpi-mdd").text_content()
        sharpe_text = await frame.locator("#kpi-sharpe").text_content()
        final_wealth = await frame.locator("#kpi-final-wealth").text_content()
        div_yield = await frame.locator("#report-div-yield").text_content()

        print(f"[TEST] 6. KPI 확인: CAGR={cagr_text}, MDD={mdd_text}, Sharpe={sharpe_text}, Wealth={final_wealth}, DivYield={div_yield}")
        assert cagr_text and "%" in cagr_text, f"CAGR 지표 비정상: {cagr_text}"
        assert mdd_text and "%" in mdd_text, f"MDD 지표 비정상: {mdd_text}"
        assert "₩" in final_wealth, f"최종 평가액 비정상: {final_wealth}"
        assert "연" in div_yield and "%" in div_yield, f"배당수익률 비정상: {div_yield}"

        # 7. 월간 수익률 매트릭스 테이블 검증
        monthly_rows = await frame.locator("#monthly-returns-tbody tr").count()
        print(f"[TEST] 7. 월간 수익률 매트릭스 행 개수: {monthly_rows}")
        assert monthly_rows >= 3, f"월간 수익률 매트릭스 행 부족: {monthly_rows}"

        first_row_text = await frame.locator("#monthly-returns-tbody tr").first.inner_text()
        print(f"[TEST] 7.1 월간 수익률 첫 행 샘플: {first_row_text}")
        assert re.search(r"[+-]\d+\.\d+", first_row_text), "월간 수익률에 실제 수치가 렌더링되지 않았습니다!"

        # 8. 최근 리밸런싱 실행 로그 테이블 검증
        rebalance_rows = await frame.locator("#rebalance-log-tbody tr").count()
        print(f"[TEST] 8. 최근 리밸런싱 로그 행 개수: {rebalance_rows}")
        assert rebalance_rows >= 4, f"리밸런싱 로그 행 부족: {rebalance_rows}"

        # 9. 메인 차트 인터랙티브 호버 검증
        hover_area = frame.locator("#chart-hover-area")
        await hover_area.hover(position={"x": 500, "y": 100})
        await page.wait_for_timeout(1000)

        tooltip = frame.locator("#chart-interactive-tooltip")
        is_visible = await tooltip.is_visible()
        date_header = await frame.locator("#tooltip-date-header").text_content()
        bas_val = await frame.locator("#tooltip-bas-val").text_content()
        bench_val = await frame.locator("#tooltip-bench-val").text_content()
        print(f"[TEST] 9. 차트 호버 툴팁 검증: Visible={is_visible}, Date={date_header}, BAS={bas_val}, SPY={bench_val}")
        assert is_visible, "차트 호버 툴팁이 표시되지 않습니다."
        assert "실시간 퀀트 백테스트 추적" in date_header or "CRASH" in date_header or "TIGHTENING" in date_header, f"호버 날짜 헤더 이상: {date_header}"
        assert "BAS:" in bas_val and "%" in bas_val, f"호버 BAS 수익률 이상: {bas_val}"

        # 10. 스크린샷 캡처 1: 정적 자산배분 실시간 백테스트 리포트
        artifact_dir = Path("C:/Users/jbw06/.gemini/antigravity/brain/695d1c44-09fb-4b39-b4e6-b9c370839614")
        shot1 = artifact_dir / "static_backtest_live_report_verified.png"
        await page.screenshot(path=str(shot1), full_page=True)
        print(f"[TEST] 10. 정적 백테스트 리포트 스크린샷 저장 완료: {shot1}")

        # 11. 트라이포드 모드 전환 후 시뮬레이션 실행 검증
        print("[TEST] 11. 트라이포드 모드 전환 중...")
        nav_studio = frame.locator("#nav-btn-builder")
        await nav_studio.click()
        await page.wait_for_timeout(1000)

        tripod_tab = frame.locator("#mode-tripod")
        await tripod_tab.click()
        await page.wait_for_timeout(1000)

        run_btn2 = frame.locator("#btn-run-simulation")
        await run_btn2.click()
        print("[TEST] 12. 트라이포드 시뮬레이션 실행 버튼 클릭...")

        await frame.wait_for_selector("#view-analytics:not(.hidden)", timeout=35000)
        await page.wait_for_timeout(2000)

        tripod_banner = await frame.locator("#view-analytics h1").text_content()
        tripod_cagr = await frame.locator("#kpi-cagr").text_content()
        tripod_mdd = await frame.locator("#kpi-mdd").text_content()
        print(f"[TEST] 13. 트라이포드 리포트 결과: 배너={tripod_banner}, CAGR={tripod_cagr}, MDD={tripod_mdd}")
        assert "트라이포드" in tripod_banner, f"트라이포드 배너 제목 이상: {tripod_banner}"
        assert tripod_cagr and "%" in tripod_cagr, f"트라이포드 CAGR 이상: {tripod_cagr}"

        # 14. 스크린샷 캡처 2: 트라이포드 실시간 백테스트 리포트
        shot2 = artifact_dir / "tripod_backtest_live_report_verified.png"
        await page.screenshot(path=str(shot2), full_page=True)
        print(f"[TEST] 14. 트라이포드 백테스트 리포트 스크린샷 저장 완료: {shot2}")

        await browser.close()
        print("\n✅ [SUCCESS] 백테스팅 리포트 전체 실시간 엔진 검증 100% 통과!")

if __name__ == "__main__":
    asyncio.run(run())
