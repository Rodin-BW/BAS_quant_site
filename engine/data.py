import re
from typing import Dict, List, Optional, Tuple
import pandas as pd
import yfinance as yf
import streamlit as st

# 정적 및 동적 자산배분 프리셋
STATIC_PRESETS = {
    "글로벌 올웨더 (Ray Dalio All Weather)": {
        "SPY": 0.30,   # 미국 대형주 30%
        "TLT": 0.40,   # 미국 장기채 40%
        "IEF": 0.15,   # 미국 중기채 15%
        "GLD": 0.075,  # 금 7.5%
        "DBC": 0.075   # 원자재 7.5%
    },
    "골든 버터플라이 (Golden Butterfly)": {
        "SPY": 0.20,   # 대형주 20%
        "IWM": 0.20,   # 소형가치주 20%
        "TLT": 0.20,   # 장기채 20%
        "SHY": 0.20,   # 단기채 20%
        "GLD": 0.20    # 금 20%
    },
    "영구 포트폴리오 (Permanent Portfolio)": {
        "SPY": 0.25,   # 주식 25%
        "TLT": 0.25,   # 장기채 25%
        "GLD": 0.25,   # 금 25%
        "BIL": 0.25    # 초단기채(현금) 25%
    },
    "클래식 60/40 (Classic 60/40)": {
        "SPY": 0.60,   # 주식 60%
        "BND": 0.40    # 종합채권 40%
    },
    "한국형 올웨더 (K-All Weather)": {
        "069500.KS": 0.30,  # KODEX 200 (한국주식 30%)
        "148070.KS": 0.40,  # KOSEF 국고채10년 (한국채권 40%)
        "132030.KS": 0.15,  # KODEX 골드선물(H) (금 15%)
        "130730.KS": 0.15   # KOSEF 단기자금 (단기채/현금 15%)
    }
}

CANARY_PRESETS = {
    "VAA (Vigilant Asset Allocation - 공격형)": {
        "offensive": ["SPY", "IWM", "EFA", "EEM"],
        "defensive": ["LQD", "IEF", "SHY"],
        "canary": ["VWO", "BND"],
        "description": "카나리아 자산(VWO, BND)의 13612 모멘텀이 모두 양수면 공격자산 1위, 하나라도 음수면 수비자산 1위"
    },
    "DAA (Defensive Asset Allocation - 방어형)": {
        "offensive": ["SPY", "IWM", "QQQ", "VGK", "EWJ", "EEM", "VNQ", "GLD", "TLT", "HYG", "LQD"],
        "defensive": ["SHY", "IEF", "BIL"],
        "canary": ["VWO", "BND"],
        "description": "카나리아 2개 모두 양수시 공격자산 100%, 1개 음수시 공격 50%/수비 50%, 둘 다 음수시 수비자산 100%"
    },
    "한국형 카나리아 동적 자산배분": {
        "offensive": ["069500.KS", "229200.KS", "122630.KS"],
        "defensive": ["148070.KS", "130730.KS"],
        "canary": ["148070.KS", "069500.KS"],
        "description": "한국 대표 주식과 채권 카나리아 신호에 따라 공격 ETF와 채권/단기자금으로 동적 전환"
    }
}

BENCHMARK_PRESETS = {
    "미국 S&P 500 (SPY)": "SPY",
    "미국 나스닥 100 (QQQ)": "QQQ",
    "미국 다우 존스 (DIA)": "DIA",
    "한국 코스피 200 (069500.KS)": "069500.KS",
    "한국 코스닥 150 (229200.KS)": "229200.KS",
    "전세계 주식 (ACWI)": "ACWI"
}

