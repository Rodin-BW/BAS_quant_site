import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from engine.backtest import (
    calculate_metrics,
    calculate_drawdown,
    run_rebalancing_backtest,
    run_momentum_backtest,
    run_sma_crossover_backtest,
    BacktestResult
)
from engine.data import normalize_ticker


@pytest.fixture
def sample_price_data():
    """테스트용 가상 주가 시계열 생성 (2년치, 2개 자산)"""
    dates = pd.date_range(start="2022-01-01", end="2023-12-31", freq="B")
    np.random.seed(42)
    
    # asset_a: 꾸준한 우상향
    returns_a = np.random.normal(loc=0.0005, scale=0.01, size=len(dates))
    prices_a = 100 * np.cumprod(1 + returns_a)
    
    # asset_b: 횡보 및 하락/상승 반복
    returns_b = np.random.normal(loc=0.0001, scale=0.015, size=len(dates))
    prices_b = 100 * np.cumprod(1 + returns_b)
    
    df = pd.DataFrame({
        "ETF_A": prices_a,
        "ETF_B": prices_b
    }, index=dates)
    return df


def test_calculate_metrics_math():
    """성과 지표 수식(CAGR, MDD, Sharpe 등)의 수학적 정확성 검증"""
    # 252일 동안 매일 0.1%씩 오르는 경우 (복리 연 28.6%)
    daily_rets = pd.Series([0.001] * 252)
    metrics = calculate_metrics(daily_rets, risk_free_rate=0.02)
    
    expected_total_return = (1.001 ** 252) - 1
    assert pytest.approx(metrics["total_return"], 1e-4) == expected_total_return
    assert pytest.approx(metrics["cagr"], 1e-4) == expected_total_return
    assert metrics["mdd"] == 0.0  # 계속 상승했으므로 MDD는 0
    assert metrics["annual_volatility"] == pytest.approx(0.0, 1e-4)
    assert metrics["ulcer_index"] == 0.0  # 낙폭이 없으므로 궤양지수 0
    assert metrics["downside_deviation"] == 0.0  # 하방 손실이 없으므로 0

    # 하락을 포함하는 변동성 시리즈로 추가 검증
    mixed_rets = pd.Series([0.02, -0.01, 0.015, -0.02, 0.005] * 50)
    m_mixed = calculate_metrics(mixed_rets, risk_free_rate=0.02)
    assert "sortino_ratio" in m_mixed
    assert "ulcer_index" in m_mixed
    assert "ulcer_performance_index" in m_mixed
    assert m_mixed["ulcer_index"] >= 0.0
    assert m_mixed["downside_deviation"] > 0.0


def test_calculate_drawdown():
    """Drawdown 계산식 검증"""
    prices = pd.Series([100, 120, 90, 110, 80], index=pd.date_range("2023-01-01", periods=5))
    dd = calculate_drawdown(prices)
    
    # 고점 100 -> 0%
    # 고점 120 -> 0%
    # 90 -> (90-120)/120 = -0.25 (-25%)
    # 110 -> (110-120)/120 = -0.0833
    # 80 -> (80-120)/120 = -0.3333 (-33.33%)
    assert dd.iloc[0] == 0.0
    assert dd.iloc[1] == 0.0
    assert pytest.approx(dd.iloc[2], 1e-4) == -0.25
    assert pytest.approx(dd.iloc[4], 1e-4) == -0.3333333


def test_rebalancing_backtest(sample_price_data):
    """정적 비중 리밸런싱 백테스트 작동 검증"""
    weights = {"ETF_A": 0.6, "ETF_B": 0.4}
    res = run_rebalancing_backtest(sample_price_data, weights=weights, rebalance_freq="M")
    
    assert isinstance(res, BacktestResult)
    assert len(res.daily_portfolio_value) == len(sample_price_data)
    assert res.daily_portfolio_value.iloc[0] == pytest.approx(100.0, 1e-2)  # 시작값 100 기준
    assert "cagr" in res.metrics
    assert "mdd" in res.metrics
    assert "sharpe_ratio" in res.metrics
    assert res.metrics["mdd"] <= 0.0  # MDD는 항상 0 이하 (음수 또는 0)


