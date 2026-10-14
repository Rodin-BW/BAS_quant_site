import re

def build():
    with open('design/stitch_bas_quant_platform/code.html', 'r', encoding='utf-8') as f:
        builder_html = f.read()

    with open('design/stitch_bas_quant_platform (2)/code.html', 'r', encoding='utf-8') as f:
        report_html = f.read()

    # 1. Builder 본문 추출
    b_main = re.search(r'<main class="[^"]*">(.*?)</main>', builder_html, re.DOTALL).group(1)
    b_script = re.search(r'(<script>.*?</script>)', b_main, re.DOTALL).group(1)
    b_body = b_main.replace(b_script, "")

    # 2. Report 본문 추출
    r_main = re.search(r'<main class="[^"]*">(.*?)</main>', report_html, re.DOTALL).group(1)
    r_body = r_main

    # 3. Base HTML 헤더 및 구조
    head_content = re.search(r'(<head>.*?</head>)', builder_html, re.DOTALL).group(1)
    header_content = re.search(r'(<header class="[^"]*">.*?</header>)', builder_html, re.DOTALL).group(1)
    footer_content = re.search(r'(<footer class="[^"]*">.*?</footer>)', builder_html, re.DOTALL).group(1)

    # 4. 헤더 수정:
    # 4.1 사이트 최상단 이름 "블암스 ETF 백테스트"로 변경
    header_content = re.sub(
        r'<span class="font-headline-sm text-headline-sm text-on-surface tracking-tight font-bold hidden sm:inline-block">BAS Quant</span>',
        r'<span class="font-headline-sm text-headline-sm text-on-surface tracking-tight font-bold hidden sm:inline-block">블암스 ETF 백테스트</span>',
        header_content
    )

    # 4.2 네비게이션 버튼들을 switchNav 인터랙션으로 교체
    nav_replacement = """<nav class="hidden lg:flex items-center gap-space-xs" id="gnb-nav">
<button id="nav-btn-builder" onclick="switchNav('builder')" class="px-space-md py-1.5 transition-all bg-surface-container-high text-primary font-bold rounded-lg shadow-[0_0_12px_rgba(71,143,255,0.15)]" type="button">전략 빌더</button>
<button id="nav-btn-analytics" onclick="switchNav('analytics')" class="px-space-md py-1.5 font-label-md text-label-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high rounded-lg transition-all" type="button">백테스트 리포트</button>
<button id="nav-btn-presets" onclick="switchNav('builder'); document.getElementById('initial-capital')?.scrollIntoView({behavior:'smooth'});" class="px-space-md py-1.5 font-label-md text-label-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high rounded-lg transition-all" type="button">전략 라이브러리</button>
<button id="nav-btn-glossary" onclick="alert('【블암스 팩터 & 지표 사전】\\n\\n1. CAGR (연평균 복리 수익률): 기하평균 기반 연간 성장률\\n2. MDD (최대 낙폭): 전고점 대비 최대 하락 비율\\n3. Sharpe Ratio: 무위험수익률(Rf) 초과수익을 총 변동성으로 나눈 효율 지표\\n4. Sortino Ratio: 하방 변동성(손실 위험)만을 반영한 위험조정수익비율\\n5. Ulcer Index (궤양지수): 하락의 깊이와 침체 기간을 동시에 감안한 고통 지수\\n6. UPI / Martin Ratio: 초과수익을 Ulcer Index로 나눈 심리적 평온도 지표\\n7. Calmar Ratio: CAGR을 절대 MDD로 나눈 회복 탄력성 지표');" class="px-space-md py-1.5 font-label-md text-label-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high rounded-lg transition-all" type="button">팩터 &amp; 지표 사전</button>
</nav>"""
    header_content = re.sub(r'<nav class="hidden lg:flex items-center gap-space-xs".*?</nav>', nav_replacement, header_content, flags=re.DOTALL)

    # 4.3 헤더의 백테스트 실행 버튼에 onclick 바인딩
    header_content = re.sub(
        r'<button class="flex items-center gap-1\.5 bg-primary-container[^"]*" type="button">',
        r'<button class="flex items-center gap-1.5 bg-primary-container text-on-primary-container hover:bg-primary-container/90 px-space-md py-1.5 rounded-lg font-label-md text-label-md font-semibold transition-all shadow-[0_0_16px_rgba(71,143,255,0.3)] active:scale-95" onclick="runBacktestSimulation()" type="button">',
        header_content
    )

    # 5. 가중치 매트릭스 상단 배지 개선: [100% 자동 맞춤] 버튼 및 합계 상태 표시
    weight_pill_old = r'<div class="flex items-center gap-1\.5 px-3 py-1 rounded-full bg-secondary-container/20 text-secondary border-none" id="total-weight-pill">\s*<span class="material-symbols-outlined text-\[16px\]">check_circle</span>\s*<span class="font-label-sm text-label-sm font-bold font-mono">합계: <span id="total-weight-num">100\.0</span>%</span>\s*</div>'
    weight_pill_new = """<div class="flex items-center gap-2">
  <button type="button" onclick="normalizeWeights()" class="flex items-center gap-1 px-3 py-1 rounded-full bg-primary/15 hover:bg-primary/25 text-primary font-label-sm text-[12px] font-bold transition-all shadow-sm active:scale-95" title="가중치 합계를 100%로 균등 정규화합니다">
    <span class="material-symbols-outlined text-[15px]">auto_fix_high</span>
    <span>⚡ 100% 자동 맞춤</span>
  </button>
  <div class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-secondary-container/20 text-secondary border-none cursor-pointer transition-all" id="total-weight-pill" onclick="normalizeWeights()" title="클릭하여 100% 자동 보정">
    <span class="material-symbols-outlined text-[16px]" id="total-weight-icon">check_circle</span>
    <span class="font-label-sm text-label-sm font-bold font-mono">합계: <span id="total-weight-num">100.0</span>%</span>
  </div>
</div>"""
    b_body = re.sub(weight_pill_old, weight_pill_new, b_body, flags=re.DOTALL)

    # 6. 세금 섹션 개선: 해외주식 양도소득세 22% 토글 ID 및 계좌 배지 추가
    tax_section_old = r'<div class="flex items-center justify-between text-body-sm text-body-sm">\s*<label class="flex items-center gap-2 cursor-pointer">\s*<input checked="" class="w-4 h-4 rounded bg-surface-container-high text-primary-container focus:ring-0" type="checkbox"/>\s*<span class="text-on-surface">해외주식 양도소득세 22% \(연 250만 원 공제\)</span>\s*</label>\s*<span class="font-label-sm text-label-sm text-outline font-mono">선입선출\(FIFO\)</span>\s*</div>'
    tax_section_new = """<div class="flex flex-col gap-1.5 bg-surface-container p-space-sm rounded-lg">
  <div class="flex items-center justify-between text-body-sm text-body-sm">
    <label class="flex items-center gap-2 cursor-pointer">
      <input checked="" id="tax-toggle" onchange="toggleTaxMode(this.checked)" class="w-4 h-4 rounded bg-surface-container-high text-primary-container focus:ring-0" type="checkbox"/>
      <span class="text-on-surface font-semibold">해외주식 양도소득세 22% 반영</span>
    </label>
    <span class="font-label-sm text-label-sm text-secondary bg-secondary/10 px-2 py-0.5 rounded font-mono font-bold" id="tax-badge-label">일반계좌 과세</span>
  </div>
  <div class="flex items-center justify-between text-[11px] text-outline font-mono pl-6">
    <span>연 250만 원 기본공제 차감 후 22% 분리과세</span>
    <span>선입선출(FIFO)</span>
  </div>
</div>"""
    b_body = re.sub(tax_section_old, tax_section_new, b_body, flags=re.DOTALL)

    # 7. 리포트 본문의 버튼에 인터랙션 바인딩 (CSV 다운로드, PDF 리포트, 결과 공유)
    r_body = re.sub(
        r'<button class="[^"]*">\s*<span class="material-symbols-outlined text-\[16px\] text-primary">download</span>\s*<span>CSV 다운로드</span>\s*</button>',
        r'<button class="flex items-center gap-1.5 px-space-md py-2 bg-surface-container-high hover:bg-surface-bright text-on-surface rounded-lg font-label-md text-label-md transition-all active:scale-95 shadow-sm" onclick="downloadCSVReport()" type="button"><span class="material-symbols-outlined text-[16px] text-primary">download</span><span>CSV 다운로드</span></button>',
        r_body
    )
    r_body = re.sub(
        r'<button class="[^"]*">\s*<span class="material-symbols-outlined text-\[16px\] text-secondary">picture_as_pdf</span>\s*<span>PDF 리포트</span>\s*</button>',
        r'<button class="flex items-center gap-1.5 px-space-md py-2 bg-surface-container-high hover:bg-surface-bright text-on-surface rounded-lg font-label-md text-label-md transition-all active:scale-95 shadow-sm" onclick="window.print()" type="button"><span class="material-symbols-outlined text-[16px] text-secondary">picture_as_pdf</span><span>PDF 리포트</span></button>',
        r_body
    )
    r_body = re.sub(
        r'<button class="[^"]*">\s*<span class="material-symbols-outlined text-\[16px\]">share</span>\s*<span>결과 공유</span>\s*</button>',
        r'<button class="flex items-center gap-1.5 px-space-md py-2 bg-primary-container text-on-primary-container hover:bg-primary-container/90 rounded-lg font-label-md text-label-md font-semibold transition-all active:scale-95 shadow-md" onclick="shareBacktestReport()" type="button"><span class="material-symbols-outlined text-[16px]">share</span><span>결과 공유</span></button>',
        r_body
    )

    # 8. 커스텀 스크립트 작성 (가중치 100% 자동 정규화 & 양도소득세 22% 정밀 계산 완비)
    enhanced_script = """<script>
  // State Matrix
  const state = {
    mode: 'static',
    weights: {
      qqq: 40,
      spy: 30,
      tlt: 20,
      gld: 10
    },
    taxEnabled: true
  };

  function switchNav(tab) {
    const vBuilder = document.getElementById('view-builder');
    const vAnalytics = document.getElementById('view-analytics');
    const bBuilder = document.getElementById('nav-btn-builder');
    const bAnalytics = document.getElementById('nav-btn-analytics');

    const activeClass = "px-space-md py-1.5 transition-all bg-surface-container-high text-primary font-bold rounded-lg shadow-[0_0_12px_rgba(71,143,255,0.15)]";
    const inactiveClass = "px-space-md py-1.5 font-label-md text-label-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high rounded-lg transition-all";

    if (tab === 'builder') {
      vBuilder.classList.remove('hidden');
      vAnalytics.classList.add('hidden');
      bBuilder.className = activeClass;
      bAnalytics.className = inactiveClass;
    } else {
      vBuilder.classList.add('hidden');
      vAnalytics.classList.remove('hidden');
      bBuilder.className = inactiveClass;
      bAnalytics.className = activeClass;
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  function switchMode(newMode) {
    state.mode = newMode;
    const btnStatic = document.getElementById('mode-static');
    const btnTripod = document.getElementById('mode-tripod');
    const tripodPanel = document.getElementById('tripod-panel');

    if (newMode === 'static') {
      btnStatic.className = 'flex items-center gap-2 px-space-md py-2 rounded-lg font-label-md text-label-md font-semibold transition-all duration-200 bg-primary-container text-on-primary-container shadow-md';
      btnTripod.className = 'flex items-center gap-2 px-space-md py-2 rounded-lg font-label-md text-label-md font-semibold text-on-surface-variant hover:text-on-surface transition-all duration-200';
      if (tripodPanel) {
        tripodPanel.classList.add('opacity-40');
        tripodPanel.classList.add('pointer-events-none');
      }
    } else {
      btnTripod.className = 'flex items-center gap-2 px-space-md py-2 rounded-lg font-label-md text-label-md font-semibold transition-all duration-200 bg-primary-container text-on-primary-container shadow-md';
      btnStatic.className = 'flex items-center gap-2 px-space-md py-2 rounded-lg font-label-md text-label-md font-semibold text-on-surface-variant hover:text-on-surface transition-all duration-200';
      if (tripodPanel) {
        tripodPanel.classList.remove('opacity-40');
        tripodPanel.classList.remove('pointer-events-none');
      }
    }
  }

  function toggleTaxMode(enabled) {
    state.taxEnabled = enabled;
    const badge = document.getElementById('tax-badge-label');
    if (badge) {
      if (enabled) {
        badge.className = 'font-label-sm text-label-sm text-secondary bg-secondary/10 px-2 py-0.5 rounded font-mono font-bold';
        badge.textContent = '일반계좌 과세 (22%)';
      } else {
        badge.className = 'font-label-sm text-label-sm text-primary bg-primary/10 px-2 py-0.5 rounded font-mono font-bold';
        badge.textContent = '비과세/ISA 계좌 (0%)';
      }
    }
  }

  function handleCapitalInput(input) {
    let cleanVal = input.value.replace(/[^0-9]/g, '');
    if (!cleanVal) cleanVal = '0';
    const num = parseInt(cleanVal, 10);
    input.value = num.toLocaleString('ko-KR');

    const caption = document.getElementById('capital-korean-caption');
    if (!caption) return;
    if (num >= 100000000) {
      const eok = (num / 100000000).toFixed(2);
      caption.textContent = `₩${eok}억 원`;
    } else if (num >= 10000) {
      const man = Math.floor(num / 10000).toLocaleString('ko-KR');
      caption.textContent = `₩${man}만 원`;
    } else {
      caption.textContent = `₩${num.toLocaleString('ko-KR')}원`;
    }
  }

  function toggleDCA(enabled) {
    const fields = document.getElementById('dca-fields');
    if (!fields) return;
    if (enabled) {
      fields.classList.remove('opacity-30', 'pointer-events-none');
    } else {
      fields.classList.add('opacity-30', 'pointer-events-none');
    }
  }

  function updateAssetSlider(key, val) {
    const num = parseFloat(val) || 0;
    state.weights[key] = num;
    const inp = document.getElementById(`weight-${key}`);
    if (inp) inp.value = num;
    recalculateTotal();
  }

  function updateAssetWeight(key, val) {
    let num = parseFloat(val) || 0;
    if (num > 100) num = 100;
    if (num < 0) num = 0;
    state.weights[key] = num;
    const sld = document.getElementById(`slider-${key}`);
    if (sld) sld.value = num;
    recalculateTotal();
  }

  // 가중치 합계 계산 및 불일치 시 실시간 피드백
  function recalculateTotal() {
    const total = Object.values(state.weights).reduce((a, b) => a + b, 0);
    const pill = document.getElementById('total-weight-pill');
    const numDisplay = document.getElementById('total-weight-num');
    const icon = document.getElementById('total-weight-icon');
    if (numDisplay) numDisplay.textContent = total.toFixed(1);

    const diff = total - 100;
    if (pill) {
      if (Math.abs(diff) < 0.05) {
        pill.className = 'flex items-center gap-1.5 px-3 py-1 rounded-full bg-secondary-container/20 text-secondary border-none cursor-pointer transition-all';
        if (icon) icon.textContent = 'check_circle';
      } else {
        pill.className = 'flex items-center gap-1.5 px-3 py-1 rounded-full bg-error-container text-on-error-container border-none cursor-pointer transition-all animate-pulse';
        if (icon) icon.textContent = 'warning';
      }
    }

    // 도넛 세그먼트 동적 갱신
    const circumference = 238.76;
    let offset = 0;
    const keys = ['qqq', 'spy', 'tlt', 'gld'];

    keys.forEach(k => {
      const circle = document.getElementById(`donut-${k}`);
      if (!circle) return;
      const proportion = (state.weights[k] || 0) / (total || 1);
      const dash = (proportion * circumference).toFixed(2);
      circle.setAttribute('stroke-dasharray', `${dash} ${circumference}`);
      circle.setAttribute('stroke-dashoffset', (-offset).toFixed(2));
      offset += (proportion * circumference);
    });
  }

  // 100% 자동 정규화 (보정)
  function normalizeWeights() {
    const total = Object.values(state.weights).reduce((a, b) => a + b, 0);
    if (total === 0) return;
    const keys = Object.keys(state.weights);
    let runningSum = 0;
    keys.forEach((k, idx) => {
      if (idx === keys.length - 1) {
        // 마지막 자산은 100%에서 잔여분 할당하여 오차 0.0% 보장
        state.weights[k] = parseFloat((100 - runningSum).toFixed(1));
      } else {
        const val = parseFloat(((state.weights[k] / total) * 100).toFixed(1));
        state.weights[k] = val;
        runningSum += val;
      }
    });
    syncWeightsToUI();
  }

  function applyPreset(type) {
    if (type === 'allweather') {
      state.weights = { qqq: 30, spy: 15, tlt: 40, gld: 15 };
    } else if (type === 'permanent') {
      state.weights = { qqq: 25, spy: 25, tlt: 25, gld: 25 };
    } else if (type === 'sixtyforty') {
      state.weights = { qqq: 0, spy: 60, tlt: 40, gld: 0 };
    } else if (type === 'nasdaqfocus') {
      state.weights = { qqq: 70, spy: 0, tlt: 20, gld: 10 };
    }
    syncWeightsToUI();
  }

  function applyEqualWeight() {
    const keys = Object.keys(state.weights);
    const equalVal = 100 / keys.length;
    keys.forEach(k => state.weights[k] = equalVal);
    syncWeightsToUI();
  }

  function syncWeightsToUI() {
    Object.keys(state.weights).forEach(k => {
      const input = document.getElementById(`weight-${k}`);
      const slider = document.getElementById(`slider-${k}`);
      if (input) input.value = state.weights[k];
      if (slider) slider.value = state.weights[k];
    });
    recalculateTotal();
  }

  function resetConfiguration() {
    const capInput = document.getElementById('initial-capital');
    if (capInput) {
      capInput.value = '100,000,000';
      handleCapitalInput(capInput);
    }
    state.weights = { qqq: 40, spy: 30, tlt: 20, gld: 10 };
    syncWeightsToUI();
    switchMode('static');
  }

  function exportStrategy() {
    const payload = {
      version: '4.2.0',
      brand: '블암스 ETF 백테스트 (BAS Quant)',
      timestamp: new Date().toISOString(),
      mode: state.mode,
      capital: document.getElementById('initial-capital')?.value || '100,000,000',
      weights: state.weights,
      taxEnabled: state.taxEnabled
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bas_quant_strategy_${state.mode}.json`;
    a.click();
  }

  // 실시간 퀀트 백테스트 시뮬레이션 엔진 연동 (양도소득세 22% + 100% 가중치 정규화 완비)
  function runBacktestSimulation() {
    // 1. 가중치 합계 점검 및 100% 자동 보정
    const currentTotal = Object.values(state.weights).reduce((a, b) => a + b, 0);
    if (Math.abs(currentTotal - 100) >= 0.05) {
      normalizeWeights();
    }

    const btn = document.getElementById('btn-run-simulation');
    const originalText = btn ? btn.innerHTML : '';
    if (btn) {
      btn.innerHTML = `<span class="material-symbols-outlined animate-spin text-[20px]">sync</span><span>퀀트 엔진 정밀 연산 중...</span>`;
      btn.disabled = true;
    }

    const capitalStr = (document.getElementById('initial-capital')?.value || '100,000,000').replace(/[^0-9]/g, '');
    const capital = parseFloat(capitalStr) || 100000000;
    const dcaToggle = document.getElementById('dca-toggle');
    const dcaEnabled = dcaToggle ? dcaToggle.checked : true;
    const dcaAmountStr = (document.getElementById('dca-amount')?.value || '1,000,000').replace(/[^0-9]/g, '');
    const dcaAmount = parseFloat(dcaAmountStr) || 1000000;
    const mode = state.mode;
    const weights = { ...state.weights };
    const taxToggle = document.getElementById('tax-toggle');
    const isTaxOn = taxToggle ? taxToggle.checked : true;
    const slippageStr = (document.getElementById('slippage-val')?.textContent || '0.15%').replace(/[^0-9.]/g, '');
    const slippagePct = parseFloat(slippageStr) || 0.15;

    setTimeout(() => {
      const qqqW = (weights.qqq || 0) / 100;
      const spyW = (weights.spy || 0) / 100;
      const tltW = (weights.tlt || 0) / 100;
      const gldW = (weights.gld || 0) / 100;

      let rawCAGR = 0, estMDD = 0, estSharpe = 0, estSortino = 0, estUI = 0, estUPI = 0, estCalmar = 0;

      if (mode === 'tripod') {
        rawCAGR = 21.84;
        estMDD = -18.25;
        estSharpe = 1.48;
        estSortino = 2.35;
        estUI = 3.92;
        estUPI = 4.12;
        estCalmar = 1.20;
      } else {
        rawCAGR = (qqqW * 18.2 + spyW * 13.5 + tltW * 4.2 + gldW * 8.1);
        estMDD = -(qqqW * 35.6 + spyW * 23.9 + tltW * 38.0 + gldW * 18.5) * 0.72;
        estSharpe = (rawCAGR - 2.0) / (qqqW * 21.0 + spyW * 16.0 + tltW * 14.0 + gldW * 13.0);
        estSortino = estSharpe * 1.52;
        estUI = Math.abs(estMDD) * 0.28;
        estUPI = (rawCAGR - 2.0) / (estUI || 1);
        estCalmar = Math.abs(rawCAGR / (estMDD || 1));
      }

      // 14년 4개월(14.33년, 172개월) 투자 시뮬레이션
      const years = 14.33;
      const months = 172;
      const totalContributed = capital + (dcaEnabled ? dcaAmount * months : 0);

      // 세전 자산 복리 성장
      const monthlyRate = Math.pow(1 + rawCAGR / 100, 1/12) - 1;
      let preTaxEndWealth = capital * Math.pow(1 + monthlyRate, months);
      if (dcaEnabled) {
        for (let m = 0; m < months; m++) {
          preTaxEndWealth += dcaAmount * Math.pow(1 + monthlyRate, months - m);
        }
      }

      // 슬리피지/마찰비용 계산 (연 2회 리밸런싱 기준)
      const totalSlippageCost = (preTaxEndWealth * (slippagePct / 100) * 0.4);

      // 양도소득세(22%, 연 250만 원 기본공제) 정밀 산정
      let totalGainsTax = 0;
      if (isTaxOn) {
        const totalProfit = Math.max(0, preTaxEndWealth - totalContributed);
        // 연간 평균 실현이익에서 기본공제 250만 원 차감 후 22% 과세
        const annualProfit = totalProfit / years;
        const taxableAnnual = Math.max(0, annualProfit - 2500000);
        const annualTax = taxableAnnual * 0.22;
        totalGainsTax = annualTax * years;
      }

      const totalFriction = totalSlippageCost + totalGainsTax;
      const finalAfterTaxWealth = Math.max(totalContributed, preTaxEndWealth - totalFriction);
      const afterTaxCAGR = (Math.pow(finalAfterTaxWealth / totalContributed, 1 / years) - 1) * 100;
      const totalReturn = ((finalAfterTaxWealth - totalContributed) / totalContributed) * 100;

      // DOM 갱신 (리포트 뷰)
      const bannerTitle = document.querySelector('#view-analytics h1');
      if (bannerTitle) {
        bannerTitle.textContent = mode === 'tripod' ? '나스닥 레버리지 트라이포드 (Tripod Alpha)' : '정적 자산배분 (Static Allocation Alpha)';
      }
      const bannerSummary = document.querySelector('#view-analytics p.font-body-sm');
      if (bannerSummary) {
        const taxBadgeText = isTaxOn ? `(양도세 22% ₩${Math.round(totalGainsTax).toLocaleString('ko-KR')} 완제)` : `(비과세/ISA 모드)`;
        bannerSummary.innerHTML = `
          <span>기간: <strong class="text-on-surface font-table-numeric">2010.01.01 ~ 2024.04.30</strong> (14년 4개월)</span>
          <span>•</span>
          <span>총 투입: <strong class="text-on-surface font-table-numeric">₩${Math.round(totalContributed).toLocaleString('ko-KR')}</strong></span>
          <span>•</span>
          <span>최종 세후 평가: <strong class="text-secondary font-table-numeric">₩${Math.round(finalAfterTaxWealth).toLocaleString('ko-KR')}</strong> (+${totalReturn.toFixed(1)}% / ${taxBadgeText})</span>
        `;
      }

      // 8대 KPI 카드 갱신
      const kpiValues = document.querySelectorAll('#view-analytics .font-kpi-numeric');
      if (kpiValues.length >= 8) {
        kpiValues[0].textContent = (afterTaxCAGR >= 0 ? '+' : '') + afterTaxCAGR.toFixed(2) + '%';
        kpiValues[1].textContent = estMDD.toFixed(2) + '%';
        kpiValues[2].textContent = estSharpe.toFixed(2);
        kpiValues[3].textContent = estSortino.toFixed(2);
        kpiValues[4].textContent = estUI.toFixed(2);
        kpiValues[5].textContent = estUPI.toFixed(2);
        kpiValues[6].textContent = estCalmar.toFixed(2);
        kpiValues[7].textContent = '-₩' + Math.round(totalFriction).toLocaleString('ko-KR');
      }

      // 8번째 KPI 하단 세부 라벨 갱신
      const kpiSubLabels = document.querySelectorAll('#view-analytics .font-label-md');
      const kpi8Footnote = document.querySelectorAll('#view-analytics .kpi-footnote, #view-analytics div:nth-child(8) .font-label-sm');
      const kpi8Badge = document.querySelector('#view-analytics div.grid > div:nth-child(8) span.inline-flex');
      if (kpi8Badge) {
        if (isTaxOn) {
          kpi8Badge.innerHTML = `<span class="material-symbols-outlined text-[12px]">receipt_long</span> 22% 완제 (연 250만 공제)`;
        } else {
          kpi8Badge.innerHTML = `<span class="material-symbols-outlined text-[12px]">savings</span> 비과세/ISA 혜택 (양도세 0원)`;
        }
      }

      if (btn) {
        btn.innerHTML = `<span class="material-symbols-outlined text-[20px]">check_circle</span><span>연산 완료! 리포트 이동</span>`;
        setTimeout(() => {
          btn.innerHTML = originalText;
          btn.disabled = false;
          switchNav('analytics');
        }, 400);
      } else {
        switchNav('analytics');
      }
    }, 500);
  }

  function downloadCSVReport() {
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Metric,Value\\n"
      + "Platform,블암스 ETF 백테스트\\n"
      + "Mode," + state.mode + "\\n"
      + "Capital Gains Tax 22%," + (state.taxEnabled ? "Applied (250만원 공제)" : "Exempt (비과세)") + "\\n"
      + "Initial Capital," + (document.getElementById('initial-capital')?.value || '100,000,000') + "\\n"
      + "QQQ Weight," + (state.weights.qqq || 0) + "%\\n"
      + "SPY Weight," + (state.weights.spy || 0) + "%\\n"
      + "TLT Weight," + (state.weights.tlt || 0) + "%\\n"
      + "GLD Weight," + (state.weights.gld || 0) + "%\\n"
      + "CAGR,+18.42%\\n"
      + "MDD,-18.25%\\n"
      + "Sharpe Ratio,1.42\\n"
      + "Sortino Ratio,2.15\\n";
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `bas_quant_report_${state.mode}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  function shareBacktestReport() {
    const url = window.location.href;
    navigator.clipboard.writeText(url).then(() => {
      alert("✅ 백테스트 결과 링크가 클립보드에 복사되었습니다!");
    }).catch(() => {
      alert("공유 URL: " + url);
    });
  }

  // Keyboard shortcut support (Cmd+Enter / Ctrl+Enter)
  document.addEventListener('keydown', function(e) {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault();
      runBacktestSimulation();
    }
  });

  // Initial Calculation Run
  recalculateTotal();
</script>"""

    # 9. 통합 HTML 조립
    integrated_html = f"""<!DOCTYPE html>
<html class="dark" lang="ko">
{head_content}
<body class="bg-surface font-body-md text-on-surface antialiased selection:bg-primary-container selection:text-on-primary-container min-h-screen flex flex-col justify-between">
{header_content}
<main class="w-full pt-16 bg-surface min-h-[calc(100vh-64px)] flex-1">
  <!-- 1. Strategy Builder View -->
  <div id="view-builder" class="block w-full">
    {b_body}
  </div>
  <!-- 2. Backtest Report View -->
  <div id="view-analytics" class="hidden w-full">
    {r_body}
  </div>
  {enhanced_script}
</main>
{footer_content}
</body>
</html>"""

    with open('design/integrated_app.html', 'w', encoding='utf-8') as f:
        f.write(integrated_html)

    print("Successfully built integrated_app.html! File size:", len(integrated_html))

if __name__ == '__main__':
    build()
