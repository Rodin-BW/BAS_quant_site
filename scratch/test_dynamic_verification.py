import urllib.request
import json
import time
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

payloads = [
    ('DAA 균형형 (2015-2024)', {
        'mode': 'dynamic',
        'startDate': '2015-01-01',
        'endDate': '2024-01-01',
        'initialCapital': 100000000,
        'dynamic': {
            'model': 'DAA',
            'offensive': ['SPY', 'QQQ', 'IWM', 'VGK', 'EWJ', 'EEM', 'VNQ', 'GLD', 'TLT', 'HYG', 'LQD'],
            'defensive': ['SHY', 'IEF', 'LQD'],
            'canary': ['VWO', 'BND'],
            'topN': 2,
            'lookbackMonths': 6
        }
    }),
    ('VAA 공격형 (2015-2024)', {
        'mode': 'dynamic',
        'startDate': '2015-01-01',
        'endDate': '2024-01-01',
        'initialCapital': 100000000,
        'dynamic': {
            'model': 'VAA',
            'offensive': ['SPY', 'IWM', 'QQQ', 'VGK', 'EWJ', 'EEM', 'VNQ', 'GLD', 'TLT', 'HYG'],
            'defensive': ['LQD', 'IEF', 'SHY'],
            'canary': ['SPY', 'EFA', 'EEM', 'AGG'],
            'topN': 1,
            'lookbackMonths': 6
        }
    }),
    ('듀얼 모멘텀 (2015-2024)', {
        'mode': 'dynamic',
        'startDate': '2015-01-01',
        'endDate': '2024-01-01',
        'initialCapital': 100000000,
        'dynamic': {
            'model': 'MOMENTUM',
            'offensive': ['SPY', 'EFA', 'AGG', 'BIL'],
            'defensive': ['AGG'],
            'canary': [],
            'topN': 1,
            'lookbackMonths': 12
        }
    })
]

print("=== 동적 자산배분 모델별 실시간 퀀트 백테스트 검증 ===")
for name, p in payloads:
    t0 = time.time()
    req = urllib.request.Request(
        'http://127.0.0.1:8502/api/backtest',
        data=json.dumps(p).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    res = urllib.request.urlopen(req)
    d = json.loads(res.read().decode('utf-8'))
    elapsed = time.time() - t0
    cagr = d.get('cagr')
    mdd = d.get('mdd')
    sharpe = d.get('sharpe')
    wealth = d.get('finalWealth')
    reb_cnt = len(d.get('recentRebalances', []))
    curve_cnt = len(d.get('curveData', []))
    print(f"[{name}] (소요시간: {elapsed:.2f}s)")
    print(f"  - CAGR: {cagr:.2f}% | MDD: {mdd:.2f}% | Sharpe: {sharpe:.2f}")
    print(f"  - 최종 평가금액: ₩{wealth:,}원 (초기 1억원 대비)")
    print(f"  - 일봉 데이터 포인트: {curve_cnt}개, 리밸런싱 기록: {reb_cnt}개")
    if reb_cnt > 0:
        sample = d['recentRebalances'][0]
        print(f"  - 최근 리밸런싱 샘플: 날짜={sample.get('date')}, 시그널={sample.get('type')}, 보유={sample.get('alloc')}, 조치={sample.get('action')}")
    print()
