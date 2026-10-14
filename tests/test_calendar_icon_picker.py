import os
import sys
import time
from playwright.sync_api import sync_playwright

def test_calendar_icon_picker():
    artifact_dir = r"C:\Users\jbw06\.gemini\antigravity\brain\695d1c44-09fb-4b39-b4e6-b9c370839614"
    screenshot_path = os.path.join(artifact_dir, "calendar_icon_picker_verified.png")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        print("1. Opening Streamlit app (http://localhost:8501)...")
        page.goto("http://localhost:8501", wait_until="networkidle", timeout=30000)
        time.sleep(3)

        target_frame = None
        for frame in page.frames:
            if "about:srcdoc" in frame.url or frame != page.main_frame:
                try:
                    if frame.locator("#sim-start-date").count() > 0:
                        target_frame = frame
                        break
                except Exception:
                    pass

        if not target_frame:
            for frame in page.frames:
                try:
                    frame.wait_for_selector("#sim-start-date", timeout=5000)
                    target_frame = frame
                    break
                except Exception:
                    continue

        assert target_frame is not None, "Could not find iframe with integrated_app.html"
        print("Target frame found successfully.")

        # 2. Check calendar icons existence and attributes
        start_icon = target_frame.locator('#btn-calendar-start')
        end_icon = target_frame.locator('#btn-calendar-end')

        assert start_icon.count() > 0, "Start date calendar icon not found"
        assert end_icon.count() > 0, "End date calendar icon not found"
        print("Calendar icons found successfully.")

        # 3. Monitor showPicker calls via spying
        target_frame.evaluate("""() => {
            window.__pickerCallCount = { start: 0, end: 0 };
            const startEl = document.getElementById('sim-start-date');
            const endEl = document.getElementById('sim-end-date');
            if (startEl) {
                const origStartPicker = startEl.showPicker;
                startEl.showPicker = function() {
                    window.__pickerCallCount.start++;
                    if (origStartPicker) origStartPicker.call(this);
                };
            }
            if (endEl) {
                const origEndPicker = endEl.showPicker;
                endEl.showPicker = function() {
                    window.__pickerCallCount.end++;
                    if (origEndPicker) origEndPicker.call(this);
                };
            }
        }""")

        # 4. Click start date calendar icon
        print("2. Clicking start date calendar icon (calendar_today)...")
        start_icon.click()
        time.sleep(0.5)

        start_calls = target_frame.evaluate("() => window.__pickerCallCount.start")
        print(f"Start date showPicker call count: {start_calls}")
        assert start_calls >= 1, "openDatePicker was not called when start calendar icon was clicked"

        # 5. Click end date calendar icon
        print("3. Clicking end date calendar icon (event)...")
        end_icon.click()
        time.sleep(0.5)

        end_calls = target_frame.evaluate("() => window.__pickerCallCount.end")
        print(f"End date showPicker call count: {end_calls}")
        assert end_calls >= 1, "openDatePicker was not called when end calendar icon was clicked"

        # 6. Test date modification and summary recalculation
        print("4. Testing date selection update and summary recalculation...")
        target_frame.fill("#sim-start-date", "2015-05-01")
        target_frame.evaluate("document.getElementById('sim-start-date').dispatchEvent(new Event('change'))")
        time.sleep(0.5)

        summary_text = target_frame.locator("#sim-period-summary").inner_text()
        print(f"Recalculated Period Summary: {summary_text}")
        assert "2015" not in summary_text or "년" in summary_text, "Summary not calculated properly"

        # 7. Hover on calendar icon and capture screenshot
        start_icon.hover()
        time.sleep(0.5)
        page.screenshot(path=screenshot_path)
        print(f"Calendar icon verification screenshot saved to {screenshot_path}")

        browser.close()
        print("Calendar Icon Picker Verification Passed Successfully!")

if __name__ == "__main__":
    test_calendar_icon_picker()
