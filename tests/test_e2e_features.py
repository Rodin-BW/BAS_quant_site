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

        # =========================================================================
        # [신규 검증] 없는 종목 필터링 및 유효 종목 실시간 추가 검증
        # =========================================================================
        print("2.1 Testing non-existent ticker filtering...", flush=True)
        dialog_messages = []
        page.on("dialog", lambda dialog: (dialog_messages.append(dialog.message), dialog.accept()))

        search_input = target_frame.locator("#ticker-search-input")
        add_btn = target_frame.locator("#btn-add-asset")
        error_box = target_frame.locator("#ticker-error-box")
        error_msg = target_frame.locator("#ticker-error-msg")

        # 1) 없는 종목 입력 후 추가 시도
        search_input.fill("INVALID_TICKER_999")
        add_btn.dispatch_event("click")
        time.sleep(2)

        # 에러 박스 또는 다이얼로그 경고 메시지가 발생했는지 확인
        error_text = error_msg.text_content().strip() if error_msg.count() > 0 else ""
        print(f"Captured Error Banner Text: '{error_text}' | Dialogs: {dialog_messages}", flush=True)
        assert "존재하지 않거나" in error_text or any("존재하지 않는 종목" in msg or "유효하지 않은" in msg for msg in dialog_messages), "Non-existent ticker should trigger warning alert or error banner"

        # 자산 목록에 INVALID_TICKER_999가 절대 추가되지 않았는지 확인
        asset_list_text = target_frame.locator("#asset-list-container").text_content()
        assert "INVALID_TICKER_999" not in asset_list_text, "Invalid ticker must NOT be added to portfolio"
        print("Non-existent ticker successfully filtered out!", flush=True)

        # 2) 실제 존재하는 종목(NVDA) 입력 후 추가 시도
        print("2.2 Testing valid live ticker addition (NVDA)...", flush=True)
        search_input.fill("NVDA")
        add_btn.dispatch_event("click")
        time.sleep(2.5)

        asset_list_text_after = target_frame.locator("#asset-list-container").text_content()
        assert "NVDA" in asset_list_text_after, "Valid ticker NVDA should be added to portfolio"
        print("Valid ticker (NVDA) successfully verified and added to portfolio!", flush=True)

        # 종목 필터링 및 추가 검증 스크린샷 저장
        ticker_filter_screenshot = os.path.join(artifact_dir, "ticker_filter_and_valid_add_verified.png")
        page.screenshot(path=ticker_filter_screenshot, full_page=True)
        print(f"Ticker filter verification screenshot saved to {ticker_filter_screenshot}", flush=True)

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

        # =========================================================================
        # 10. 트라이포드 전략 종목 선택 및 파라미터 세부 튜닝 검증
        # =========================================================================
        print("11. Testing Tripod Strategy Mode and Custom Assets...", flush=True)
        # 상단 네비게이션을 통해 Builder View로 복귀
        target_frame.evaluate("window.scrollTo(0, 0)")
        nav_builder = target_frame.locator("#nav-btn-builder")
        nav_builder.dispatch_event("click")
        time.sleep(1)

        # 트라이포드 모드 탭 전환
        btn_mode_tripod = target_frame.locator("#mode-tripod")
        btn_mode_tripod.dispatch_event("click")
        time.sleep(1)

        # 단일 뷰 검증: static 패널은 hidden이고 tripod 패널이 보여야 함
        static_panel = target_frame.locator("#static-panel")
        tripod_panel = target_frame.locator("#tripod-panel")
        assert "hidden" in static_panel.get_attribute("class"), "Static panel should be hidden in tripod mode"
        assert "hidden" not in tripod_panel.get_attribute("class"), "Tripod panel should be visible in tripod mode"
        print("Tripod single view mode verified successfully!", flush=True)

        # 10.1 트라이포드 프리셋 버튼 테스트 (반도체 프리셋 클릭)
        print("12. Testing Tripod Archetype Preset (Semiconductor)...", flush=True)
        btn_semicon = tripod_panel.locator("button:has-text('반도체')")
        btn_semicon.dispatch_event("click")
        time.sleep(0.5)

        val_core = target_frame.locator("#tripod-asset-core").input_value()
        val_panic = target_frame.locator("#tripod-asset-panic").input_value()
        val_base = target_frame.locator("#tripod-asset-base").input_value()
        print(f"Semicon Preset Values -> Core: {val_core}, Panic: {val_panic}, Base: {val_base}", flush=True)
        assert val_core == "USD", f"Core should be USD, got {val_core}"
        assert val_panic == "SOXL", f"Panic should be SOXL, got {val_panic}"
        assert val_base == "SOXX", f"Base should be SOXX, got {val_base}"

        # 10.2 트라이포드 4대 슬롯 드롭다운 선택상자 테스트
        print("13. Testing Tripod Asset Slot Select Dropdowns...", flush=True)
        sel_buffer = target_frame.locator("#tripod-select-buffer")
        sel_core = target_frame.locator("#tripod-select-core")
        sel_panic = target_frame.locator("#tripod-select-panic")

        sel_buffer.select_option("SGOV")
        sel_core.select_option("QLD")
        sel_panic.select_option("TQQQ")
        time.sleep(0.5)

        assert target_frame.locator("#tripod-asset-buffer").input_value() == "SGOV", "Buffer input should sync to SGOV"
        assert target_frame.locator("#tripod-asset-core").input_value() == "QLD", "Core input should sync to QLD"
        assert target_frame.locator("#tripod-asset-panic").input_value() == "TQQQ", "Panic input should sync to TQQQ"
        print("Tripod asset slot dropdown sync verified successfully!", flush=True)

        # 10.2-1 트라이포드 직접 입력 슬롯에 없는 종목 입력 시 필터링 검증
        print("13.1 Testing invalid ticker filtering on Tripod custom input...", flush=True)
        core_input = target_frame.locator("#tripod-asset-core")
        core_input.fill("INVALID_CORE_999")
        core_input.dispatch_event("change")
        time.sleep(1.5)
        val_after_invalid = core_input.input_value()
        print(f"Core value after invalid input attempt: {val_after_invalid}", flush=True)
        assert val_after_invalid == "QLD", f"Invalid core ticker should be rolled back to QLD: got {val_after_invalid}"
        print("Tripod custom slot invalid ticker successfully filtered and rolled back!", flush=True)

        # 10.3 트라이포드 파라미터 세부 튜닝 모달 오픈 및 값 변경
        print("14. Testing Tripod Parameter Tuning Modal...", flush=True)
        btn_open_tune = target_frame.locator("#btn-open-tripod-tune-modal")
        tune_modal = target_frame.locator("#tripod-tune-modal")
        assert "hidden" in tune_modal.get_attribute("class"), "Tune modal should be hidden initially"

        btn_open_tune.dispatch_event("click")
        time.sleep(0.5)
        assert "hidden" not in tune_modal.get_attribute("class"), "Tune modal should be visible after clicking open"
        print("Tripod tune modal opened successfully!", flush=True)

        # 모달 열린 상태 스크린샷 캡처
        modal_tune_screenshot = os.path.join(artifact_dir, "tripod_tune_modal_opened.png")
        page.screenshot(path=modal_tune_screenshot, full_page=True)
        print(f"Tune modal screenshot saved to {modal_tune_screenshot}", flush=True)

        # 파라미터 값 변경 (VIX 28.0 -> 32.0, 낙폭 사다리 -12% / -22% / -32%, RSI 30 -> 25)
        input_vix = target_frame.locator("#tune-vix")
        input_l1_drop = target_frame.locator("#tune-ladder1-drop")
        input_l2_drop = target_frame.locator("#tune-ladder2-drop")
        input_l3_drop = target_frame.locator("#tune-ladder3-drop")
        input_rsi_panic = target_frame.locator("#tune-rsi-panic")

        input_vix.fill("32.0")
        input_l1_drop.fill("-12")
        input_l2_drop.fill("-22")
        input_l3_drop.fill("-32")
        input_rsi_panic.fill("25")
        time.sleep(0.5)

        # 파라미터 저장 및 적용 클릭
        btn_save_params = target_frame.locator("#btn-save-tripod-params")
        btn_save_params.dispatch_event("click")
        time.sleep(0.5)
        assert "hidden" in tune_modal.get_attribute("class"), "Tune modal should close after save"
        print("Tripod tune modal saved and closed successfully!", flush=True)

        # 10.4 3대 축 카드 UI에 실시간 변경된 파라미터 반영 검증
        print("15. Verifying dynamic Tripod 3-Axis cards UI updates...", flush=True)
        card_vix_text = target_frame.locator("#tripod-card-vix").text_content().strip()
        card_drops_text = target_frame.locator("#tripod-card-drops").text_content().strip()
        card_rsi_val_text = target_frame.locator("#tripod-card-rsi-val").text_content().strip()
        card_rsi_text = target_frame.locator("#tripod-card-rsi").text_content().strip()

        print(f"Updated Tripod Cards -> VIX: {card_vix_text}, Drops: {card_drops_text}, RSI: {card_rsi_text}", flush=True)
        assert card_vix_text == "32.0", f"Card VIX should be updated to 32.0: got {card_vix_text}"
        assert card_drops_text == "-12% / -22% / -32%", f"Card Drops should be -12% / -22% / -32%: got {card_drops_text}"
        assert card_rsi_val_text == "25.0", f"Card RSI val should be 25.0: got {card_rsi_val_text}"
        assert "< 25.0" in card_rsi_text, f"Card RSI text should contain < 25.0: got {card_rsi_text}"

        # 트라이포드 세부 튜닝 완료 화면 스크린샷 캡처
        tripod_verified_screenshot = os.path.join(artifact_dir, "tripod_param_tuning_verified.png")
        page.screenshot(path=tripod_verified_screenshot, full_page=True)
        print(f"Tripod verified screenshot saved to {tripod_verified_screenshot}", flush=True)

        # 10.5 트라이포드 시뮬레이션 실행 및 리포트 검증
        print("16. Running Tripod simulation with tuned parameters...", flush=True)
        target_frame.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        run_btn = target_frame.locator("#btn-run-simulation")
        run_btn.dispatch_event("click")
        target_frame.locator("#kpi-cagr").wait_for(state="visible", timeout=35000)
        time.sleep(2)

        tripod_cagr = target_frame.locator("#kpi-cagr").text_content().strip()
        tripod_mdd = target_frame.locator("#kpi-mdd").text_content().strip()
        print(f"Tripod Simulation Result -> CAGR: {tripod_cagr}, MDD: {tripod_mdd}", flush=True)
        assert tripod_cagr != "" and "%" in tripod_cagr, f"Tripod CAGR should be rendered: {tripod_cagr}"

        browser.close()
        print("All Report Interactive Buttons, Tripod Dropdowns, and Parameter Tuning Features Passed Successfully!", flush=True)

if __name__ == "__main__":
    test_e2e_features()