def test_momentum_backtest(sample_price_data):
    """모멘텀 전략 백테스트 검증"""
    res = run_momentum_backtest(sample_price_data, lookback_months=3, top_n=1)
    assert isinstance(res, BacktestResult)
    assert len(res.daily_portfolio_value) == len(sample_price_data)
    assert res.metrics["total_return"] is not None


def test_sma_crossover_backtest(sample_price_data):
    """단순이동평균 교차 전략 백테스트 검증"""
    series = sample_price_data["ETF_A"]
    res = run_sma_crossover_backtest(series, short_window=10, long_window=30)
    assert isinstance(res, BacktestResult)
    assert len(res.daily_portfolio_value) == len(series)


def test_normalize_ticker():
    """한국 및 미국 티커 정규화 로직 검증"""
    assert normalize_ticker("069500") == "069500.KS"
    assert normalize_ticker("122630.ks") == "122630.KS"
    assert normalize_ticker("spy") == "SPY"
    assert normalize_ticker(" QQQ ") == "QQQ"


def test_band_rebalancing(sample_price_data):
    """밴드 리밸런싱: 오차가 허용 밴드(예: 10%p)를 넘을 때만 리밸런싱 실행되는지 검증"""
    weights = {"ETF_A": 0.5, "ETF_B": 0.5}
    # 밴드 15%p 설정
    res_band = run_rebalancing_backtest(
        sample_price_data,
        weights=weights,
        rebalance_freq="None",  # 정기 리밸런싱 없이 오직 밴드로만
        band_threshold=0.15
    )
    assert isinstance(res_band, BacktestResult)
    # 리밸런싱 기록 확인
    for record in res_band.rebalance_history.to_dict("records"):
        assert "Band" in record.get("Reason", "") or "Rebalance" in record.get("Type", "")


def test_calculate_13612_momentum():
    """13612 모멘텀 스코어 (12*R1 + 4*R3 + 2*R6 + 1*R12) 수식 검증"""
    from engine.backtest import calculate_13612_momentum
    # 13개월 주가 (월별 100, 101, 102 ... 112)
    dates = pd.date_range("2022-01-01", periods=13, freq="ME")
    # 매월 1%씩 상승
    prices = pd.Series([100 * (1.01 ** i) for i in range(13)], index=dates)
    score = calculate_13612_momentum(prices)
    # R1 = 0.01, R3 = (1.01^3)-1, R6 = (1.01^6)-1, R12 = (1.01^12)-1
    r1 = prices.iloc[-1] / prices.iloc[-2] - 1
    r3 = prices.iloc[-1] / prices.iloc[-4] - 1
    r6 = prices.iloc[-1] / prices.iloc[-7] - 1
    r12 = prices.iloc[-1] / prices.iloc[-13] - 1
    expected_score = 12 * r1 + 4 * r3 + 2 * r6 + 1 * r12
    assert pytest.approx(score, 1e-4) == expected_score


def test_canary_vaa_strategy():
    """VAA 카나리아 전략 동작 검증"""
    from engine.backtest import run_canary_backtest
    dates = pd.date_range("2021-01-01", "2023-12-31", freq="B")
    np.random.seed(42)
    # 자산군 생성: 공격(SPY, QQQ), 수비(SHY), 카나리아(BND)
    df = pd.DataFrame({
        "SPY": 100 * np.cumprod(1 + np.random.normal(0.0004, 0.01, len(dates))),
        "QQQ": 100 * np.cumprod(1 + np.random.normal(0.0006, 0.012, len(dates))),
        "SHY": 100 * np.cumprod(1 + np.random.normal(0.0001, 0.002, len(dates))),
        "BND": 100 * np.cumprod(1 + np.random.normal(0.0002, 0.004, len(dates)))
    }, index=dates)
    
    res = run_canary_backtest(
        price_df=df,
        offensive_assets=["SPY", "QQQ"],
        defensive_assets=["SHY"],
        canary_assets=["BND"],
        model_type="VAA",
        top_n=1
    )
    assert isinstance(res, BacktestResult)
    assert len(res.daily_portfolio_value) == len(df)
    assert res.metrics["cagr"] is not None


