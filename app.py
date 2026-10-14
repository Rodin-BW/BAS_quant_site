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
# 2. 프리미엄 핀테크 모던 UI 스타일시트
# ----------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }
    
    /* 레이아웃 & 패딩 */
    .block-container {
        padding-top: 2.2rem !important;
        padding-bottom: 9rem !important;
        max-width: 1400px !important;
    }
    
    /* 사이드바 숨김 */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* 헤더 카드 */
    .app-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        color: white;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.25);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .app-header-title {
        font-size: 24px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .app-header-sub {
        font-size: 13px;
        color: #94A3B8;
        margin-top: 4px;
        font-weight: 400;
    }
    
    /* 카드 컴포넌트 */
    .section-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 22px 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* 전략 선택 필(Pill) 스타일 */
    .strategy-pill {
        border-radius: 12px;
        padding: 16px 20px;
        border: 1.5px solid #E2E8F0;
        cursor: pointer;
        transition: all 0.2s ease;
        background: #F8FAFC;
    }
    .strategy-pill.active {
        border-color: #2563EB;
        background: #EFF6FF;
    }
    
    /* KPI 메트릭 카드 */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 16px;
        text-align: left;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        height: 100%;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }
    .kpi-label {
        font-size: 12px;
        font-weight: 600;
        color: #64748B;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .kpi-value {
        font-size: 21px;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.15;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .kpi-sub {
        font-size: 11px;
        font-weight: 600;
        white-space: nowrap;
    }
    .kpi-stat-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    
    /* 뱃지 슬라이더 아이템 */
    .asset-item-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    
    /* Streamlit 라디오 & 탭 정돈 */
    div[data-testid="stRadio"] > div {
        gap: 12px;
    }
    
    /* 버튼 호버 */
    button[kind="primary"] {
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 0.6rem 1.2rem !important;
        background: #2563EB !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
    }
    button[kind="primary"]:hover {
        background: #1D4ED8 !important;
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.4) !important;
    }
    button[kind="secondary"] {
        border-radius: 10px !important;
        font-weight: 600 !important;
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
                        <span style='background: #0F172A; color: white; font-weight: 700; padding: 3px 8px; border-radius: 6px; font-size: 13px;'>{t}</span>
                        <span style='font-size: 13px; font-weight: 600; color: #334155;'>{desc}</span>
                    </div>
                    <span style='background: #EFF6FF; border: 1px solid #BFDBFE; color: #1D4ED8; font-weight: 700; padding: 2px 8px; border-radius: 8px; font-size: 13px;'>{curr_val:.1f}%</span>
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
    bar_color = "#10B981" if is_exact_100 else ("#F59E0B" if tot_w < 100.0 else "#EF4444")
    status_txt = "🟢 100.0% 완벽한 균형" if is_exact_100 else (f"🟠 {100.0 - tot_w:.1f}%p 부족" if tot_w < 100.0 else f"🔴 {tot_w - 100.0:.1f}%p 초과")

    st.markdown(
        f"""
        <div style='background-color: #F8FAFC; border-radius: 8px; padding: 10px 14px; margin-top: 10px; display: flex; justify-content: space-between; align-items: center; border-left: 5px solid {bar_color};'>
            <span style='font-size: 13px; color: #475569;'><b>목표 비중 합계</b>: {status_txt}</span>
            <span style='font-size: 17px; font-weight: 800; color: {bar_color};'>{tot_w:.1f}%</span>
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
        fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": False})
        return

    labels = []
    values = []
    palette = ["#2563EB", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#06B6D4", "#EC4899", "#6366F1"]
    for t, w in valid_items.items():
        desc = POPULAR_ETF_CATALOG.get(t, t).split(" | ")[-1] if " | " in POPULAR_ETF_CATALOG.get(t, t) else t
        labels.append(f"{t} ({desc[:7]})")
        values.append(w)

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        textinfo="percent",
        hoverinfo="label+value+percent",
        marker=dict(colors=palette[:len(labels)], line=dict(color='#FFFFFF', width=2))
    )])
    tot = sum(values)
    center_col = "#10B981" if abs(tot - 100.0) < 0.1 else "#F59E0B"
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=11)),
        height=320,
        margin=dict(l=10, r=10, t=10, b=30),
        annotations=[dict(
            text=f"<span style='font-size:12px;color:#64748B;'>총 자산</span><br><b style='font-size:20px;color:{center_col};'>{len(values)}개</b><br><span style='font-size:11px;color:#64748B;'>합계 {tot:.1f}%</span>",
            x=0.5, y=0.5,
            showarrow=False
        )]
    )
    st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": False})


# ----------------------------------------------------
# 6. 전략 빌더 화면 (메인 구성)
# ----------------------------------------------------
def render_strategy_builder():
    # Step 1: 전략 선택
    st.markdown("#### 🛠️ Step 1. 운용할 전략 선택")
    col_st1, col_st2 = st.columns(2)
    
    # 세션 상태 전략 저장
    curr_strat = st.session_state.get("selected_strategy", "static")
    with col_st1:
        st_clicked = st.button(
            "🏛️ 정적 자산배분 (올웨더 / 60/40 / 영구 포트폴리오)",
            use_container_width=True,
            type="primary" if curr_strat == "static" else "secondary"
        )
        if st_clicked:
            st.session_state["selected_strategy"] = "static"
            st.rerun()
            
    with col_st2:
        tp_clicked = st.button(
            "⚡ 나스닥 레버리지 트라이포드 (3대 축: 현금스위칭 · MDD분할 · RSI과매도)",
            use_container_width=True,
            type="primary" if curr_strat == "tripod" else "secondary"
        )
        if tp_clicked:
            st.session_state["selected_strategy"] = "tripod"
            st.rerun()

    is_tripod = (st.session_state.get("selected_strategy", "static") == "tripod")
    strategy_cat = "🏛️ 나스닥 레버리지 트라이포드" if is_tripod else "정적 자산배분 (올웨더, 영구, 60/40, 커스텀)"

    st.markdown("---")
    
    # Step 2: 자산 배분 & 포트폴리오 설정
    st.markdown("#### 🎨 Step 2. 포트폴리오 구성 및 목표 비중")
    col_left, col_right = st.columns([5.5, 4.5])

    active_tickers = []
    tripod_params = {}
    weights = {}
    rebal_freq = "M"
    band_pct = None

    with col_left:
        if not is_tripod:
            preset_choice = st.selectbox(
                "전략 프리셋 불러오기",
                options=list(STATIC_PRESETS.keys()) + ["직접 입력/커스텀"],
                key="bld_st_preset"
            )
            default_dict = STATIC_PRESETS.get(preset_choice, {"SPY": 0.4, "QQQ": 0.3, "069500.KS": 0.3})
            weights = render_static_asset_builder(
                key_prefix="bld_static",
                default_dict=default_dict,
                preset_choice=preset_choice
            )
            active_tickers = list(weights.keys())

            col_rf1, col_rf2 = st.columns(2)
            with col_rf1:
                rebal_freq = st.selectbox("정기 리밸런싱 주기", ["M (월간)", "Q (분기)", "Y (연간)", "None (Buy & Hold)"], index=0, key="bld_rfreq")
            with col_rf2:
                use_band = st.checkbox("허용 오차 밴드 리밸런싱 적용", value=True, key="bld_uband")
            if use_band:
                band_val = st.slider("허용 오차폭 (±%p)", 1.0, 20.0, 5.0, step=0.5, key="bld_bval")
                band_pct = band_val / 100.0

        else:
            st.markdown(
                """
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 14px 18px; margin-bottom: 14px;">
                    <div style="font-weight: 700; color: #0F172A; font-size: 14px; margin-bottom: 4px;">💡 나스닥 레버리지 트라이포드(Tripod) 전략 원리</div>
                    <div style="font-size: 12px; color: #64748B; line-height: 1.5;">
                        평상시 상시 현금(30%)과 QQQ/QLD로 복리를 추구하며 음의 복리를 방어하다가, 
                        시장이 폭락할 때 과거 40년 MDD 마일스톤 및 RSI 과매도 신호에 따라 예비 현금을 3배 레버리지(TQQQ)로 기계적 분할 전환합니다.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # 3대 축 파라미터 간결한 카드 구성
            with st.container(border=True):
                st.markdown("##### 1️⃣ 제1축: 자산 배분 & 상시 현금 비중")
                col_t1, col_t2, col_t3 = st.columns(3)
                with col_t1:
                    tp_base = st.text_input("1배수 기준 ETF", value="QQQ", key="tp_base")
                with col_t2:
                    tp_2x = st.text_input("2배수 레버리지", value="QLD", key="tp_2x")
                with col_t3:
                    tp_3x = st.text_input("3배수 레버리지", value="TQQQ", key="tp_3x")

                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    tp_cash_pct = st.slider("평상시 현금 비중 (%)", 10.0, 50.0, 30.0, step=5.0, key="tp_cash_pct")
                with col_c2:
                    tp_qld_ratio = st.slider("투자금 중 2배수(QLD) 비율 (%)", 0.0, 100.0, 50.0, step=5.0, key="tp_qld_ratio")

            with st.container(border=True):
                st.markdown("##### 2️⃣ 제2축: MDD 기준 분할 매수 타점")
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    tp_mdd1 = st.number_input("1차 조정 MDD (%)", -25.0, -5.0, -10.0, step=1.0, key="tp_mdd1")
                with col_m2:
                    tp_mdd2 = st.number_input("2차 하락 MDD (%)", -35.0, -10.0, -20.0, step=1.0, key="tp_mdd2")
                with col_m3:
                    tp_mdd3 = st.number_input("3차 대폭락 MDD (%)", -60.0, -20.0, -30.0, step=1.0, key="tp_mdd3")

            with st.container(border=True):
                st.markdown("##### 3️⃣ 제3축: RSI 과매도 기술적 지표")
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    tp_rsi1 = st.slider("1차 과매도 기준 (RSI)", 30.0, 50.0, 40.0, step=1.0, key="tp_rsi1")
                with col_r2:
                    tp_rsi2 = st.slider("극단적 공포 기준 (RSI)", 15.0, 35.0, 30.0, step=1.0, key="tp_rsi2")

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

    with col_right:
        st.markdown("###### 📊 평상시 포트폴리오 목표 비중 시각화")
        render_clean_donut_chart(weights)

    st.markdown("---")

    # Step 3: 시뮬레이션 환경 & DCA 세팅
    st.markdown("#### ⚙️ Step 3. 시뮬레이션 환경 & DCA(적립식) 세팅")
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)

    with col_e1:
        st.markdown("###### 1. 통화 & 자본금")
        base_cur_choice = st.radio("기준 통화", ["🇰🇷 KRW (원화)", "🇺🇸 USD (달러)"], index=0, key="bld_cur", horizontal=True)
        base_cur_code = "KRW" if "KRW" in base_cur_choice else "USD"
        cur_sym = "₩" if base_cur_code == "KRW" else "$"
        
        default_cap_str = "100,000,000" if base_cur_code == "KRW" else "100,000"
        init_cap_input = st.text_input(
            f"초기 자본금 ({base_cur_code})",
            value=st.session_state.get(f"bld_cap_{base_cur_code}", default_cap_str),
            help="세 자리마다 콤마(,)가 포함된 금액으로 입력할 수 있습니다.",
            key=f"bld_cap_input_{base_cur_code}"
        )
        # 콤마 및 특수문자 제거 후 정수 변환
        cleaned_cap = re.sub(r"[^\d]", "", init_cap_input)
        init_capital = float(cleaned_cap) if cleaned_cap else (100000000.0 if base_cur_code == "KRW" else 100000.0)
        st.session_state[f"bld_cap_{base_cur_code}"] = f"{int(init_capital):,}"
        st.caption(f"💵 적용 금액: **{cur_sym}{int(init_capital):,}** ({format_currency_compact(init_capital, base_cur_code)})")

        enable_dca = st.checkbox("💵 DCA 정기 적립식 투자", value=False, key="bld_dca_chk")
        dca_amount = 0.0
        dca_freq = "M"
        if enable_dca:
            default_dca_str = "1,000,000" if base_cur_code == "KRW" else "1,000"
            dca_input = st.text_input(
                f"정기 납입액 ({base_cur_code})",
                value=st.session_state.get(f"bld_dca_{base_cur_code}", default_dca_str),
                help="세 자리마다 콤마(,)가 포함된 금액으로 입력할 수 있습니다.",
                key=f"bld_dca_input_{base_cur_code}"
            )
            cleaned_dca = re.sub(r"[^\d]", "", dca_input)
            dca_amount = float(cleaned_dca) if cleaned_dca else (1000000.0 if base_cur_code == "KRW" else 1000.0)
            st.session_state[f"bld_dca_{base_cur_code}"] = f"{int(dca_amount):,}"
            st.caption(f"💵 적용 납입액: **{cur_sym}{int(dca_amount):,}** ({format_currency_compact(dca_amount, base_cur_code)})")

            dca_freq_choice = st.selectbox("적립 주기", ["월간 (매월 1회)", "연간 (매년 1회)"], index=0, key="bld_dca_fq")
            dca_freq = "M" if "월간" in dca_freq_choice else "Y"

    with col_e2:
        st.markdown("###### 2. 백테스트 기간")
        today = datetime.date.today()
        start_date = st.date_input("시작일", value=today - datetime.timedelta(days=365 * 6), key="bld_sdate")
        end_date = st.date_input("종료일", value=today, key="bld_edate")
        if start_date >= end_date:
            st.error("⚠️ 시작일은 종료일보다 이전이어야 합니다.")

    with col_e3:
        st.markdown("###### 3. 거래비용 & 슬리피지")
        commission_pct = st.number_input("매매 수수료 (%)", value=0.015, step=0.005, format="%.3f", key="bld_comm") / 100.0
        slippage_pct = st.number_input("슬리피지 (%)", value=0.05, step=0.01, format="%.2f", key="bld_slip") / 100.0
        total_fee_rate = commission_pct + slippage_pct
        st.caption(f"총 1회 거래비용: **{(total_fee_rate*100):.3f}%**")

    with col_e4:
        st.markdown("###### 4. 과세 & 벤치마크")
        apply_tax = st.checkbox("양도소득세(22%) 반영", value=True, key="bld_tax_chk")
        tax_rate = 0.22 if apply_tax else 0.0
        tax_deduction = (2500000.0 if base_cur_code == "KRW" else 2000.0) if apply_tax else 0.0

        selected_bm_labels = st.multiselect(
            "비교 벤치마크",
            options=list(BENCHMARK_PRESETS.keys()),
            default=["미국 S&P 500 (SPY)", "한국 코스피 200 (069500.KS)"],
            key="bld_bm_sel"
        )
        bm_tickers = [BENCHMARK_PRESETS[l] for l in selected_bm_labels]
        enable_absolute_hurdle = st.checkbox("절대수익률 기준선 (연 5%)", value=True, key="bld_hurdle_chk")
        target_abs_cagr = 0.05

    # 최하단 실행 액션 바
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); border-radius: 14px; padding: 22px 28px; margin-top: 32px; margin-bottom: 20px; color: white;">
            <div style="font-size: 16px; font-weight: 700; margin-bottom: 4px;">⚡ 전략 설정이 완료되었습니다</div>
            <div style="font-size: 13px; color: #94A3B8;">아래 버튼을 누르면 실시간 시뮬레이션을 실행하고 결과 분석 화면으로 이동합니다.</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    run_btn = st.button("🚀 백테스팅 실행하기 (결과 화면으로 이동) ➡️", type="primary", use_container_width=True, key="bld_run_btn")

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
    col_ret, col_meta = st.columns([2.5, 7.5])
    with col_ret:
        if st.button("⬅️ 🛠️ 전략 구성 변경하러 가기", use_container_width=True, key="btn_back_to_bld"):
            st.session_state["active_view"] = "builder"
            st.rerun()
    with col_meta:
        dca_desc = f" | **DCA 적립**: {config['dca_amount']:,.0f} {config['base_cur_code']}/({config.get('dca_freq', 'M')})" if config.get("enable_dca") else ""
        st.success(
            f"✅ **전략**: {config['strategy_cat']} | "
            f"**기간**: {config['start_date']} ~ {config['end_date']} | "
            f"**초기 자본**: {config['init_capital']:,.0f} ({config['base_cur_code']}){dca_desc}"
        )

    with st.expander("🧩 적용된 전략 및 백테스트 환경 명세", expanded=False):
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
    # KPI 요약 카드 렌더링
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

    if enable_dca and "total_contributed" in m:
        contrib_disp = format_currency_compact(m['total_contributed'], base_cur_code)
        ret_label = f"{m['dca_total_return']*100:+.1f}% (원금대비)" if "dca_total_return" in m else f"{m['total_return']*100:+.1f}%"
        kpi_cards = [
            ("총 투입 원금", contrib_disp, "DCA 적립 원금", "#64748B"),
            ("최종 세후 평가액", val_disp, f"수익률 {ret_label}", "#10B981" if final_val >= m['total_contributed'] else "#EF4444"),
            ("실질 복리 (CAGR)", f"{m['cagr']*100:.2f}%", bm_cagr_str, "#10B981" if m['cagr'] >= 0 else "#EF4444"),
            ("최대 낙폭 (MDD)", f"{m['mdd']*100:.2f}%", bm_mdd_str, "#EF4444"),
            ("샤프 지수 (Sharpe)", f"{m['sharpe_ratio']:.2f}", bm_sharpe_str or "총변동성 초과수익", "#2563EB"),
            ("소티노 지수 (Sortino)", f"{sortino_val:.2f}", "하방위험 초과수익", "#0D9488"),
            ("궤양지수 (UI)", f"{ulcer_val:.2f}%", "낙폭 깊이·기간 스트레스", "#D97706"),
            ("궤양성과 (UPI)", f"{upi_val:.2f}", "마틴 비율 (초과수익/UI)", "#7C3AED")
        ]
    else:
        ret_label = f"{m['total_return']*100:+.1f}%"
        kpi_cards = [
            ("최종 세후 평가액", val_disp, f"수익률 {ret_label}", "#10B981" if final_val >= float(init_capital) else "#EF4444"),
            ("실질 복리 (CAGR)", f"{m['cagr']*100:.2f}%", bm_cagr_str, "#10B981" if m['cagr'] >= 0 else "#EF4444"),
            ("최대 낙폭 (MDD)", f"{m['mdd']*100:.2f}%", bm_mdd_str, "#EF4444"),
            ("샤프 지수 (Sharpe)", f"{m['sharpe_ratio']:.2f}", bm_sharpe_str or "총변동성 초과수익", "#2563EB"),
            ("소티노 지수 (Sortino)", f"{sortino_val:.2f}", "하방위험 초과수익", "#0D9488"),
            ("궤양지수 (UI)", f"{ulcer_val:.2f}%", "낙폭 깊이·기간 스트레스", "#D97706"),
            ("궤양성과 (UPI)", f"{upi_val:.2f}", "마틴 비율 (초과수익/UI)", "#7C3AED"),
            ("칼마 지수 (Calmar)", f"{calmar_val:.2f}", "CAGR / MDD 비율", "#0284C7")
        ]

    # 상단 8개 지표 (2줄 4열 깔끔한 그리드 레이아웃)
    row1 = kpi_cards[:4]
    row2 = kpi_cards[4:]

    cols1 = st.columns(len(row1))
    for idx, (label, val_txt, sub_txt, sub_col) in enumerate(row1):
        with cols1[idx]:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{val_txt}</div>
                    <div class="kpi-sub" style="color: {sub_col};">{sub_txt}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    cols2 = st.columns(len(row2))
    for idx, (label, val_txt, sub_txt, sub_col) in enumerate(row2):
        with cols2[idx]:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{val_txt}</div>
                    <div class="kpi-sub" style="color: {sub_col};">{sub_txt}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 서브 통계 바: 비용, 세금, 연간 변동성, 일간 승률 미니 칩
    st.markdown(
        f"""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 10px 18px; margin-top: 12px; margin-bottom: 20px; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; font-size: 13px; color: #475569;">
            <div>💰 <b>총 발생 거래비용</b>: <span style="font-weight: 700; color: #0F172A;">{fees_disp}</span></div>
            <div>🧾 <b>총 납부 세금</b>: <span style="font-weight: 700; color: #0F172A;">{taxes_disp}</span></div>
            <div>📉 <b>연율화 변동성</b>: <span style="font-weight: 700; color: #0F172A;">{vol_val*100:.2f}%</span></div>
            <div>🎯 <b>일간 상승 승률</b>: <span style="font-weight: 700; color: #0F172A;">{win_rate_val*100:.1f}%</span></div>
            <div>🛡️ <b>칼마 비율 (CAGR/MDD)</b>: <span style="font-weight: 700; color: #0F172A;">{calmar_val:.2f}</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ----------------------------------------------------
    # 상세 탭 (자산 성장 차트, 종합 성과표, 월별 매트릭스, 투자 내역)
    # ----------------------------------------------------
    t1, t2, t3, t4 = st.tabs([
        "📈 자산 성장 차트 & 성과 비교표",
        "📅 월별/연도별 수익률 매트릭스",
        "📋 월별 ETF 보유 내역",
        "🔄 리밸런싱 / 거래비용 / 세금 로그"
    ])

    with t1:
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            row_heights=[0.7, 0.3],
            subplot_titles=(f"포트폴리오 vs 벤치마크 실질 자산 성장 ({base_cur_code})", "Drawdown (고점 대비 낙폭 %)")
        )

        # 종합 포트폴리오 곡선
        fig.add_trace(
            go.Scatter(
                x=portfolio_res.daily_portfolio_value.index,
                y=portfolio_res.daily_portfolio_value.values,
                name="⭐ 퀀트 포트폴리오",
                line=dict(color="#2563EB", width=3.2)
            ),
            row=1, col=1
        )

        palette = ["#94A3B8", "#10B981", "#F59E0B"]
        for idx, (bm, bdata) in enumerate(bm_results.items()):
            color = palette[idx % len(palette)]
            fig.add_trace(
                go.Scatter(
                    x=bdata["series"].index,
                    y=bdata["series"].values,
                    name=f"지수: {bm}",
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
                    line=dict(color="#8B5CF6", width=1.8, dash="dash")
                ),
                row=1, col=1
            )

        fig.add_trace(
            go.Scatter(
                x=portfolio_res.drawdown.index,
                y=portfolio_res.drawdown.values * 100.0,
                name="MDD (낙폭)",
                fill="tozeroy",
                line=dict(color="#EF4444", width=1.2),
                fillcolor="rgba(239, 68, 68, 0.15)"
            ),
            row=2, col=1
        )

        fig.update_layout(
            height=620,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=-0.22, xanchor="center", x=0.5),
            margin=dict(l=20, r=20, t=50, b=65)
        )
        fig.update_yaxes(title_text=f"자산 가치 ({cur_sym})", row=1, col=1)
        fig.update_yaxes(title_text="낙폭 (%)", row=2, col=1)
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
                lambda v: "color: #10B981; font-weight: 600;" if isinstance(v, (int, float)) and v > 0
                else ("color: #EF4444; font-weight: 600;" if isinstance(v, (int, float)) and v < 0 else "")
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
                mime="text/csv"
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
    # 보고서 하단: 1. 월별 및 연도별 수익률 매트릭스 (%)
    # ----------------------------------------------------
    st.markdown("---")
    st.markdown(
        """
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px 24px; margin-top: 10px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
            <div style="font-size: 16px; font-weight: 700; color: #0F172A; margin-bottom: 6px; display: flex; align-items: center; gap: 8px;">
                📅 연도별 및 월별 수익률 매트릭스 (Monthly & Annual Returns %)
            </div>
            <div style="font-size: 13px; color: #64748B;">
                시뮬레이션 전 기간 동안의 월별 실현 수익률과 연간(YTD) 누적 수익률 종합 데이터입니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    m_mat = portfolio_res.monthly_returns
    if not m_mat.empty:
        styled = (m_mat * 100.0).style.format("{:.2f}%", na_rep="-").map(
            lambda v: "color: #10B981; font-weight: 700;" if isinstance(v, (int, float)) and v > 0
            else ("color: #EF4444; font-weight: 700;" if isinstance(v, (int, float)) and v < 0 else "")
        )
        st.dataframe(styled, use_container_width=True)

        col_m_dl1, col_m_dl2 = st.columns([7, 3])
        with col_m_dl2:
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

    # ----------------------------------------------------
    # 보고서 하단: 2. 월별 ETF 투자 히스토리 요약 섹션
    # ----------------------------------------------------
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px 24px; margin-top: 10px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
            <div style="font-size: 16px; font-weight: 700; color: #0F172A; margin-bottom: 6px; display: flex; align-items: center; gap: 8px;">
                📜 월별 ETF 투자 히스토리 및 포트폴리오 비중 (Monthly Investment History)
            </div>
            <div style="font-size: 13px; color: #64748B;">
                시뮬레이션 전 기간 동안 월말 기준 실제 보유한 ETF 자산군과 비중의 변화 내역입니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if hasattr(portfolio_res, "monthly_holdings") and not portfolio_res.monthly_holdings.empty:
        m_holdings_df = portfolio_res.monthly_holdings.copy()
        
        # 가독성을 높인 컬럼 명칭 변경
        disp_holdings = m_holdings_df.rename(columns={
            "Year_Month": "투자 시점 (연-월)",
            "Holdings": "보유 ETF 구성 및 비중 내역"
        })
        st.dataframe(disp_holdings, use_container_width=True, hide_index=True)

        col_dl1, col_dl2 = st.columns([7, 3])
        with col_dl2:
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
    col_ret1, col_ret2 = st.columns([3, 1])
    with col_ret1:
        st.markdown(
            """
            <div style="padding-top: 6px;">
                <span style="font-size: 15px; font-weight: 700; color: #0F172A;">🔄 전략 설정을 변경하시겠습니까?</span><br>
                <span style="font-size: 13px; color: #64748B;">전략 구성 화면으로 돌아가 ETF 비중이나 DCA 적립 금액을 재설정할 수 있습니다.</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_ret2:
        if st.button("🛠️ 전략 구성 화면으로 돌아가기", use_container_width=True, key="res_back_to_bld_btn"):
            st.session_state["active_view"] = "builder"
            st.rerun()

    st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True)


# ----------------------------------------------------
# 9. 메인 진입점 및 화면 라우팅
# ----------------------------------------------------
def main():
    if "active_view" not in st.session_state:
        st.session_state["active_view"] = "builder"

    curr_active = st.session_state.get("active_view", "builder")
    default_idx = 0 if curr_active == "builder" else 1

    # 상단 모던 헤더
    st.markdown(
        """
        <div class="app-header">
            <div>
                <h1 class="app-header-title">⚡ 블암스 ETF 백테스팅</h1>
                <div class="app-header-sub">정적 자산배분 · 나스닥 트라이포드 · DCA 정기 적립식 실시간 퀀트 백테스터</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_nav1, col_nav2 = st.columns([7, 3])
    with col_nav1:
        view_options = ["🛠️ 1. 전략 구성 (빌더)", "📊 2. 백테스트 결과 분석"]
        selected_view_choice = st.radio(
            "화면 전환",
            options=view_options,
            index=default_idx,
            horizontal=True,
            label_visibility="collapsed",
            key=f"nav_radio_{curr_active}"
        )
        if "2." in selected_view_choice and curr_active != "result":
            st.session_state["active_view"] = "result"
            st.rerun()
        elif "1." in selected_view_choice and curr_active != "builder":
            st.session_state["active_view"] = "builder"
            st.rerun()
    with col_nav2:
        if st.button("🔄 전체 설정 초기화", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

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
            st.warning("⚠️ 아직 전략이 구성되지 않았거나 백테스트가 실행되지 않았습니다. 먼저 '전략 구성 (빌더)' 화면에서 ETF를 추가하고 실행해 주세요.")
            if st.button("🛠️ 전략 구성 화면으로 이동", type="primary"):
                st.session_state["active_view"] = "builder"
                st.rerun()
        else:
            render_backtest_results(cfg)


if __name__ == "__main__":
    main()
