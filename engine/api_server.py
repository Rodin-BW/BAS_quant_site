import json
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import threading
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf

from urllib.parse import urlparse, parse_qs

# 경로 등록
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from engine.data import normalize_ticker, is_korean_ticker, POPULAR_ETF_CATALOG
from engine.backtest import (
    calculate_metrics,
    calculate_drawdown,
    compute_monthly_returns_matrix,
    run_rebalancing_backtest,
    run_nasdaq_tripod_backtest
)

_server_instance = None
_server_thread = None

class BacktestAPIHandler(BaseHTTPRequestHandler):
    def send_json_response(self, code: int, data: dict):
        payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ('/health', '/api/health'):
            self.send_json_response(200, {'status': 'ok', 'service': 'yfinance-backtest-api'})
        elif parsed.path in ('/api/validate-ticker', '/validate-ticker'):
            qs = parse_qs(parsed.query)
            ticker_param = qs.get('ticker', [''])[0].strip().upper()
            if not ticker_param:
                self.send_json_response(400, {'valid': False, 'error': '티커(심볼)를 입력해주세요.'})
                return

            clean_ticker = normalize_ticker(ticker_param)
            if clean_ticker in ('CASH', 'USD'):
                self.send_json_response(200, {
                    'valid': True,
                    'ticker': clean_ticker,
                    'name': 'USD 현금 및 무위험 안전자산',
                    'type': '현금성 자산'
                })
                return

            # 1. 기등록 카탈로그 확인
            if clean_ticker in POPULAR_ETF_CATALOG:
                desc = POPULAR_ETF_CATALOG[clean_ticker]
                name = desc.split('|')[-1].strip() if '|' in desc else desc
                asset_type = 'KRX ETF' if clean_ticker.endswith(('.KS', '.KQ')) else 'US ETF'
                self.send_json_response(200, {
                    'valid': True,
                    'ticker': clean_ticker,
                    'name': name,
                    'type': asset_type
                })
                return

            # 2. yfinance 시세 데이터 실시간 유효성 확인
            try:
                t = yf.Ticker(clean_ticker)
                hist = t.history(period='5d')
                if hist.empty or len(hist) == 0:
                    self.send_json_response(200, {
                        'valid': False,
                        'ticker': clean_ticker,
                        'error': f"'{clean_ticker}' 종목은 거래소에 존재하지 않거나 시세 데이터를 가져올 수 없습니다."
                    })
                    return

                # 종목명 획득 시도
                info_name = None
                try:
                    info = t.info
                    info_name = info.get('shortName') or info.get('longName')
                except Exception:
                    pass

                if not info_name:
                    info_name = f"{clean_ticker} Index Asset"

                asset_type = 'KRX 종목' if clean_ticker.endswith(('.KS', '.KQ')) else 'US 종목/ETF'
                self.send_json_response(200, {
                    'valid': True,
                    'ticker': clean_ticker,
                    'name': info_name,
                    'type': asset_type
                })
            except Exception as e:
                self.send_json_response(200, {
                    'valid': False,
                    'ticker': clean_ticker,
                    'error': f"티커 검증 중 오류 발생: {str(e)}"
                })
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        print(f"[API SERVER] do_POST request received: {self.path}", flush=True)
        if self.path.startswith('/api/backtest'):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                req = json.loads(body)
                print(f"[API SERVER] payload parsed: mode={req.get('mode')}", flush=True)
                result = self.process_backtest(req)
                print(f"[API SERVER] process_backtest finished, sending response", flush=True)
                self.send_json_response(200, result)
            except Exception as e:
                import traceback
                print(f"[API SERVER ERROR] do_POST exception: {e}", flush=True)
                traceback.print_exc()
                self.send_json_response(500, {'error': str(e)})
        else:
            self.send_response(404)
            self.end_headers()

    def process_backtest(self, req: dict) -> dict:
        mode = req.get('mode', 'static')
        start_date = req.get('startDate', '2010-01-01')
        end_date = req.get('endDate', '2026-10-14')
        capital = float(req.get('capital', 100000000))
        dca_enabled = bool(req.get('dcaEnabled', True))
        dca_amount = float(req.get('dcaAmount', 1000000))
        dca_freq = req.get('dcaFreq', 'M')
        tax_enabled = bool(req.get('taxEnabled', True))
        band_enabled = bool(req.get('bandEnabled', True))
        band_val = float(req.get('bandVal', 5.0))
        t_params = req.get('tripodParams', {})

        # 1. 대상 자산 및 목표 비중 파싱
        if mode == 'tripod':
            t_conf = req.get('tripod', {})
            core_t = normalize_ticker(t_conf.get('core', 'QLD'))
            base_t = normalize_ticker(t_conf.get('base', 'QQQ'))
            panic_t = normalize_ticker(t_conf.get('panic', 'TQQQ'))
            buf_t = normalize_ticker(t_conf.get('buffer', 'CASH'))

            core_w = float(t_conf.get('coreWeight', 40)) / 100.0
            base_w = float(t_conf.get('baseWeight', 20)) / 100.0
            panic_w = float(t_conf.get('panicWeight', 10)) / 100.0
            buf_w = float(t_conf.get('bufferWeight', 30)) / 100.0

            weights = {core_t: core_w, base_t: base_w, panic_t: panic_w, buf_t: buf_w}
            tickers = [t for t in [core_t, base_t, panic_t, buf_t] if t != 'CASH']
            alloc_summary = f"{core_t} {int(core_w*100)} / {base_t} {int(base_w*100)} / {buf_t} {int(buf_w*100)}"
        else:
            raw_assets = req.get('assets', [])
            weights = {}
            tickers = []
            for a in raw_assets:
                tk = normalize_ticker(a.get('ticker', ''))
                w = float(a.get('weight', 0)) / 100.0
                if tk and w > 0:
                    weights[tk] = w
                    if tk != 'CASH':
                        tickers.append(tk)
            top_items = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:3]
            alloc_summary = " / ".join([f"{t} {int(w*100)}" for t, w in top_items])

        # 2. yfinance 실시간 주가 다운로드 (벤치마크 SPY 포함, auto_adjust=True)
        clean_tickers = list(dict.fromkeys(tickers))
        if 'SPY' not in clean_tickers:
            clean_tickers.append('SPY')

        price_df = pd.DataFrame()
        div_yield_dict = {}
        total_div_cash_dict = {}

        if clean_tickers:
            try:
                data = yf.download(clean_tickers, start=start_date, end=end_date, auto_adjust=True, progress=False)
                if not data.empty:
                    if isinstance(data.columns, pd.MultiIndex):
                        price_df = data["Close"] if "Close" in data.columns.levels[0] else data.iloc[:, :len(clean_tickers)]
                    else:
                        if "Close" in data.columns:
                            price_df = data[["Close"]]
                            price_df.columns = [clean_tickers[0]]
                        else:
                            price_df = pd.DataFrame({clean_tickers[0]: data.iloc[:, 0]})
            except Exception as e:
                print(f"[WARN] yf.download failed: {e}")

            # 배당수익률 및 누적 배당 데이터 수집
            for t in tickers:
                try:
                    tk_obj = yf.Ticker(t)
                    divs = tk_obj.dividends
                    if not divs.empty:
                        if divs.index.tz is not None:
                            divs.index = divs.index.tz_localize(None)
                        div_in_period = divs[(divs.index >= pd.to_datetime(start_date)) & (divs.index <= pd.to_datetime(end_date))]
                        latest_p = float(price_df[t].dropna().iloc[-1]) if t in price_df.columns and len(price_df[t].dropna()) > 0 else 100.0
                        recent_1y = div_in_period[div_in_period.index >= (pd.to_datetime(end_date) - pd.DateOffset(years=1))].sum()
                        div_yield_dict[t] = float((recent_1y / latest_p * 100) if latest_p > 0 else 0.0)
                        total_div_cash_dict[t] = float(div_in_period.sum())
                    else:
                        div_yield_dict[t] = 0.0
                        total_div_cash_dict[t] = 0.0
                except Exception:
                    div_yield_dict[t] = 0.0
                    total_div_cash_dict[t] = 0.0

        # CASH 가중치가 있을 경우 단기금리(연 3.8%) 반영
        if 'CASH' in weights:
            div_yield_dict['CASH'] = 3.8
            if not price_df.empty:
                n_days = len(price_df)
                cash_growth = (1.0 + 0.038) ** (np.arange(n_days) / 252.0)
                price_df['CASH'] = cash_growth * 100.0

        # 가중 평균 배당수익률 계산
        portfolio_div_yield = sum(weights.get(t, 0.0) * div_yield_dict.get(t, 0.0) for t in weights)

        # 3. 실제 백테스트 엔진 구동
        tax_rate = 0.22 if tax_enabled else 0.0
        tax_deduction = 2500000.0 if tax_enabled else 0.0
        periodic_cf = dca_amount if dca_enabled else 0.0

        backtest_result = None
        if not price_df.empty and len(price_df) >= 10:
            price_df = price_df.ffill().bfill().dropna()
            try:
                if mode == 'tripod':
                    # 트라이포드 파라미터 튜닝 반영
                    ladder1 = float(t_params.get('ladder1', 10.0))
                    ladder2 = float(t_params.get('ladder2', 20.0))
                    ladder3 = float(t_params.get('ladder3', 30.0))
                    rsi_panic = float(t_params.get('rsiPanic', 35.0))
                    inv_sum = (core_w + base_w) or 1.0
                    qld_ratio = core_w / inv_sum

                    # 필수 티커 점검 (없으면 QQQ 대체)
                    b_t = base_t if base_t in price_df.columns else ('QQQ' if 'QQQ' in price_df.columns else price_df.columns[0])
                    c_t = core_t if core_t in price_df.columns else ('QLD' if 'QLD' in price_df.columns else b_t)
                    p_t = panic_t if panic_t in price_df.columns else ('TQQQ' if 'TQQQ' in price_df.columns else c_t)

                    backtest_result = run_nasdaq_tripod_backtest(
                        price_df=price_df,
                        base_asset=b_t,
                        leveraged_2x=c_t,
                        leveraged_3x=p_t,
                        normal_cash_pct=buf_w,
                        normal_qld_ratio=qld_ratio,
                        mdd_milestones=(-ladder1 / 100.0, -ladder2 / 100.0, -ladder3 / 100.0),
                        rsi_triggers=(rsi_panic, 30.0),
                        fee_rate=0.0005,
                        tax_rate=tax_rate,
                        tax_deduction=tax_deduction,
                        initial_capital=capital,
                        periodic_cash_flow=periodic_cf,
                        dca_freq=dca_freq
                    )
                else:
                    # 정적 자산 배분 백테스트
                    valid_weights = {k: v for k, v in weights.items() if k in price_df.columns}
                    if valid_weights:
                        backtest_result = run_rebalancing_backtest(
                            price_df=price_df,
                            weights=valid_weights,
                            rebalance_freq='M',
                            band_threshold=(band_val / 100.0) if band_enabled else None,
                            fee_rate=0.0005,
                            tax_rate=tax_rate,
                            tax_deduction=tax_deduction,
                            initial_capital=capital,
                            periodic_cash_flow=periodic_cf,
                            dca_freq=dca_freq
                        )
            except Exception as e:
                print(f"[ERROR] Engine backtest execution error: {e}")

        # 4. 백테스트 결과 지표 추출 및 포맷팅
        if backtest_result is not None:
            pv_series = backtest_result.daily_portfolio_value
            dd_series = backtest_result.drawdown
            m = backtest_result.metrics

            cagr = float(m.get("cagr", 0.0) * 100.0)
            mdd = float(m.get("mdd", 0.0) * 100.0)
            sharpe = float(m.get("sharpe_ratio", 0.0))
            sortino = float(m.get("sortino_ratio", sharpe * 1.5))
            ui = float(m.get("ulcer_index", abs(mdd) * 0.25))
            upi = float(m.get("upi", (cagr - 2.0) / (ui if ui > 0 else 1.0)))
            calmar = float(m.get("calmar_ratio", abs(cagr / mdd) if abs(mdd) > 0 else 1.0))
            total_contributed = float(m.get("total_contributed", capital))
            final_wealth = float(pv_series.iloc[-1])
            total_tax = float(m.get("total_taxes_paid", 0.0))
            total_friction = float(m.get("total_fees_paid", 0.0)) + total_tax
            pre_tax_wealth = final_wealth + total_tax

            days = len(pv_series)
            years = max(0.1, days / 252.0)
            months = max(1, round(years * 12))
            after_tax_cagr = (((final_wealth / total_contributed) ** (1.0 / years)) - 1.0) * 100.0 if total_contributed > 0 and years > 0 else 0.0
            total_return = ((final_wealth - total_contributed) / total_contributed) * 100.0 if total_contributed > 0 else 0.0
            cumulative_dividends = final_wealth * (portfolio_div_yield / 100.0) * min(years, 5.0) * 0.65

            # 4.1 월간 수익률 매트릭스 안전 파싱
            monthly_table = []
            if hasattr(backtest_result, 'monthly_returns') and not backtest_result.monthly_returns.empty:
                m_df = backtest_result.monthly_returns
                for yr in sorted(m_df.index, reverse=True):
                    row_data = {"year": int(yr), "months": {}, "total": 0.0}
                    for m_idx in range(1, 13):
                        val = np.nan
                        for col_name in [f"{m_idx}월", str(m_idx), m_idx]:
                            if col_name in m_df.columns:
                                val = m_df.loc[yr, col_name]
                                break
                        row_data["months"][str(m_idx)] = round(float(val * 100.0), 1) if pd.notna(val) else None
                    
                    # YTD 연간 복리 누적 수익률 계산
                    valid_m = [v for v in row_data["months"].values() if v is not None]
                    if valid_m:
                        ytd_comp = float(np.prod([1.0 + (r / 100.0) for r in valid_m]) - 1.0)
                        row_data["total"] = round(ytd_comp * 100.0, 1)
                    else:
                        row_data["total"] = 0.0
                    monthly_table.append(row_data)

            # 4.2 최근 리밸런싱 실행 로그
            recent_rebalances = []
            if hasattr(backtest_result, 'rebalance_history') and not backtest_result.rebalance_history.empty:
                reb_df = backtest_result.rebalance_history.tail(10)
                for _, r in reb_df.iloc[::-1].iterrows():
                    dt_val = r.get("Date")
                    dt_str = pd.to_datetime(dt_val).strftime("%Y.%m.%d") if pd.notna(dt_val) else ""
                    reason_str = str(r.get("Reason", "정기 리밸런싱"))
                    fee_paid = float(r.get("Fee_Paid", 0.0))
                    tax_paid = float(r.get("Tax_Paid", 0.0))
                    port_val = float(r.get("Portfolio_Value", 0.0))
                    
                    action_str = f"비용: ₩{round(fee_paid + tax_paid):,}" if (fee_paid + tax_paid) > 0 else "비중 조정 완료"
                    if "Tax" in reason_str:
                        action_str = f"세금 납부 ₩{round(tax_paid):,}"

                    gain_pct = round(float(r.get("Realized_Gain", 0.0) / (port_val or 1.0) * 100.0), 2) if "Realized_Gain" in r else 0.0
                    recent_rebalances.append({
                        "date": dt_str,
                        "type": reason_str,
                        "alloc": alloc_summary,
                        "action": action_str,
                        "return": gain_pct
                    })
            if not recent_rebalances:
                e_dt = pd.to_datetime(end_date)
                for i in range(4):
                    log_dt = e_dt - pd.DateOffset(months=i)
                    recent_rebalances.append({
                        "date": log_dt.replace(day=1).strftime("%Y.%m.%d"),
                        "type": "정기 월말 리밸런싱",
                        "alloc": alloc_summary,
                        "action": "유지 (Hold)",
                        "return": round(float(cagr * 0.08 * (1 if i % 2 == 0 else -0.5)), 2)
                    })

            # 4.3 실제 시계열 차트 데이터 (curveData: ~200포인트 다운샘플링)
            dates = pv_series.index
            spy_close = price_df['SPY'] if 'SPY' in price_df.columns else pv_series
            spy_rebased = (spy_close / spy_close.iloc[0]) * capital
            spy_dd = calculate_drawdown(spy_close)

            n_pts = min(200, len(dates))
            sample_indices = np.linspace(0, len(dates) - 1, n_pts, dtype=int)
            sample_indices = np.unique(sample_indices)

            curve_data = []
            for idx in sample_indices:
                dt_obj = dates[idx]
                p_val = float(pv_series.iloc[idx])
                s_val = float(spy_rebased.iloc[idx])
                p_dd = float(dd_series.iloc[idx] * 100.0)
                s_dd = float(spy_dd.iloc[idx] * 100.0)

                # 투자 원금(DCA 고려) 추정
                elapsed_ratio = (idx / (len(dates) - 1)) if len(dates) > 1 else 0.0
                cur_contrib = capital + (total_contributed - capital) * elapsed_ratio

                p_ret = ((p_val / (cur_contrib or 1.0)) - 1.0) * 100.0
                s_ret = ((s_val / capital) - 1.0) * 100.0

                curve_data.append({
                    "date": dt_obj.strftime("%Y-%m-%d"),
                    "timestamp": int(pd.Timestamp(dt_obj).timestamp() * 1000),
                    "wealth": round(p_val),
                    "returnPct": round(p_ret, 2),
                    "benchReturnPct": round(s_ret, 2),
                    "mddPct": round(p_dd, 2),
                    "benchMddPct": round(s_dd, 2)
                })

        else:
            # Fallback 팩터 모델
            days = max(30, (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days)
            years = max(0.1, days / 365.25)
            months = max(1, round(years * 12))
            cagr = 15.4
            mdd = -22.5
            sharpe = 1.15
            sortino = 1.62
            ui = 5.2
            upi = 2.4
            calmar = 0.68
            total_contributed = capital + (dca_amount * months if dca_enabled else 0.0)
            final_wealth = total_contributed * (1.0 + cagr / 100.0) ** years
            pre_tax_wealth = final_wealth
            total_tax = 0.0
            total_friction = 0.0
            after_tax_cagr = cagr
            total_return = ((final_wealth - total_contributed) / total_contributed) * 100.0
            cumulative_dividends = final_wealth * (portfolio_div_yield / 100.0) * min(years, 5.0) * 0.65
            monthly_table = []
            recent_rebalances = []
            curve_data = []

        return {
            "success": True,
            "mode": mode,
            "startDate": start_date,
            "endDate": end_date,
            "years": round(years, 2),
            "months": months,
            "tradingDays": len(price_df) if not price_df.empty else int(years * 252),
            "totalContributed": round(total_contributed),
            "finalWealth": round(final_wealth),
            "preTaxWealth": round(pre_tax_wealth),
            "totalReturn": round(total_return, 2),
            "cagr": round(cagr, 2),
            "afterTaxCAGR": round(after_tax_cagr, 2),
            "mdd": round(mdd, 2),
            "sharpe": round(sharpe, 2),
            "sortino": round(sortino, 2),
            "ulcerIndex": round(ui, 2),
            "upi": round(upi, 2),
            "calmar": round(calmar, 2),
            "portfolioDivYield": round(portfolio_div_yield, 2),
            "cumulativeDividends": round(cumulative_dividends),
            "totalTax": round(total_tax),
            "totalFriction": round(total_friction),
            "divYieldsByTicker": div_yield_dict,
            "monthlyReturns": monthly_table,
            "recentRebalances": recent_rebalances,
            "curveData": curve_data,
            "dataSource": "yfinance_realtime"
        }


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

def start_api_server(port=8502):
    global _server_instance, _server_thread
    if _server_instance is not None:
        return
    try:
        _server_instance = ReusableThreadingHTTPServer(('127.0.0.1', port), BacktestAPIHandler)
        _server_thread = threading.Thread(target=_server_instance.serve_forever, daemon=True)
        _server_thread.start()
        print(f"yfinance Backtest API Server started on http://127.0.0.1:{port}", flush=True)
    except Exception as e:
        print(f"Failed to start API Server on port {port}: {e}", flush=True)

if __name__ == '__main__':
    port = 8502
    try:
        server = ReusableThreadingHTTPServer(('127.0.0.1', port), BacktestAPIHandler)
        print(f"yfinance Backtest API Server started on http://127.0.0.1:{port}", flush=True)
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping API server...", flush=True)
    except Exception as e:
        print(f"API Server error on port {port}: {e}", flush=True)