def test_align_and_convert_currency():
    """USD 및 KRW 통화 일원화 환산 검증"""
    from engine.data import align_and_convert_currency
    dates = pd.date_range("2023-01-01", periods=3, freq="B")
    price_df = pd.DataFrame({
        "SPY": [100.0, 100.0, 100.0],       # USD
        "069500.KS": [130000.0, 130000.0, 130000.0]  # KRW
    }, index=dates)
    
    fx_series = pd.Series([1300.0, 1300.0, 1300.0], index=dates)
    
    # KRW 기준 일원화: SPY가 100 * 1300 = 130,000 KRW로 변환되어야 함
    df_krw = align_and_convert_currency(price_df, base_currency="KRW", fx_series=fx_series)
    assert df_krw["SPY"].iloc[0] == 130000.0
    assert df_krw["069500.KS"].iloc[0] == 130000.0
    
    # USD 기준 일원화: 069500.KS가 130,000 / 1300 = 100 USD로 변환되어야 함
    df_usd = align_and_convert_currency(price_df, base_currency="USD", fx_series=fx_series)
    assert df_usd["SPY"].iloc[0] == 100.0
    assert df_usd["069500.KS"].iloc[0] == 100.0


def test_calculate_benchmark_metrics():
    """포트폴리오와 벤치마크 간의 알파, 베타, 상관계수 산출 검증"""
    from engine.backtest import calculate_relative_metrics
    dates = pd.date_range("2023-01-01", periods=252, freq="B")
    np.random.seed(42)
    bm_rets = pd.Series(np.random.normal(0.0005, 0.01, len(dates)), index=dates)
    # 포트폴리오가 벤치마크의 1.2배 변동성을 가질 때 베타는 약 1.2
    port_rets = bm_rets * 1.2 + np.random.normal(0.0001, 0.002, len(dates))
    
    rel = calculate_relative_metrics(port_rets, bm_rets, risk_free_rate=0.02)
    assert "beta" in rel
    assert "correlation" in rel
    assert pytest.approx(rel["beta"], 0.2) == 1.2
    assert rel["correlation"] > 0.8


def test_generate_absolute_return_series():
    """연 목표 절대수익률(예: 5%) 시계열 생성 검증"""
    from engine.backtest import generate_absolute_return_series
    dates = pd.date_range("2023-01-01", periods=252, freq="B")
    series = generate_absolute_return_series(dates, annual_target_rate=0.05, initial_capital=100.0)
    
    assert len(series) == 252
    assert series.iloc[0] == 100.0
    # 252 거래일 후 자산 가치는 약 105.0
    assert pytest.approx(series.iloc[-1], 0.2) == 105.0


def test_transaction_cost_and_taxes():
    """거래비용(수수료+슬리피지) 및 양도소득세(연말 정산, 22%, 공제액) 반영 검증"""
    dates = pd.date_range("2022-01-01", "2023-12-31", freq="B")
    # 꾸준히 100% 상승하는 자산 (큰 실현이익 발생)
    prices = pd.DataFrame({
        "ETF_A": [100.0 * (1.0 + 0.002 * i) for i in range(len(dates))],
        "ETF_B": [100.0] * len(dates)
    }, index=dates)
    
    # 1. 세금/비용 없는 경우 (초기 자본 1억 원)
    res_raw = run_rebalancing_backtest(
        prices,
        weights={"ETF_A": 0.5, "ETF_B": 0.5},
        rebalance_freq="M",
        fee_rate=0.0,
        tax_rate=0.0,
        initial_capital=100000000.0
    )
    
    # 2. 거래비용 0.1% + 양도소득세 22% (연 기본공제 250만원)
    res_taxed = run_rebalancing_backtest(
        prices,
        weights={"ETF_A": 0.5, "ETF_B": 0.5},
        rebalance_freq="M",
        fee_rate=0.001,
        tax_rate=0.22,
        tax_deduction=2500000.0,
        initial_capital=100000000.0
    )
    
    # 비용과 세금이 반영된 포트폴리오의 최종 가치는 원시 포트폴리오보다 낮아야 함
    assert res_taxed.daily_portfolio_value.iloc[-1] < res_raw.daily_portfolio_value.iloc[-1]
    assert "total_fees_paid" in res_taxed.metrics
    assert "total_taxes_paid" in res_taxed.metrics
    assert res_taxed.metrics["total_fees_paid"] > 0
    assert res_taxed.metrics["total_taxes_paid"] > 0


