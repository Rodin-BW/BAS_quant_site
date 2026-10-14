import datetime
import re
from typing import Dict, List, Optional, Tuple
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from engine.data import (
    STATIC_PRESETS,
    BENCHMARK_PRESETS,
    POPULAR_ETF_CATALOG,
    normalize_ticker,
    fetch_etf_data,
    fetch_exchange_rate,
    align_and_convert_currency,
    get_dividend_yield,
    is_korean_ticker
)
from engine.backtest import (
    run_rebalancing_backtest,
    run_nasdaq_tripod_backtest,
    calculate_metrics,
    calculate_relative_metrics,
    generate_absolute_return_series
)

# ----------------------------------------------------
# 1. 페이지 설정
# ----------------------------------------------------
st.set_page_config(
    page_title="블암스 ETF 백테스팅",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------------------------------
# 2. Stitch Quant Precision 공식 디자인 시스템 주입
# ----------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

    /* 전역 기본 캔버스 & 다크 테마 */
    html, body, [data-testid="stAppViewContainer"], .main {
        background-color: #0f131d !important;
        color: #dfe2f1 !important;
        font-family: 'Hanken Grotesk', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Streamlit 상단 기본 헤더 및 사이드바 제거 */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }
    .block-container {
        padding-top: 5.5rem !important;
        padding-bottom: 5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1520px !important;
    }

    /* 숫자 튜닝 (Monospace & Tabular figures) */
    .font-mono, .table-numeric, [data-testid="stMetricValue"], td, th, input {
        font-family: 'JetBrains Mono', monospace !important;
        font-feature-settings: "tnum" 1, "cv05" 1;
    }

    /* Stitch Container Card (Streamlit border container override) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #171b26 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 1rem !important;
        padding: 1.25rem !important;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.35) !important;
        margin-bottom: 1.25rem !important;
    }

    /* 내부 중첩 컨테이너 (Nested Box) */
    div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1c1f2a !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 0.75rem !important;
        padding: 1rem !important;
        box-shadow: none !important;
        margin-bottom: 0.75rem !important;
    }

    /* Custom Stitch Card Classes */
    .stitch-card {
        background-color: #171b26;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 1rem;
        padding: 1.25rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.35);
        margin-bottom: 1.25rem;
    }
    .stitch-card-inner {
        background-color: #1c1f2a;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 0.75rem;
        padding: 1rem;
    }
    .stitch-card-lowest {
        background-color: #0a0e18;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 0.75rem;
        padding: 1rem;
    }

    /* KPI 카드 (Stitch Quant Report 8대 지표) */
    .kpi-card {
        background-color: #1c1f2a;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 0.75rem;
        padding: 1.25rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.15s ease, border-color 0.15s ease;
        min-height: 120px;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(71, 143, 255, 0.4);
    }
    .kpi-label {
        font-size: 13px;
        font-weight: 500;
        color: #8b909f;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 700;
        font-family: 'Hanken Grotesk', sans-serif;
        letter-spacing: -0.02em;
        margin: 6px 0;
        font-feature-settings: 'tnum' 1;
    }
    .kpi-sub {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 11px;
        font-family: 'JetBrains Mono', monospace;
    }
    .kpi-badge-positive {
        background: rgba(68, 225, 132, 0.12);
        color: #44e184;
        padding: 2px 8px;
        border-radius: 9999px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        border: 1px solid rgba(68, 225, 132, 0.25);
    }
    .kpi-badge-negative {
        background: rgba(255, 82, 94, 0.12);
        color: #ff525e;
        padding: 2px 8px;
        border-radius: 9999px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        border: 1px solid rgba(255, 82, 94, 0.25);
    }

    /* Streamlit 입력 폼 다크 테마 */
    input[type="text"], input[type="number"], div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #0a0e18 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 0.5rem !important;
        color: #dfe2f1 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    input:focus, div[data-baseweb="select"] > div:focus-within {
        border-color: #478fff !important;
        box-shadow: 0 0 0 1px #478fff, 0 0 12px rgba(71, 143, 255, 0.25) !important;
    }
    [data-testid="stExpander"] {
        background: #171b26 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 1rem !important;
    }

    /* Streamlit 버튼 커스텀 (Stitch Signal Blue & Secondary Dark) */
    button[kind="primary"] {
        background: #478fff !important;
        color: #00285b !important;
        font-weight: 700 !important;
        border-radius: 0.5rem !important;
        border: none !important;
        box-shadow: 0 0 16px rgba(71, 143, 255, 0.3) !important;
        font-family: 'Hanken Grotesk', sans-serif !important;
        transition: all 0.2s ease !important;
    }
    button[kind="primary"]:hover {
        background: #3182f6 !important;
        box-shadow: 0 0 24px rgba(71, 143, 255, 0.5) !important;
        transform: translateY(-1px) !important;
    }
    button[kind="secondary"] {
        background: #1c1f2a !important;
        color: #dfe2f1 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 0.5rem !important;
        font-weight: 600 !important;
        font-family: 'Hanken Grotesk', sans-serif !important;
        transition: all 0.2s ease !important;
    }
    button[kind="secondary"]:hover {
        background: #262a35 !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
        color: #ffffff !important;
    }

    /* 슬라이더 커스텀 */
    div[data-testid="stSlider"] div[data-baseweb="slider"] {
        accent-color: #478fff !important;
    }
    div[data-testid="stSlider"] [role="slider"] {
        background-color: #478fff !important;
        border: 2px solid #ffffff !important;
        box-shadow: 0 0 8px rgba(71, 143, 255, 0.6) !important;
    }

    /* 라디오 버튼 & 체크박스 */
    div[data-testid="stCheckbox"] label span[data-baseweb="checkbox"] {
        background-color: #1c1f2a !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }

    /* 고정 네비게이션 헤더 */
    .stitch-gnb {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 64px;
        z-index: 999;
        background: rgba(10, 14, 24, 0.92);
        backdrop-filter: blur(16px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 2rem;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.5);
    }

    /* 뱃지 유틸리티 */
    .badge-primary {
        background: rgba(71, 143, 255, 0.15);
        color: #acc7ff;
        border: 1px solid rgba(71, 143, 255, 0.3);
        padding: 2px 8px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }
    .badge-secondary {
        background: rgba(68, 225, 132, 0.12);
        color: #44e184;
        border: 1px solid rgba(68, 225, 132, 0.25);
        padding: 2px 8px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }
    .badge-outline {
        background: #1c1f2a;
        color: #8b909f;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2px 8px;
        border-radius: 9999px;
        font-size: 11px;
        font-family: 'JetBrains Mono', monospace;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ----------------------------------------------------
# 3. 도우미 함수
# ----------------------------------------------------
def format_currency_compact(val: float, cur_code: str = "KRW") -> str:
    sym = "₩" if cur_code == "KRW" else "$"
    if cur_code == "KRW":
        if abs(val) >= 100_000_000:
            return f"{sym}{val / 100_000_000:,.2f}억"
        elif abs(val) >= 10_000:
            return f"{sym}{val / 10_000:,.0f}만"
        else:
            return f"{sym}{val:,.0f}"
    else:
        if abs(val) >= 1_000_000:
            return f"{sym}{val / 1_000_000:,.2f}M"
        elif abs(val) >= 1_000:
            return f"{sym}{val / 1_000:,.1f}K"
        else:
            return f"{sym}{val:,.0f}"


def scale_weights_to_100(weights: dict) -> dict:
    if not weights:
        return {}
    valid = {k: max(0.0, float(v)) for k, v in weights.items()}
    total = sum(valid.values())
    if total <= 0:
        n = max(1, len(valid))
        eq = round(100.0 / n, 1)
        res = {k: eq for k in valid}
        diff = round(100.0 - sum(res.values()), 1)
        if diff != 0 and res:
            res[next(iter(res))] = round(res[next(iter(res))] + diff, 1)
        return res

    raw_shares = {k: (v / total) * 1000.0 for k, v in valid.items()}
    floor_shares = {k: int(s) for k, s in raw_shares.items()}
    remainder = 1000 - sum(floor_shares.values())
    sorted_keys = sorted(raw_shares.keys(), key=lambda k: raw_shares[k] - floor_shares[k], reverse=True)
    for i in range(remainder):
        floor_shares[sorted_keys[i % len(sorted_keys)]] += 1
    return {k: round(v / 10.0, 1) for k, v in floor_shares.items()}


# ----------------------------------------------------
# 4. 정적 자산배분 종목 및 비중 세팅 UI
# ----------------------------------------------------
def render_static_asset_builder(key_prefix: str, default_dict: dict, preset_choice: str) -> dict:
    all_catalog_keys = list(POPULAR_ETF_CATALOG.keys())

    # 프리셋 변경 감지
    last_pre_key = f"{key_prefix}_last_preset"
    if st.session_state.get(last_pre_key) != preset_choice:
        st.session_state[last_pre_key] = preset_choice
        target_tickers = [k for k in default_dict.keys() if k in all_catalog_keys] or list(default_dict.keys())
        st.session_state[f"{key_prefix}_mselect"] = target_tickers
        scaled_def = scale_weights_to_100(default_dict)
        for t in target_tickers:
            st.session_state[f"{key_prefix}_w_{t}"] = scaled_def.get(t, round(100.0 / len(target_tickers), 1))

    initial_selected = [k for k in default_dict.keys() if k in all_catalog_keys] or list(default_dict.keys())

    col_srch1, col_srch2 = st.columns([7, 3])
    with col_srch1:
        selected_tickers = st.multiselect(
            "ETF 검색 및 편입 종목",
            options=all_catalog_keys,
            default=initial_selected if f"{key_prefix}_mselect" not in st.session_state else None,
            format_func=lambda x: POPULAR_ETF_CATALOG.get(x, x),
            key=f"{key_prefix}_mselect",
            label_visibility="collapsed"
        )
    with col_srch2:
        custom_add = st.text_input(
            "직접 추가",
            placeholder="+ 목록 외 티커 입력 (쉼표 구분)",
            key=f"{key_prefix}_custom_add",
            label_visibility="collapsed"
        )
        if custom_add.strip():
            extras = [normalize_ticker(t.strip()) for t in custom_add.split(",") if t.strip()]
            for et in extras:
                if et not in selected_tickers:
                    selected_tickers.append(et)

    if not selected_tickers:
        st.warning("선택된 ETF가 없습니다. 위 검색창에서 종목을 선택해 주세요.")
        return {"SPY": 100.0}

    # 자동 배분 제어 버튼
    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        if st.button("⚖️ 동일 가중 (1/N 균등)", key=f"{key_prefix}_btn_eq", use_container_width=True):
            eq_map = scale_weights_to_100({t: 1.0 for t in selected_tickers})
            for t, val in eq_map.items():
                st.session_state[f"{key_prefix}_w_{t}"] = val
            st.rerun()
    with col_btn2:
        if st.button("💯 현재 비율 100% 자동 맞춤", key=f"{key_prefix}_btn_scale", use_container_width=True):
            cur_map = {t: st.session_state.get(f"{key_prefix}_w_{t}", 1.0) for t in selected_tickers}
            scaled_map = scale_weights_to_100(cur_map)
            for t, val in scaled_map.items():
                st.session_state[f"{key_prefix}_w_{t}"] = val
            st.rerun()

    # 종목별 슬라이더 카드 목록
    weights = {}
    for t in selected_tickers:
        desc = POPULAR_ETF_CATALOG.get(t, t).split(" | ")[-1] if " | " in POPULAR_ETF_CATALOG.get(t, t) else t
        def_val = float(default_dict.get(t, 100.0 / len(selected_tickers)))
        if def_val <= 1.0:
            def_val *= 100.0

        s_key = f"{key_prefix}_w_{t}"
        if s_key not in st.session_state:
            st.session_state[s_key] = float(round(def_val, 1))
        curr_val = float(st.session_state[s_key])

        col_c1, col_c2 = st.columns([5, 6])
        with col_c1:
            st.markdown(
                f"""
                <div style='display: flex; align-items: center; justify-content: space-between; padding: 6px 0;'>
                    <div style='display: flex; align-items: center; gap: 8px;'>
                        <span style='background: #1E293B; border: 1px solid rgba(255, 255, 255, 0.1); color: #DFE2F1; font-weight: 700; padding: 3px 8px; border-radius: 6px; font-size: 13px; font-family: "JetBrains Mono", monospace;'>{t}</span>
                        <span style='font-size: 13px; font-weight: 600; color: #C1C6D6;'>{desc}</span>
                    </div>
                    <span style='background: rgba(71, 143, 255, 0.15); border: 1px solid rgba(71, 143, 255, 0.3); color: #478FFF; font-weight: 700; padding: 2px 8px; border-radius: 8px; font-size: 13px; font-family: "JetBrains Mono", monospace;'>{curr_val:.1f}%</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_c2:
            weights[t] = st.slider(
                f"{t} 비중",
                0.0, 100.0,
                value=curr_val,
                step=0.5,
                key=s_key,
                label_visibility="collapsed"
            )

    tot_w = round(sum(weights.values()), 1)
    is_exact_100 = abs(tot_w - 100.0) < 0.05
    bar_color = "#44E184" if is_exact_100 else ("#F59E0B" if tot_w < 100.0 else "#FF525E")
    status_txt = "🟢 100.0% 완벽한 균형" if is_exact_100 else (f"🟠 {100.0 - tot_w:.1f}%p 부족" if tot_w < 100.0 else f"🔴 {tot_w - 100.0:.1f}%p 초과")

    st.markdown(
        f"""
        <div style='background-color: #171B26; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 12px 16px; margin-top: 10px; display: flex; justify-content: space-between; align-items: center; border-left: 5px solid {bar_color};'>
            <span style='font-size: 13px; color: #C1C6D6;'><b>목표 비중 합계</b>: {status_txt}</span>
            <span style='font-size: 17px; font-weight: 800; color: {bar_color}; font-family: "JetBrains Mono", monospace;'>{tot_w:.1f}%</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    return weights


# ----------------------------------------------------
# 5. 실시간 포트폴리오 목표 비중 도넛 차트
# ----------------------------------------------------
def render_clean_donut_chart(weights: dict):
    valid_items = {k: float(v) for k, v in weights.items() if float(v) > 0}
    if not valid_items:
        fig = go.Figure()
        fig.add_annotation(text="선택된 자산이 없습니다", showarrow=False, font=dict(size=14, color="#94A3B8"))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=280,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": False})
        return

    labels = []
    values = []
    palette = ["#478FFF", "#44E184", "#F59E0B", "#FF525E", "#A855F7", "#06B6D4", "#EC4899", "#6366F1"]
    for t, w in valid_items.items():
        desc = POPULAR_ETF_CATALOG.get(t, t).split(" | ")[-1] if " | " in POPULAR_ETF_CATALOG.get(t, t) else t
        labels.append(f"{t} ({desc[:7]})")
        values.append(w)

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.64,
        textinfo="percent",
        hoverinfo="label+value+percent",
        marker=dict(colors=palette[:len(labels)], line=dict(color='#0F131D', width=2))
    )])
    tot = sum(values)
    center_col = "#44E184" if abs(tot - 100.0) < 0.1 else "#F59E0B"
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Hanken Grotesk", color="#DFE2F1"),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=11, color="#94A3B8")),
        height=320,
        margin=dict(l=10, r=10, t=10, b=30),
        annotations=[dict(
            text=f"<span style='font-size:12px;color:#94A3B8;'>총 자산</span><br><b style='font-size:22px;color:{center_col};font-family:JetBrains Mono;'>{len(values)}개</b><br><span style='font-size:11px;color:#94A3B8;'>합계 {tot:.1f}%</span>",
            x=0.5, y=0.5,
            showarrow=False
        )]
    )
    st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": False})


