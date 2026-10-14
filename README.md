# ⚡ 블암스 ETF 백테스팅 (BAS Quant Platform)

> **한국 & 미국 상장 ETF 기반 퀀트 투자 분석 및 실시간 백테스팅 플랫폼**  
> 정적 자산배분 · 나스닥 레버리지 트라이포드(Tripod) 전략 · DCA 정기 적립식 시뮬레이션 및 전문 기관급 위험조정 지표 완벽 제공

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📌 프로젝트 소개 (Overview)

**블암스 ETF 백테스팅**은 개인 투자자가 직관적이면서도 기관급 정밀도로 ETF 포트폴리오를 설계하고 검증할 수 있도록 제작된 모던 퀀트 백테스팅 웹 솔루션입니다.

초보 투자자부터 전문 퀀트 투자자까지 모두 만족할 수 있도록 **미니멀 & 세련된 핀테크 UI(Toss / Snowball 스타일)**를 적용하였으며, 단순 수익률 비교를 넘어 **소티노 지수, 궤양지수(Ulcer Index), 궤양성과지수(UPI/Martin), 칼마 지수, 양도소득세 정산, 거래비용(수수료+슬리피지)**까지 실전 투자 환경을 100% 동일하게 시뮬레이션합니다.

---

## 🎯 핵심 전략 엔진 (Core Strategies)

### 1. 🏛️ 정적 자산배분 (Static Asset Allocation)
- **올웨더(All Weather)**, **영구 포트폴리오(Permanent)**, **주식/채권 60:40**, **나스닥 집중** 등 검증된 대가들의 자산배분 프리셋 1초 로드.
- **실시간 비중 도넛 차트** 및 슬라이더·뱃지 일체형 카드 인터페이스.
- 동일 가중(1/N) 배분 및 현재 비율 기준 100% 자동 정규화 원클릭 지원.
- 정기 리밸런싱(월간/분기/연간/Buy & Hold)과 **허용 오차폭(±%p) 밴드 리밸런싱** 지원.

### 2. ⚡ 나스닥 레버리지 트라이포드 전략 (Nasdaq Leverage Tripod)
음의 복리 효과(계좌 녹아내림)를 방어하고 시장 우상향 시 폭발적인 복리 수익을 추구하는 3대 축 전략:
- **제1축: 자산 배분 & 스위칭**
  - 평상시 상시 현금 비중(예: 30%)과 1배수(QQQ), 2배수(QLD) ETF를 보유하여 상승 복리를 누리며 예비 탄약을 비축.
- **제2축: 과거 40년 데이터 기반 MDD 분할 매수**
  - 감정에 치우친 물타기를 배제하고 고점 대비 낙폭(-10%, -20%, -30%) 마일스톤에 따라 기계적 분할 진입.
- **제3축: RSI 과매도 공포 탐지**
  - 일봉/주봉 RSI가 과매도(40 이하, 30 이하) 구간 및 극단적 공포에 도달 시 비축된 현금을 3배 레버리지(TQQQ)로 집중 전환.

### 3. 💵 DCA 정기 적립식 투자 엔진 (Dollar Cost Averaging)
- 단순 거치식 투자뿐만 아니라 매월/매분기/매년 규칙적으로 자금을 추가 투입하는 실전 적립식 투자 시뮬레이션.
- 총 투입 원금 대비 실질 수익률(MWRR/DCA Return) 정밀 계산.

---

## 📊 기관급 성과 및 위험조정 지표 (Metrics)

| 지표 | 국문 명칭 | 설명 |
| :--- | :--- | :--- |
| **CAGR** | 연평균 복리 수익률 | 전체 시뮬레이션 기간 동안의 연율화 기하학적 복리 수익률 |
| **MDD** | 최대 낙폭 | 전고점 대비 계좌 가치가 하락한 최대 손실 폭 |
| **Sharpe Ratio** | 샤프 지수 | 총 변동성 1단위당 얻은 무위험 초과 수익률 |
| **Sortino Ratio** | 소티노 지수 | 하방 변동성(Downside Risk)만을 패널티로 부여한 실질 초과 수익 지표 |
| **Ulcer Index (UI)** | 궤양지수 | 낙폭의 깊이(Depth)와 회복까지 걸린 고통스러운 보유 기간(Duration)의 2차 RMS 수치 |
| **UPI (Martin Ratio)** | 궤양성과지수 | 궤양지수 1단위당 창출한 초과 수익률 (장기 투자 심리 안정도 측정) |
| **Calmar Ratio** | 칼마 지수 | 최대 낙폭(MDD) 대비 연평균 복리 수익률(CAGR)의 비율 |
| **Tax & Cost** | 실전 세금/비용 | 미국 해외주식 22% 양도소득세(연 250만 원 공제 반영) 및 편도 거래비용(수수료+슬리피지) 실시간 정산 |

---

## 🖥️ 화면 프리뷰 (UI Highlights)

### 1. 전략 구성 (빌더) 화면
- 2-Way 세그먼트 버튼을 통한 직관적인 전략 전환
- 세 자리 콤마(`100,000,000`) 지원 입력창 및 한글 환산(₩1.00억) 캡션

### 2. 8대 핵심 KPI 카드 & 자산 성장 차트
- 2행 4열로 오와 열이 맞춰진 직관적 KPI 카드
- S&P 500(SPY), 코스피 200(069500.KS), 절대수익 기준선(연 5%)과의 다중 비교 벤치마크 및 MDD 언더워터 차트

### 3. 보고서 하단 상세 내역
- **연도별/월별 수익률 매트릭스 (%)**: 각 연도별 1~12월 수익률 및 YTD 성과표
- **월별 ETF 투자 히스토리**: 시뮬레이션 기간 동안의 월말 보유 ETF 구성 및 비중 변화 (CSV 다운로드 지원)

---

## 🚀 로컬 실행 방법 (Quick Start)

### 1. 저장소 복제 (Clone)
```bash
git clone https://github.com/Rodin-BW/BAS_quant_site.git
cd BAS_quant_site
```

### 2. 가상환경 생성 및 의존성 설치
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. 웹 애플리케이션 실행
```bash
streamlit run app.py
```
브라우저에서 `http://localhost:8501`로 접속하여 즉시 테스트할 수 있습니다.

---

## 🛠️ 기술 스택 (Tech Stack)

- **Frontend / Framework**: Streamlit, Custom HTML/CSS (Pretendard Font & Toss FinTech Theme)
- **Data Engine**: Pandas, NumPy, yfinance (Yahoo Finance Real-time & Historical Data)
- **Visualization**: Plotly Graph Objects (Interactive Multi-subplot charts)
- **Testing & Verification**: Pytest (수학적 퀀트 공식 및 통합 테스트 20건 전수 검증), Playwright (E2E UI 무결성 자동화)

---

## 📄 라이선스 (License)

이 프로젝트는 [MIT License](LICENSE)를 따릅니다.
누구나 자유롭게 수정 및 배포할 수 있습니다.