def test_tripod_backtest(sample_price_data):
    """트라이포드(3대 엔진 결합: 정적 + 동적 카나리아 + 모멘텀) 앙상블 백테스트 검증"""
    from engine.backtest import run_tripod_backtest
    dates = sample_price_data.index
    # 4개 자산 확장
    np.random.seed(42)
    df = pd.DataFrame({
        "SPY": sample_price_data["ETF_A"],
        "TLT": sample_price_data["ETF_B"],
        "GLD": 100 * np.cumprod(1 + np.random.normal(0.0002, 0.008, len(dates))),
        "BND": 100 * np.cumprod(1 + np.random.normal(0.0001, 0.003, len(dates)))
    }, index=dates)
    
    tripod_res = run_tripod_backtest(
        price_df=df,
        tripod_weights={"static": 0.4, "canary": 0.4, "momentum": 0.2},
        static_params={"weights": {"SPY": 0.5, "TLT": 0.5}, "rebalance_freq": "M"},
        canary_params={
            "offensive": ["SPY", "GLD"],
            "defensive": ["TLT", "BND"],
            "canary": ["BND"],
            "model_type": "VAA",
            "top_n": 1
        },
        momentum_params={"lookback_months": 3, "top_n": 1},
        fee_rate=0.0005,
        tax_rate=0.0,
        initial_capital=10000.0
    )
    
    assert hasattr(tripod_res, "sub_results")
    assert "static" in tripod_res.sub_results
    assert "canary" in tripod_res.sub_results
    assert "momentum" in tripod_res.sub_results
    assert len(tripod_res.daily_portfolio_value) == len(df)
    assert tripod_res.metrics["cagr"] is not None
    assert tripod_res.metrics["total_return"] is not None


def test_multi_strategy_and_monthly_holdings(sample_price_data):
    """멀티 전략(동적1 + 동적2 등 자유 결합) 및 전략별 월별 보유 ETF 내역 검증"""
    from engine.backtest import run_multi_strategy_portfolio
    dates = sample_price_data.index
    np.random.seed(42)
    df = pd.DataFrame({
        "SPY": sample_price_data["ETF_A"],
        "QQQ": 100 * np.cumprod(1 + np.random.normal(0.0006, 0.012, len(dates))),
        "TLT": sample_price_data["ETF_B"],
        "BND": 100 * np.cumprod(1 + np.random.normal(0.0001, 0.003, len(dates))),
        "BIL": 100 * np.cumprod(1 + np.random.normal(0.0001, 0.001, len(dates)))
    }, index=dates)
    
    # 2개의 동적 전략을 50:50으로 믹스 (전략 1: VAA, 전략 2: 듀얼모멘텀)
    strategies_config = [
        {
            "name": "전략 1: VAA 카나리아",
            "weight": 0.5,
            "type": "canary",
            "params": {
                "offensive": ["SPY", "QQQ"],
                "defensive": ["TLT", "BIL"],
                "canary": ["BND"],
                "model_type": "VAA",
                "top_n": 1
            }
        },
        {
            "name": "전략 2: 모멘텀 전략",
            "weight": 0.5,
            "type": "momentum",
            "params": {
                "tickers": ["SPY", "QQQ", "TLT"],
                "lookback_months": 3,
                "top_n": 1
            }
        }
    ]
    
    multi_res = run_multi_strategy_portfolio(
        price_df=df,
        strategies=strategies_config,
        fee_rate=0.0005,
        tax_rate=0.0,
        initial_capital=10000.0
    )
    
    assert len(multi_res.daily_portfolio_value) == len(df)
    assert hasattr(multi_res, "monthly_holdings")
    assert not multi_res.monthly_holdings.empty
    # 각 서브 전략의 월별 보유 내역도 존재하는지 확인
    assert hasattr(multi_res, "sub_results")
    assert len(multi_res.sub_results) == 2
    for s_name, s_res in multi_res.sub_results.items():
        assert hasattr(s_res, "monthly_holdings")
        assert not s_res.monthly_holdings.empty