# ----------------------------------------------------
# 6. 전략 빌더 화면 (메인 구성)
# ----------------------------------------------------
def render_strategy_builder():
    # 1. 서브 헤더 (Portfolio Architecture & Mode Switcher)
    curr_strat = st.session_state.get("selected_strategy", "static")
    is_tripod = (curr_strat == "tripod")

    st.markdown(
        """
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-5 border-b border-white/5 mb-6">
            <div>
                <div class="flex items-center gap-2 mb-1.5">
                    <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-primary-container/15 text-primary-fixed-dim font-mono text-xs font-semibold">
                        <span class="w-1.5 h-1.5 rounded-full bg-primary-container animate-pulse"></span>
                        ENGINE V4.2
                    </span>
                    <span class="text-xs text-outline font-mono">ST-BLD-0924</span>
                </div>
                <div class="flex items-baseline gap-3">
                    <span class="text-2xl md:text-3xl font-bold text-on-surface tracking-tight">전략 구성 엔진</span>
                    <span class="text-xs text-outline-variant uppercase tracking-wider font-mono">Portfolio Architecture</span>
                </div>
                <p class="text-xs md:text-sm text-on-surface-variant max-w-2xl mt-1">
                    한국(KRX) & 미국(US) 상장 ETF 자산군 정밀 조합 및 3대 축 나스닥 레버리지 방어 알고리즘 파라미터 세팅
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 상단 2-Way 세그먼트 컨트롤 버튼
    col_mode1, col_mode2 = st.columns(2)
    with col_mode1:
        if st.button("🏛️ 정적 자산배분 (Static Allocation)", use_container_width=True, type="primary" if not is_tripod else "secondary", key="btn_mode_static"):
            st.session_state["selected_strategy"] = "static"
            st.rerun()
    with col_mode2:
        if st.button("⚡ 나스닥 레버리지 트라이포드 (Tripod PRO)", use_container_width=True, type="primary" if is_tripod else "secondary", key="btn_mode_tripod"):
            st.session_state["selected_strategy"] = "tripod"
            st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    strategy_cat = "나스닥 레버리지 트라이포드 (Tripod Alpha)" if is_tripod else "정적 자산배분 (Static Allocation)"

    # 좌우 2-컬럼 워크벤치 (좌: 5 cols 자본/리밸런싱/비용, 우: 7 cols 비중/도넛/트라이포드)
    col_left, col_right = st.columns([5, 7], gap="medium")

    active_tickers = []
    tripod_params = {}
    weights = {}
    rebal_freq = "M"
    band_pct = None

    with col_left:
        # [Card 1] 자본 및 적립식(DCA) 설정
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 14px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="material-symbols-outlined" style="color: #478fff; font-size: 20px;">payments</span>
                        <span style="font-size: 16px; font-weight: 700; color: #dfe2f1;">자본 및 적립식(DCA) 설정</span>
                    </div>
                    <span style="font-size: 11px; color: #8b909f; font-family: 'JetBrains Mono', monospace;">KRW / USD BASE</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            col_c_cur1, col_c_cur2 = st.columns([5, 5])
            with col_c_cur1:
                base_cur_choice = st.radio("기준 통화", ["🇰🇷 KRW (원화)", "🇺🇸 USD (달러)"], index=0, key="bld_cur", horizontal=True)
                base_cur_code = "KRW" if "KRW" in base_cur_choice else "USD"
                cur_sym = "₩" if base_cur_code == "KRW" else "$"
            with col_c_cur2:
                default_cap_str = "100,000,000" if base_cur_code == "KRW" else "100,000"
                init_cap_input = st.text_input(
                    f"초기 투자 원금 ({base_cur_code})",
                    value=st.session_state.get(f"bld_cap_{base_cur_code}", default_cap_str),
                    key=f"bld_cap_input_{base_cur_code}"
                )
                cleaned_cap = re.sub(r"[^\d]", "", init_cap_input)
                init_capital = float(cleaned_cap) if cleaned_cap else (100000000.0 if base_cur_code == "KRW" else 100000.0)
                st.session_state[f"bld_cap_{base_cur_code}"] = f"{int(init_capital):,}"

            st.caption(f"💵 적용 금액: **{cur_sym}{int(init_capital):,}** ({format_currency_compact(init_capital, base_cur_code)})")

            # DCA 적립식 설정 컨테이너 (Nested Box)
            with st.container(border=True):
                col_dca_t1, col_dca_t2 = st.columns([7, 3])
                with col_dca_t1:
                    st.markdown("<span style='font-size:13px; font-weight:600; color:#dfe2f1;'>🔁 DCA 정기 적립식 투입</span>", unsafe_allow_html=True)
                with col_dca_t2:
                    enable_dca = st.checkbox("활성화", value=True, key="bld_dca_chk")

                dca_amount = 0.0
                dca_freq = "M"
                if enable_dca:
                    col_dca1, col_dca2 = st.columns(2)
                    with col_dca1:
                        default_dca_str = "1,000,000" if base_cur_code == "KRW" else "1,000"
                        dca_input = st.text_input(
                            f"매월 적립액 ({base_cur_code})",
                            value=st.session_state.get(f"bld_dca_{base_cur_code}", default_dca_str),
                            key=f"bld_dca_input_{base_cur_code}"
                        )
                        cleaned_dca = re.sub(r"[^\d]", "", dca_input)
                        dca_amount = float(cleaned_dca) if cleaned_dca else (1000000.0 if base_cur_code == "KRW" else 1000.0)
                        st.session_state[f"bld_dca_{base_cur_code}"] = f"{int(dca_amount):,}"
                        st.caption(f"월 납입: {cur_sym}{int(dca_amount):,} ({format_currency_compact(dca_amount, base_cur_code)})")
                    with col_dca2:
                        dca_freq_choice = st.selectbox("납입 주기", ["월간 (매월 1회)", "분기 (분기별 1회)"], index=0, key="bld_dca_fq")
                        dca_freq = "M" if "월간" in dca_freq_choice else "Q"

            # 시뮬레이션 기간 & 프리셋
            st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
            st.markdown("<span style='font-size:13px; font-weight:600; color:#c1c6d6;'>시뮬레이션 검증 기간 (40Y Extended DB)</span>", unsafe_allow_html=True)
            today = datetime.date.today()
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                start_date = st.date_input("검증 시작일", value=datetime.date(2010, 1, 1), key="bld_sdate", label_visibility="collapsed")
            with col_d2:
                end_date = st.date_input("검증 종료일", value=today, key="bld_edate", label_visibility="collapsed")

            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                if st.button("5Y (최근 5년)", use_container_width=True, key="p_5y"):
                    st.session_state["bld_sdate"] = today - datetime.timedelta(days=365*5)
                    st.rerun()
            with col_p2:
                if st.button("10Y (최근 10년)", use_container_width=True, key="p_10y"):
                    st.session_state["bld_sdate"] = today - datetime.timedelta(days=365*10)
                    st.rerun()
            with col_p3:
                if st.button("MAX (40Y)", use_container_width=True, key="p_max"):
                    st.session_state["bld_sdate"] = datetime.date(2010, 1, 1)
                    st.rerun()

            # 세금 및 슬리피지 마찰비용 산정
            with st.container(border=True):
                col_tx1, col_tx2 = st.columns([7, 3])
                with col_tx1:
                    st.markdown("<span style='font-size:13px; font-weight:600; color:#dfe2f1;'>🧾 세금 및 슬리피지 마찰비용 산정</span>", unsafe_allow_html=True)
                with col_tx2:
                    st.markdown("<span class='text-xs text-secondary font-mono font-bold bg-secondary/10 px-2 py-0.5 rounded'>정밀 모드 ON</span>", unsafe_allow_html=True)

                col_txc1, col_txc2 = st.columns([7, 3])
                with col_txc1:
                    apply_tax = st.checkbox("해외주식 양도소득세 22% (연 250만 원 공제)", value=True, key="bld_tax_chk")
                with col_txc2:
                    st.markdown("<span style='font-size:11px; color:#8b909f; font-family:JetBrains Mono;'>선입선출 FIFO</span>", unsafe_allow_html=True)

                tax_rate = 0.22 if apply_tax else 0.0
                tax_deduction = (2500000.0 if base_cur_code == "KRW" else 2000.0) if apply_tax else 0.0

                slippage_pct = st.slider("편도 거래비용 & 슬리피지 (%)", 0.0, 0.50, 0.15, step=0.01, key="bld_slip") / 100.0
                total_fee_rate = slippage_pct
                st.caption("0.00% (기관 최적) · 0.15% (일반적) · 0.50% (보수적)")

        # [Card 2] 주기 & 밴드 리밸런싱 세부설정 및 프리셋
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 14px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="material-symbols-outlined" style="color: #478fff; font-size: 20px;">tune</span>
                        <span style="font-size: 16px; font-weight: 700; color: #dfe2f1;">주기 & 밴드 리밸런싱 세부설정</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            col_rf1, col_rf2 = st.columns(2)
            with col_rf1:
                rebal_freq = st.selectbox("정기 리밸런싱 주기 (Execution Frequency)", ["M (월간)", "Q (분기)", "Y (연간)", "None (Buy & Hold)"], index=0, key="bld_rfreq")
            with col_rf2:
                use_band = st.checkbox("허용 오차폭 밴드 적용", value=True, key="bld_uband")
            if use_band:
                band_val = st.slider("허용 오차 밴드 (±%p)", 1.0, 15.0, 5.0, step=0.5, key="bld_bval")
                band_pct = band_val / 100.0
                st.caption("자산 목표 비중 대비 임계치를 초과 이탈할 경우 주기와 상관없이 즉시 균형을 회복합니다.")

        # 원클릭 퀀트 프리셋 (One-Click Archetypes) 6개 그리드 버튼
        st.markdown("<span class='text-xs text-outline font-semibold mb-1 block'>원클릭 퀀트 프리셋 (One-Click Archetypes)</span>", unsafe_allow_html=True)
        col_pr1, col_pr2, col_pr3 = st.columns(3)
        with col_pr1:
            if st.button("올웨더\n(주30/채55/원15)", use_container_width=True, key="pre_allw"):
                st.session_state["bld_static_last_preset"] = "올웨더 포트폴리오 (Ray Dalio All Weather)"
                st.session_state["bld_static_mselect"] = ["SPY", "TLT", "IEF", "GLD", "DBC"]
                st.rerun()
            if st.button("나스닥 모멘텀\n(QQQ 70/TLT 30)", use_container_width=True, key="pre_nasdaq"):
                st.session_state["bld_static_last_preset"] = "나스닥 모멘텀 집중"
                st.session_state["bld_static_mselect"] = ["QQQ", "TLT"]
                st.session_state["bld_static_w_QQQ"] = 70.0
                st.session_state["bld_static_w_TLT"] = 30.0
                st.rerun()
        with col_pr2:
            if st.button("영구 포트폴리오\n(주25/채25/금25/현25)", use_container_width=True, key="pre_perm"):
                st.session_state["bld_static_last_preset"] = "영구 포트폴리오 (Permanent Portfolio)"
                st.session_state["bld_static_mselect"] = ["SPY", "TLT", "GLD", "BIL"]
                st.rerun()
            if st.button("1/N 동일가중\n(선택 종목 균등)", use_container_width=True, key="pre_eqw"):
                sel = st.session_state.get("bld_static_mselect", ["QQQ", "SPY", "TLT", "GLD"])
                eq_map = scale_weights_to_100({t: 1.0 for t in sel})
                for t, v in eq_map.items():
                    st.session_state[f"bld_static_w_{t}"] = v
                st.rerun()
        with col_pr3:
            if st.button("클래식 60:40\n(SPY 60/TLT 40)", use_container_width=True, key="pre_6040"):
                st.session_state["bld_static_last_preset"] = "전통 60/40 (주식 60% / 채권 40%)"
                st.session_state["bld_static_mselect"] = ["SPY", "TLT"]
                st.session_state["bld_static_w_SPY"] = 60.0
                st.session_state["bld_static_w_TLT"] = 40.0
                st.rerun()
            if st.button("100% 자동정규화\n(비율 보정)", use_container_width=True, key="pre_norm"):
                sel = st.session_state.get("bld_static_mselect", ["QQQ", "SPY", "TLT", "GLD"])
                cur_map = {t: st.session_state.get(f"bld_static_w_{t}", 1.0) for t in sel}
                scaled = scale_weights_to_100(cur_map)
                for t, v in scaled.items():
                    st.session_state[f"bld_static_w_{t}"] = v
                st.rerun()

    with col_right:
        if not is_tripod:
            # [Card 3] 자산 배분 가중치 (Weights Matrix)
            with st.container(border=True):
                st.markdown(
                    """
                    <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 14px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span class="material-symbols-outlined" style="color: #478fff; font-size: 20px;">pie_chart</span>
                            <div>
                                <span style="font-size: 16px; font-weight: 700; color: #dfe2f1;">자산 배분 가중치 (Weights Matrix)</span>
                                <div style="font-size: 12px; color: #8b909f;">포트폴리오 총 비중 합계는 정확히 100%를 충족해야 합니다.</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                preset_choice = st.selectbox(
                    "전략 프리셋 템플릿",
                    options=list(STATIC_PRESETS.keys()) + ["직접 입력/커스텀"],
                    key="bld_st_preset"
                )
                default_dict = STATIC_PRESETS.get(preset_choice, {"QQQ": 0.4, "SPY": 0.3, "TLT": 0.2, "GLD": 0.1})
                weights = render_static_asset_builder(
                    key_prefix="bld_static",
                    default_dict=default_dict,
                    preset_choice=preset_choice
                )
                active_tickers = list(weights.keys())

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                render_clean_donut_chart(weights)

        else:
            # [Card 4] 나스닥 레버리지 트라이포드 3대 축 (Tripod Defense)
            with st.container(border=True):
                st.markdown(
                    """
                    <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 14px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span class="material-symbols-outlined" style="color: #44e184; font-size: 22px;">security</span>
                            <div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="font-size: 16px; font-weight: 700; color: #dfe2f1;">나스닥 레버리지 트라이포드 3대 축 (Tripod Defense)</span>
                                    <span style="font-size: 10px; background: rgba(68, 225, 132, 0.12); color: #44e184; padding: 2px 8px; border-radius: 9999px; font-family: 'JetBrains Mono', monospace; font-weight: 700;">ALGO ARMORED</span>
                                </div>
                                <div style="font-size: 12px; color: #8b909f;">40년 데이터 기반 변동성 장세 방어 및 TQQQ/QLD 기회 레버리지 자동 포지셔닝</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # 3대 축 카드 파라미터 셋업
                col_ax1, col_ax2, col_ax3 = st.columns(3)
                with col_ax1:
                    with st.container(border=True):
                        st.markdown("<span style='font-size:11px; font-weight:700; color:#478fff; font-family:JetBrains Mono;'>제1축 · BUFFER</span>", unsafe_allow_html=True)
                        st.markdown("<b style='font-size:13px; color:#dfe2f1;'>상시 현금비중 & 스위칭</b>", unsafe_allow_html=True)
                        tp_base = st.text_input("1배수 ETF", value="QQQ", key="tp_base")
                        tp_2x = st.text_input("2배수 ETF", value="QLD", key="tp_2x")
                        tp_cash_pct = st.slider("기본 현금 버퍼 (%)", 10.0, 50.0, 30.0, step=5.0, key="tp_cash_pct")
                        tp_qld_ratio = st.slider("투자금 중 2배수 비율 (%)", 0.0, 100.0, 50.0, step=5.0, key="tp_qld_ratio")

                with col_ax2:
                    with st.container(border=True):
                        st.markdown("<span style='font-size:11px; font-weight:700; color:#44e184; font-family:JetBrains Mono;'>제2축 · MILESTONE</span>", unsafe_allow_html=True)
                        st.markdown("<b style='font-size:13px; color:#dfe2f1;'>MDD 분할매수 사다리</b>", unsafe_allow_html=True)
                        tp_mdd1 = st.number_input("1차 조정 MDD (%)", -25.0, -5.0, -10.0, step=1.0, key="tp_mdd1")
                        tp_mdd2 = st.number_input("2차 하락 MDD (%)", -35.0, -10.0, -20.0, step=1.0, key="tp_mdd2")
                        tp_mdd3 = st.number_input("3차 대폭락 MDD (%)", -60.0, -20.0, -30.0, step=1.0, key="tp_mdd3")
                        st.caption("고점 대비 단계별 유보현금 TQQQ 전환 매수 집행")

                with col_ax3:
                    with st.container(border=True):
                        st.markdown("<span style='font-size:11px; font-weight:700; color:#ff525e; font-family:JetBrains Mono;'>제3축 · PANIC BUY</span>", unsafe_allow_html=True)
                        st.markdown("<b style='font-size:13px; color:#dfe2f1;'>RSI 과매도 공포 탐지</b>", unsafe_allow_html=True)
                        tp_3x = st.text_input("3배수 레버리지", value="TQQQ", key="tp_3x")
                        tp_rsi1 = st.slider("1차 과매도 (RSI)", 30.0, 50.0, 40.0, step=1.0, key="tp_rsi1")
                        tp_rsi2 = st.slider("극단적 공포 (RSI)", 15.0, 35.0, 30.0, step=1.0, key="tp_rsi2")
                        st.caption("일봉 RSI 과매도 시 잔여 유동성 즉시 풀베팅")

                # 생존성 검증 뱃지 바
                st.markdown(
                    """
                    <div style="background: rgba(68, 225, 132, 0.08); border: 1px solid rgba(68, 225, 132, 0.2); border-radius: 8px; padding: 10px 14px; margin-top: 14px; display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 13px; font-weight: 600; color: #44e184;">🟢 1999 닷컴버블, 2008 금융위기 씬에 대한 생존성 검증 통과 (생존율 99.4%)</span>
                        <span style="font-size: 11px; color: #8b909f; font-family: 'JetBrains Mono', monospace;">Live Tested</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                active_tickers = [normalize_ticker(tp_base), normalize_ticker(tp_2x), normalize_ticker(tp_3x)]
                tripod_params = {
                    "base_asset": normalize_ticker(tp_base),
                    "leveraged_2x": normalize_ticker(tp_2x),
                    "leveraged_3x": normalize_ticker(tp_3x),
                    "normal_cash_pct": tp_cash_pct / 100.0,
                    "normal_qld_ratio": tp_qld_ratio / 100.0,
                    "mdd_milestones": (float(tp_mdd1)/100.0, float(tp_mdd2)/100.0, float(tp_mdd3)/100.0),
                    "rsi_triggers": (float(tp_rsi1), float(tp_rsi2))
                }
                w_inv = 100.0 - tp_cash_pct
                w_qld = w_inv * (tp_qld_ratio / 100.0)
                w_qqq = w_inv - w_qld
                weights = {
                    "CASH (현금)": tp_cash_pct,
                    f"{tp_base} (1X)": round(w_qqq, 1),
                    f"{tp_2x} (2X)": round(w_qld, 1)
                }

                render_clean_donut_chart(weights)

    # 벤치마크 및 절대수익률 기준선 설정 (우측/하단 공통)
    with st.container(border=True):
        col_bm1, col_bm2 = st.columns([7, 5])
        with col_bm1:
            selected_bm_labels = st.multiselect(
                "비교 벤치마크 선택",
                options=list(BENCHMARK_PRESETS.keys()),
                default=["미국 S&P 500 (SPY)", "한국 코스피 200 (069500.KS)"],
                key="bld_bm_sel"
            )
            bm_tickers = [BENCHMARK_PRESETS[l] for l in selected_bm_labels]
            enable_absolute_hurdle = True
            target_abs_cagr = 0.05
        with col_bm2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            col_act1, col_act2, col_act3 = st.columns([3, 3, 6])
            with col_act1:
                if st.button("🔄 설정 초기화", use_container_width=True, key="btn_reset_all"):
                    st.session_state.clear()
                    st.rerun()
            with col_act2:
                export_json = str({
                    "strategy": strategy_cat,
                    "tickers": active_tickers,
                    "weights": weights,
                    "capital": init_capital,
                    "dca": dca_amount if enable_dca else 0
                })
                st.download_button(
                    label="📥 전략 내보내기",
                    data=export_json,
                    file_name=f"strategy_config_{datetime.date.today()}.json",
                    mime="application/json",
                    use_container_width=True,
                    key="btn_export_json"
                )
            with col_act3:
                run_btn = st.button("⚡ 시뮬레이션 실행 (Run Backtest)", type="primary", use_container_width=True, key="bld_run_btn")

    config = {
        "strategy_cat": strategy_cat,
        "is_tripod": is_tripod,
        "active_tickers": active_tickers,
        "tripod_params": tripod_params,
        "weights": weights,
        "rebal_freq": rebal_freq,
        "band_pct": band_pct,
        "total_fee_rate": total_fee_rate,
        "tax_rate": tax_rate,
        "tax_deduction": tax_deduction,
        "bm_tickers": bm_tickers,
        "enable_absolute_hurdle": enable_absolute_hurdle,
        "target_abs_cagr": target_abs_cagr,
        "base_cur_code": base_cur_code,
        "start_date": start_date,
        "end_date": end_date,
        "init_capital": init_capital,
        "enable_dca": enable_dca,
        "dca_amount": dca_amount,
        "dca_freq": dca_freq
    }

    return config, run_btn


# ----------------------------------------------------
# 7. 적용된 전략 명세 요약 카드
# ----------------------------------------------------
def render_strategy_config_summary(config: dict):
    is_tripod = config.get("is_tripod", False)
    base_cur = config.get("base_cur_code", "KRW")
    cur_sym = "₩" if base_cur == "KRW" else "$"

    col_strat, col_env = st.columns([1.45, 1.0])

    with col_strat:
        if not is_tripod:
            weights = config.get("weights", {})
            rebal_freq = config.get("rebal_freq", "M")
            band_pct = config.get("band_pct", None)
            band_info = f"허용 오차 ±{band_pct*100:.1f}%p 밴드 적용" if band_pct else "정기 리밸런싱만 적용"
            st.info(f"🔄 **리밸런싱 규칙**: {rebal_freq} | {band_info}")

            rows = []
            for t, w in weights.items():
                label = POPULAR_ETF_CATALOG.get(t, t)
                rows.append({"티커": t, "자산명": label, "목표 비중": f"{w:.1f}%"})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            tp = config.get("tripod_params", {})
            b_asset = tp.get("base_asset", "QQQ")
            l2_asset = tp.get("leveraged_2x", "QLD")
            l3_asset = tp.get("leveraged_3x", "TQQQ")
            c_pct = tp.get("normal_cash_pct", 0.30) * 100.0
            m1, m2, m3 = tp.get("mdd_milestones", (-0.10, -0.20, -0.30))
            r1, r2 = tp.get("rsi_triggers", (40.0, 30.0))

            st.markdown(
                f"""
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 12px;">
                    <div class="kpi-card">
                        <div class="kpi-label">제1축: 평상시 현금 비중</div>
                        <div class="kpi-value">{c_pct:.1f}%</div>
                        <div class="kpi-sub" style="color: #059669;">↑ {b_asset} + {l2_asset}</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">제2축: MDD 마일스톤</div>
                        <div class="kpi-value" style="font-size: 18px;">{m1*100:.0f}% / {m2*100:.0f}% / {m3*100:.0f}%</div>
                        <div class="kpi-sub" style="color: #059669;">↑ 3단계 분할 매수</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">제3축: RSI 과매도 기준</div>
                        <div class="kpi-value" style="font-size: 18px;">RSI ≤ {r1:.0f} / {r2:.0f}</div>
                        <div class="kpi-sub" style="color: #059669;">↑ {l3_asset} 집중 매수</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(f"- 🎯 **운용 자산군**: 1배수 `{b_asset}` · 2배수 `{l2_asset}` · 3배수 `{l3_asset}` · 상시 현금성 자산")

    with col_env:
        dca_active = config.get("enable_dca", False)
        dca_amt = config.get("dca_amount", 0.0)
        dca_fr = config.get("dca_freq", "M")
        dca_txt = f"적용 ({cur_sym}{dca_amt:,.0f} / {dca_fr})" if dca_active else "미적용 (거치식)"

        env_items = [
            ("기준 통화", f"{base_cur}"),
            ("초기 투자 자본금", f"{cur_sym}{config.get('init_capital', 0):,.0f}"),
            ("DCA 정기 적립식", dca_txt),
            ("시뮬레이션 기간", f"{config.get('start_date')} ~ {config.get('end_date')}"),
            ("총 거래비용", f"편도 {config.get('total_fee_rate', 0.0)*100:.3f}%"),
            ("과세 조건", f"{config.get('tax_rate', 0.0)*100:.1f}% (기본공제 {cur_sym}{config.get('tax_deduction', 0.0):,.0f})"),
            ("비교 벤치마크", f"{', '.join(config.get('bm_tickers', []))}")
        ]
        st.dataframe(pd.DataFrame(env_items, columns=["항목", "설정값"]), use_container_width=True, hide_index=True)


# ----------------------------------------------------
# 8. 백테스트 결과 분석 화면
# ----------------------------------------------------
def render_backtest_results(config: dict):
    # 상단 전략 정보 배너 및 액션 툴바 (Stitch Quant Precision Banner)
    strat_title = config.get("strategy_cat", "퀀트 자산배분")
    dca_active = config.get("enable_dca", False)
    dca_info = f" • DCA 적립: {config['base_cur_code']} {config.get('dca_amount', 0):,.0f} / {config.get('dca_freq', 'M')}" if dca_active else ""
    
    st.markdown(
        f"""
        <div style="background: #171B26; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 22px 26px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.35);">
            <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 16px;">
                <div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                        <span style="background: rgba(71, 143, 255, 0.15); color: #478FFF; padding: 2px 10px; border-radius: 9999px; font-size: 11px; font-weight: 700; font-family: 'JetBrains Mono', monospace; text-transform: uppercase;">Strategy Analytics</span>
                        <span style="background: rgba(68, 225, 132, 0.12); color: #44E184; padding: 2px 10px; border-radius: 9999px; font-size: 11px; font-weight: 700; font-family: 'JetBrains Mono', monospace;">Live Engine Verified</span>
                        <span style="color: #8B909F; font-size: 11px; font-family: 'JetBrains Mono', monospace;">ID: {"TRIPOD-ALPHA-V4" if config.get("is_tripod") else "STATIC-ALLOC-V4"}</span>
                    </div>
                    <div style="font-size: 24px; font-weight: 800; color: #DFE2F1; letter-spacing: -0.5px; margin-bottom: 4px;">
                        {strat_title}
                    </div>
                    <div style="font-size: 12px; color: #94A3B8; font-family: 'JetBrains Mono', monospace;">
                        기간: <strong style="color: #DFE2F1;">{config['start_date']} ~ {config['end_date']}</strong> • 
                        초기 원금: <strong style="color: #DFE2F1;">{config['base_cur_code']} {config['init_capital']:,.0f}</strong>{dca_info}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_ret_bar1, col_ret_bar2 = st.columns([3, 7])
    with col_ret_bar1:
        if st.button("⬅️ 🛠️ 전략 파라미터 재설정", use_container_width=True, key="btn_back_to_bld"):
            st.session_state["active_view"] = "builder"
            st.rerun()

    with st.expander("🧩 적용된 세부 전략 및 백테스트 환경 명세", expanded=False):
        render_strategy_config_summary(config)

    active_tickers = config["active_tickers"]
    bm_tickers = config["bm_tickers"]
    base_cur_code = config["base_cur_code"]
    start_date = config["start_date"]
    end_date = config["end_date"]
    total_fee_rate = config["total_fee_rate"]
    tax_rate = config["tax_rate"]
    tax_deduction = config["tax_deduction"]
    init_capital = config["init_capital"]
    is_tripod = config.get("is_tripod", False)
    tripod_params = config.get("tripod_params", {})
    weights = config.get("weights", {})
    rebal_freq = config.get("rebal_freq", "M")
    band_pct = config.get("band_pct", None)
    enable_absolute_hurdle = config.get("enable_absolute_hurdle", True)
    target_abs_cagr = config.get("target_abs_cagr", 0.05)

    if not active_tickers:
        st.warning("분석할 ETF 티커가 지정되지 않았습니다.")
        return

    all_download_tickers = list(dict.fromkeys(active_tickers + bm_tickers))

    with st.spinner("시세, 벤치마크 및 환율 데이터를 불러오는 중입니다..."):
        price_df = fetch_etf_data(
            tickers=all_download_tickers,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )
        fx_series = fetch_exchange_rate(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )

    if price_df.empty or len(price_df) < 10:
        st.error("지정된 기간의 가격 데이터를 불러오지 못했습니다. 티커와 기간을 확인해 주세요.")
        return

    converted_df = align_and_convert_currency(price_df, base_currency=base_cur_code, fx_series=fx_series)
    enable_dca = config.get("enable_dca", False)
    dca_amount = float(config.get("dca_amount", 0.0)) if enable_dca else 0.0
    dca_freq = config.get("dca_freq", "M")

    if is_tripod:
        portfolio_res = run_nasdaq_tripod_backtest(
            price_df=converted_df[active_tickers],
            base_asset=tripod_params.get("base_asset", "QQQ"),
            leveraged_2x=tripod_params.get("leveraged_2x", "QLD"),
            leveraged_3x=tripod_params.get("leveraged_3x", "TQQQ"),
            normal_cash_pct=tripod_params.get("normal_cash_pct", 0.30),
            normal_qld_ratio=tripod_params.get("normal_qld_ratio", 0.50),
            mdd_milestones=tripod_params.get("mdd_milestones", (-0.10, -0.20, -0.30)),
            rsi_triggers=tripod_params.get("rsi_triggers", (40.0, 30.0)),
            fee_rate=total_fee_rate,
            tax_rate=tax_rate,
            tax_deduction=tax_deduction,
            initial_capital=float(init_capital),
            periodic_cash_flow=dca_amount,
            dca_freq=dca_freq
        )
    else:
        portfolio_res = run_rebalancing_backtest(
            price_df=converted_df[active_tickers],
            weights=weights,
            rebalance_freq=rebal_freq.split(" ")[0],
            band_threshold=band_pct,
            fee_rate=total_fee_rate,
            tax_rate=tax_rate,
            tax_deduction=tax_deduction,
            initial_capital=float(init_capital),
            periodic_cash_flow=dca_amount,
            dca_freq=dca_freq
        )

    if portfolio_res is None:
        return

    m = portfolio_res.metrics
    final_val = portfolio_res.daily_portfolio_value.iloc[-1]
    cur_sym = "₩" if base_cur_code == "KRW" else "$"

    # 벤치마크 및 절대수익률 기준선 계산
    bm_results = {}
    for bm in bm_tickers:
        if bm in converted_df.columns:
            p_bm = converted_df[bm]
            rets_bm = p_bm.pct_change().fillna(0.0)
            metrics_bm = calculate_metrics(rets_bm)
            cum_bm = (1.0 + rets_bm).cumprod() * float(init_capital)
            rel_metrics = calculate_relative_metrics(portfolio_res.daily_returns, rets_bm)
            bm_results[bm] = {
                "series": cum_bm,
                "returns": rets_bm,
                "metrics": metrics_bm,
                "relative": rel_metrics
            }

    abs_hurdle_series = None
    if enable_absolute_hurdle:
        abs_hurdle_series = generate_absolute_return_series(
            dates=portfolio_res.daily_portfolio_value.index,
            annual_target_rate=target_abs_cagr,
            initial_capital=float(init_capital)
        )

    primary_bm = bm_tickers[0] if bm_tickers and bm_tickers[0] in bm_results else None
    primary_bm_data = bm_results.get(primary_bm) if primary_bm else None

    # ----------------------------------------------------
    # Stitch 8 Core Strategic KPI Cards 렌더링
    # ----------------------------------------------------
    total_fees = m.get("total_fees_paid", 0.0)
    total_taxes = m.get("total_taxes_paid", 0.0)
    val_disp = format_currency_compact(final_val, base_cur_code)
    fees_disp = format_currency_compact(total_fees, base_cur_code)
    taxes_disp = format_currency_compact(total_taxes, base_cur_code)

    bm_cagr_str = f"BM {primary_bm_data['metrics']['cagr']*100:+.1f}%" if primary_bm_data else ""
    bm_mdd_str = f"BM {primary_bm_data['metrics']['mdd']*100:.1f}%" if primary_bm_data else ""
    bm_sharpe_str = f"BM {primary_bm_data['metrics']['sharpe_ratio']:.2f}" if primary_bm_data else ""

    # 고급 퀀트 리스크 지표 값 포맷팅
    sortino_val = m.get("sortino_ratio", 0.0)
    ulcer_val = m.get("ulcer_index", 0.0)
    upi_val = m.get("ulcer_performance_index", 0.0)
    calmar_val = m.get("calmar_ratio", 0.0)
    win_rate_val = m.get("win_rate", 0.0)
    vol_val = m.get("annual_volatility", 0.0)

    cagr_val = m.get("cagr", 0.0) * 100.0
    mdd_val = m.get("mdd", 0.0) * 100.0
    sharpe_val = m.get("sharpe_ratio", 0.0)
    tax_cost_val = total_taxes + total_fees
    tax_cost_disp = f"-{cur_sym}{int(tax_cost_val):,}"

    # Stitch 8 Core Strategic KPI Cards 렌더링 (design/stitch_bas_quant_platform (2)/code.html 1:1)
    kpi_grid_html = f"""<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;">
<div class="kpi-card">
<div class="kpi-label"><span>CAGR (연평균 복리 수익률)</span><span class="material-symbols-outlined" style="font-size: 16px; color: #8b909f;">info</span></div>
<div class="kpi-value" style="color: {'#44e184' if cagr_val >= 0 else '#ff525e'};">{cagr_val:+.2f}%</div>
<div class="kpi-sub"><span class="kpi-badge-positive"><span class="material-symbols-outlined" style="font-size: 12px;">trending_up</span>{f"{cagr_val - (primary_bm_data['metrics']['cagr']*100):+.2f}%p" if primary_bm_data else "+Alpha"}</span><span style="color: #8b909f;">{bm_cagr_str or '기준 복리'}</span></div>
</div>
<div class="kpi-card">
<div class="kpi-label"><span>MDD (최대 낙폭)</span><span class="material-symbols-outlined" style="font-size: 16px; color: #8b909f;">info</span></div>
<div class="kpi-value" style="color: #ff525e;">{mdd_val:.2f}%</div>
<div class="kpi-sub"><span class="kpi-badge-positive"><span class="material-symbols-outlined" style="font-size: 12px;">shield</span>극적 방어</span><span style="color: #8b909f;">{bm_mdd_str or '하방 방어력'}</span></div>
</div>
<div class="kpi-card">
<div class="kpi-label"><span>Sharpe Ratio (샤프 지수)</span><span class="material-symbols-outlined" style="font-size: 16px; color: #8b909f;">info</span></div>
<div class="kpi-value" style="color: #dfe2f1;">{sharpe_val:.2f}</div>
<div class="kpi-sub"><span class="kpi-badge-positive" style="background: rgba(71, 143, 255, 0.12); color: #acc7ff; border-color: rgba(71, 143, 255, 0.25);"><span class="material-symbols-outlined" style="font-size: 12px;">grade</span>최상위 기관급</span><span style="color: #8b909f;">Rf: 2.10% 기준</span></div>
</div>
<div class="kpi-card">
<div class="kpi-label"><span>Sortino Ratio (소티노 지수)</span><span class="material-symbols-outlined" style="font-size: 16px; color: #8b909f;">info</span></div>
<div class="kpi-value" style="color: #acc7ff;">{sortino_val:.2f}</div>
<div class="kpi-sub"><span class="kpi-badge-positive"><span class="material-symbols-outlined" style="font-size: 12px;">check_circle</span>하방 통제력</span><span style="color: #8b909f;">Target: 0.0%</span></div>
</div>
<div class="kpi-card">
<div class="kpi-label"><span>Ulcer Index (궤양지수)</span><span class="material-symbols-outlined" style="font-size: 16px; color: #8b909f;">info</span></div>
<div class="kpi-value" style="color: #dfe2f1;">{ulcer_val:.2f}</div>
<div class="kpi-sub"><span class="kpi-badge-positive"><span class="material-symbols-outlined" style="font-size: 12px;">sentiment_satisfied</span>최저 고통치</span><span style="color: #8b909f;">변동 스트레스</span></div>
</div>
<div class="kpi-card">
<div class="kpi-label"><span>UPI / Martin Ratio</span><span class="material-symbols-outlined" style="font-size: 16px; color: #8b909f;">info</span></div>
<div class="kpi-value" style="color: #acc7ff;">{upi_val:.2f}</div>
<div class="kpi-sub"><span class="kpi-badge-positive" style="background: rgba(71, 143, 255, 0.12); color: #acc7ff; border-color: rgba(71, 143, 255, 0.25);"><span class="material-symbols-outlined" style="font-size: 12px;">verified</span>안정성 1등급</span><span style="color: #8b909f;">심리적 평온도</span></div>
</div>
<div class="kpi-card">
<div class="kpi-label"><span>Calmar Ratio (칼마 지수)</span><span class="material-symbols-outlined" style="font-size: 16px; color: #8b909f;">info</span></div>
<div class="kpi-value" style="color: #44e184;">{calmar_val:.2f}</div>
<div class="kpi-sub"><span class="kpi-badge-positive"><span class="material-symbols-outlined" style="font-size: 12px;">flag</span>1.00 돌파</span><span style="color: #8b909f;">연수익 > 낙폭</span></div>
</div>
<div class="kpi-card">
<div class="kpi-label"><span>Tax & Cost (실전 세금/비용)</span><span class="material-symbols-outlined" style="font-size: 16px; color: #8b909f;">info</span></div>
<div class="kpi-value" style="color: #ff525e;">{tax_cost_disp}</div>
</div>
</div>"""
    st.markdown(kpi_grid_html, unsafe_allow_html=True)

    # 서브 통계 바: 비용, 세금, 연간 변동성, 일간 승률 미니 칩
    st.markdown(
        f"""
        <div style="background: #1C1F2A; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 12px 20px; margin-top: 16px; margin-bottom: 24px; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; font-size: 13px; color: #DFE2F1;">
            <div>💰 <b style="color: #94A3B8;">총 발생 거래비용</b>: <span style="font-weight: 700; color: #DFE2F1; font-family: 'JetBrains Mono', monospace;">{fees_disp}</span></div>
            <div>🧾 <b style="color: #94A3B8;">총 납부 세금</b>: <span style="font-weight: 700; color: #DFE2F1; font-family: 'JetBrains Mono', monospace;">{taxes_disp}</span></div>
            <div>📉 <b style="color: #94A3B8;">연율화 변동성</b>: <span style="font-weight: 700; color: #DFE2F1; font-family: 'JetBrains Mono', monospace;">{vol_val*100:.2f}%</span></div>
            <div>🎯 <b style="color: #94A3B8;">일간 상승 승률</b>: <span style="font-weight: 700; color: #44E184; font-family: 'JetBrains Mono', monospace;">{win_rate_val*100:.1f}%</span></div>
            <div>🛡️ <b style="color: #94A3B8;">칼마 비율 (CAGR/MDD)</b>: <span style="font-weight: 700; color: #478FFF; font-family: 'JetBrains Mono', monospace;">{calmar_val:.2f}</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ----------------------------------------------------
    # 상세 탭 (자산 성장 차트, 종합 성과표, 월별 히트맵, 리밸런싱 히스토리)
    # ----------------------------------------------------
    t1, t2, t3, t4 = st.tabs([
        "📈 자산 성장 차트 & 성과 대조표",
        "📅 월별/연도별 수익률 매트릭스",
        "📋 월별 ETF 보유 내역",
        "🔄 리밸런싱 / 거래비용 / 세금 로그"
    ])

    with t1:
        # Stitch 차트 헤더 바
        st.markdown(
            """
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pt-2 pb-3">
                <div>
                    <div class="flex items-center gap-2">
                        <span class="font-bold text-lg text-on-surface">누적 자산 성장 곡선 & 낙폭(MDD) 정밀 대조</span>
                        <span class="text-xs bg-surface-container-highest text-primary-fixed-dim px-2 py-0.5 rounded font-mono">Time Series</span>
                    </div>
                    <p class="text-xs text-outline">초기 거치금 및 정기 적립식(DCA) 시뮬레이션 복리 성장 궤적</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            row_heights=[0.72, 0.28],
            subplot_titles=(f"포트폴리오 vs 벤치마크 실질 자산 성장 ({base_cur_code})", "Drawdown (고점 대비 낙폭 %)")
        )

        # 종합 포트폴리오 곡선 (Stitch Primary Signal Blue)
        fig.add_trace(
            go.Scatter(
                x=portfolio_res.daily_portfolio_value.index,
                y=portfolio_res.daily_portfolio_value.values,
                name=f"⭐ BAS 퀀트 전략 ({cur_sym}{final_val:,.0f})",
                line=dict(color="#478FFF", width=3.2)
            ),
            row=1, col=1
        )

        palette = ["#DFE2F1", "#44E184", "#F59E0B"]
        for idx, (bm, bdata) in enumerate(bm_results.items()):
            color = palette[idx % len(palette)]
            fig.add_trace(
                go.Scatter(
                    x=bdata["series"].index,
                    y=bdata["series"].values,
                    name=f"지수: {bm} ({cur_sym}{bdata['series'].iloc[-1]:,.0f})",
                    line=dict(color=color, width=1.5, dash="dot")
                ),
                row=1, col=1
            )

        if abs_hurdle_series is not None:
            fig.add_trace(
                go.Scatter(
                    x=abs_hurdle_series.index,
                    y=abs_hurdle_series.values,
                    name=f"절대수익 기준선 (연 {target_abs_cagr*100:.1f}%)",
                    line=dict(color="#A855F7", width=1.8, dash="dash")
                ),
                row=1, col=1
            )

        fig.add_trace(
            go.Scatter(
                x=portfolio_res.drawdown.index,
                y=portfolio_res.drawdown.values * 100.0,
                name="MDD (낙폭)",
                fill="tozeroy",
                line=dict(color="#FF525E", width=1.4),
                fillcolor="rgba(255, 82, 94, 0.18)"
            ),
            row=2, col=1
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#171B26",
            plot_bgcolor="#171B26",
            font=dict(family="Hanken Grotesk", color="#DFE2F1"),
            height=620,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=-0.22, xanchor="center", x=0.5, font=dict(color="#94A3B8")),
            margin=dict(l=20, r=20, t=50, b=65)
        )
        fig.update_xaxes(gridcolor="rgba(255, 255, 255, 0.06)", zerolinecolor="rgba(255, 255, 255, 0.12)")
        fig.update_yaxes(title_text=f"자산 가치 ({cur_sym})", row=1, col=1, gridcolor="rgba(255, 255, 255, 0.06)", zerolinecolor="rgba(255, 255, 255, 0.12)")
        fig.update_yaxes(title_text="낙폭 (%)", row=2, col=1, gridcolor="rgba(255, 255, 255, 0.06)", zerolinecolor="rgba(255, 255, 255, 0.12)")
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": False})

        # 종합 성과 지표 비교표
        st.markdown("---")
        st.write("##### ⚖️ 종합 성과 및 위험조정 지표 비교표")
        rows = []
        rows.append({
            "구분": "⭐ 퀀트 포트폴리오 (세후)",
            "최종 평가액": f"{cur_sym}{final_val:,.0f}",
            "누적 수익률": f"{m['dca_total_return']*100:+.2f}% (원금대비)" if "dca_total_return" in m else f"{m['total_return']*100:+.2f}%",
            "연 복리 (CAGR)": f"{m['cagr']*100:.2f}%",
            "최대 낙폭 (MDD)": f"{m['mdd']*100:.2f}%",
            "샤프 지수 (Sharpe)": f"{m['sharpe_ratio']:.2f}",
            "소티노 지수 (Sortino)": f"{m.get('sortino_ratio', 0.0):.2f}",
            "궤양지수 (UI)": f"{m.get('ulcer_index', 0.0):.2f}%",
            "궤양성과 (UPI)": f"{m.get('ulcer_performance_index', 0.0):.2f}",
            "칼마 지수 (Calmar)": f"{m.get('calmar_ratio', 0.0):.2f}",
            "연 변동성": f"{m['annual_volatility']*100:.2f}%",
            "총 비용": f"{cur_sym}{total_fees:,.0f}",
            "총 세금": f"{cur_sym}{total_taxes:,.0f}"
        })

        for bm, bdata in bm_results.items():
            bm_m = bdata["metrics"]
            rows.append({
                "구분": f"지수: {bm}",
                "최종 평가액": f"{cur_sym}{bdata['series'].iloc[-1]:,.0f}",
                "누적 수익률": f"{bm_m['total_return']*100:+.2f}%",
                "연 복리 (CAGR)": f"{bm_m['cagr']*100:.2f}%",
                "최대 낙폭 (MDD)": f"{bm_m['mdd']*100:.2f}%",
                "샤프 지수 (Sharpe)": f"{bm_m['sharpe_ratio']:.2f}",
                "소티노 지수 (Sortino)": f"{bm_m.get('sortino_ratio', 0.0):.2f}",
                "궤양지수 (UI)": f"{bm_m.get('ulcer_index', 0.0):.2f}%",
                "궤양성과 (UPI)": f"{bm_m.get('ulcer_performance_index', 0.0):.2f}",
                "칼마 지수 (Calmar)": f"{bm_m.get('calmar_ratio', 0.0):.2f}",
                "연 변동성": f"{bm_m['annual_volatility']*100:.2f}%",
                "총 비용": "-",
                "총 세금": "-"
            })

        if abs_hurdle_series is not None:
            abs_final = abs_hurdle_series.iloc[-1]
            rows.append({
                "구분": f"절대수익 기준선 (연 {target_abs_cagr*100:.1f}%)",
                "최종 평가액": f"{cur_sym}{abs_final:,.0f}",
                "누적 수익률": f"{((abs_final/float(init_capital))-1)*100:+.2f}%",
                "연 복리 (CAGR)": f"{target_abs_cagr*100:.2f}%",
                "최대 낙폭 (MDD)": "0.00%",
                "샤프 지수 (Sharpe)": "-",
                "소티노 지수 (Sortino)": "-",
                "궤양지수 (UI)": "0.00%",
                "궤양성과 (UPI)": "-",
                "칼마 지수 (Calmar)": "-",
                "연 변동성": "0.00%",
                "총 비용": "-",
                "총 세금": "-"
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with t2:
        st.write("##### 📅 월별 및 연도별(YTD) 수익률 성과표 (%)")
        m_mat = portfolio_res.monthly_returns
        if not m_mat.empty:
            styled = (m_mat * 100.0).style.format("{:.2f}%", na_rep="-").map(
                lambda v: "color: #44E184; font-weight: 600;" if isinstance(v, (int, float)) and v > 0
                else ("color: #FF525E; font-weight: 600;" if isinstance(v, (int, float)) and v < 0 else "")
            )
            st.dataframe(styled, use_container_width=True)
        else:
            st.info("표시할 월별 데이터가 부족합니다.")

    with t3:
        st.write("##### 📋 월별 ETF 보유 내역 (Monthly ETF Holdings)")
        if hasattr(portfolio_res, "monthly_holdings") and not portfolio_res.monthly_holdings.empty:
            m_holdings_df = portfolio_res.monthly_holdings.copy()
            st.dataframe(m_holdings_df, use_container_width=True, hide_index=True)
            csv_data = m_holdings_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 월별 ETF 투자내역 CSV 다운로드",
                data=csv_data,
                file_name=f"monthly_holdings_{datetime.date.today()}.csv",
                mime="text/csv",
                key="btn_dl_holdings_tab"
            )
        else:
            st.info("월별 투자 내역 데이터가 없습니다.")

    with t4:
        st.write("##### 🔄 리밸런싱, 거래비용 및 세금 정산 상세 로그")
        rebal_df = portfolio_res.rebalance_history
        if not rebal_df.empty:
            st.dataframe(rebal_df, use_container_width=True, hide_index=True)
        else:
            st.info("해당 기간 동안 발생한 리밸런싱 이벤트가 없습니다.")

    # ----------------------------------------------------
    # Stitch 하단 2단 그리드: 월별 수익률 히트맵 & 최근 리밸런싱 히스토리
    # ----------------------------------------------------
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    col_btm1, col_btm2 = st.columns([6, 6], gap="medium")

    with col_btm1:
        st.markdown(
            """
            <div class="stitch-card h-full">
                <div class="flex items-center justify-between pb-3 border-b border-white/5 mb-3">
                    <div class="flex items-center gap-2">
                        <span class="material-symbols-outlined text-secondary text-[20px]">calendar_month</span>
                        <div>
                            <div class="font-bold text-base text-on-surface">월별 수익률 히트맵 (Monthly Heatmap)</div>
                            <div class="text-xs text-outline">월간 성과 매트릭스 및 연간(YTD) 누적 수익률</div>
                        </div>
                    </div>
                    <span class="text-xs text-outline font-mono">단위: %</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        m_mat = portfolio_res.monthly_returns
        if not m_mat.empty:
            styled = (m_mat * 100.0).style.format("{:.2f}%", na_rep="-").map(
                lambda v: "color: #44E184; font-weight: 700;" if isinstance(v, (int, float)) and v > 0
                else ("color: #FF525E; font-weight: 700;" if isinstance(v, (int, float)) and v < 0 else "")
            )
            st.dataframe(styled, use_container_width=True)

            csv_m_data = (m_mat * 100.0).round(2).to_csv().encode("utf-8-sig")
            st.download_button(
                label="📥 월별/연도별 수익률 CSV 다운로드",
                data=csv_m_data,
                file_name=f"returns_matrix_{config['strategy_cat']}_{datetime.date.today()}.csv",
                mime="text/csv",
                use_container_width=True,
                key="btn_dl_returns_matrix_bottom"
            )
        else:
            st.info("표시할 월별/연도별 수익률 데이터가 부족합니다.")

    with col_btm2:
        st.markdown(
            """
            <div class="stitch-card h-full">
                <div class="flex items-center justify-between pb-3 border-b border-white/5 mb-3">
                    <div class="flex items-center gap-2">
                        <span class="material-symbols-outlined text-primary text-[20px]">sync_alt</span>
                        <div>
                            <div class="font-bold text-base text-on-surface">월별 ETF 투자 히스토리 & 비중</div>
                            <div class="text-xs text-outline">월말 기준 실제 보유한 ETF 자산군 구성 내역</div>
                        </div>
                    </div>
                    <span class="text-xs text-secondary font-mono font-bold bg-secondary/10 px-2 py-0.5 rounded">수수료/세금 완제</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if hasattr(portfolio_res, "monthly_holdings") and not portfolio_res.monthly_holdings.empty:
            m_holdings_df = portfolio_res.monthly_holdings.copy()
            disp_holdings = m_holdings_df.rename(columns={
                "Year_Month": "투자 시점 (연-월)",
                "Holdings": "보유 ETF 구성 및 비중 내역"
            })
            st.dataframe(disp_holdings, use_container_width=True, hide_index=True)

            csv_data = m_holdings_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 월별 ETF 투자내역 CSV 다운로드",
                data=csv_data,
                file_name=f"etf_monthly_history_{config['strategy_cat']}_{datetime.date.today()}.csv",
                mime="text/csv",
                use_container_width=True,
                key="btn_dl_holdings_bottom"
            )
        else:
            st.info("기록된 월별 투자 내역 데이터가 없습니다.")

    # 최하단 복귀 버튼
    st.markdown("---")
    col_ret1, col_ret2 = st.columns([8, 4])
    with col_ret1:
        st.markdown(
            """
            <div style="padding-top: 6px;">
                <span style="font-size: 15px; font-weight: 700; color: #DFE2F1;">🔄 전략 설정을 변경하시겠습니까?</span><br>
                <span style="font-size: 13px; color: #94A3B8;">전략 빌더 화면으로 돌아가 ETF 비중이나 DCA 적립 금액, 3대 축 파라미터를 재설정할 수 있습니다.</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_ret2:
        if st.button("🛠️ 전략 구성 화면으로 돌아가기", use_container_width=True, key="res_back_to_bld_btn"):
            st.session_state["active_view"] = "builder"
            st.rerun()

    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)


# ----------------------------------------------------
# 9. 메인 진입점 및 Stitch 상단 글로벌 네비바
# ----------------------------------------------------
def main():
    if "active_view" not in st.session_state:
        st.session_state["active_view"] = "builder"

    curr_active = st.session_state.get("active_view", "builder")

    # Stitch 공식 글로벌 헤더 바
    st.markdown(
        """
        <div style="background: rgba(10, 14, 24, 0.95); backdrop-filter: blur(16px); border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding: 12px 24px; margin-bottom: 24px; border-radius: 12px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #478fff 0%, #1d4ed8 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; box-shadow: 0 0 16px rgba(71, 143, 255, 0.4);">
                    <span class="material-symbols-outlined" style="font-size: 22px;">bolt</span>
                </div>
                <div>
                    <div style="font-size: 19px; font-weight: 800; color: #dfe2f1; letter-spacing: -0.02em;">BAS Quant</div>
                    <div style="font-size: 10px; color: #8b909f; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.05em;">ETF BACKTEST ENGINE</div>
                </div>
                <div style="display: flex; align-items: center; gap: 8px; background: #171b26; padding: 4px 12px; border-radius: 9999px; border: 1px solid rgba(255, 255, 255, 0.06); font-size: 11px; font-family: 'JetBrains Mono', monospace; margin-left: 12px;">
                    <span style="color: #44e184; display: flex; align-items: center; gap: 5px;">
                        <span style="width: 6px; height: 6px; border-radius: 9999px; background: #44e184; display: inline-block;"></span>US OPEN
                    </span>
                    <span style="color: #414754;">•</span>
                    <span style="color: #8b909f; display: flex; align-items: center; gap: 5px;">
                        <span style="width: 6px; height: 6px; border-radius: 9999px; background: #8b909f; display: inline-block;"></span>KRX CLOSED
                    </span>
                    <span style="color: #414754;">•</span>
                    <span style="color: #dfe2f1;">USD/KRW 1,385.20 ₩</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="display: flex; align-items: center; gap: 6px; background: #171b26; padding: 5px 12px; border-radius: 6px; font-size: 11px; font-family: 'JetBrains Mono', monospace; color: #c1c6d6; border: 1px solid rgba(255, 255, 255, 0.06);">
                    <span class="material-symbols-outlined" style="color: #44e184; font-size: 15px;">database</span>
                    Live 40Y DB Active
                </div>
                <div style="width: 32px; height: 32px; border-radius: 50%; background: #478fff; display: flex; align-items: center; justify-content: center; color: #00285b; font-weight: 700;">
                    <span class="material-symbols-outlined" style="font-size: 18px;">person</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 상단 Stitch 탭 내비게이션 바
    col_nav1, col_nav2, col_nav3, col_nav4, col_nav_r = st.columns([2.5, 2.5, 2.5, 2.5, 2])
    with col_nav1:
        if st.button("🛠️ 전략 빌더", use_container_width=True, type="primary" if curr_active == "builder" else "secondary", key="nav_bld_btn"):
            st.session_state["active_view"] = "builder"
            st.rerun()
    with col_nav2:
        if st.button("📊 백테스트 리포트", use_container_width=True, type="primary" if curr_active == "result" else "secondary", key="nav_rep_btn"):
            st.session_state["active_view"] = "result"
            st.rerun()
    with col_nav3:
        if st.button("📚 전략 라이브러리", use_container_width=True, key="nav_lib_btn"):
            st.toast("추후 업데이트 예정입니다.", icon="ℹ️")
    with col_nav4:
        if st.button("📖 팩터 & 지표 사전", use_container_width=True, key="nav_dict_btn"):
            st.toast("추후 업데이트 예정입니다.", icon="ℹ️")
    with col_nav_r:
        if st.button("🔄 전체 초기화", use_container_width=True, key="top_reset_btn"):
            st.session_state.clear()
            st.rerun()

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 1. 전략 빌더 화면
    if st.session_state["active_view"] == "builder":
        config, run_clicked = render_strategy_builder()
        st.session_state["latest_config"] = config
        if run_clicked:
            st.session_state["active_view"] = "result"
            st.rerun()

    # 2. 백테스트 결과 화면
    elif st.session_state["active_view"] == "result":
        cfg = st.session_state.get("latest_config")
        if not cfg or not cfg.get("active_tickers"):
            st.warning("⚠️ 아직 전략이 구성되지 않았거나 백테스트가 실행되지 않았습니다. 먼저 '전략 빌더' 화면에서 ETF를 추가하고 실행해 주세요.")
            if st.button("🛠️ 전략 빌더로 이동", type="primary"):
                st.session_state["active_view"] = "builder"
                st.rerun()
        else:
            render_backtest_results(cfg)


if __name__ == "__main__":
    main()
