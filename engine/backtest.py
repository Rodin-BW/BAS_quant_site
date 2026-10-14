from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd


@dataclass
class BacktestResult:
    daily_portfolio_value: pd.Series
    daily_returns: pd.Series
    drawdown: pd.Series
    metrics: Dict[str, Any]
    monthly_returns: pd.DataFrame
    rebalance_history: pd.DataFrame
    sub_results: Optional[Dict[str, Any]] = None
    monthly_holdings: Optional[pd.DataFrame] = None


def calculate_drawdown(series: pd.Series) -> pd.Series:
    """누적 자산 가치 시계열로부터 Drawdown(낙폭) 시리즈 계산"""
    cum_max = series.cummax()
    drawdown = (series - cum_max) / cum_max
    return drawdown.fillna(0.0)


def calculate_metrics(daily_returns: pd.Series, risk_free_rate: float = 0.02) -> Dict[str, float]:
    """일간 수익률 시리즈를 기반으로 주요 퀀트 투자 성과 지표 계산"""
    clean_rets = daily_returns.dropna()
    n_days = len(clean_rets)
    
    if n_days == 0:
        return {
            "total_return": 0.0,
            "cagr": 0.0,
            "annual_volatility": 0.0,
            "sharpe_ratio": 0.0,
            "mdd": 0.0,
            "calmar_ratio": 0.0,
            "win_rate": 0.0,
        }
    
    # 1. 누적 수익률 & CAGR
    cum_wealth = (1.0 + clean_rets).cumprod()
    total_return = cum_wealth.iloc[-1] - 1.0 if len(cum_wealth) > 0 else 0.0
    
    years = n_days / 252.0
    if years > 0 and (1.0 + total_return) > 0:
        cagr = ((1.0 + total_return) ** (1.0 / years)) - 1.0
    else:
        cagr = 0.0
        
    # 2. 변동성 & 샤프 지수
    daily_vol = clean_rets.std()
    annual_vol = daily_vol * np.sqrt(252) if not np.isnan(daily_vol) else 0.0
    
    if annual_vol > 1e-8:
        sharpe_ratio = (cagr - risk_free_rate) / annual_vol
    else:
        sharpe_ratio = 0.0
        
    # 3. MDD (최대 낙폭)
    dd = calculate_drawdown(cum_wealth)
    mdd = float(dd.min())
    
    # 4. Calmar Ratio
    calmar_ratio = cagr / abs(mdd) if abs(mdd) > 1e-8 else 0.0
    
    # 5. 소티노 지수 (Sortino Ratio) & 하방 변동성 (Downside Deviation)
    # 무위험 수익률(일간 환산) 이하의 음의 수익률 편차만 반영
    daily_rf = (1.0 + risk_free_rate) ** (1.0 / 252.0) - 1.0
    downside_diff = clean_rets - daily_rf
    negative_returns = downside_diff[downside_diff < 0]
    if len(negative_returns) > 0:
        downside_std_daily = np.sqrt(np.mean(negative_returns ** 2))
        downside_deviation = float(downside_std_daily * np.sqrt(252))
    else:
        downside_deviation = 0.0

    if downside_deviation > 1e-8:
        sortino_ratio = float((cagr - risk_free_rate) / downside_deviation)
    else:
        sortino_ratio = 0.0

    # 6. 궤양지수 (Ulcer Index, UI) & 궤양성과지수 (Ulcer Performance Index / Martin Ratio, UPI)
    # UI = sqrt(mean(drawdown_pct ^ 2)), Peter Martin(1987) 정의 (drawdown은 % 단위, 0~100)
    dd_pct = dd * 100.0  # e.g., -15.5%
    ulcer_index = float(np.sqrt(np.mean(dd_pct ** 2))) if len(dd_pct) > 0 else 0.0
    
    # UPI (Martin Ratio) = (CAGR - RiskFree) / Ulcer_Index (UI는 % 단위이므로 CAGR도 % 또는 소수점에 맞춰 일관성 유지)
    # 표준적으로 (CAGR - rf) [%] / UI [%]
    if ulcer_index > 1e-8:
        upi = float(((cagr - risk_free_rate) * 100.0) / ulcer_index)
    else:
        upi = 0.0

    # 7. 승률 (일간 상승일 비율)
    active_days = clean_rets[clean_rets != 0]
    win_rate = (len(clean_rets[clean_rets > 0]) / len(active_days)) if len(active_days) > 0 else 0.0

    return {
        "total_return": float(total_return),
        "cagr": float(cagr),
        "annual_volatility": float(annual_vol),
        "sharpe_ratio": float(sharpe_ratio),
        "sortino_ratio": float(sortino_ratio),
        "downside_deviation": float(downside_deviation),
        "ulcer_index": float(ulcer_index),
        "ulcer_performance_index": float(upi),
        "mdd": float(mdd),
        "calmar_ratio": float(calmar_ratio),
        "win_rate": float(win_rate),
    }


def calculate_relative_metrics(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    risk_free_rate: float = 0.02
) -> Dict[str, float]:
    """
    포트폴리오와 벤치마크 간의 상대 성과 지표 (Beta, Alpha, Correlation, Tracking Error, Information Ratio) 계산
    """
    comb = pd.concat([portfolio_returns, benchmark_returns], axis=1).dropna()
    if len(comb) < 10:
        return {"beta": 1.0, "alpha": 0.0, "correlation": 0.0, "information_ratio": 0.0}
        
    p_rets = comb.iloc[:, 0]
    b_rets = comb.iloc[:, 1]
    
    cov_mat = np.cov(p_rets, b_rets)
    cov = cov_mat[0, 1]
    b_var = cov_mat[1, 1]
    
    beta = float(cov / b_var) if b_var > 1e-12 else 1.0
    
    # 상관계수
    corr = float(np.corrcoef(p_rets, b_rets)[0, 1]) if b_var > 1e-12 else 0.0
    
    # 연율화 수익률
    p_cagr = calculate_metrics(p_rets, risk_free_rate)["cagr"]
    b_cagr = calculate_metrics(b_rets, risk_free_rate)["cagr"]
    
    # 젠센의 알파 (Jensen's Alpha)
    alpha = float(p_cagr - (risk_free_rate + beta * (b_cagr - risk_free_rate)))
    
    # Tracking Error & Information Ratio
    diff = p_rets - b_rets
    te = float(diff.std() * np.sqrt(252))
    ir = float((p_cagr - b_cagr) / te) if te > 1e-8 else 0.0
    
    return {
        "beta": beta,
        "alpha": alpha,
        "correlation": corr,
        "information_ratio": ir,
        "tracking_error": te
    }


def generate_absolute_return_series(
    dates: pd.DatetimeIndex,
    annual_target_rate: float = 0.05,
    initial_capital: float = 100.0
) -> pd.Series:
    """연 목표 절대수익률(Hurdle Rate) 복리 성장 곡선 시계열 생성"""
    n = len(dates)
    if n == 0:
        return pd.Series(dtype=float)
    daily_rate = (1.0 + annual_target_rate) ** (1.0 / 252.0) - 1.0
    growth = (1.0 + daily_rate) ** np.arange(n)
    return pd.Series(initial_capital * growth, index=dates)