def test_multi_strategy_with_tripod_substrategy(sample_price_data):
    """멀티 전략 믹스 내에 트라이포드 앙상블이 서브 전략으로 포함된 경우 검증"""
    from engine.backtest import run_multi_strategy_portfolio
    from engine.data import STATIC_PRESETS
    dates = sample_price_data.index
    np.random.seed(42)
    df = pd.DataFrame({
        "SPY": sample_price_data["ETF_A"],
        "TLT": sample_price_data["ETF_B"],
        "GLD": 100 * np.cumprod(1 + np.random.normal(0.0002, 0.008, len(dates))),
        "DBC": 100 * np.cumprod(1 + np.random.normal(0.0001, 0.009, len(dates))),
        "IEF": 100 * np.cumprod(1 + np.random.normal(0.0001, 0.002, len(dates))),
        "QQQ": 100 * np.cumprod(1 + np.random.normal(0.0005, 0.011, len(dates))),
        "SHY": 100 * np.cumprod(1 + np.random.normal(0.00005, 0.001, len(dates))),
        "BND": 100 * np.cumprod(1 + np.random.normal(0.0001, 0.003, len(dates)))
    }, index=dates)

    static_preset = STATIC_PRESETS["글로벌 올웨더 (Ray Dalio All Weather)"]
    strategies = [
        {
            "name": "전략 1: 트라이포드 앙상블",
            "weight": 0.5,
            "type": "tripod",
            "params": {
                "tripod_weights": {"static": 0.4, "canary": 0.4, "momentum": 0.2},
                "static_params": {"weights": static_preset, "rebalance_freq": "M"},
                "canary_params": {
                    "offensive": ["SPY", "QQQ"], "defensive": ["SHY"], "canary": ["BND"], "model_type": "VAA", "top_n": 1
                },
                "momentum_params": {"lookback_months": 3, "top_n": 1}
            }
        },
        {
            "name": "전략 2: 단독 정적 올웨더",
            "weight": 0.5,
            "type": "static",
            "params": {
                "weights": static_preset,
                "rebalance_freq": "M"
            }
        }
    ]

    res = run_multi_strategy_portfolio(
        price_df=df,
        strategies=strategies,
        fee_rate=0.0005,
        tax_rate=0.0,
        initial_capital=10000.0
    )

    assert len(res.daily_portfolio_value) == len(df)
    assert not res.monthly_holdings.empty
    assert "전략 1: 트라이포드 앙상블" in res.sub_results
    assert "전략 2: 단독 정적 올웨더" in res.sub_results


def test_dca_rebalancing_backtest(sample_price_data):
    """정적 자산 배분 DCA 정기 적립식 백테스트 검증"""
    res = run_rebalancing_backtest(
        price_df=sample_price_data,
        weights={"ETF_A": 0.6, "ETF_B": 0.4},
        rebalance_freq="M",
        initial_capital=1000.0,
        periodic_cash_flow=100.0,
        dca_freq="M"
    )

    # 초기 1000 + 약 24개월 * 100 = 약 3300 ~ 3400 원금 투입
    assert res.metrics["total_contributed"] > 1000.0
    assert "dca_total_return" in res.metrics
    # DCA 적립 이벤트가 rebalance_history에 포함되어 있는지 확인
    dca_records = res.rebalance_history[res.rebalance_history["Reason"].str.contains("DCA", na=False)]
    assert len(dca_records) > 10


