"""
블암스 ETF 백테스트 (BAS Quant Platform)
Engineered for Institutional-Grade Quantitative Portfolio & Tripod Leverage Backtesting
"""

import sys
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

# 퀀트 엔진 패키지 경로 등록
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from engine.backtest import (
    run_rebalancing_backtest,
    run_tripod_backtest,
    calculate_metrics,
    calculate_drawdown,
)
from engine.data import fetch_etf_data
from engine.api_server import start_api_server

# 0. 백엔드 yfinance 실시간 연산 API 서버 가동 (Port 8502)
start_api_server(8502)

# 1. Streamlit 전역 페이지 설정
st.set_page_config(
    page_title="블암스 ETF 백테스트",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. 전역 여백 제거 및 풀스크린 스타일 주입
st.markdown("""
<style>
    /* Streamlit 순수 헤더/푸터/사이드바 여백 완벽 제거 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        width: 100% !important;
    }
    iframe {
        border: none !important;
        width: 100% !important;
        height: 100vh !important;
        min-height: 1400px !important;
    }
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background-color: #0f131d !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow-x: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. 통합 Stitch 디자인 앱 렌더링
html_file = project_root / "design" / "integrated_app.html"

if not html_file.exists():
    st.error("design/integrated_app.html 파일을 찾을 수 없습니다. make_integrated_html.py를 실행하십시오.")
else:
    with open(html_file, "r", encoding="utf-8") as f:
        integrated_html = f.read()

    # Stitch 원본 디자인 1:1 무결성 렌더링
    components.html(integrated_html, height=2200, scrolling=True)