# 검색 및 태그 선택용 인기/대표 ETF 카탈로그 (한국 & 미국)
POPULAR_ETF_CATALOG = {
    # 미국 대표 ETF
    "SPY": "SPY | S&P 500 미국 대형주",
    "IVV": "IVV | iShares Core S&P 500",
    "VOO": "VOO | Vanguard S&P 500",
    "QQQ": "QQQ | Invesco NASDAQ 100 나스닥 기술주",
    "QLD": "QLD | ProShares Ultra QQQ (나스닥 2X 레버리지)",
    "TQQQ": "TQQQ | ProShares UltraPro QQQ (나스닥 3X 레버리지)",
    "SSO": "SSO | ProShares Ultra S&P500 (S&P 2X 레버리지)",
    "UPRO": "UPRO | ProShares UltraPro S&P500 (S&P 3X 레버리지)",
    "SOXL": "SOXL | Direxion Daily Semiconductor Bull 3X (반도체 3X)",
    "IWM": "IWM | Russell 2000 미국 소형주",
    "IWD": "IWD | Russell 1000 Value 대형 가치주",
    "IWO": "IWO | Russell 2000 Growth 소형 성장주",
    "DIA": "DIA | 다우존스 30 산업평균",
    "VTI": "VTI | Vanguard 미국 전체 주식시장",
    "SCHD": "SCHD | Schwab US Dividend 미국 배당성장",
    "MTUM": "MTUM | iShares 미국 모멘텀 팩터",
    "QUAL": "QUAL | iShares 미국 퀄리티 팩터",
    "SOXX": "SOXX | iShares 미국 반도체",
    "SMH": "SMH | VanEck 미국 반도체 25",
    "XLK": "XLK | 미국 테크놀로지 섹터",
    "XLF": "XLF | 미국 금융 섹터",
    "XLE": "XLE | 미국 에너지 섹터",
    "XLV": "XLV | 미국 헬스케어 섹터",
    "TLT": "TLT | 미국 20년+ 초장기국채",
    "IEF": "IEF | 미국 7-10년 중기국채",
    "SHY": "SHY | 미국 1-3년 단기국채",
    "BIL": "BIL | 미국 1-3개월 초단기국채/현금",
    "BND": "BND | Vanguard 미국 종합채권",
    "AGG": "AGG | iShares 미국 종합채권",
    "LQD": "LQD | 미국 투자등급 회사채",
    "HYG": "HYG | 미국 하이일드 회사채",
    "TIP": "TIP | 미국 물가연동채(TIPS)",
    "GLD": "GLD | SPDR 금 현물 (Gold)",
    "IAU": "IAU | iShares 금 현물",
    "SLV": "SLV | iShares 은 현물 (Silver)",
    "DBC": "DBC | Invesco 원자재/원유/곡물 종합",
    "VNQ": "VNQ | Vanguard 미국 부동산 리츠",
    "VT": "VT | Vanguard 전세계 주식",
    "EFA": "EFA | 선진국(미국 제외) 대형주",
    "EEM": "EEM | 신흥국(이머징) 주식",
    "VWO": "VWO | Vanguard 신흥국 주식",
    "VGK": "VGK | 유럽 선진국 주식",
    "EWJ": "EWJ | 일본 주식",
    # 한국 대표 ETF (KRX)
    "069500.KS": "069500.KS | KODEX 200 (한국 코스피 대표주)",
    "102110.KS": "102110.KS | TIGER 200 (한국 코스피)",
    "229200.KS": "229200.KS | KODEX 코스닥150 (한국 기술주)",
    "122630.KS": "122630.KS | KODEX 레버리지 (코스피 2X)",
    "114800.KS": "114800.KS | KODEX 인버스 (코스피 -1X)",
    "379800.KS": "379800.KS | TIGER 미국S&P500",
    "381180.KS": "381180.KS | TIGER 미국나스닥100",
    "448330.KS": "448330.KS | TIGER 미국배당다우존스 (한국형 SCHD)",
    "458730.KS": "458730.KS | ACE 미국배당다우존스",
    "396500.KS": "396500.KS | TIGER 미국테크TOP10 INDXX",
    "453810.KS": "453810.KS | PLUS 고배당주",
    "148070.KS": "148070.KS | KOSEF 국고채10년 (한국 장기국채)",
    "305080.KS": "305080.KS | TIGER 단기통안채 (한국 단기채)",
    "130730.KS": "130730.KS | KOSEF 단기자금 (한국 현금성)",
    "132030.KS": "132030.KS | KODEX 골드선물(H) (금 선물)",
    "261220.KS": "261220.KS | KODEX WTI원유선물(H)",
    "411060.KS": "411060.KS | ACE 미국채10년선물"
}


def normalize_ticker(ticker: str) -> str:
    """한국 6자리 숫자 티커인 경우 자동으로 .KS를 부여하고 공백/대소문자를 정규화"""
    t = ticker.strip().upper()
    if re.fullmatch(r"\d{6}", t):
        return f"{t}.KS"
    return t


