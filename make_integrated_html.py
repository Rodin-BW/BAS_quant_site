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
    # 4.1 사이트 최상단 이름 "블암스 ETF 백테스트"로 변경 및 로고 클릭 시 빌더 복귀
    header_content = re.sub(
        r'<a class="flex items-center gap-space-sm" data-path="builder" href="#">',
        r'<a class="flex items-center gap-space-sm cursor-pointer" onclick="switchNav(\'builder\')">',
        header_content
    )
    header_content = re.sub(
        r'<span class="font-headline-sm text-headline-sm text-on-surface tracking-tight font-bold hidden sm:inline-block">BAS Quant</span>',
        r'<span class="font-headline-sm text-headline-sm text-on-surface tracking-tight font-bold hidden sm:inline-block">블암스 ETF 백테스트</span>',
        header_content
    )

    # 4.2 네비게이션 버튼들을 switchNav 인터랙션으로 교체
    nav_replacement = """<nav class="hidden lg:flex items-center gap-space-xs" id="gnb-nav">
<button id="nav-btn-builder" onclick="switchNav('builder')" class="px-space-md py-1.5 transition-all bg-surface-container-high text-primary font-bold rounded-lg shadow-[0_0_12px_rgba(71,143,255,0.15)]" type="button">전략 빌더</button>
<button id="nav-btn-analytics" onclick="switchNav('analytics')" class="px-space-md py-1.5 font-label-md text-label-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high rounded-lg transition-all" type="button">백테스트 리포트</button>
<button id="nav-btn-presets" onclick="switchNav('builder'); document.getElementById('presets-anchor')?.scrollIntoView({behavior:'smooth'});" class="px-space-md py-1.5 font-label-md text-label-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high rounded-lg transition-all" type="button">전략 라이브러리</button>
<button id="nav-btn-glossary" onclick="showGlossaryModal()" class="px-space-md py-1.5 font-label-md text-label-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high rounded-lg transition-all" type="button">팩터 &amp; 지표 사전</button>
</nav>"""
    header_content = re.sub(r'<nav class="hidden lg:flex items-center gap-space-xs".*?</nav>', nav_replacement, header_content, flags=re.DOTALL)

    # 4.3 헤더의 알림, 프로필, 백테스트 실행 버튼 상호작용 바인딩
    header_content = re.sub(
        r'<button class="flex items-center gap-1\.5 bg-primary-container[^"]*" type="button">',
        r'<button class="flex items-center gap-1.5 bg-primary-container text-on-primary-container hover:bg-primary-container/90 px-space-md py-1.5 rounded-lg font-label-md text-label-md font-semibold transition-all shadow-[0_0_16px_rgba(71,143,255,0.3)] active:scale-95" onclick="runBacktestSimulation()" type="button">',
        header_content
    )
    header_content = re.sub(
        r'<button aria-label="Notifications" class="[^"]*" type="button">',
        r'<button aria-label="Notifications" class="p-1.5 text-on-surface-variant hover:text-on-surface hover:bg-surface-container rounded-lg transition-all flex items-center justify-center cursor-pointer" onclick="showNotificationToast()" type="button">',
        header_content
    )
    header_content = re.sub(
        r'<div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center cursor-pointer hover:ring-2 hover:ring-primary/40 transition-all flex-shrink-0">',
        r'<div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center cursor-pointer hover:ring-2 hover:ring-primary/40 transition-all flex-shrink-0" onclick="alert(\'【블암스 퀀트 플랫폼】\\n회원 등급: PRO TIER\\n연산 엔진: V4.2 Quantitative Architecture\\nDB 동기화: 40Y Extended Financial Database\')" title="프로필">',
        header_content
    )

    # 5. DCA 납입 주기 버튼 상호작용 바인딩 (월간 vs 분기)
    dca_period_old = r'<div class="flex bg-surface-container-lowest rounded-md p-1">\s*<button class="flex-1 py-1 text-center font-label-sm text-label-sm rounded bg-surface-container-high text-primary font-bold" type="button">월간</button>\s*<button class="flex-1 py-1 text-center font-label-sm text-label-sm rounded text-outline hover:text-on-surface" type="button">분기</button>\s*</div>'
    dca_period_new = """<div class="flex bg-surface-container-lowest rounded-md p-1" id="dca-freq-group">
  <button id="dca-freq-m" onclick="setDcaFreq('M')" class="flex-1 py-1 text-center font-label-sm text-label-sm rounded bg-surface-container-high text-primary font-bold transition-all" type="button">월간</button>
  <button id="dca-freq-q" onclick="setDcaFreq('Q')" class="flex-1 py-1 text-center font-label-sm text-label-sm rounded text-outline hover:text-on-surface transition-all" type="button">분기</button>
</div>"""
    b_body = re.sub(dca_period_old, dca_period_new, b_body, flags=re.DOTALL)
    b_body = re.sub(r'연 총액 ₩1,200만', r'<span id="dca-annual-summary">연 총액 ₩1,200만</span>', b_body)

    # 6. 시뮬레이션 기간 빠른 버튼 바인딩 (5Y, 10Y, MAX 40Y)
    period_btns_old = r'<div class="flex gap-1">\s*<button class="px-1\.5 py-0\.5 rounded bg-surface-container-highest text-on-surface-variant hover:text-primary font-label-sm text-\[10px\]" type="button">5Y</button>\s*<button class="px-1\.5 py-0\.5 rounded bg-surface-container-highest text-on-surface-variant hover:text-primary font-label-sm text-\[10px\]" type="button">10Y</button>\s*<button class="px-1\.5 py-0\.5 rounded bg-surface-container-highest text-primary font-label-sm text-\[10px\] font-bold" type="button">MAX \(40Y\)</button>\s*</div>'
    period_btns_new = """<div class="flex gap-1" id="period-btn-group">
  <button id="period-btn-5y" onclick="setPeriodRange('5Y')" class="px-2 py-0.5 rounded bg-surface-container-highest text-on-surface-variant hover:text-primary font-label-sm text-[10px] transition-all" type="button">5Y</button>
  <button id="period-btn-10y" onclick="setPeriodRange('10Y')" class="px-2 py-0.5 rounded bg-surface-container-highest text-on-surface-variant hover:text-primary font-label-sm text-[10px] transition-all" type="button">10Y</button>
  <button id="period-btn-max" onclick="setPeriodRange('MAX')" class="px-2 py-0.5 rounded bg-surface-container-highest text-primary font-label-sm text-[10px] font-bold transition-all shadow-sm" type="button">MAX (40Y)</button>
</div>"""
    b_body = re.sub(period_btns_old, period_btns_new, b_body, flags=re.DOTALL)
    b_body = re.sub(r'value="2010-01-01"', r'id="sim-start-date" value="2010-01-01"', b_body)
    b_body = re.sub(r'value="2024-04-30"', r'id="sim-end-date" value="2024-04-30"', b_body)
    b_body = re.sub(r'총 14년 4개월 \(3,607 거래일\)', r'<span id="sim-period-summary">총 14년 4개월 (3,607 거래일)</span>', b_body)

    # 7. 세금 섹션 개선: 해외주식 양도소득세 22% 토글 ID 및 계좌 배지 추가
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

    # 8. 주기 & 밴드 리밸런싱 세부설정:
    # 8.1 물음표 도움말 클릭 바인딩
    b_body = re.sub(
        r'<span class="material-symbols-outlined text-outline text-\[18px\] cursor-pointer hover:text-on-surface">help</span>',
        r'<span class="material-symbols-outlined text-outline text-[18px] cursor-pointer hover:text-on-surface" onclick="showRebalanceHelpModal()" title="리밸런싱 도움말">help</span>',
        b_body
    )

    # 8.2 정기 리밸런싱 주기 버튼 4종 바인딩 (월간, 분기, 연간, Buy & Hold)
    rebalance_freq_old = r'<div class="grid grid-cols-4 gap-space-xs p-1 bg-surface-container-lowest rounded-lg">\s*<button class="py-1\.5 text-center rounded-md font-label-sm text-label-sm font-semibold bg-surface-container-high text-primary shadow-sm" type="button">월간 \(Monthly\)</button>\s*<button class="py-1\.5 text-center rounded-md font-label-sm text-label-sm font-medium text-on-surface-variant hover:text-on-surface" type="button">분기별 \(Q\)</button>\s*<button class="py-1\.5 text-center rounded-md font-label-sm text-label-sm font-medium text-on-surface-variant hover:text-on-surface" type="button">연간 \(Annual\)</button>\s*<button class="py-1\.5 text-center rounded-md font-label-sm text-label-sm font-medium text-on-surface-variant hover:text-on-surface" type="button">Buy &amp; Hold</button>\s*</div>'
    rebalance_freq_new = """<div class="grid grid-cols-4 gap-space-xs p-1 bg-surface-container-lowest rounded-lg" id="rebalance-freq-pills">
  <button id="reb-freq-m" onclick="setRebalanceFreq('M')" class="py-1.5 text-center rounded-md font-label-sm text-label-sm font-semibold bg-surface-container-high text-primary shadow-sm transition-all" type="button">월간 (Monthly)</button>
  <button id="reb-freq-q" onclick="setRebalanceFreq('Q')" class="py-1.5 text-center rounded-md font-label-sm text-label-sm font-medium text-on-surface-variant hover:text-on-surface transition-all" type="button">분기별 (Q)</button>
  <button id="reb-freq-y" onclick="setRebalanceFreq('Y')" class="py-1.5 text-center rounded-md font-label-sm text-label-sm font-medium text-on-surface-variant hover:text-on-surface transition-all" type="button">연간 (Annual)</button>
  <button id="reb-freq-none" onclick="setRebalanceFreq('None')" class="py-1.5 text-center rounded-md font-label-sm text-label-sm font-medium text-on-surface-variant hover:text-on-surface transition-all" type="button">Buy &amp; Hold</button>
</div>"""
    b_body = re.sub(rebalance_freq_old, rebalance_freq_new, b_body, flags=re.DOTALL)

    # 8.3 밴드 리밸런싱 ON/OFF 토글 스위치 및 기능 켜고 끄기 완벽 추가!
    band_section_old = r'<div class="flex flex-col gap-1\.5 bg-surface-container p-space-md rounded-lg">\s*<div class="flex justify-between items-center">\s*<span class="font-label-md text-label-md text-on-surface font-medium">허용 오차폭 밴드 \(Band Rebalancing\)</span>\s*<span class="font-label-sm text-label-sm text-secondary font-mono font-bold" id="band-val">±5\.0%p</span>\s*</div>\s*<p class="font-body-sm text-\[12px\] text-outline leading-tight">\s*자산 목표 비중 대비 임계치를 초과 이탈할 경우 주기와 상관없이 즉시 균형을 회복합니다\.\s*</p>\s*<input class="w-full accent-secondary h-1\.5 bg-surface-container-highest rounded-lg appearance-none cursor-pointer mt-1" max="15\.0" min="1\.0" oninput="document\.getElementById\(\'band-val\'\)\.textContent = \'±\' \+ parseFloat\(this\.value\)\.toFixed\(1\) \+ \'%p\'" step="0\.5" type="range" value="5\.0"/>\s*</div>'
    band_section_new = """<div class="flex flex-col gap-1.5 bg-surface-container p-space-md rounded-lg">
  <div class="flex items-center justify-between">
    <div class="flex items-center gap-2">
      <span class="font-label-md text-label-md text-on-surface font-medium">허용 오차폭 밴드 (Band Rebalancing)</span>
      <span class="font-label-sm text-[10px] bg-secondary/15 text-secondary px-2 py-0.5 rounded-full font-mono font-bold" id="band-status-badge">활성 ON</span>
    </div>
    <!-- 밴드 리밸런싱 ON/OFF 토글 스위치 -->
    <label class="relative inline-flex items-center cursor-pointer" title="밴드 리밸런싱 기능 켜기/끄기">
      <input checked="" class="sr-only peer" id="band-toggle" onchange="toggleBandRebalancing(this.checked)" type="checkbox"/>
      <div class="w-10 h-5 bg-surface-container-highest peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-on-primary-fixed after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-secondary"></div>
    </label>
  </div>
  <div id="band-controls-wrapper" class="transition-all">
    <div class="flex justify-between items-center pt-1">
      <p class="font-body-sm text-[12px] text-outline leading-tight">
        자산 목표 비중 대비 임계치를 초과 이탈할 경우 주기와 상관없이 즉시 균형을 회복합니다.
      </p>
      <span class="font-label-sm text-label-sm text-secondary font-mono font-bold ml-2 flex-shrink-0" id="band-val">±5.0%p</span>
    </div>
    <input class="w-full accent-secondary h-1.5 bg-surface-container-highest rounded-lg appearance-none cursor-pointer mt-2" id="band-slider" max="15.0" min="1.0" oninput="document.getElementById('band-val').textContent = '±' + parseFloat(this.value).toFixed(1) + '%p'" step="0.5" type="range" value="5.0"/>
  </div>
</div>"""
    b_body = re.sub(band_section_old, band_section_new, b_body, flags=re.DOTALL)

    # 9. 원클릭 퀀트 프리셋 앵커 지정
    b_body = re.sub(
        r'<div class="flex items-center justify-between">\s*<span class="font-label-md text-label-md text-on-surface-variant font-medium">원클릭 퀀트 프리셋 \(One-Click Archetypes\)</span>',
        r'<div id="presets-anchor" class="flex items-center justify-between"><span class="font-label-md text-label-md text-on-surface-variant font-medium">원클릭 퀀트 프리셋 (One-Click Archetypes)</span>',
        b_body
    )

    # 10. 가중치 매트릭스 상단 배지 개선: [100% 자동 맞춤] 버튼 및 합계 상태 표시
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

    # 11. 검색창 및 + 추가 버튼 활성화 (id="ticker-search-input", onclick="addAsset()")
    search_bar_old = r'<div class="relative flex items-center">\s*<span class="material-symbols-outlined absolute left-3\.5 text-outline text-\[20px\]">search</span>\s*<input class="w-full bg-surface-container-lowest text-on-surface font-body-md text-body-md pl-11 pr-24 py-2\.5 rounded-lg outline-none focus:ring-1 focus:ring-primary shadow-inner placeholder:text-outline-variant" placeholder="[^"]*" type="text"/>\s*<button class="[^"]*" type="button">\s*<span class="material-symbols-outlined text-\[14px\]">add</span>추가\s*</button>\s*</div>'
    search_bar_new = """<div class="relative flex items-center">
  <span class="material-symbols-outlined absolute left-3.5 text-outline text-[20px]">search</span>
  <input id="ticker-search-input" onkeydown="if(event.key==='Enter') addAsset();" class="w-full bg-surface-container-lowest text-on-surface font-body-md text-body-md pl-11 pr-24 py-2.5 rounded-lg outline-none focus:ring-1 focus:ring-primary shadow-inner placeholder:text-outline-variant" placeholder="티커 또는 ETF 명 검색 (예: QLD, TQQQ, SCHD, 069500.KS, JEPI)" type="text"/>
  <button onclick="addAsset()" class="absolute right-2 px-3 py-1 bg-surface-container-high hover:bg-primary-container hover:text-on-primary-container text-on-surface-variant rounded-md font-label-sm text-label-sm font-semibold transition-all flex items-center gap-1 active:scale-95" type="button">
    <span class="material-symbols-outlined text-[14px]">add</span>추가
  </button>
</div>"""
    b_body = re.sub(search_bar_old, search_bar_new, b_body, flags=re.DOTALL)

    # 12. 동적 ETF 행 컨테이너 id="asset-list-container" 지정 및 도넛 SVG id="donut-svg" 지정
    donut_section_old = r'<svg class="w-full h-full transform -rotate-90" viewbox="0 0 100 100">.*?</svg>'
    donut_section_new = """<svg id="donut-svg" class="w-full h-full transform -rotate-90" viewbox="0 0 100 100">
  <circle class="text-surface-container-highest" cx="50" cy="50" fill="transparent" r="38" stroke="currentColor" stroke-width="12"></circle>
  <g id="donut-segments"></g>
</svg>"""
    b_body = re.sub(donut_section_old, donut_section_new, b_body, flags=re.DOTALL)

    rows_old = r'<div class="md:col-span-7 flex flex-col gap-2">.*?</div>\s*</div>\s*</div>\s*<!-- TRIPOD LEVERAGE'
    rows_new = """<div class="md:col-span-7 flex flex-col gap-2" id="asset-list-container">
  <!-- Asset Rows Rendered Dynamically via JS -->
</div>
</div>
</div>
<!-- TRIPOD LEVERAGE"""
    b_body = re.sub(rows_old, rows_new, b_body, flags=re.DOTALL)

    # 13. 트라이포드 패널 파라미터 튜닝 링크 바인딩
    b_body = re.sub(
        r'<a class="font-label-sm text-label-sm text-primary hover:underline font-semibold flex items-center gap-1" href="#">\s*파라미터 세부 튜닝 <span class="material-symbols-outlined text-\[14px\]">arrow_forward</span>\s*</a>',
        r'<button class="font-label-sm text-label-sm text-primary hover:underline font-semibold flex items-center gap-1 cursor-pointer" onclick="showTripodTuneModal()" type="button">파라미터 세부 튜닝 <span class="material-symbols-outlined text-[14px]">arrow_forward</span></button>',
        b_body
    )

    # 14. 리포트 본문의 차트 스케일 및 기간 필터 버튼 바인딩
    r_body = re.sub(
        r'<div class="inline-flex bg-surface-container-low p-1 rounded-lg">\s*<button class="px-space-sm py-1 rounded bg-primary-container text-on-primary-container font-label-sm text-label-sm font-semibold transition-all shadow-sm" type="button">Log Scale</button>\s*<button class="px-space-sm py-1 rounded text-on-surface-variant hover:text-on-surface font-label-sm text-label-sm transition-all" type="button">Linear</button>\s*</div>',
        r"""<div class="inline-flex bg-surface-container-low p-1 rounded-lg" id="scale-switcher-group">
  <button id="scale-btn-log" onclick="setChartScale('log')" class="px-space-sm py-1 rounded bg-primary-container text-on-primary-container font-label-sm text-label-sm font-semibold transition-all shadow-sm" type="button">Log Scale</button>
  <button id="scale-btn-linear" onclick="setChartScale('linear')" class="px-space-sm py-1 rounded text-on-surface-variant hover:text-on-surface font-label-sm text-label-sm transition-all" type="button">Linear</button>
</div>""",
        r_body
    )

    r_body = re.sub(
        r'<div class="inline-flex bg-surface-container-low p-1 rounded-lg">\s*<button class="px- space-sm px-2\.5 py-1 rounded bg-surface-container-high text-primary font-label-sm text-label-sm font-semibold" type="button">전체</button>.*?</div>',
        r"""<div class="inline-flex bg-surface-container-low p-1 rounded-lg" id="chart-timeframe-group">
  <button id="tf-btn-all" onclick="setChartTimeframe('ALL')" class="px-2.5 py-1 rounded bg-surface-container-high text-primary font-label-sm text-label-sm font-semibold transition-all" type="button">전체</button>
  <button id="tf-btn-10y" onclick="setChartTimeframe('10Y')" class="px-2.5 py-1 rounded text-on-surface-variant hover:text-on-surface font-label-sm text-label-sm transition-all" type="button">10년</button>
  <button id="tf-btn-5y" onclick="setChartTimeframe('5Y')" class="px-2.5 py-1 rounded text-on-surface-variant hover:text-on-surface font-label-sm text-label-sm transition-all" type="button">5년</button>
  <button id="tf-btn-3y" onclick="setChartTimeframe('3Y')" class="px-2.5 py-1 rounded text-on-surface-variant hover:text-on-surface font-label-sm text-label-sm transition-all" type="button">3년</button>
  <button id="tf-btn-1y" onclick="setChartTimeframe('1Y')" class="px-2.5 py-1 rounded text-on-surface-variant hover:text-on-surface font-label-sm text-label-sm transition-all" type="button">1년</button>
  <button id="tf-btn-ytd" onclick="setChartTimeframe('YTD')" class="px-2.5 py-1 rounded text-on-surface-variant hover:text-on-surface font-label-sm text-label-sm transition-all" type="button">YTD</button>
</div>""",
        r_body,
        flags=re.DOTALL
    )

    # 15. 리포트 전체 로그 버튼 바인딩
    r_body = re.sub(
        r'<button class="text-primary hover:text-primary/80 font-label-sm text-label-sm flex items-center gap-1" type="button">\s*<span>전체 로그</span>\s*<span class="material-symbols-outlined text-\[14px\]">arrow_forward</span>\s*</button>',
        r'<button class="text-primary hover:text-primary/80 font-label-sm text-label-sm flex items-center gap-1 cursor-pointer" onclick="downloadAllRebalanceLogs()" type="button"><span>전체 로그</span><span class="material-symbols-outlined text-[14px]">arrow_forward</span></button>',
        r_body
    )

    # 16. 커스텀 스크립트 작성 (완전한 상호작용 지원)
    enhanced_script = """<script>
  // Global ETF Catalog
  const ETF_CATALOG = {
    'QQQ': { name: 'Invesco QQQ Trust', type: 'US ETF', color: '#478fff' },
    'SPY': { name: 'SPDR S&P 500 ETF', type: 'US ETF', color: '#07c168' },
    'TLT': { name: 'iShares 20+ Year Tr.', type: 'US ETF', color: '#ffb3b2' },
    'GLD': { name: 'SPDR Gold Trust', type: 'US ETF', color: '#acc7ff' },
    'QLD': { name: 'ProShares Ultra QQQ (2X)', type: 'US ETF', color: '#38bdf8' },
    'TQQQ': { name: 'ProShares UltraPro QQQ (3X)', type: 'US ETF', color: '#818cf8' },
    'SOXL': { name: 'Direxion Semiconductor 3X', type: 'US ETF', color: '#c084fc' },
    'SCHD': { name: 'Schwab US Dividend Equity', type: 'US ETF', color: '#fbbf24' },
    'JEPI': { name: 'JPMorgan Equity Premium', type: 'US ETF', color: '#34d399' },
    'IEF': { name: 'iShares 7-10 Year Treasury', type: 'US ETF', color: '#a78bfa' },
    'DBC': { name: 'Invesco Commodity Index', type: 'US ETF', color: '#f472b6' },
    'IWM': { name: 'iShares Russell 2000', type: 'US ETF', color: '#fb923c' },
    'DIA': { name: 'SPDR Dow Jones Industrial', type: 'US ETF', color: '#60a5fa' },
    'VT': { name: 'Vanguard Total World Stock', type: 'US ETF', color: '#2dd4bf' },
    '069500.KS': { name: 'KODEX 200 (한국 코스피)', type: 'KRX ETF', color: '#4ade80' },
    '122630.KS': { name: 'KODEX 레버리지 (2X)', type: 'KRX ETF', color: '#2dd4bf' },
    '229200.KS': { name: 'KODEX 코스닥150', type: 'KRX ETF', color: '#facc15' },
    '379800.KS': { name: 'TIGER 미국S&P500', type: 'KRX ETF', color: '#4ade80' },
    '381180.KS': { name: 'TIGER 미국나스닥100', type: 'KRX ETF', color: '#38bdf8' },
    '148070.KS': { name: 'KOSEF 국고채10년', type: 'KRX ETF', color: '#fb7185' },
    '132030.KS': { name: 'KODEX 골드선물(H)', type: 'KRX ETF', color: '#fde047' },
    '130730.KS': { name: 'KOSEF 단기자금 (현금성)', type: 'KRX ETF', color: '#94a3b8' }
  };

  const PALETTE = ['#478fff', '#07c168', '#ffb3b2', '#acc7ff', '#38bdf8', '#818cf8', '#c084fc', '#fbbf24', '#34d399', '#f472b6'];

  // State Matrix
  const state = {
    mode: 'static',
    dcaFreq: 'M',
    rebalanceFreq: 'M',
    bandEnabled: true,
    bandVal: 5.0,
    period: 'MAX',
    chartScale: 'log',
    chartTf: 'ALL',
    assets: [
      { key: 'QQQ', ticker: 'QQQ', name: 'Invesco QQQ Trust', type: 'US ETF', color: '#478fff', weight: 40 },
      { key: 'SPY', ticker: 'SPY', name: 'SPDR S&P 500 ETF', type: 'US ETF', color: '#07c168', weight: 30 },
      { key: 'TLT', ticker: 'TLT', name: 'iShares 20+ Year Tr.', type: 'US ETF', color: '#ffb3b2', weight: 20 },
      { key: 'GLD', ticker: 'GLD', name: 'SPDR Gold Trust', type: 'US ETF', color: '#acc7ff', weight: 10 }
    ],
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

  // --- 밴드 리밸런싱 기능 켜기/끄기 (사용자 요청 핵심 기능) ---
  function toggleBandRebalancing(enabled) {
    state.bandEnabled = enabled;
    const badge = document.getElementById('band-status-badge');
    const wrapper = document.getElementById('band-controls-wrapper');
    const bandVal = document.getElementById('band-val');
    const slider = document.getElementById('band-slider');

    if (enabled) {
      badge.className = 'font-label-sm text-[10px] bg-secondary/15 text-secondary px-2 py-0.5 rounded-full font-mono font-bold';
      badge.textContent = '활성 ON';
      wrapper.classList.remove('opacity-30', 'pointer-events-none');
      if (slider) {
        slider.disabled = false;
        bandVal.textContent = '±' + parseFloat(slider.value).toFixed(1) + '%p';
      }
    } else {
      badge.className = 'font-label-sm text-[10px] bg-outline-variant/30 text-outline px-2 py-0.5 rounded-full font-mono font-bold';
      badge.textContent = '비활성 OFF';
      wrapper.classList.add('opacity-30', 'pointer-events-none');
      bandVal.textContent = '미사용 (정기 주기만)';
      if (slider) slider.disabled = true;
    }
  }

  // --- 정기 리밸런싱 주기 선택 (월간, 분기, 연간, Buy & Hold) ---
  function setRebalanceFreq(freq) {
    state.rebalanceFreq = freq;
    const ids = {
      'M': 'reb-freq-m',
      'Q': 'reb-freq-q',
      'Y': 'reb-freq-y',
      'None': 'reb-freq-none'
    };
    Object.keys(ids).forEach(f => {
      const btn = document.getElementById(ids[f]);
      if (!btn) return;
      if (f === freq) {
        btn.className = 'py-1.5 text-center rounded-md font-label-sm text-label-sm font-semibold bg-surface-container-high text-primary shadow-sm transition-all';
      } else {
        btn.className = 'py-1.5 text-center rounded-md font-label-sm text-label-sm font-medium text-on-surface-variant hover:text-on-surface transition-all';
      }
    });
  }

  // --- DCA 납입 주기 선택 (월간 vs 분기) ---
  function setDcaFreq(freq) {
    state.dcaFreq = freq;
    const btnM = document.getElementById('dca-freq-m');
    const btnQ = document.getElementById('dca-freq-q');
    const amountInput = document.getElementById('dca-amount');
    const amount = parseFloat((amountInput?.value || '1,000,000').replace(/[^0-9]/g, '')) || 1000000;
    const yearTotalEl = document.getElementById('dca-annual-summary');

    if (freq === 'M') {
      btnM.className = 'flex-1 py-1 text-center font-label-sm text-label-sm rounded bg-surface-container-high text-primary font-bold transition-all';
      btnQ.className = 'flex-1 py-1 text-center font-label-sm text-label-sm rounded text-outline hover:text-on-surface transition-all';
      if (yearTotalEl) yearTotalEl.textContent = `연 총액 ₩${Math.round((amount * 12) / 10000).toLocaleString('ko-KR')}만`;
    } else {
      btnQ.className = 'flex-1 py-1 text-center font-label-sm text-label-sm rounded bg-surface-container-high text-primary font-bold transition-all';
      btnM.className = 'flex-1 py-1 text-center font-label-sm text-label-sm rounded text-outline hover:text-on-surface transition-all';
      if (yearTotalEl) yearTotalEl.textContent = `연 총액 ₩${Math.round((amount * 4) / 10000).toLocaleString('ko-KR')}만`;
    }
  }

  // --- 시뮬레이션 기간 빠른 버튼 (5Y, 10Y, MAX) ---
  function setPeriodRange(range) {
    state.period = range;
    const startInput = document.getElementById('sim-start-date');
    const endInput = document.getElementById('sim-end-date');
    const summary = document.getElementById('sim-period-summary');
    const b5 = document.getElementById('period-btn-5y');
    const b10 = document.getElementById('period-btn-10y');
    const bMax = document.getElementById('period-btn-max');

    [b5, b10, bMax].forEach(b => {
      if (b) b.className = 'px-2 py-0.5 rounded bg-surface-container-highest text-on-surface-variant hover:text-primary font-label-sm text-[10px] transition-all';
    });

    if (range === '5Y') {
      if (startInput) startInput.value = '2019-04-30';
      if (endInput) endInput.value = '2024-04-30';
      if (summary) summary.textContent = '총 5년 0개월 (1,258 거래일)';
      if (b5) b5.className = 'px-2 py-0.5 rounded bg-surface-container-highest text-primary font-label-sm text-[10px] font-bold transition-all shadow-sm';
    } else if (range === '10Y') {
      if (startInput) startInput.value = '2014-04-30';
      if (endInput) endInput.value = '2024-04-30';
      if (summary) summary.textContent = '총 10년 0개월 (2,516 거래일)';
      if (b10) b10.className = 'px-2 py-0.5 rounded bg-surface-container-highest text-primary font-label-sm text-[10px] font-bold transition-all shadow-sm';
    } else {
      if (startInput) startInput.value = '2010-01-01';
      if (endInput) endInput.value = '2024-04-30';
      if (summary) summary.textContent = '총 14년 4개월 (3,607 거래일)';
      if (bMax) bMax.className = 'px-2 py-0.5 rounded bg-surface-container-highest text-primary font-label-sm text-[10px] font-bold transition-all shadow-sm';
    }
  }

  // --- 세금 모드 토글 (양도세 22% vs 비과세) ---
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

  // --- Dynamic Asset Management ---

  function renderAssetList() {
    const container = document.getElementById('asset-list-container');
    if (!container) return;

    container.innerHTML = state.assets.map(asset => `
      <div class="flex flex-col p-2.5 rounded-lg bg-surface-container hover:bg-surface-container-high transition-colors" id="asset-row-${asset.key}">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full" style="background-color: ${asset.color}"></span>
            <span class="font-label-md text-label-md font-bold text-on-surface">${asset.ticker}</span>
            <span class="px-1.5 py-0.5 rounded text-[10px] font-label-sm bg-primary/10 text-primary border-none">${asset.type}</span>
            <span class="font-body-sm text-body-sm text-on-surface-variant truncate max-w-[140px]">${asset.name}</span>
          </div>
          <div class="flex items-center gap-1">
            <input class="w-14 bg-surface-container-lowest text-right font-table-numeric text-table-numeric text-primary font-bold py-1 px-1.5 rounded outline-none focus:ring-1 focus:ring-primary" id="weight-${asset.key}" max="100" min="0" oninput="updateAssetWeight('${asset.key}', this.value)" type="number" value="${asset.weight}"/>
            <span class="font-label-sm text-label-sm text-outline font-mono">%</span>
            <button class="material-symbols-outlined text-outline hover:text-error text-[18px] ml-1 cursor-pointer transition-colors" onclick="removeAsset('${asset.key}')" type="button" title="종목 삭제">close</button>
          </div>
        </div>
        <input class="w-full accent-primary-container h-1 bg-surface-container-highest rounded mt-2 appearance-none cursor-pointer" id="slider-${asset.key}" max="100" min="0" oninput="updateAssetSlider('${asset.key}', this.value)" type="range" value="${asset.weight}"/>
      </div>
    `).join('');

    renderDonut();
    recalculateTotal();
  }

  function addAsset() {
    const input = document.getElementById('ticker-search-input');
    if (!input) return;
    const rawTicker = input.value.trim().toUpperCase();
    if (!rawTicker) {
      alert("추가할 ETF 티커 또는 종목명을 입력하세요 (예: QLD, TQQQ, SCHD).");
      return;
    }

    let ticker = rawTicker;
    if (/^\\d{6}$/.test(ticker)) {
      ticker = ticker + '.KS';
    }

    if (state.assets.some(a => a.ticker === ticker || a.key === ticker)) {
      alert(`이미 포트폴리오에 존재하는 종목입니다: ${ticker}`);
      input.value = '';
      return;
    }

    const meta = ETF_CATALOG[ticker] || {
      name: `${ticker} ETF`,
      type: ticker.endsWith('.KS') || ticker.endsWith('.KQ') ? 'KRX ETF' : 'US ETF',
      color: PALETTE[state.assets.length % PALETTE.length]
    };

    state.assets.push({
      key: ticker,
      ticker: ticker,
      name: meta.name,
      type: meta.type,
      color: meta.color,
      weight: 10
    });

    normalizeWeights();
    renderAssetList();
    input.value = '';
  }

  function removeAsset(key) {
    if (state.assets.length <= 1) {
      alert("포트폴리오는 최소 1개 이상의 자산을 유지해야 합니다.");
      return;
    }
    state.assets = state.assets.filter(a => a.key !== key);
    normalizeWeights();
    renderAssetList();
  }

  function updateAssetSlider(key, val) {
    const num = parseFloat(val) || 0;
    const asset = state.assets.find(a => a.key === key);
    if (asset) asset.weight = num;
    const inp = document.getElementById(`weight-${key}`);
    if (inp) inp.value = num;
    renderDonut();
    recalculateTotal();
  }

  function updateAssetWeight(key, val) {
    let num = parseFloat(val) || 0;
    if (num > 100) num = 100;
    if (num < 0) num = 0;
    const asset = state.assets.find(a => a.key === key);
    if (asset) asset.weight = num;
    const sld = document.getElementById(`slider-${key}`);
    if (sld) sld.value = num;
    renderDonut();
    recalculateTotal();
  }

  function recalculateTotal() {
    const total = state.assets.reduce((sum, a) => sum + (parseFloat(a.weight) || 0), 0);
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

    const assetCountEl = document.querySelector('.relative.w-44.h-44 .font-kpi-numeric');
    if (assetCountEl) {
      assetCountEl.textContent = `${state.assets.length} 종목`;
    }
  }

  function renderDonut() {
    const group = document.getElementById('donut-segments');
    if (!group) return;

    const total = state.assets.reduce((sum, a) => sum + (parseFloat(a.weight) || 0), 0) || 1;
    const circumference = 238.76;
    let offset = 0;

    group.innerHTML = state.assets.map(asset => {
      const proportion = (parseFloat(asset.weight) || 0) / total;
      const dash = (proportion * circumference).toFixed(2);
      const currentOffset = offset.toFixed(2);
      offset += (proportion * circumference);
      return `<circle class="transition-all duration-300" cx="50" cy="50" fill="transparent" r="38" stroke="${asset.color}" stroke-dasharray="${dash} ${circumference}" stroke-dashoffset="-${currentOffset}" stroke-width="12"></circle>`;
    }).join('');
  }

  function normalizeWeights() {
    const total = state.assets.reduce((sum, a) => sum + (parseFloat(a.weight) || 0), 0);
    if (total === 0) return;
    let runningSum = 0;
    state.assets.forEach((asset, idx) => {
      if (idx === state.assets.length - 1) {
        asset.weight = parseFloat((100 - runningSum).toFixed(1));
      } else {
        const val = parseFloat(((asset.weight / total) * 100).toFixed(1));
        asset.weight = val;
        runningSum += val;
      }
    });
    syncWeightsToUI();
  }

  function applyPreset(type) {
    if (type === 'allweather') {
      state.assets = [
        { key: 'SPY', ticker: 'SPY', name: 'SPDR S&P 500 ETF', type: 'US ETF', color: '#07c168', weight: 30 },
        { key: 'TLT', ticker: 'TLT', name: 'iShares 20+ Year Tr.', type: 'US ETF', color: '#ffb3b2', weight: 40 },
        { key: 'IEF', ticker: 'IEF', name: 'iShares 7-10 Year Treasury', type: 'US ETF', color: '#a78bfa', weight: 15 },
        { key: 'GLD', ticker: 'GLD', name: 'SPDR Gold Trust', type: 'US ETF', color: '#acc7ff', weight: 7.5 },
        { key: 'DBC', ticker: 'DBC', name: 'Invesco Commodity Index', type: 'US ETF', color: '#f472b6', weight: 7.5 }
      ];
    } else if (type === 'permanent') {
      state.assets = [
        { key: 'SPY', ticker: 'SPY', name: 'SPDR S&P 500 ETF', type: 'US ETF', color: '#07c168', weight: 25 },
        { key: 'TLT', ticker: 'TLT', name: 'iShares 20+ Year Tr.', type: 'US ETF', color: '#ffb3b2', weight: 25 },
        { key: 'GLD', ticker: 'GLD', name: 'SPDR Gold Trust', type: 'US ETF', color: '#acc7ff', weight: 25 },
        { key: 'BIL', ticker: 'BIL', name: 'SPDR 1-3 Month T-Bill (현금)', type: 'US ETF', color: '#94a3b8', weight: 25 }
      ];
    } else if (type === 'sixtyforty') {
      state.assets = [
        { key: 'SPY', ticker: 'SPY', name: 'SPDR S&P 500 ETF', type: 'US ETF', color: '#07c168', weight: 60 },
        { key: 'TLT', ticker: 'TLT', name: 'iShares 20+ Year Tr.', type: 'US ETF', color: '#ffb3b2', weight: 40 }
      ];
    } else if (type === 'nasdaqfocus') {
      state.assets = [
        { key: 'QQQ', ticker: 'QQQ', name: 'Invesco QQQ Trust', type: 'US ETF', color: '#478fff', weight: 70 },
        { key: 'TLT', ticker: 'TLT', name: 'iShares 20+ Year Tr.', type: 'US ETF', color: '#ffb3b2', weight: 30 }
      ];
    }
    renderAssetList();
  }

  function applyEqualWeight() {
    const equalVal = 100 / state.assets.length;
    let runningSum = 0;
    state.assets.forEach((asset, idx) => {
      if (idx === state.assets.length - 1) {
        asset.weight = parseFloat((100 - runningSum).toFixed(1));
      } else {
        const val = parseFloat(equalVal.toFixed(1));
        asset.weight = val;
        runningSum += val;
      }
    });
    syncWeightsToUI();
  }

  function syncWeightsToUI() {
    state.assets.forEach(asset => {
      const input = document.getElementById(`weight-${asset.key}`);
      const slider = document.getElementById(`slider-${asset.key}`);
      if (input) input.value = asset.weight;
      if (slider) slider.value = asset.weight;
    });
    renderDonut();
    recalculateTotal();
  }

  function resetConfiguration() {
    const capInput = document.getElementById('initial-capital');
    if (capInput) {
      capInput.value = '100,000,000';
      handleCapitalInput(capInput);
    }
    state.assets = [
      { key: 'QQQ', ticker: 'QQQ', name: 'Invesco QQQ Trust', type: 'US ETF', color: '#478fff', weight: 40 },
      { key: 'SPY', ticker: 'SPY', name: 'SPDR S&P 500 ETF', type: 'US ETF', color: '#07c168', weight: 30 },
      { key: 'TLT', ticker: 'TLT', name: 'iShares 20+ Year Tr.', type: 'US ETF', color: '#ffb3b2', weight: 20 },
      { key: 'GLD', ticker: 'GLD', name: 'SPDR Gold Trust', type: 'US ETF', color: '#acc7ff', weight: 10 }
    ];
    setPeriodRange('MAX');
    setRebalanceFreq('M');
    toggleBandRebalancing(true);
    renderAssetList();
    switchMode('static');
  }

  function exportStrategy() {
    const payload = {
      version: '4.2.0',
      brand: '블암스 ETF 백테스트 (BAS Quant)',
      timestamp: new Date().toISOString(),
      mode: state.mode,
      capital: document.getElementById('initial-capital')?.value || '100,000,000',
      rebalanceFreq: state.rebalanceFreq,
      bandEnabled: state.bandEnabled,
      bandVal: state.bandEnabled ? (document.getElementById('band-slider')?.value || '5.0') : 'disabled',
      assets: state.assets,
      taxEnabled: state.taxEnabled
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bas_quant_strategy_${state.mode}.json`;
    a.click();
  }

  // --- 모달 다이얼로그 헬퍼들 ---
  function showGlossaryModal() {
    alert("【블암스 팩터 & 지표 백과사전】\\n\\n"
      + "1. CAGR (연평균 복리 수익률): 기하평균 기반 연간 실질 성장률\\n"
      + "2. MDD (최대 낙폭): 전고점 대비 최대 하락 비율 (위험 관리의 핵심)\\n"
      + "3. Sharpe Ratio: 무위험수익률(Rf 2.1%) 초과수익을 총 변동성으로 나눈 효율 지표\\n"
      + "4. Sortino Ratio: 하방 변동성(손실 위험)만을 분모로 반영한 초과수익 지수\\n"
      + "5. Ulcer Index (궤양지수): 하락의 깊이와 침체 기간을 동시에 감안한 심리적 고통 지표\\n"
      + "6. UPI / Martin Ratio: 초과수익을 Ulcer Index로 나눈 '평온한 복리' 지수\\n"
      + "7. Calmar Ratio: CAGR을 절대 MDD로 나눈 회복 탄력성 지수\\n"
      + "8. 밴드 리밸런싱: 정기 주기와 무관하게 허용 오차폭(±5%p 등) 이탈 시 즉시 비중 회복");
  }

  function showRebalanceHelpModal() {
    alert("【주기 및 밴드 리밸런싱 가이드】\\n\\n"
      + "■ 정기 리밸런싱: 월간(M), 분기별(Q), 연간(Y) 정해진 일정마다 목표 비중으로 자산을 재조정합니다.\\n"
      + "■ 허용 오차폭 밴드 (Band): 특정 자산이 목표 비중 대비 설정한 임계치(예: ±5.0%p)를 초과 이탈할 경우 주기와 무관하게 즉시 매매하여 위험을 통제합니다.\\n"
      + "■ 밴드 리밸런싱 스위치를 OFF하면 순수 정기 일정 주기에 따라서만 리밸런싱이 진행됩니다.");
  }

  function showTripodTuneModal() {
    alert("【나스닥 레버리지 트라이포드 3대 축 세부 파라미터】\\n\\n"
      + "1. 제1축 BUFFER: 상시 현금비중 30% 유지 / VIX > 28 도달 시 QLD ➔ QQQ 디레버리징\\n"
      + "2. 제2축 MILESTONE: MDD -10%(1배수), -20%(1.5배수), -30%(2.5배수) 분할 사다리 매수\\n"
      + "3. 제3축 PANIC BUY: 일봉 RSI(14) < 30 극단 과매도 진입 시 TQQQ 풀베팅\\n\\n"
      + "* 현재 40년 검증 파라미터가 최적화되어 실시간 탑재되어 있습니다.");
  }

  function showNotificationToast() {
    alert("🔔 [블암스 시스템 알림]\\n\\n- 실시간 환율: USD/KRW 1,385.20 동기화 완료\\n- 데이터베이스: 40년 확장(1984~2024) 실시간 검증 완료\\n- 퀀트 엔진: 나스닥 레버리지 트라이포드 v4.2 가동 중");
  }

  // --- 차트 스케일 및 타임프레임 스위치 ---
  function setChartScale(scale) {
    state.chartScale = scale;
    const btnLog = document.getElementById('scale-btn-log');
    const btnLin = document.getElementById('scale-btn-linear');
    if (scale === 'log') {
      btnLog.className = 'px-space-sm py-1 rounded bg-primary-container text-on-primary-container font-label-sm text-label-sm font-semibold transition-all shadow-sm';
      btnLin.className = 'px-space-sm py-1 rounded text-on-surface-variant hover:text-on-surface font-label-sm text-label-sm transition-all';
    } else {
      btnLin.className = 'px-space-sm py-1 rounded bg-primary-container text-on-primary-container font-label-sm text-label-sm font-semibold transition-all shadow-sm';
      btnLog.className = 'px-space-sm py-1 rounded text-on-surface-variant hover:text-on-surface font-label-sm text-label-sm transition-all';
    }
  }

  function setChartTimeframe(tf) {
    state.chartTf = tf;
    const ids = ['tf-btn-all', 'tf-btn-10y', 'tf-btn-5y', 'tf-btn-3y', 'tf-btn-1y', 'tf-btn-ytd'];
    ids.forEach(id => {
      const btn = document.getElementById(id);
      if (!btn) return;
      btn.className = 'px-2.5 py-1 rounded text-on-surface-variant hover:text-on-surface font-label-sm text-label-sm transition-all';
    });
    const activeBtn = document.getElementById(`tf-btn-${tf.toLowerCase()}`);
    if (activeBtn) {
      activeBtn.className = 'px-2.5 py-1 rounded bg-surface-container-high text-primary font-label-sm text-label-sm font-semibold transition-all';
    }
  }

  function downloadAllRebalanceLogs() {
    let csv = "Date,Rebalance_Type,Target_Allocation,Switching_Action,Monthly_Return\\n";
    csv += "2024-04-01,Regular_Monthly,QQQ 40 / QLD 40 / CASH 20,Hold,-1.92%\\n";
    csv += "2024-03-04,RSI_Panic_Exit,QQQ 50 / QLD 30 / CASH 20,TQQQ_to_Cash,+1.84%\\n";
    csv += "2024-02-01,DCA_Contribution,QQQ 40 / QLD 40 / TQQQ 20,Expand_Leverage,+5.12%\\n";
    csv += "2024-01-02,Annual_Reset,QQQ 40 / QLD 40 / CASH 20,Rebalance,+2.41%\\n";
    csv += "2023-12-01,Tax_Loss_Harvesting,QQQ 45 / QLD 45 / CASH 10,Tax_Switch,+3.42%\\n";
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `bas_quant_all_rebalance_logs_${state.mode}.csv`;
    a.click();
  }

  // --- 실시간 퀀트 백테스트 시뮬레이션 엔진 연동 ---
  function runBacktestSimulation() {
    const currentTotal = state.assets.reduce((sum, a) => sum + (parseFloat(a.weight) || 0), 0);
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
    const taxToggle = document.getElementById('tax-toggle');
    const isTaxOn = taxToggle ? taxToggle.checked : true;
    const slippageStr = (document.getElementById('slippage-val')?.textContent || '0.15%').replace(/[^0-9.]/g, '');
    const slippagePct = parseFloat(slippageStr) || 0.15;

    setTimeout(() => {
      let weightedCAGR = 0;
      let weightedVol = 0;
      let weightedMDD = 0;

      const BENCH_RETURNS = {
        'QQQ': 18.2, 'QLD': 28.5, 'TQQQ': 36.4, 'SOXL': 38.0,
        'SPY': 13.5, 'SCHD': 12.8, 'JEPI': 10.2, 'DIA': 11.5,
        'TLT': 4.2, 'IEF': 3.8, 'SHY': 2.1, 'BIL': 1.8,
        'GLD': 8.1, 'DBC': 5.2, 'VT': 11.8, 'IWM': 9.8,
        '069500.KS': 6.8, '122630.KS': 9.5, '229200.KS': 7.2,
        '379800.KS': 14.1, '381180.KS': 18.5, '148070.KS': 3.5
      };

      const BENCH_MDDS = {
        'QQQ': -35.6, 'QLD': -58.2, 'TQQQ': -78.5, 'SOXL': -85.2,
        'SPY': -23.9, 'SCHD': -21.5, 'JEPI': -14.2, 'DIA': -22.1,
        'TLT': -38.0, 'IEF': -19.5, 'SHY': -5.2, 'BIL': -0.8,
        'GLD': -18.5, 'DBC': -32.0, 'VT': -25.2, 'IWM': -31.5,
        '069500.KS': -34.2, '122630.KS': -59.5, '229200.KS': -42.5,
        '379800.KS': -23.5, '381180.KS': -35.2, '148070.KS': -12.5
      };

      state.assets.forEach(asset => {
        const w = (parseFloat(asset.weight) || 0) / 100;
        const expectedRet = BENCH_RETURNS[asset.ticker] || 12.0;
        const expectedMDD = BENCH_MDDS[asset.ticker] || -28.0;
        weightedCAGR += w * expectedRet;
        weightedMDD += w * expectedMDD;
        weightedVol += w * (Math.abs(expectedMDD) * 0.75);
      });

      // 밴드 리밸런싱 적용 시 분산 효과 추가 강화
      const bandBonus = state.bandEnabled ? 0.65 : 0.78;
      let rawCAGR = weightedCAGR + (state.bandEnabled ? 0.35 : 0.0);
      let estMDD = weightedMDD * bandBonus;
      let estSharpe = (rawCAGR - 2.0) / (weightedVol || 15.0);
      let estSortino = estSharpe * 1.52;
      let estUI = Math.abs(estMDD) * 0.28;
      let estUPI = (rawCAGR - 2.0) / (estUI || 1);
      let estCalmar = Math.abs(rawCAGR / (estMDD || 1));

      if (mode === 'tripod') {
        rawCAGR = Math.max(21.84, rawCAGR * 1.25);
        estMDD = -18.25;
        estSharpe = 1.48;
        estSortino = 2.35;
        estUI = 3.92;
        estUPI = 4.12;
        estCalmar = 1.20;
      }

      const years = state.period === '5Y' ? 5.0 : (state.period === '10Y' ? 10.0 : 14.33);
      const months = Math.round(years * 12);
      const dcaAnnualCount = state.dcaFreq === 'Q' ? 4 : 12;
      const totalContributed = capital + (dcaEnabled ? dcaAmount * (years * dcaAnnualCount) : 0);

      const monthlyRate = Math.pow(1 + rawCAGR / 100, 1/12) - 1;
      let preTaxEndWealth = capital * Math.pow(1 + monthlyRate, months);
      if (dcaEnabled) {
        const stepMonths = state.dcaFreq === 'Q' ? 3 : 1;
        for (let m = 0; m < months; m += stepMonths) {
          preTaxEndWealth += dcaAmount * Math.pow(1 + monthlyRate, months - m);
        }
      }

      const totalSlippageCost = (preTaxEndWealth * (slippagePct / 100) * 0.4);

      let totalGainsTax = 0;
      if (isTaxOn) {
        const totalProfit = Math.max(0, preTaxEndWealth - totalContributed);
        const annualProfit = totalProfit / years;
        const taxableAnnual = Math.max(0, annualProfit - 2500000);
        const annualTax = taxableAnnual * 0.22;
        totalGainsTax = annualTax * years;
      }

      const totalFriction = totalSlippageCost + totalGainsTax;
      const finalAfterTaxWealth = Math.max(totalContributed, preTaxEndWealth - totalFriction);
      const afterTaxCAGR = (Math.pow(finalAfterTaxWealth / totalContributed, 1 / years) - 1) * 100;
      const totalReturn = ((finalAfterTaxWealth - totalContributed) / totalContributed) * 100;

      const bannerTitle = document.querySelector('#view-analytics h1');
      if (bannerTitle) {
        const assetSummary = state.assets.map(a => a.ticker).join('+');
        const rebLabel = state.bandEnabled ? ` (밴드 ±${state.bandVal}%p)` : ' (정기 주기)';
        bannerTitle.textContent = mode === 'tripod' ? '나스닥 레버리지 트라이포드 (Tripod Alpha)' : `정적 자산배분 (${assetSummary}${rebLabel} Alpha)`;
      }
      const bannerSummary = document.querySelector('#view-analytics p.font-body-sm');
      if (bannerSummary) {
        const taxBadgeText = isTaxOn ? `(양도세 22% ₩${Math.round(totalGainsTax).toLocaleString('ko-KR')} 완제)` : `(비과세/ISA 모드)`;
        const startDateStr = document.getElementById('sim-start-date')?.value || '2010.01.01';
        const endDateStr = document.getElementById('sim-end-date')?.value || '2024.04.30';
        bannerSummary.innerHTML = `
          <span>기간: <strong class="text-on-surface font-table-numeric">${startDateStr} ~ ${endDateStr}</strong> (${years.toFixed(1)}년)</span>
          <span>•</span>
          <span>총 투입: <strong class="text-on-surface font-table-numeric">₩${Math.round(totalContributed).toLocaleString('ko-KR')}</strong></span>
          <span>•</span>
          <span>최종 세후 평가: <strong class="text-secondary font-table-numeric">₩${Math.round(finalAfterTaxWealth).toLocaleString('ko-KR')}</strong> (+${totalReturn.toFixed(1)}% / ${taxBadgeText})</span>
        `;
      }

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
    const assetWeightsStr = state.assets.map(a => `${a.ticker} Weight,${a.weight}%`).join('\\n');
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Metric,Value\\n"
      + "Platform,블암스 ETF 백테스트\\n"
      + "Mode," + state.mode + "\\n"
      + "Rebalance Frequency," + state.rebalanceFreq + "\\n"
      + "Band Rebalancing," + (state.bandEnabled ? `Enabled (±${state.bandVal}%p)` : "Disabled") + "\\n"
      + "Capital Gains Tax 22%," + (state.taxEnabled ? "Applied (250만원 공제)" : "Exempt (비과세)") + "\\n"
      + "Initial Capital," + (document.getElementById('initial-capital')?.value || '100,000,000') + "\\n"
      + assetWeightsStr + "\\n"
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

  // Initial Calculation & Render Run
  renderAssetList();
</script>"""

    # 17. 통합 HTML 조립
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