def test_dca_multi_strategy(sample_price_data):
    """멀티 전략 믹스 DCA 적립식 백테스트 검증"""
    from engine.backtest import run_multi_strategy_portfolio
    strategies = [
        {
            "name": "전략 1",
            "weight": 0.5,
            "type": "static",
            "params": {"weights": {"ETF_A": 0.5, "ETF_B": 0.5}}
        },
        {
            "name": "전략 2",
            "weight": 0.5,
            "type": "momentum",
            "params": {"tickers": ["ETF_A", "ETF_B"], "lookback_months": 3, "top_n": 1}
        }
    ]

    res = run_multi_strategy_portfolio(
        price_df=sample_price_data,
        strategies=strategies,
        initial_capital=1000.0,
        periodic_cash_flow=200.0,
        dca_freq="M"
    )

    assert res.metrics["total_contributed"] > 1000.0
    assert "dca_total_return" in res.metrics


def test_calculate_rsi():
    """RSI(상대강도지수 14일) 계산 검증"""
    from engine.backtest import calculate_rsi
    dates = pd.date_range("2023-01-01", periods=100, freq="B")
    # 지속 하락 시 RSI는 30 이하로 떨어져야 함
    falling_prices = pd.Series([100.0 * (0.98 ** i) for i in range(100)], index=dates)
    rsi_falling = calculate_rsi(falling_prices, period=14)
    assert rsi_falling.iloc[-1] < 30.0

    # 지속 상승 시 RSI는 70 이상으로 상승해야 함
    rising_prices = pd.Series([100.0 * (1.02 ** i) for i in range(100)], index=dates)
    rsi_rising = calculate_rsi(rising_prices, period=14)
    assert rsi_rising.iloc[-1] > 70.0


def test_nasdaq_tripod_strategy():
    """정통 나스닥 레버리지 트라이포드(Tripod) 전략 백테스트 검증:
    1축: 상시 현금 비중 30% 및 레버리지 스위칭
    2축: MDD 기준 분할 매수(-10%, -20%, -30%)
    3축: 과매도 RSI(40/30) 지표 결합
    """
    from engine.backtest import run_nasdaq_tripod_backtest
    dates = pd.date_range("2020-01-01", "2023-12-31", freq="B")
    n = len(dates)

    # 1. 상승 후 -35% 폭락했다가 회복하는 시나리오 데이터 생성
    qqq_prices = [100.0]
    for i in range(1, n):
        if i < 200:
            ret = 0.001  # 평상시 상승
        elif i < 350:
            ret = -0.004 # 폭락장 (MDD -35% 이상 도달)
        else:
            ret = 0.002  # 회복 및 반등
        qqq_prices.append(qqq_prices[-1] * (1.0 + ret))

    qqq_series = pd.Series(qqq_prices, index=dates)
    # QLD(2배수), TQQQ(3배수) 가격 시계열 합성
    qld_series = pd.Series([100.0 * ((p / 100.0) ** 2.0) for p in qqq_prices], index=dates)
    tqqq_series = pd.Series([100.0 * ((p / 100.0) ** 3.0) for p in qqq_prices], index=dates)

    df = pd.DataFrame({
        "QQQ": qqq_series,
        "QLD": qld_series,
        "TQQQ": tqqq_series
    }, index=dates)

    res = run_nasdaq_tripod_backtest(
        price_df=df,
        base_asset="QQQ",
        leveraged_2x="QLD",
        leveraged_3x="TQQQ",
        normal_cash_pct=0.30,
        normal_qld_ratio=0.50,
        mdd_milestones=(-0.10, -0.20, -0.30),
        rsi_triggers=(40.0, 30.0),
        fee_rate=0.0005,
        initial_capital=100000000.0,
        periodic_cash_flow=1000000.0,
        dca_freq="M"
    )

    assert len(res.daily_portfolio_value) == n
    assert res.metrics["cagr"] is not None
    assert "total_contributed" in res.metrics
    assert hasattr(res, "monthly_holdings")
    assert not res.monthly_holdings.empty
    # 폭락 구간에서 TQQQ 비중이 확대되었는지 이력 확인
    rebal_reasons = " ".join(res.rebalance_history["Reason"].tolist())
    assert "대폭락" in rebal_reasons or "하락" in rebal_reasons or "조정" in rebal_reasons