def compute_monthly_returns_matrix(daily_returns: pd.Series) -> pd.DataFrame:
    """일간 수익률을 연도별-월별 수익률 표(Matrix)로 변환"""
    if daily_returns.empty:
        return pd.DataFrame()
    
    monthly_ret = daily_returns.resample("ME").apply(lambda x: (1.0 + x).prod() - 1.0)
    
    df = pd.DataFrame({
        "Year": monthly_ret.index.year,
        "Month": monthly_ret.index.month,
        "Return": monthly_ret.values
    })
    
    matrix = df.pivot(index="Year", columns="Month", values="Return")
    month_names = {i: f"{i}월" for i in range(1, 13)}
    matrix = matrix.rename(columns=month_names)
    
    annual_ret = daily_returns.resample("YE").apply(lambda x: (1.0 + x).prod() - 1.0)
    matrix["연간 (YTD)"] = annual_ret.groupby(annual_ret.index.year).first()
    
    return matrix


def calculate_13612_momentum(price_series: pd.Series) -> float:
    """
    13612 카나리아 가중 모멘텀 스코어 산출:
    12 * R(1m) + 4 * R(3m) + 2 * R(6m) + 1 * R(12m)
    - DatetimeIndex인 경우 DateOffset 기반 asof 검색을 통해 영업일/휴일/데이터 빈도에 무관하게 정밀 계산
    """
    clean_p = price_series.dropna()
    if len(clean_p) < 2:
        return 0.0
    
    p_now = clean_p.iloc[-1]
    
    if isinstance(clean_p.index, pd.DatetimeIndex):
        t_now = clean_p.index[-1]
        p_1m = clean_p.asof(t_now - pd.DateOffset(months=1))
        p_3m = clean_p.asof(t_now - pd.DateOffset(months=3))
        p_6m = clean_p.asof(t_now - pd.DateOffset(months=6))
        p_12m = clean_p.asof(t_now - pd.DateOffset(months=12))
        
        # 이전 데이터가 없는 경우 가용한 가장 오래된 값 사용
        p_1m = p_1m if pd.notna(p_1m) else clean_p.iloc[0]
        p_3m = p_3m if pd.notna(p_3m) else p_1m
        p_6m = p_6m if pd.notna(p_6m) else p_3m
        p_12m = p_12m if pd.notna(p_12m) else p_6m
    else:
        n = len(clean_p)
        p_1m = clean_p.iloc[-min(n, 22)]
        p_3m = clean_p.iloc[-min(n, 64)] if n >= 64 else p_1m
        p_6m = clean_p.iloc[-min(n, 127)] if n >= 127 else p_3m
        p_12m = clean_p.iloc[-min(n, 253)] if n >= 253 else p_6m

    r1 = (p_now / p_1m) - 1.0 if p_1m > 0 else 0.0
    r3 = (p_now / p_3m) - 1.0 if p_3m > 0 else 0.0
    r6 = (p_now / p_6m) - 1.0 if p_6m > 0 else 0.0
    r12 = (p_now / p_12m) - 1.0 if p_12m > 0 else 0.0
    
    return float(12.0 * r1 + 4.0 * r3 + 2.0 * r6 + 1.0 * r12)