def is_korean_ticker(ticker: str) -> bool:
    """한국 거래소 티커 여부 판별 (.KS 코스피 또는 .KQ 코스닥)"""
    t = normalize_ticker(ticker)
    return t.endswith(".KS") or t.endswith(".KQ")


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_etf_data(
    tickers: List[str],
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """
    yfinance를 사용하여 ETF의 수정 종가(Adjusted Close)를 다운로드합니다.
    분배락(배당락) 및 액면분할이 완전하게 반영된 Total Return Index 가격을 반환합니다.
    (규칙: session 인수 주입 없이 yf 기본 세션 사용)
    """
    clean_tickers = list(dict.fromkeys([normalize_ticker(t) for t in tickers if t.strip()]))
    if not clean_tickers:
        return pd.DataFrame()

    try:
        # auto_adjust=True로 배당금 및 액면분할이 자동 재투자 반영된 수정주가를 직접 로드
        data = yf.download(
            tickers=clean_tickers,
            start=start_date,
            end=end_date,
            auto_adjust=True,
            progress=False
        )
        
        if data.empty:
            return pd.DataFrame()

        # MultiIndex 컬럼 처리
        if isinstance(data.columns, pd.MultiIndex):
            if "Close" in data.columns.levels[0]:
                prices = data["Close"]
            else:
                prices = data.iloc[:, :len(clean_tickers)]
        else:
            if "Close" in data.columns:
                prices = data[["Close"]]
                prices.columns = [clean_tickers[0]]
            else:
                prices = pd.DataFrame({clean_tickers[0]: data.iloc[:, 0]})

        # 시간대(timezone) 제거
        if prices.index.tz is not None:
            prices.index = prices.index.tz_localize(None)
            
        prices.index = pd.to_datetime(prices.index)
        
        # 한국/미국 거래일 불일치 보정 (ffill 후 bfill)
        prices = prices.ffill().bfill().dropna()
        return prices
    except Exception as e:
        st.error(f"데이터 다운로드 중 오류 발생: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_exchange_rate(start_date: str, end_date: str) -> pd.Series:
    """USD/KRW 환율(USDKRW=X) 시계열을 수집합니다."""
    try:
        fx = yf.download("USDKRW=X", start=start_date, end=end_date, auto_adjust=True, progress=False)
        if fx.empty:
            return pd.Series(dtype=float)
        
        if isinstance(fx.columns, pd.MultiIndex):
            fx_close = fx["Close"].iloc[:, 0]
        elif "Close" in fx.columns:
            fx_close = fx["Close"]
        else:
            fx_close = fx.iloc[:, 0]
            
        if fx_close.index.tz is not None:
            fx_close.index = fx_close.index.tz_localize(None)
        fx_close.index = pd.to_datetime(fx_close.index)
        return fx_close.ffill().bfill()
    except Exception:
        return pd.Series(dtype=float)


def align_and_convert_currency(
    price_df: pd.DataFrame,
    base_currency: str = "KRW",
    fx_series: Optional[pd.Series] = None
) -> pd.DataFrame:
    """
    포트폴리오의 각 자산 가격을 기준 통화(base_currency: 'KRW' 또는 'USD')로 일원화 변환합니다.
    - base_currency == 'KRW': 미국 ETF(USD)는 환율(USD/KRW)을 곱하여 원화 가격으로 환산
    - base_currency == 'USD': 한국 ETF(KRW)는 환율(USD/KRW)로 나누어 달러 가격으로 환산
    """
    if price_df.empty or fx_series is None or fx_series.empty:
        return price_df

    # 환율 데이터를 price_df의 날짜 인덱스에 맞추어 리인덱스 및 ffill
    aligned_fx = fx_series.reindex(price_df.index).ffill().bfill()
    converted_df = price_df.copy()

    for col in price_df.columns:
        is_kr = is_korean_ticker(col)
        if base_currency == "KRW":
            if not is_kr:
                # 미국 ETF(USD) -> KRW (환율 곱)
                converted_df[col] = price_df[col] * aligned_fx
        elif base_currency == "USD":
            if is_kr:
                # 한국 ETF(KRW) -> USD (환율 나눔)
                converted_df[col] = price_df[col] / aligned_fx

    return converted_df


def get_dividend_yield(ticker: str) -> float:
    """ETF의 최근 배당 수익률 (TTM) 조회 (yfinance 기본 정보)"""
    try:
        t = normalize_ticker(ticker)
        yf_ticker = yf.Ticker(t)
        info = getattr(yf_ticker, "fast_info", {})
        # yield 정보 확인
        dy = getattr(info, "dividend_yield", None)
        if dy is None:
            # fallback: summary info
            info_dict = getattr(yf_ticker, "info", {})
            dy = info_dict.get("dividendYield", 0.0)
        return float(dy) if dy else 0.0
    except Exception:
        return 0.0
