import os
import sys
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def test_daily_bars_chart():
    artifact_dir = r"C:\Users\jbw06\.gemini\antigravity\brain\695d1c44-09fb-4b39-b4e6-b9c370839614"
    screenshot_path = os.path.join(artifact_dir, "daily_bars_chart_verified.png")

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
                    if frame.locator("#btn-run-simulation").count() > 0:
                        target_frame = frame
                        break
                except Exception:
                    pass

        assert target_frame is not None, "Target frame not found"
        print("Target frame located successfully.")

        # 2. Click Run Simulation
        print("2. Running backtest simulation with live yfinance data...")
        target_frame.locator("#btn-run-simulation").click()

        # 3. Wait for analytics view and KPI results
        target_frame.locator("#kpi-cagr").wait_for(state="visible", timeout=35000)
        time.sleep(2)

        # 4. Verify Daily Bars curveData in state
        curve_info = target_frame.evaluate("""() => {
            const res = window.state.lastResult;
            const curve = res ? res.curveData : [];
            const rendered = window.state.activeRenderedPoints || [];
            const pathD = document.getElementById('curve-bas-line')?.getAttribute('d') || '';
            const resText = document.getElementById('chart-resolution-text')?.textContent || '';
            return {
                tradingDays: res ? res.tradingDays : 0,
                curveLen: curve ? curve.length : 0,
                renderedLen: rendered.length,
                pathLength: pathD.length,
                resolutionText: resText,
                sampleFirst: curve && curve.length > 0 ? curve[0] : null,
                sampleLast: curve && curve.length > 0 ? curve[curve.length - 1] : null
            };
        }""")

        print(f"Trading Days: {curve_info['tradingDays']}")
        print(f"CurveData Points Count (Daily Bars): {curve_info['curveLen']}")
        print(f"Rendered Daily Points Count: {curve_info['renderedLen']}")
        print(f"SVG Path String Length: {curve_info['pathLength']} chars")
        print(f"Resolution Text: {curve_info['resolutionText']}")
        print(f"First Bar: {curve_info['sampleFirst']}")
        print(f"Last Bar: {curve_info['sampleLast']}")

        assert curve_info['curveLen'] >= 2000, f"Expected thousands of daily bars, got {curve_info['curveLen']}"
        assert curve_info['curveLen'] == curve_info['tradingDays'], "Curve data points should match trading days 1:1"
        assert "일봉 기준 (Daily Bars)" in curve_info['resolutionText'], f"Resolution text mismatch: {curve_info['resolutionText']}"
        assert curve_info['pathLength'] > 5000, "SVG path should contain high-density daily points"

        # 5. Test Chart Hover Action on Daily Bar
        print("3. Testing interactive chart hover on daily bar...")
        chart_area = target_frame.locator("#chart-hover-area")
        box = chart_area.bounding_box()
        assert box is not None, "Chart hover area not found"

        # Hover in the middle
        page.mouse.move(box["x"] + box["width"] * 0.6, box["y"] + box["height"] * 0.4)
        time.sleep(1)

        tooltip_text = target_frame.locator("#tooltip-date-header").text_content()
        tooltip_bas = target_frame.locator("#tooltip-bas-val").text_content()
        print(f"Hover Tooltip Date: {tooltip_text}")
        print(f"Hover Tooltip BAS Return: {tooltip_bas}")

        assert "일봉" in tooltip_text, f"Tooltip date should indicate Daily Bar: {tooltip_text}"
        assert "BAS:" in tooltip_bas, "Tooltip BAS return missing"

        # 6. Capture verified screenshot
        page.screenshot(path=screenshot_path)
        print(f"Daily bars chart screenshot saved to {screenshot_path}")

        browser.close()
        print("Daily Bars Chart Verification Passed Successfully!")

if __name__ == "__main__":
    test_daily_bars_chart()