def run_rebalancing_backtest(
    price_df: pd.DataFrame,
    weights: Dict[str, float],
    rebalance_freq: str = "M",
    band_threshold: Optional[float] = None,
    fee_rate: float = 0.0005,
    tax_rate: float = 0.0,
    tax_deduction: float = 0.0,
    initial_capital: float = 100.0,
    risk_free_rate: float = 0.02,
    periodic_cash_flow: float = 0.0,
    dca_freq: str = "M"
) -> BacktestResult:
    """
    정적 자산 배분, 정기 리밸런싱, 밴드 리밸런싱, DCA 적립식 투자 및 거래비용/양도소득세 연말정산 지원 백테스트
    """
    clean_prices = price_df.ffill().bfill().dropna()
    dates = clean_prices.index
    assets = [a for a in weights.keys() if a in clean_prices.columns]
    
    if not assets:
        raise ValueError("가격 데이터에 존재하는 자산이 없습니다.")
        
    total_w = sum(weights[a] for a in assets)
    target_weights = {a: weights[a] / total_w for a in assets}
    
    asset_returns = clean_prices[assets].pct_change().fillna(0.0)
    
    portfolio_value = [initial_capital]
    current_asset_values = {a: initial_capital * target_weights[a] for a in assets}
    cost_basis_values = {a: initial_capital * target_weights[a] for a in assets}
    
    rebalance_records = []
    last_rebal_period = None
    last_dca_period = (dates[0].year, dates[0].month) if dca_freq == "M" else dates[0].year
    total_contributed = initial_capital
    
    total_fees_paid = 0.0
    total_taxes_paid = 0.0
    yearly_realized_gains = 0.0
    current_year = dates[0].year
    monthly_holdings_dict = {}
    
    for i in range(1, len(dates)):
        cur_date = dates[i]
        
        # 0. 연도 변경 시 양도소득세 정산 (연말 정산)
        if cur_date.year != current_year:
            if tax_rate > 0 and yearly_realized_gains > tax_deduction:
                tax_payable = (yearly_realized_gains - tax_deduction) * tax_rate
                total_taxes_paid += tax_payable
                cur_port = sum(current_asset_values.values())
                if cur_port > 0:
                    for a in assets:
                        current_asset_values[a] *= (1.0 - tax_payable / cur_port)
                rebalance_records.append({
                    "Date": dates[i - 1],
                    "Reason": f"Tax Settlement ({current_year}년도 양도세)",
                    "Realized_Gain": yearly_realized_gains,
                    "Portfolio_Value": sum(current_asset_values.values()),
                    "Fee_Paid": 0.0,
                    "Tax_Paid": tax_payable
                })
            current_year = cur_date.year
            yearly_realized_gains = 0.0
        
        # 1. 일간 자산 가치 변동 반영
        for a in assets:
            current_asset_values[a] *= (1.0 + asset_returns.loc[cur_date, a])
            
        # 1-1. DCA 정기 추가 납입 처리
        if periodic_cash_flow > 0:
            dca_period_key = (cur_date.year, cur_date.month) if dca_freq == "M" else cur_date.year
            if dca_period_key != last_dca_period:
                last_dca_period = dca_period_key
                total_contributed += periodic_cash_flow
                dca_fee = periodic_cash_flow * fee_rate
                total_fees_paid += dca_fee
                net_deposit = periodic_cash_flow - dca_fee
                for a in assets:
                    allocated = net_deposit * target_weights[a]
                    current_asset_values[a] += allocated
                    cost_basis_values[a] += allocated
                rebalance_records.append({
                    "Date": cur_date,
                    "Reason": f"DCA Deposit ({'월간' if dca_freq == 'M' else '연간'} 정기적립)",
                    "Realized_Gain": 0.0,
                    "Portfolio_Value": sum(current_asset_values.values()),
                    "Fee_Paid": dca_fee,
                    "Tax_Paid": 0.0
                })

        cur_port_val = sum(current_asset_values.values())
        
        # 2. 리밸런싱 조건 검사
        rebal_reason = None
        
        if rebalance_freq == "M":
            period_key = (cur_date.year, cur_date.month)
            if last_rebal_period != period_key:
                rebal_reason = "Periodic (Monthly)"
                last_rebal_period = period_key
        elif rebalance_freq == "Q":
            period_key = (cur_date.year, (cur_date.month - 1) // 3)
            if last_rebal_period != period_key:
                rebal_reason = "Periodic (Quarterly)"
                last_rebal_period = period_key
        elif rebalance_freq == "Y":
            period_key = cur_date.year
            if last_rebal_period != period_key:
                rebal_reason = "Periodic (Yearly)"
                last_rebal_period = period_key
                
        # 밴드 리밸런싱 검사
        if band_threshold is not None and band_threshold > 0:
            breached_assets = []
            for a in assets:
                cur_w = current_asset_values[a] / cur_port_val if cur_port_val > 0 else 0
                target_w = target_weights[a]
                diff = abs(cur_w - target_w)
                if diff >= band_threshold:
                    breached_assets.append(f"{a} ({cur_w*100:.1f}% vs {target_w*100:.1f}%)")
            if breached_assets:
                rebal_reason = f"Band Breach: {', '.join(breached_assets)}"

        # 3. 리밸런싱 실행
        if rebal_reason and i > 1:
            turnover = 0.0
            rebal_gain = 0.0
            
            for a in assets:
                target_val = cur_port_val * target_weights[a]
                trade_diff = target_val - current_asset_values[a]
                turnover += abs(trade_diff)
                
                # 매도 시 실현 손익 계산 (양도세 산정용)
                if trade_diff < 0:
                    sold_amount = abs(trade_diff)
                    cb = cost_basis_values[a]
                    cur_val_a = current_asset_values[a]
                    gain_fraction = (cur_val_a - cb) / cur_val_a if cur_val_a > 0 else 0.0
                    gain = sold_amount * gain_fraction
                    rebal_gain += gain
                    cost_basis_values[a] -= (sold_amount * (cb / cur_val_a if cur_val_a > 0 else 1.0))
                else:
                    # 매수 시 취득원가 추가
                    cost_basis_values[a] += trade_diff
                    
                current_asset_values[a] = target_val
                
            fee = turnover * fee_rate
            total_fees_paid += fee
            yearly_realized_gains += max(0.0, rebal_gain)
            cur_port_val -= fee
            
            if cur_port_val > 0:
                for a in assets:
                    current_asset_values[a] *= (1.0 - fee / (cur_port_val + fee))
                    
            rebalance_records.append({
                "Date": cur_date,
                "Reason": rebal_reason,
                "Realized_Gain": max(0.0, rebal_gain),
                "Portfolio_Value": cur_port_val,
                "Fee_Paid": fee,
                "Tax_Paid": 0.0
            })
            
        portfolio_value.append(cur_port_val)
        
        # 월별 보유 비중 스냅샷 기록
        ym = f"{cur_date.year}-{cur_date.month:02d}"
        tot_v = sum(current_asset_values.values())
        if tot_v > 0:
            h_strs = [f"{a} ({current_asset_values[a]/tot_v*100:.1f}%)" for a in assets if current_asset_values[a] > 0]
            monthly_holdings_dict[ym] = ", ".join(h_strs)

    # 마지막 연도 잔여 세금 정산
    if tax_rate > 0 and yearly_realized_gains > tax_deduction:
        tax_payable = (yearly_realized_gains - tax_deduction) * tax_rate
        total_taxes_paid += tax_payable
        portfolio_value[-1] -= tax_payable
        rebalance_records.append({
            "Date": dates[-1],
            "Reason": f"Tax Settlement ({current_year}년도 최종 양도세)",
            "Realized_Gain": yearly_realized_gains,
            "Portfolio_Value": portfolio_value[-1],
            "Fee_Paid": 0.0,
            "Tax_Paid": tax_payable
        })
        
    val_series = pd.Series(portfolio_value, index=dates)
    daily_rets = val_series.pct_change().fillna(0.0)
    dd_series = calculate_drawdown(val_series)
    metrics = calculate_metrics(daily_rets, risk_free_rate=risk_free_rate)
    metrics["total_fees_paid"] = float(total_fees_paid)
    metrics["total_taxes_paid"] = float(total_taxes_paid)
    metrics["total_contributed"] = float(total_contributed)
    if periodic_cash_flow > 0 and total_contributed > 0:
        # DCA 투자원금 대비 실질 수익률(MWR / 단순 원금 대비 누적수익률)
        metrics["dca_total_return"] = float((val_series.iloc[-1] - total_contributed) / total_contributed)
    
    monthly_matrix = compute_monthly_returns_matrix(daily_rets)
    rebal_df = pd.DataFrame(rebalance_records)
    monthly_holdings_df = pd.DataFrame([
        {"Year_Month": ym, "Holdings": h} for ym, h in monthly_holdings_dict.items()
    ])
    
    return BacktestResult(
        daily_portfolio_value=val_series,
        daily_returns=daily_rets,
        drawdown=dd_series,
        metrics=metrics,
        monthly_returns=monthly_matrix,
        rebalance_history=rebal_df,
        monthly_holdings=monthly_holdings_df
    )


def run_canary_backtest(
    price_df: pd.DataFrame,
    offensive_assets: List[str],
    defensive_assets: List[str],
    canary_assets: List[str],
    model_type: str = "VAA",
    top_n: int = 1,
    fee_rate: float = 0.0005,
    tax_rate: float = 0.0,
    tax_deduction: float = 0.0,
    initial_capital: float = 100.0,
    risk_free_rate: float = 0.02,
    periodic_cash_flow: float = 0.0,
    dca_freq: str = "M"
) -> BacktestResult:
    """
    카나리아 동적 자산 배분 백테스트 (VAA / DAA 지원) + DCA 적립식 투자 + 거래비용 및 세금 반영
    """
    clean_prices = price_df.ffill().bfill().dropna()
    dates = clean_prices.index
    asset_returns = clean_prices.pct_change().fillna(0.0)
    
    warmup_days = min(252, len(dates) // 3)
    
    all_trade_assets = list(set(offensive_assets + defensive_assets))
    active_weights = {a: 1.0 / len(all_trade_assets) for a in all_trade_assets}
    
    cur_port_val = initial_capital
    portfolio_value = [cur_port_val]
    rebal_records = []
    monthly_holdings_dict = {}
    last_month = None
    last_dca_period = (dates[0].year, dates[0].month) if dca_freq == "M" else dates[0].year
    total_contributed = initial_capital
    
    total_fees_paid = 0.0
    total_taxes_paid = 0.0
    yearly_realized_gains = 0.0
    current_year = dates[0].year
    
    cost_basis = cur_port_val
    
    for i in range(1, len(dates)):
        cur_date = dates[i]
        
        # 연도 변경 시 양도세 정산
        if cur_date.year != current_year:
            if tax_rate > 0 and yearly_realized_gains > tax_deduction:
                tax_payable = (yearly_realized_gains - tax_deduction) * tax_rate
                total_taxes_paid += tax_payable
                cur_port_val -= tax_payable
                rebal_records.append({
                    "Date": dates[i - 1],
                    "Reason": f"Tax Settlement ({current_year}년도 양도세)",
                    "Realized_Gain": yearly_realized_gains,
                    "Portfolio_Value": cur_port_val,
                    "Fee_Paid": 0.0,
                    "Tax_Paid": tax_payable
                })
            current_year = cur_date.year
            yearly_realized_gains = 0.0
        
        day_ret = sum(active_weights.get(a, 0.0) * asset_returns.loc[cur_date, a] for a in all_trade_assets if a in asset_returns.columns)
        cur_port_val *= (1.0 + day_ret)

        # DCA 정기 적립 납입 처리
        if periodic_cash_flow > 0:
            dca_period_key = (cur_date.year, cur_date.month) if dca_freq == "M" else cur_date.year
            if dca_period_key != last_dca_period:
                last_dca_period = dca_period_key
                total_contributed += periodic_cash_flow
                dca_fee = periodic_cash_flow * fee_rate
                total_fees_paid += dca_fee
                net_deposit = periodic_cash_flow - dca_fee
                cur_port_val += net_deposit
                cost_basis += net_deposit
                rebal_records.append({
                    "Date": cur_date,
                    "Reason": f"DCA Deposit ({'월간' if dca_freq == 'M' else '연간'} 정기적립)",
                    "Realized_Gain": 0.0,
                    "Portfolio_Value": cur_port_val,
                    "Fee_Paid": dca_fee,
                    "Tax_Paid": 0.0
                })
        
        if i >= warmup_days and cur_date.month != last_month:
            last_month = cur_date.month
            
            canary_scores = {
                c: calculate_13612_momentum(clean_prices[c].iloc[:i+1])
                for c in canary_assets if c in clean_prices.columns
            }
            
            if model_type == "VAA":
                is_safe = all(score > 0 for score in canary_scores.values()) if canary_scores else True
                offensive_share = 1.0 if is_safe else 0.0
                defensive_share = 1.0 - offensive_share
            elif model_type == "DAA":
                n_pos = sum(1 for score in canary_scores.values() if score > 0)
                n_tot = len(canary_scores) if canary_scores else 1
                offensive_share = n_pos / n_tot
                defensive_share = 1.0 - offensive_share
            else:
                offensive_share = 1.0
                defensive_share = 0.0

            off_scores = {
                a: calculate_13612_momentum(clean_prices[a].iloc[:i+1])
                for a in offensive_assets if a in clean_prices.columns
            }
            sorted_off = sorted(off_scores.items(), key=lambda x: x[1], reverse=True)
            chosen_off = [x[0] for x in sorted_off[:top_n] if x[1] > 0]
            
            def_scores = {
                a: calculate_13612_momentum(clean_prices[a].iloc[:i+1])
                for a in defensive_assets if a in clean_prices.columns
            }
            sorted_def = sorted(def_scores.items(), key=lambda x: x[1], reverse=True)
            chosen_def = [sorted_def[0][0]] if sorted_def else []

            new_weights = {a: 0.0 for a in all_trade_assets}
            if offensive_share > 0 and chosen_off:
                w_each = offensive_share / len(chosen_off)
                for a in chosen_off:
                    new_weights[a] += w_each
            elif offensive_share > 0 and not chosen_off:
                defensive_share += offensive_share
                
            if defensive_share > 0 and chosen_def:
                for a in chosen_def:
                    new_weights[a] += defensive_share

            turnover = sum(abs(new_weights.get(a, 0.0) - active_weights.get(a, 0.0)) for a in all_trade_assets)
            fee = cur_port_val * turnover * fee_rate
            total_fees_paid += fee
            
            # 실현손익 추정
            if turnover > 0.1:
                cur_gain = max(0.0, cur_port_val - cost_basis) * (turnover / 2.0)
                yearly_realized_gains += cur_gain
                cost_basis = cur_port_val
                
            cur_port_val -= fee
            active_weights = new_weights
            
            rebal_records.append({
                "Date": cur_date,
                "Model": model_type,
                "Canary_Status": "SAFE (공격)" if offensive_share == 1.0 else ("DEFENSIVE (수비)" if offensive_share == 0.0 else f"HYBRID ({int(offensive_share*100)}% 공격)"),
                "Offensive": ", ".join(chosen_off) if chosen_off else "None",
                "Defensive": ", ".join(chosen_def) if chosen_def else "None",
                "Portfolio_Value": cur_port_val,
                "Fee_Paid": fee,
                "Tax_Paid": 0.0
            })
            
        portfolio_value.append(cur_port_val)

        # 월별 보유 비중 스냅샷 기록
        ym = f"{cur_date.year}-{cur_date.month:02d}"
        tot_w = sum(active_weights.values())
        if tot_w > 0:
            h_strs = [f"{a} ({active_weights[a]/tot_w*100:.1f}%)" for a in all_trade_assets if active_weights.get(a, 0.0) > 0.001]
            monthly_holdings_dict[ym] = ", ".join(h_strs) if h_strs else "CASH (100.0%)"
        else:
            monthly_holdings_dict[ym] = "CASH (100.0%)"

    if tax_rate > 0 and yearly_realized_gains > tax_deduction:
        tax_payable = (yearly_realized_gains - tax_deduction) * tax_rate
        total_taxes_paid += tax_payable
        portfolio_value[-1] -= tax_payable
        rebal_records.append({
            "Date": dates[-1],
            "Reason": f"Tax Settlement ({current_year}년도 최종 양도세)",
            "Realized_Gain": yearly_realized_gains,
            "Portfolio_Value": portfolio_value[-1],
            "Fee_Paid": 0.0,
            "Tax_Paid": tax_payable
        })

    val_series = pd.Series(portfolio_value, index=dates)
    daily_rets = val_series.pct_change().fillna(0.0)
    dd_series = calculate_drawdown(val_series)
    metrics = calculate_metrics(daily_rets, risk_free_rate=risk_free_rate)
    metrics["total_fees_paid"] = float(total_fees_paid)
    metrics["total_taxes_paid"] = float(total_taxes_paid)
    metrics["total_contributed"] = float(total_contributed)
    if periodic_cash_flow > 0 and total_contributed > 0:
        metrics["dca_total_return"] = float((val_series.iloc[-1] - total_contributed) / total_contributed)
    monthly_matrix = compute_monthly_returns_matrix(daily_rets)
    rebal_df = pd.DataFrame(rebal_records)
    monthly_holdings_df = pd.DataFrame([
        {"Year_Month": ym, "Holdings": h} for ym, h in monthly_holdings_dict.items()
    ])
    
    return BacktestResult(
        daily_portfolio_value=val_series,
        daily_returns=daily_rets,
        drawdown=dd_series,
        metrics=metrics,
        monthly_returns=monthly_matrix,
        rebalance_history=rebal_df,
        monthly_holdings=monthly_holdings_df
    )


def run_momentum_backtest(
    price_df: pd.DataFrame,
    lookback_months: int = 6,
    top_n: int = 1,
    fee_rate: float = 0.0005,
    tax_rate: float = 0.0,
    tax_deduction: float = 0.0,
    initial_capital: float = 100.0,
    risk_free_rate: float = 0.02,
    periodic_cash_flow: float = 0.0,
    dca_freq: str = "M"
) -> BacktestResult:
    """상대 및 절대 모멘텀 전략 백테스트 + DCA 적립식 투자 + 비용/세금 반영"""
    clean_prices = price_df.ffill().bfill().dropna()
    dates = clean_prices.index
    asset_returns = clean_prices.pct_change().fillna(0.0)
    
    lookback_days = lookback_months * 21
    portfolio_value = [initial_capital]
    cur_port_val = initial_capital
    active_weights = {col: 1.0 / len(clean_prices.columns) for col in clean_prices.columns}
    
    rebal_records = []
    monthly_holdings_dict = {}
    last_month = None
    last_dca_period = (dates[0].year, dates[0].month) if dca_freq == "M" else dates[0].year
    total_contributed = initial_capital
    total_fees_paid = 0.0
    total_taxes_paid = 0.0
    yearly_realized_gains = 0.0
    current_year = dates[0].year
    cost_basis = cur_port_val
    
    for i in range(1, len(dates)):
        cur_date = dates[i]
        
        if cur_date.year != current_year:
            if tax_rate > 0 and yearly_realized_gains > tax_deduction:
                tax_payable = (yearly_realized_gains - tax_deduction) * tax_rate
                total_taxes_paid += tax_payable
                cur_port_val -= tax_payable
                rebal_records.append({
                    "Date": dates[i - 1],
                    "Reason": f"Tax Settlement ({current_year}년도 양도세)",
                    "Portfolio_Value": cur_port_val,
                    "Fee_Paid": 0.0,
                    "Tax_Paid": tax_payable
                })
            current_year = cur_date.year
            yearly_realized_gains = 0.0
            
        day_ret = sum(active_weights.get(col, 0.0) * asset_returns.loc[cur_date, col] for col in clean_prices.columns)
        cur_port_val *= (1.0 + day_ret)

        # DCA 정기 적립 처리
        if periodic_cash_flow > 0:
            dca_period_key = (cur_date.year, cur_date.month) if dca_freq == "M" else cur_date.year
            if dca_period_key != last_dca_period:
                last_dca_period = dca_period_key
                total_contributed += periodic_cash_flow
                dca_fee = periodic_cash_flow * fee_rate
                total_fees_paid += dca_fee
                net_deposit = periodic_cash_flow - dca_fee
                cur_port_val += net_deposit
                cost_basis += net_deposit
                rebal_records.append({
                    "Date": cur_date,
                    "Reason": f"DCA Deposit ({'월간' if dca_freq == 'M' else '연간'} 정기적립)",
                    "Selected": ", ".join([c for c, w in active_weights.items() if w > 0.01]) or "CASH",
                    "Portfolio_Value": cur_port_val,
                    "Fee_Paid": dca_fee,
                    "Tax_Paid": 0.0
                })
        
        if i >= lookback_days and cur_date.month != last_month:
            last_month = cur_date.month
            past_prices = clean_prices.iloc[i - lookback_days]
            now_prices = clean_prices.iloc[i]
            mom_scores = (now_prices - past_prices) / past_prices
            
            sorted_assets = mom_scores.sort_values(ascending=False)
            selected = [a for a in sorted_assets.index[:top_n] if sorted_assets[a] > 0]
            
            new_weights = {col: 0.0 for col in clean_prices.columns}
            if selected:
                weight_each = 1.0 / len(selected)
                for a in selected:
                    new_weights[a] = weight_each
            
            turnover = sum(abs(new_weights[c] - active_weights.get(c, 0.0)) for c in clean_prices.columns)
            fee = cur_port_val * turnover * fee_rate
            total_fees_paid += fee
            if turnover > 0.1:
                yearly_realized_gains += max(0.0, cur_port_val - cost_basis) * (turnover / 2.0)
                cost_basis = cur_port_val
                
            cur_port_val -= fee
            active_weights = new_weights
            
            rebal_records.append({
                "Date": cur_date,
                "Reason": "Momentum Rebalance",
                "Selected": ", ".join(selected) if selected else "CASH",
                "Portfolio_Value": cur_port_val,
                "Fee_Paid": fee,
                "Tax_Paid": 0.0
            })
            
        portfolio_value.append(cur_port_val)

        # 월별 보유 비중 스냅샷 기록
        ym = f"{cur_date.year}-{cur_date.month:02d}"
        tot_w = sum(active_weights.values())
        if tot_w > 0:
            h_strs = [f"{c} ({active_weights[c]/tot_w*100:.1f}%)" for c in clean_prices.columns if active_weights.get(c, 0.0) > 0.001]
            monthly_holdings_dict[ym] = ", ".join(h_strs) if h_strs else "CASH (100.0%)"
        else:
            monthly_holdings_dict[ym] = "CASH (100.0%)"
        
    val_series = pd.Series(portfolio_value, index=dates)
    daily_rets = val_series.pct_change().fillna(0.0)
    dd_series = calculate_drawdown(val_series)
    metrics = calculate_metrics(daily_rets, risk_free_rate=risk_free_rate)
    metrics["total_fees_paid"] = float(total_fees_paid)
    metrics["total_taxes_paid"] = float(total_taxes_paid)
    metrics["total_contributed"] = float(total_contributed)
    if periodic_cash_flow > 0 and total_contributed > 0:
        metrics["dca_total_return"] = float((val_series.iloc[-1] - total_contributed) / total_contributed)
    monthly_matrix = compute_monthly_returns_matrix(daily_rets)
    rebal_df = pd.DataFrame(rebal_records)
    monthly_holdings_df = pd.DataFrame([
        {"Year_Month": ym, "Holdings": h} for ym, h in monthly_holdings_dict.items()
    ])
    
    return BacktestResult(
        daily_portfolio_value=val_series,
        daily_returns=daily_rets,
        drawdown=dd_series,
        metrics=metrics,
        monthly_returns=monthly_matrix,
        rebalance_history=rebal_df,
        monthly_holdings=monthly_holdings_df
    )


def run_sma_crossover_backtest(
    price_series: pd.Series,
    short_window: int = 20,
    long_window: int = 60,
    fee_rate: float = 0.0005,
    tax_rate: float = 0.0,
    tax_deduction: float = 0.0,
    initial_capital: float = 100.0,
    risk_free_rate: float = 0.02
) -> BacktestResult:
    """단순 이동평균 교차 (SMA Crossover) 전략 백테스트 + 비용/세금 반영"""
    clean_series = price_series.dropna()
    dates = clean_series.index
    ticker_name = str(clean_series.name) if clean_series.name else "Asset"
    
    sma_short = clean_series.rolling(short_window).mean()
    sma_long = clean_series.rolling(long_window).mean()
    
    signal = (sma_short > sma_long).astype(int).shift(1).fillna(0)
    asset_ret = clean_series.pct_change().fillna(0.0)
    
    portfolio_value = [initial_capital]
    cur_val = initial_capital
    position = 0
    trades = []
    monthly_holdings_dict = {}
    total_fees_paid = 0.0
    total_taxes_paid = 0.0
    yearly_realized_gains = 0.0
    current_year = dates[0].year
    entry_val = cur_val
    
    for i in range(1, len(dates)):
        cur_date = dates[i]
        
        if cur_date.year != current_year:
            if tax_rate > 0 and yearly_realized_gains > tax_deduction:
                tax_payable = (yearly_realized_gains - tax_deduction) * tax_rate
                total_taxes_paid += tax_payable
                cur_val -= tax_payable
                trades.append({
                    "Date": dates[i - 1],
                    "Reason": f"Tax Settlement ({current_year}년도 양도세)",
                    "Portfolio_Value": cur_val,
                    "Fee_Paid": 0.0,
                    "Tax_Paid": tax_payable
                })
            current_year = cur_date.year
            yearly_realized_gains = 0.0
            
        new_pos = int(signal.iloc[i])
        
        if new_pos != position:
            fee = cur_val * fee_rate
            total_fees_paid += fee
            cur_val -= fee
            
            if position == 1 and new_pos == 0:
                trade_gain = max(0.0, cur_val - entry_val)
                yearly_realized_gains += trade_gain
            elif new_pos == 1:
                entry_val = cur_val
                
            position = new_pos
            trades.append({
                "Date": cur_date,
                "Reason": f"SMA Cross ({'BUY' if position == 1 else 'SELL'})",
                "Price": clean_series.iloc[i],
                "Portfolio_Value": cur_val,
                "Fee_Paid": fee,
                "Tax_Paid": 0.0
            })
            
        if position == 1:
            cur_val *= (1.0 + asset_ret.iloc[i])
            
        portfolio_value.append(cur_val)

        ym = f"{cur_date.year}-{cur_date.month:02d}"
        monthly_holdings_dict[ym] = f"{ticker_name} (100.0%)" if position == 1 else "CASH (100.0%)"
        
    val_series = pd.Series(portfolio_value, index=dates)
    daily_rets = val_series.pct_change().fillna(0.0)
    dd_series = calculate_drawdown(val_series)
    metrics = calculate_metrics(daily_rets, risk_free_rate=risk_free_rate)
    metrics["total_fees_paid"] = float(total_fees_paid)
    metrics["total_taxes_paid"] = float(total_taxes_paid)
    monthly_matrix = compute_monthly_returns_matrix(daily_rets)
    rebal_df = pd.DataFrame(trades)
    monthly_holdings_df = pd.DataFrame([
        {"Year_Month": ym, "Holdings": h} for ym, h in monthly_holdings_dict.items()
    ])
    
    return BacktestResult(
        daily_portfolio_value=val_series,
        daily_returns=daily_rets,
        drawdown=dd_series,
        metrics=metrics,
        monthly_returns=monthly_matrix,
        rebalance_history=rebal_df,
        monthly_holdings=monthly_holdings_df
    )


def run_multi_strategy_portfolio(
    price_df: pd.DataFrame,
    strategies: List[Dict[str, Any]],
    fee_rate: float = 0.0005,
    tax_rate: float = 0.0,
    tax_deduction: float = 0.0,
    initial_capital: float = 100.0,
    risk_free_rate: float = 0.02,
    periodic_cash_flow: float = 0.0,
    dca_freq: str = "M"
) -> BacktestResult:
    """
    모듈형 멀티 전략 믹스 빌더:
    사용자가 원하는 복수의 임의 전략(동적1 + 동적2, 정적 + 동적 등)을 각 지정 비중으로 분할 집행하고,
    DCA 적립식 투자, 전략별 성과, 통합 포트폴리오 가치 및 전략별 월별 ETF 보유 내역을 일목요연하게 산출
    """
    if not strategies:
        raise ValueError("최소 1개 이상의 전략이 설정되어야 합니다.")

    tot_w = sum(s.get("weight", 1.0) for s in strategies)
    if tot_w <= 0:
        tot_w = 1.0

    sub_results = {}
    rebal_list = []
    total_fees = 0.0
    total_taxes = 0.0
    total_contrib = 0.0

    for idx, strat in enumerate(strategies):
        s_name = strat.get("name", f"전략 {idx+1}")
        norm_w = strat.get("weight", 1.0) / tot_w
        cap_strat = initial_capital * norm_w
        dca_strat = periodic_cash_flow * norm_w
        stype = strat.get("type", "static")
        params = strat.get("params", {})

        s_tax_deduct = tax_deduction * norm_w

        if stype == "static":
            res = run_rebalancing_backtest(
                price_df=price_df,
                weights=params.get("weights", {}),
                rebalance_freq=params.get("rebalance_freq", "M"),
                band_threshold=params.get("band_threshold", None),
                fee_rate=fee_rate,
                tax_rate=tax_rate,
                tax_deduction=s_tax_deduct,
                initial_capital=cap_strat,
                risk_free_rate=risk_free_rate,
                periodic_cash_flow=dca_strat,
                dca_freq=dca_freq
            )
        elif stype == "canary":
            res = run_canary_backtest(
                price_df=price_df,
                offensive_assets=params.get("offensive", []),
                defensive_assets=params.get("defensive", []),
                canary_assets=params.get("canary", []),
                model_type=params.get("model_type", "VAA"),
                top_n=params.get("top_n", 1),
                fee_rate=fee_rate,
                tax_rate=tax_rate,
                tax_deduction=s_tax_deduct,
                initial_capital=cap_strat,
                risk_free_rate=risk_free_rate,
                periodic_cash_flow=dca_strat,
                dca_freq=dca_freq
            )
        elif stype == "momentum":
            # tickers 필터링 지원
            sub_df = price_df[params["tickers"]] if "tickers" in params and params["tickers"] else price_df
            res = run_momentum_backtest(
                price_df=sub_df,
                lookback_months=params.get("lookback_months", 6),
                top_n=params.get("top_n", 1),
                fee_rate=fee_rate,
                tax_rate=tax_rate,
                tax_deduction=s_tax_deduct,
                initial_capital=cap_strat,
                risk_free_rate=risk_free_rate,
                periodic_cash_flow=dca_strat,
                dca_freq=dca_freq
            )
        elif stype == "sma":
            ticker = params.get("ticker", price_df.columns[0])
            res = run_sma_crossover_backtest(
                price_series=price_df[ticker],
                short_window=params.get("short_window", 20),
                long_window=params.get("long_window", 60),
                fee_rate=fee_rate,
                tax_rate=tax_rate,
                tax_deduction=s_tax_deduct,
                initial_capital=cap_strat,
                risk_free_rate=risk_free_rate
            )
        elif stype == "tripod":
            res = run_tripod_backtest(
                price_df=price_df,
                tripod_weights=params.get("tripod_weights", {"static": 0.333, "canary": 0.333, "momentum": 0.334}),
                static_params=params.get("static_params", {}),
                canary_params=params.get("canary_params", {}),
                momentum_params=params.get("momentum_params", {}),
                fee_rate=fee_rate,
                tax_rate=tax_rate,
                tax_deduction=s_tax_deduct,
                initial_capital=cap_strat,
                risk_free_rate=risk_free_rate,
                periodic_cash_flow=dca_strat,
                dca_freq=dca_freq
            )
        else:
            raise ValueError(f"지원되지 않는 전략 유형: {stype}")

        sub_results[s_name] = res
        total_fees += res.metrics.get("total_fees_paid", 0.0)
        total_taxes += res.metrics.get("total_taxes_paid", 0.0)
        total_contrib += res.metrics.get("total_contributed", cap_strat)

        if not res.rebalance_history.empty:
            rebal_list.append(res.rebalance_history.assign(Strategy=s_name))

    # 합성 포트폴리오 가치
    combined_val = sum(res.daily_portfolio_value for res in sub_results.values())
    daily_rets = combined_val.pct_change().fillna(0.0)
    dd_series = calculate_drawdown(combined_val)
    metrics = calculate_metrics(daily_rets, risk_free_rate=risk_free_rate)
    metrics["total_fees_paid"] = float(total_fees)
    metrics["total_taxes_paid"] = float(total_taxes)
    metrics["total_contributed"] = float(total_contrib)
    if periodic_cash_flow > 0 and total_contrib > 0:
        metrics["dca_total_return"] = float((combined_val.iloc[-1] - total_contrib) / total_contrib)
    monthly_matrix = compute_monthly_returns_matrix(daily_rets)

    rebal_combined = pd.concat(rebal_list, ignore_index=True) if rebal_list else pd.DataFrame()
    if not rebal_combined.empty and "Date" in rebal_combined.columns:
        rebal_combined = rebal_combined.sort_values("Date").reset_index(drop=True)

    # 전략별 월별 ETF 보유 내역 통합 테이블 구성
    # 각 서브 전략의 Year_Month 합집합 도출
    all_yms = set()
    for res in sub_results.values():
        if hasattr(res, "monthly_holdings") and not res.monthly_holdings.empty and "Year_Month" in res.monthly_holdings.columns:
            all_yms.update(res.monthly_holdings["Year_Month"].tolist())
    
    sorted_yms = sorted(list(all_yms))
    holdings_rows = []
    for ym in sorted_yms:
        row = {"Year_Month": ym}
        summary_parts = []
        for s_name, res in sub_results.items():
            h_str = "-"
            if hasattr(res, "monthly_holdings") and not res.monthly_holdings.empty:
                m_sub = res.monthly_holdings[res.monthly_holdings["Year_Month"] == ym]
                if not m_sub.empty:
                    h_str = m_sub.iloc[0]["Holdings"]
            row[f"[{s_name}]"] = h_str
            summary_parts.append(f"{s_name}: {h_str}")
        row["Holdings"] = " | ".join(summary_parts)
        holdings_rows.append(row)

    combined_holdings_df = pd.DataFrame(holdings_rows)

    return BacktestResult(
        daily_portfolio_value=combined_val,
        daily_returns=daily_rets,
        drawdown=dd_series,
        metrics=metrics,
        monthly_returns=monthly_matrix,
        rebalance_history=rebal_combined,
        sub_results=sub_results,
        monthly_holdings=combined_holdings_df
    )


def run_tripod_backtest(
    price_df: pd.DataFrame,
    tripod_weights: Dict[str, float],
    static_params: Dict[str, Any],
    canary_params: Dict[str, Any],
    momentum_params: Dict[str, Any],
    fee_rate: float = 0.0005,
    tax_rate: float = 0.0,
    tax_deduction: float = 0.0,
    initial_capital: float = 100.0,
    risk_free_rate: float = 0.02,
    periodic_cash_flow: float = 0.0,
    dca_freq: str = "M"
) -> BacktestResult:
    """
    트라이포드(Tripod) 멀티전략 앙상블 백테스트:
    3대 독립 엔진 [①정적 자산배분 + ②동적 카나리아 VAA/DAA + ③모멘텀 추세추종]으로
    DCA 적립식 투자를 지원하며 run_multi_strategy_portfolio를 내부적으로 활용하여 일관된 인터페이스와 월별 ETF 보유 내역 제공
    """
    strategies = [
        {
            "name": "엔진 1: 정적 자산배분",
            "weight": tripod_weights.get("static", 0.333),
            "type": "static",
            "params": static_params
        },
        {
            "name": "엔진 2: 동적 카나리아",
            "weight": tripod_weights.get("canary", 0.333),
            "type": "canary",
            "params": canary_params
        },
        {
            "name": "엔진 3: 모멘텀 추세추종",
            "weight": tripod_weights.get("momentum", 0.334),
            "type": "momentum",
            "params": momentum_params
        }
    ]

    res = run_multi_strategy_portfolio(
        price_df=price_df,
        strategies=strategies,
        fee_rate=fee_rate,
        tax_rate=tax_rate,
        tax_deduction=tax_deduction,
        initial_capital=initial_capital,
        risk_free_rate=risk_free_rate,
        periodic_cash_flow=periodic_cash_flow,
        dca_freq=dca_freq
    )
    # tripod_res.sub_results 키 호환성 ("static", "canary", "momentum" 키도 접근 가능하게 매핑)
    res.sub_results["static"] = res.sub_results["엔진 1: 정적 자산배분"]
    res.sub_results["canary"] = res.sub_results["엔진 2: 동적 카나리아"]
    res.sub_results["momentum"] = res.sub_results["엔진 3: 모멘텀 추세추종"]
    return res


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Wilder의 평활 이동평균 기반 RSI(14) 계산:
    RSI = 100 * avg_gain / (avg_gain + avg_loss)
    손실이 전혀 없는 연속 상승 시 100.0, 이익이 전혀 없는 연속 하락 시 0.0을 완벽하게 반환.
    """
    delta = series.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()

    rsi = pd.Series(50.0, index=series.index)
    denom = avg_gain + avg_loss
    valid = denom > 0
    rsi[valid] = 100.0 * (avg_gain[valid] / denom[valid])
    return rsi


def run_nasdaq_tripod_backtest(
    price_df: pd.DataFrame,
    base_asset: str = "QQQ",
    leveraged_2x: str = "QLD",
    leveraged_3x: str = "TQQQ",
    normal_cash_pct: float = 0.30,
    normal_qld_ratio: float = 0.50,
    mdd_milestones: Tuple[float, float, float] = (-0.10, -0.20, -0.30),
    rsi_triggers: Tuple[float, float] = (40.0, 30.0),
    fee_rate: float = 0.0005,
    tax_rate: float = 0.0,
    tax_deduction: float = 0.0,
    initial_capital: float = 100000000.0,
    risk_free_rate: float = 0.02,
    periodic_cash_flow: float = 0.0,
    dca_freq: str = "M"
) -> BacktestResult:
    """
    정통 나스닥 레버리지 트라이포드(Tripod) 전략 백테스트 엔진:
    - 제1축: 자산 배분 (상시 현금 비중 30% 유지 및 폭락장 레버리지 스위칭)
    - 제2축: 과거 40년 MDD 기준 마틴게일식 분할 매수 (-10%, -20%, -30%)
    - 제3축: 과매도 기술적 지표 (RSI 14일 40/30) 결합
    - DCA 정기 적립식 투자 지원, 거래비용 및 연말 양도소득세 정산
    """
    clean_prices = price_df.ffill().bfill().dropna()
    dates = clean_prices.index
    n = len(dates)
    if n == 0:
        raise ValueError("가격 데이터가 비어 있습니다.")

    for t in [base_asset, leveraged_2x, leveraged_3x]:
        if t not in clean_prices.columns:
            raise ValueError(f"트라이포드 전략에 필요한 티커 {t}가 데이터에 존재하지 않습니다.")

    base_series = clean_prices[base_asset]
    base_peak = base_series.cummax()
    base_dd = (base_series - base_peak) / base_peak
    base_rsi = calculate_rsi(base_series, period=14)

    asset_returns = clean_prices[[base_asset, leveraged_2x, leveraged_3x]].pct_change().fillna(0.0)
    daily_rf = (1.0 + risk_free_rate) ** (1.0 / 252.0) - 1.0

    cash_val = initial_capital * normal_cash_pct
    invest_val = initial_capital * (1.0 - normal_cash_pct)
    holdings = {
        "CASH": cash_val,
        base_asset: invest_val * (1.0 - normal_qld_ratio),
        leveraged_2x: invest_val * normal_qld_ratio,
        leveraged_3x: 0.0
    }

    cost_basis = {
        base_asset: invest_val * (1.0 - normal_qld_ratio),
        leveraged_2x: invest_val * normal_qld_ratio,
        leveraged_3x: 0.0
    }

    portfolio_values = []
    rebalance_records = []
    monthly_holdings_dict = {}

    total_fees_paid = 0.0
    total_taxes_paid = 0.0
    total_contributed = float(initial_capital)
    yearly_realized_gains = 0.0
    current_year = dates[0].year
    cur_regime = 0

    dca_dates = set()
    if periodic_cash_flow > 0:
        if dca_freq == "M":
            month_ends = pd.Series(dates, index=dates).resample("ME").last().dropna().values
            dca_dates = set(pd.to_datetime(month_ends))
        elif dca_freq == "W":
            week_ends = pd.Series(dates, index=dates).resample("W").last().dropna().values
            dca_dates = set(pd.to_datetime(week_ends))

    for i in range(n):
        cur_date = dates[i]

        if cur_date.year != current_year:
            if tax_rate > 0 and yearly_realized_gains > tax_deduction:
                tax_payable = (yearly_realized_gains - tax_deduction) * tax_rate
                total_taxes_paid += tax_payable
                if holdings["CASH"] >= tax_payable:
                    holdings["CASH"] -= tax_payable
                else:
                    tot_p = sum(holdings.values())
                    if tot_p > 0:
                        tax_ratio = max(0.0, (tot_p - tax_payable) / tot_p)
                        for k in holdings:
                            holdings[k] *= tax_ratio
                rebalance_records.append({
                    "Date": cur_date,
                    "Reason": f"Tax Settlement ({current_year}년도 양도소득세)",
                    "Realized_Gain": yearly_realized_gains,
                    "Portfolio_Value": sum(holdings.values()),
                    "Fee_Paid": 0.0,
                    "Tax_Paid": tax_payable
                })
            yearly_realized_gains = 0.0
            current_year = cur_date.year

        if i > 0:
            holdings["CASH"] *= (1.0 + daily_rf)
            for asset in [base_asset, leveraged_2x, leveraged_3x]:
                holdings[asset] *= (1.0 + asset_returns[asset].iloc[i])

        if cur_date in dca_dates:
            holdings["CASH"] += periodic_cash_flow
            total_contributed += periodic_cash_flow

        tot_port = sum(holdings.values())

        cur_dd = base_dd.iloc[i]
        cur_rsi = base_rsi.iloc[i]

        mdd_1, mdd_2, mdd_3 = mdd_milestones
        rsi_mild, rsi_extreme = rsi_triggers

        new_regime = 0
        if cur_dd <= mdd_3 or (cur_dd <= mdd_2 and cur_rsi <= rsi_extreme):
            new_regime = 3
        elif cur_dd <= mdd_2 or (cur_dd <= mdd_1 and cur_rsi <= rsi_mild):
            new_regime = 2
        elif cur_dd <= mdd_1 or cur_rsi <= 45.0:
            new_regime = 1
        else:
            new_regime = 0

        if new_regime == 3:
            target_weights = {"CASH": 0.0, base_asset: 0.0, leveraged_2x: 0.15, leveraged_3x: 0.85}
            regime_name = "🚨 대폭락 국면 (현금 0% 소진, TQQQ 집중 매수)"
        elif new_regime == 2:
            target_weights = {"CASH": 0.10, base_asset: 0.20, leveraged_2x: 0.50, leveraged_3x: 0.20}
            regime_name = "⚠️ 본격 하락 국면 (현금 분할 투입, 레버리지 비중 확대)"
        elif new_regime == 1:
            target_weights = {"CASH": 0.20, base_asset: 0.35, leveraged_2x: 0.40, leveraged_3x: 0.05}
            regime_name = "⚡ 초기 조정 국면 (1차 분할 매수 가동)"
        else:
            w_inv = 1.0 - normal_cash_pct
            target_weights = {
                "CASH": normal_cash_pct,
                base_asset: w_inv * (1.0 - normal_qld_ratio),
                leveraged_2x: w_inv * normal_qld_ratio,
                leveraged_3x: 0.0
            }
            regime_name = f"🟢 평상시 운용 (상시 현금 {normal_cash_pct*100:.0f}% + QQQ/QLD)"

        is_month_end = (i == n - 1) or (dates[i + 1].month != cur_date.month)
        regime_changed = (new_regime != cur_regime)

        if regime_changed or is_month_end:
            trade_vol = 0.0
            rebal_gain = 0.0

            for k, tgt_w in target_weights.items():
                cur_k_val = holdings[k]
                tgt_k_val = tot_port * tgt_w
                trade_diff = tgt_k_val - cur_k_val
                trade_vol += abs(trade_diff)

                # 주식/ETF 자산 매도 시 실현 이익 계산 (양도소득세 과세표준)
                if k != "CASH":
                    if trade_diff < 0:
                        sold_amount = abs(trade_diff)
                        cb = cost_basis[k]
                        if cur_k_val > 0:
                            gain_fraction = (cur_k_val - cb) / cur_k_val
                            gain = sold_amount * gain_fraction
                            rebal_gain += gain
                            cost_basis[k] -= sold_amount * (cb / cur_k_val)
                    else:
                        # 추가 매수 시 취득원가 가산
                        cost_basis[k] += trade_diff

            fee = (trade_vol / 2.0) * fee_rate
            total_fees_paid += fee
            yearly_realized_gains += max(0.0, rebal_gain)
            tot_port -= fee
            
            for k, tgt_w in target_weights.items():
                holdings[k] = tot_port * tgt_w

            if regime_changed:
                rebalance_records.append({
                    "Date": cur_date,
                    "Reason": f"Tripod 전환: {regime_name} (MDD: {cur_dd*100:.1f}%, RSI: {cur_rsi:.1f})",
                    "Realized_Gain": max(0.0, rebal_gain),
                    "Portfolio_Value": tot_port,
                    "Fee_Paid": fee,
                    "Tax_Paid": 0.0
                })
            cur_regime = new_regime

        tot_val = sum(holdings.values())
        portfolio_values.append(tot_val)

        ym = f"{cur_date.year}-{cur_date.month:02d}"
        if tot_val > 0:
            h_str = f"현금 {holdings['CASH']/tot_val*100:.1f}%, {base_asset} {holdings[base_asset]/tot_val*100:.1f}%, {leveraged_2x} {holdings[leveraged_2x]/tot_val*100:.1f}%, {leveraged_3x} {holdings[leveraged_3x]/tot_val*100:.1f}% [{regime_name.split(' ')[1]}]"
            monthly_holdings_dict[ym] = h_str

    if tax_rate > 0 and yearly_realized_gains > tax_deduction:
        tax_payable = (yearly_realized_gains - tax_deduction) * tax_rate
        total_taxes_paid += tax_payable
        portfolio_values[-1] -= tax_payable

    val_series = pd.Series(portfolio_values, index=dates)
    daily_rets = val_series.pct_change().fillna(0.0)
    dd_series = calculate_drawdown(val_series)
    metrics = calculate_metrics(daily_rets, risk_free_rate=risk_free_rate)
    metrics["total_fees_paid"] = float(total_fees_paid)
    metrics["total_taxes_paid"] = float(total_taxes_paid)
    metrics["total_contributed"] = float(total_contributed)
    if periodic_cash_flow > 0 and total_contributed > 0:
        metrics["dca_total_return"] = float((val_series.iloc[-1] - total_contributed) / total_contributed)

    monthly_matrix = compute_monthly_returns_matrix(daily_rets)
    rebal_df = pd.DataFrame(rebalance_records)
    monthly_holdings_df = pd.DataFrame([
        {"Year_Month": ym, "Holdings": h} for ym, h in monthly_holdings_dict.items()
    ])

    return BacktestResult(
        daily_portfolio_value=val_series,
        daily_returns=daily_rets,
        drawdown=dd_series,
        metrics=metrics,
        monthly_returns=monthly_matrix,
        rebalance_history=rebal_df,
        monthly_holdings=monthly_holdings_df
    )


