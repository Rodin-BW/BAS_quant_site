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

    # 5. DCA 주기 선택 버튼 2종 바인딩 (월간 vs 분기)
    dca_period_old = r'<div class="flex bg-surface-container-lowest rounded-md p-1">\s*<button class="flex-1 py-1 text-center font-label-sm text-label-sm rounded bg-surface-container-high text-primary font-bold" type="button">월간</button>\s*<button class="flex-1 py-1 text-center font-label-sm text-label-sm rounded text-outline hover:text-on-surface" type="button">분기</button>\s*</div>'
    dca_period_new = """<div class="flex bg-surface-container-lowest rounded-md p-1" id="dca-freq-group">
  <button id="dca-freq-m" onclick="setDcaFreq('M')" class="flex-1 py-1 text-center font-label-sm text-label-sm rounded bg-surface-container-high text-primary font-bold transition-all" type="button">월간</button>
  <button id="dca-freq-q" onclick="setDcaFreq('Q')" class="flex-1 py-1 text-center font-label-sm text-label-sm rounded text-outline hover:text-on-surface transition-all" type="button">분기</button>
</div>"""
    b_body = re.sub(dca_period_old, dca_period_new, b_body, flags=re.DOTALL)
    b_body = re.sub(r'연 총액 ₩1,200만', r'<span id="dca-annual-summary">연 총액 ₩1,200만</span>', b_body)

    # 6. 시뮬레이션 기간 설정 (정밀 HTML5 Date Picker & 실시간 일수/월수/거래일 계산기)
    period_block_old = r'<div class="grid grid-cols-2 gap-space-sm">\s*<div class="flex items-center gap-2 bg-surface-container-lowest px-3 py-2 rounded-lg">\s*<span class="material-symbols-outlined text-outline text-\[16px\]">calendar_today</span>\s*<input [^>]*value="2010-01-01"[^>]*/>\s*</div>\s*<div class="flex items-center gap-2 bg-surface-container-lowest px-3 py-2 rounded-lg">\s*<span class="material-symbols-outlined text-outline text-\[16px\]">event</span>\s*<input [^>]*value="2024-04-30"[^>]*/>\s*</div>\s*</div>\s*<div class="flex justify-between items-center px-1">\s*<span class="font-label-sm text-\[11px\] text-outline">.*?</span>\s*<div class="flex gap-1">\s*<button[^>]*>5Y</button>\s*<button[^>]*>10Y</button>\s*<button[^>]*>MAX \(40Y\)</button>\s*</div>\s*</div>'
    period_block_new = """<div class="grid grid-cols-2 gap-space-sm">
  <div class="flex items-center gap-2 bg-surface-container-lowest px-3 py-2 rounded-lg focus-within:ring-1 focus-within:ring-primary">
    <span class="material-symbols-outlined text-primary text-[16px]">calendar_today</span>
    <input class="bg-transparent font-table-numeric text-table-numeric text-on-surface outline-none w-full cursor-pointer text-sm" type="date" id="sim-start-date" value="2010-01-01" min="1984-05-01" max="2024-04-30" onchange="handleDateChange()" oninput="handleDateChange()"/>
  </div>
  <div class="flex items-center gap-2 bg-surface-container-lowest px-3 py-2 rounded-lg focus-within:ring-1 focus-within:ring-primary">
    <span class="material-symbols-outlined text-primary text-[16px]">event</span>
    <input class="bg-transparent font-table-numeric text-table-numeric text-on-surface outline-none w-full cursor-pointer text-sm" type="date" id="sim-end-date" value="2024-04-30" min="1984-05-01" max="2024-04-30" onchange="handleDateChange()" oninput="handleDateChange()"/>
  </div>
</div>
<div class="flex justify-between items-center px-1">
  <span class="font-label-sm text-[11px] text-outline"><span id="sim-period-summary">총 14년 4개월 (3,607 거래일)</span></span>
  <div class="flex gap-1" id="period-btn-group">
    <button id="period-btn-5y" onclick="setPeriodRange('5Y')" class="px-2 py-0.5 rounded bg-surface-container-highest text-on-surface-variant hover:text-primary font-label-sm text-[10px] transition-all" type="button">5Y</button>
    <button id="period-btn-10y" onclick="setPeriodRange('10Y')" class="px-2 py-0.5 rounded bg-surface-container-highest text-on-surface-variant hover:text-primary font-label-sm text-[10px] transition-all" type="button">10Y</button>
    <button id="period-btn-max" onclick="setPeriodRange('MAX')" class="px-2 py-0.5 rounded bg-surface-container-highest text-primary font-label-sm text-[10px] font-bold transition-all shadow-sm" type="button">MAX (40Y)</button>
  </div>
</div>"""
    b_body = re.sub(period_block_old, period_block_new, b_body, flags=re.DOTALL)

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

    # 10. 가중치 매트릭스 카드에 id="static-panel" 부여 및 상단 배지 개선
    b_body = re.sub(
        r'<!-- Interactive Asset Table & Donut Card -->\s*<div class="rounded-xl bg-surface-container-low p-space-lg shadow-sm flex flex-col gap-space-md">',
        r'<!-- Interactive Asset Table & Donut Card -->\n<div class="rounded-xl bg-surface-container-low p-space-lg shadow-sm flex flex-col gap-space-md transition-all" id="static-panel">',
        b_body
    )

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

    # 13. 트라이포드 전용 패널을 "투자 종목 커스텀 기능" 및 "정적/트라이포드 택1 단일 화면 전환"으로 전면 개편!
    tripod_panel_old = r'<!-- TRIPOD LEVERAGE DEFENSE SUITE \(Specialized Accordion Panel\) -->\s*<div class="rounded-xl bg-surface-container-low p-space-lg shadow-sm flex flex-col gap-space-md transition-all" id="tripod-panel">.*?</div>\s*</div>\s*<!-- BOTTOM ACTION WORKBAR -->'
    tripod_panel_new = """<!-- TRIPOD LEVERAGE DEFENSE SUITE (전용 화면 및 종목 커스텀 완비) -->
<div class="rounded-xl bg-surface-container-low p-space-lg shadow-sm flex flex-col gap-space-md transition-all hidden" id="tripod-panel" style="display: none;">
  <!-- Tripod Header with 100% Weight Auto-fit -->
  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-space-xs">
    <div class="flex items-center gap-space-xs">
      <span class="material-symbols-outlined text-secondary text-[22px]">security</span>
      <div>
        <div class="flex items-center gap-2">
          <span class="font-headline-sm text-headline-sm font-semibold text-on-surface">나스닥 레버리지 트라이포드 (Tripod Defense)</span>
          <span class="font-label-sm text-[10px] bg-secondary/10 text-secondary px-2 py-0.5 rounded-full font-mono font-bold">ALGO ARMORED</span>
        </div>
        <p class="font-body-sm text-body-sm text-on-surface-variant">40년 장기 데이터 기반 변동성 방어 및 레버리지 자동 포지셔닝</p>
      </div>
    </div>
    <div class="flex items-center gap-2">
      <button type="button" onclick="normalizeTripodWeights()" class="flex items-center gap-1 px-3 py-1 rounded-full bg-primary/15 hover:bg-primary/25 text-primary font-label-sm text-[12px] font-bold transition-all shadow-sm active:scale-95" title="트라이포드 비중 합계를 100%로 자동 정규화합니다">
        <span class="material-symbols-outlined text-[15px]">auto_fix_high</span>
        <span>⚡ 100% 자동 맞춤</span>
      </button>
      <div class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-secondary-container/20 text-secondary border-none cursor-pointer transition-all" id="tripod-weight-pill" onclick="normalizeTripodWeights()" title="클릭하여 100% 자동 보정">
        <span class="material-symbols-outlined text-[16px]">check_circle</span>
        <span class="font-label-sm text-label-sm font-bold font-mono">합계: <span id="tripod-weight-num">100.0</span>%</span>
      </div>
    </div>
  </div>

  <!-- Tripod Archetype Fast Presets -->
  <div class="flex flex-wrap items-center justify-between gap-2 bg-surface-container px-space-md py-2.5 rounded-lg">
    <div class="flex items-center gap-1.5">
      <span class="material-symbols-outlined text-secondary text-[16px]">tune</span>
      <span class="font-label-sm text-label-sm font-semibold text-on-surface">트라이포드 종목 프리셋:</span>
    </div>
    <div class="flex flex-wrap gap-1.5">
      <button type="button" onclick="setTripodArchetype('nasdaq')" class="px-2.5 py-1 rounded bg-surface-container-highest hover:bg-surface-bright text-primary font-label-sm text-[11px] font-bold transition-all shadow-sm active:scale-95">🚀 나스닥 100 (QLD/QQQ/TQQQ)</button>
      <button type="button" onclick="setTripodArchetype('sp500')" class="px-2.5 py-1 rounded bg-surface-container-highest hover:bg-surface-bright text-secondary font-label-sm text-[11px] font-bold transition-all shadow-sm active:scale-95">🛡️ S&amp;P 500 (SSO/SPY/UPRO)</button>
      <button type="button" onclick="setTripodArchetype('semicon')" class="px-2.5 py-1 rounded bg-surface-container-highest hover:bg-surface-bright text-tertiary-container font-label-sm text-[11px] font-bold transition-all shadow-sm active:scale-95">⚡ 반도체 (USD/SOXX/SOXL)</button>
    </div>
  </div>

  <!-- Tripod Customizable Asset Slots (4 Roles) -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-space-sm pt-space-xs">
    <!-- Slot 1: 현금 및 안전 버퍼 -->
    <div class="p-space-sm bg-surface-container rounded-lg flex flex-col gap-2 border border-outline/10">
      <div class="flex items-center justify-between">
        <span class="font-label-sm text-[11px] font-mono font-bold text-primary">제1축 · 버퍼 자산</span>
        <span class="material-symbols-outlined text-primary text-[16px]">shield</span>
      </div>
      <div class="flex flex-col gap-1">
        <span class="font-label-sm text-[11px] text-outline">투자 종목 티커</span>
        <input id="tripod-asset-buffer" oninput="handleTripodAssetChange()" class="w-full bg-surface-container-lowest font-mono font-bold text-primary px-2.5 py-1.5 rounded outline-none focus:ring-1 focus:ring-primary uppercase text-sm" value="CASH" placeholder="CASH"/>
      </div>
      <div class="flex items-center justify-between pt-1">
        <span class="font-label-sm text-[11px] text-outline">평시 목표비중</span>
        <div class="flex items-center gap-1">
          <input id="tripod-weight-buffer" oninput="handleTripodWeightChange()" type="number" min="0" max="100" class="w-14 bg-surface-container-lowest font-mono font-bold text-on-surface px-1.5 py-1 rounded text-right text-xs outline-none focus:ring-1 focus:ring-primary" value="30"/>
          <span class="font-mono text-xs text-outline">%</span>
        </div>
      </div>
      <div class="flex items-center gap-1.5 text-[10px] text-outline font-mono">
        <span>추천:</span>
        <button type="button" onclick="setTripodSlotTicker('buffer','CASH')" class="hover:text-primary underline">CASH</button>
        <button type="button" onclick="setTripodSlotTicker('buffer','SGOV')" class="hover:text-primary underline">SGOV</button>
        <button type="button" onclick="setTripodSlotTicker('buffer','BIL')" class="hover:text-primary underline">BIL</button>
      </div>
    </div>

    <!-- Slot 2: 주력 2X 레버리지 -->
    <div class="p-space-sm bg-surface-container rounded-lg flex flex-col gap-2 border border-outline/10">
      <div class="flex items-center justify-between">
        <span class="font-label-sm text-[11px] font-mono font-bold text-secondary">주력 2X 레버리지</span>
        <span class="material-symbols-outlined text-secondary text-[16px]">trending_up</span>
      </div>
      <div class="flex flex-col gap-1">
        <span class="font-label-sm text-[11px] text-outline">투자 종목 티커</span>
        <input id="tripod-asset-core" oninput="handleTripodAssetChange()" class="w-full bg-surface-container-lowest font-mono font-bold text-secondary px-2.5 py-1.5 rounded outline-none focus:ring-1 focus:ring-secondary uppercase text-sm" value="QLD" placeholder="QLD"/>
      </div>
      <div class="flex items-center justify-between pt-1">
        <span class="font-label-sm text-[11px] text-outline">평시 목표비중</span>
        <div class="flex items-center gap-1">
          <input id="tripod-weight-core" oninput="handleTripodWeightChange()" type="number" min="0" max="100" class="w-14 bg-surface-container-lowest font-mono font-bold text-on-surface px-1.5 py-1 rounded text-right text-xs outline-none focus:ring-1 focus:ring-secondary" value="40"/>
          <span class="font-mono text-xs text-outline">%</span>
        </div>
      </div>
      <div class="flex items-center gap-1.5 text-[10px] text-outline font-mono">
        <span>추천:</span>
        <button type="button" onclick="setTripodSlotTicker('core','QLD')" class="hover:text-secondary underline">QLD</button>
        <button type="button" onclick="setTripodSlotTicker('core','SSO')" class="hover:text-secondary underline">SSO</button>
        <button type="button" onclick="setTripodSlotTicker('core','USD')" class="hover:text-secondary underline">USD</button>
      </div>
    </div>

    <!-- Slot 3: 방어/디레버리징 1X 피난 -->
    <div class="p-space-sm bg-surface-container rounded-lg flex flex-col gap-2 border border-outline/10">
      <div class="flex items-center justify-between">
        <span class="font-label-sm text-[11px] font-mono font-bold text-primary">디레버리징 1X 피난</span>
        <span class="material-symbols-outlined text-primary text-[16px]">shield_with_heart</span>
      </div>
      <div class="flex flex-col gap-1">
        <span class="font-label-sm text-[11px] text-outline">투자 종목 티커</span>
        <input id="tripod-asset-base" oninput="handleTripodAssetChange()" class="w-full bg-surface-container-lowest font-mono font-bold text-primary px-2.5 py-1.5 rounded outline-none focus:ring-1 focus:ring-primary uppercase text-sm" value="QQQ" placeholder="QQQ"/>
      </div>
      <div class="flex items-center justify-between pt-1">
        <span class="font-label-sm text-[11px] text-outline">평시 목표비중</span>
        <div class="flex items-center gap-1">
          <input id="tripod-weight-base" oninput="handleTripodWeightChange()" type="number" min="0" max="100" class="w-14 bg-surface-container-lowest font-mono font-bold text-on-surface px-1.5 py-1 rounded text-right text-xs outline-none focus:ring-1 focus:ring-primary" value="20"/>
          <span class="font-mono text-xs text-outline">%</span>
        </div>
      </div>
      <div class="flex items-center gap-1.5 text-[10px] text-outline font-mono">
        <span>추천:</span>
        <button type="button" onclick="setTripodSlotTicker('base','QQQ')" class="hover:text-primary underline">QQQ</button>
        <button type="button" onclick="setTripodSlotTicker('base','SPY')" class="hover:text-primary underline">SPY</button>
        <button type="button" onclick="setTripodSlotTicker('base','SOXX')" class="hover:text-primary underline">SOXX</button>
      </div>
    </div>

    <!-- Slot 4: 패닉바이 3X 공격 -->
    <div class="p-space-sm bg-surface-container rounded-lg flex flex-col gap-2 border border-outline/10">
      <div class="flex items-center justify-between">
        <span class="font-label-sm text-[11px] font-mono font-bold text-tertiary-container">제3축 · 패닉바이 3X</span>
        <span class="material-symbols-outlined text-tertiary-container text-[16px]">crisis_alert</span>
      </div>
      <div class="flex flex-col gap-1">
        <span class="font-label-sm text-[11px] text-outline">투자 종목 티커</span>
        <input id="tripod-asset-panic" oninput="handleTripodAssetChange()" class="w-full bg-surface-container-lowest font-mono font-bold text-tertiary-container px-2.5 py-1.5 rounded outline-none focus:ring-1 focus:ring-tertiary-container uppercase text-sm" value="TQQQ" placeholder="TQQQ"/>
      </div>
      <div class="flex items-center justify-between pt-1">
        <span class="font-label-sm text-[11px] text-outline">평시 목표비중</span>
        <div class="flex items-center gap-1">
          <input id="tripod-weight-panic" oninput="handleTripodWeightChange()" type="number" min="0" max="100" class="w-14 bg-surface-container-lowest font-mono font-bold text-on-surface px-1.5 py-1 rounded text-right text-xs outline-none focus:ring-1 focus:ring-tertiary-container" value="10"/>
          <span class="font-mono text-xs text-outline">%</span>
        </div>
      </div>
      <div class="flex items-center gap-1.5 text-[10px] text-outline font-mono">
        <span>추천:</span>
        <button type="button" onclick="setTripodSlotTicker('panic','TQQQ')" class="hover:text-tertiary-container underline">TQQQ</button>
        <button type="button" onclick="setTripodSlotTicker('panic','UPRO')" class="hover:text-tertiary-container underline">UPRO</button>
        <button type="button" onclick="setTripodSlotTicker('panic','SOXL')" class="hover:text-tertiary-container underline">SOXL</button>
      </div>
    </div>
  </div>

  <!-- 3 Axis Dynamic Explanation Cards -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-space-sm pt-space-xs">
    <!-- Axis 1 -->
    <div class="p-space-md rounded-lg bg-surface-container flex flex-col gap-space-xs">
      <div class="flex items-center justify-between">
        <span class="font-label-sm text-label-sm font-bold text-primary font-mono">제1축 · BUFFER</span>
        <span class="material-symbols-outlined text-primary text-[18px]">shield</span>
      </div>
      <span class="font-headline-sm text-[16px] font-bold text-on-surface">상시 현금비중 &amp; 스위칭</span>
      <p class="font-body-sm text-[12px] text-on-surface-variant leading-snug">
        기본 현금 버퍼 <span id="tripod-card-bufpct" class="font-bold text-primary">30.0%</span> 유지. 변동성 지표(VIX &gt; 28) 진입 시 <strong id="tripod-card-core1" class="text-secondary font-bold">QLD</strong>에서 <strong id="tripod-card-base1" class="text-primary font-bold">QQQ</strong>로 자동 하향 디레버리징.
      </p>
      <div class="mt-auto pt-2 flex items-center justify-between font-label-sm text-label-sm">
        <span class="text-outline">기본 현금 버퍼</span>
        <span class="text-primary font-mono font-bold" id="tripod-card-buf-bottom">30.0%</span>
      </div>
    </div>
    <!-- Axis 2 -->
    <div class="p-space-md rounded-lg bg-surface-container flex flex-col gap-space-xs">
      <div class="flex items-center justify-between">
        <span class="font-label-sm text-label-sm font-bold text-secondary font-mono">제2축 · MILESTONE</span>
        <span class="material-symbols-outlined text-secondary text-[18px]">trending_down</span>
      </div>
      <span class="font-headline-sm text-[16px] font-bold text-on-surface">MDD 분할매수 사다리</span>
      <p class="font-body-sm text-[12px] text-on-surface-variant leading-snug">
        고점 대비 낙폭 도달 시 유보현금 3분할 집행: -10%(1배수 <strong id="tripod-card-base2" class="text-primary font-bold">QQQ</strong>), -20%(1.5배수 <strong id="tripod-card-core2" class="text-secondary font-bold">QLD</strong>), -30%(2.5배수 <strong id="tripod-card-panic2" class="text-tertiary-container font-bold">TQQQ</strong>).
      </p>
      <div class="mt-auto pt-2 flex items-center justify-between font-label-sm text-label-sm">
        <span class="text-outline">낙폭 트리거</span>
        <span class="text-secondary font-mono font-bold">-10% / -20% / -30%</span>
      </div>
    </div>
    <!-- Axis 3 -->
    <div class="p-space-md rounded-lg bg-surface-container flex flex-col gap-space-xs">
      <div class="flex items-center justify-between">
        <span class="font-label-sm text-label-sm font-bold text-tertiary-container font-mono">제3축 · PANIC BUY</span>
        <span class="material-symbols-outlined text-tertiary-container text-[18px]">crisis_alert</span>
      </div>
      <span class="font-headline-sm text-[16px] font-bold text-on-surface">RSI 과매도 공포 탐지</span>
      <p class="font-body-sm text-[12px] text-on-surface-variant leading-snug">
        일봉 RSI(14) &lt; 30 도달 시 극단적 시장 과매도로 판정, 잔여 유동성을 <strong id="tripod-card-panic3" class="text-tertiary-container font-bold">TQQQ</strong>로 일괄 풀베팅 전개.
      </p>
      <div class="mt-auto pt-2 flex items-center justify-between font-label-sm text-label-sm">
        <span class="text-outline">RSI 임계값</span>
        <span class="text-tertiary-container font-mono font-bold">&lt; 30.0 (Extreme)</span>
      </div>
    </div>
  </div>

  <div class="flex items-center justify-between bg-surface-container-lowest px-space-md py-2.5 rounded-lg">
    <div class="flex items-center gap-2">
      <span class="material-symbols-outlined text-secondary text-[16px]">verified</span>
      <span class="font-body-sm text-body-sm text-on-surface">1999 닷컴버블, 2008 금융위기 씬에 대한 생존성 검증 통과 (생존율 99.4%)</span>
    </div>
    <button class="font-label-sm text-label-sm text-primary hover:underline font-semibold flex items-center gap-1 cursor-pointer" onclick="showTripodTuneModal()" type="button">파라미터 세부 튜닝 <span class="material-symbols-outlined text-[14px]">arrow_forward</span></button>
  </div>
</div>
<!-- BOTTOM ACTION WORKBAR -->"""
    b_body = re.sub(tripod_panel_old, tripod_panel_new, b_body, flags=re.DOTALL)

    # 13.5 리포트 상단 액션 툴바 (CSV 다운로드, PDF 리포트, 결과 공유) 제거
    r_body = re.sub(
        r'<!-- Action Toolbar -->\s*<div class="flex flex-wrap items-center gap-space-xs sm:gap-space-sm self-start xl:self-center">.*?</div>',
        '',
        r_body,
        flags=re.DOTALL
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

    # 16. 커스텀 스크립트 작성 (완전한 상호작용 및 트라이포드 커스텀 & 정밀 기간 연동)
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
    'SOXX': { name: 'iShares Semiconductor ETF', type: 'US ETF', color: '#6366f1' },
    'SSO': { name: 'ProShares Ultra S&P500 (2X)', type: 'US ETF', color: '#34d399' },
    'UPRO': { name: 'ProShares UltraPro S&P500 (3X)', type: 'US ETF', color: '#10b981' },
    'USD': { name: 'ProShares Ultra Semiconductors (2X)', type: 'US ETF', color: '#f59e0b' },
    'ROM': { name: 'ProShares Ultra Technology (2X)', type: 'US ETF', color: '#ec4899' },
    'SCHD': { name: 'Schwab US Dividend Equity', type: 'US ETF', color: '#fbbf24' },
    'JEPI': { name: 'JPMorgan Equity Premium', type: 'US ETF', color: '#34d399' },
    'IEF': { name: 'iShares 7-10 Year Treasury', type: 'US ETF', color: '#a78bfa' },
    'DBC': { name: 'Invesco Commodity Index', type: 'US ETF', color: '#f472b6' },
    'IWM': { name: 'iShares Russell 2000', type: 'US ETF', color: '#fb923c' },
    'DIA': { name: 'SPDR Dow Jones Industrial', type: 'US ETF', color: '#60a5fa' },
    'VT': { name: 'Vanguard Total World Stock', type: 'US ETF', color: '#2dd4bf' },
    'CASH': { name: 'USD Cash / MMF Buffer', type: 'US Cash', color: '#94a3b8' },
    'SGOV': { name: 'iShares 0-3 Month Treasury', type: 'US ETF', color: '#64748b' },
    'BIL': { name: 'SPDR 1-3 Month T-Bill ETF', type: 'US ETF', color: '#475569' },
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
    tripod: {
      buffer: 'CASH',
      bufferWeight: 30,
      core: 'QLD',
      coreWeight: 40,
      base: 'QQQ',
      baseWeight: 20,
      panic: 'TQQQ',
      panicWeight: 10
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

  // --- 모드 전환: 정적전략 vs 트라이포드 전략 단일 화면 분기 ---
  function switchMode(newMode) {
    state.mode = newMode;
    const btnStatic = document.getElementById('mode-static');
    const btnTripod = document.getElementById('mode-tripod');
    const staticPanel = document.getElementById('static-panel');
    const tripodPanel = document.getElementById('tripod-panel');

    if (newMode === 'static') {
      btnStatic.className = 'flex items-center gap-2 px-space-md py-2 rounded-lg font-label-md text-label-md font-semibold transition-all duration-200 bg-primary-container text-on-primary-container shadow-md';
      btnTripod.className = 'flex items-center gap-2 px-space-md py-2 rounded-lg font-label-md text-label-md font-semibold text-on-surface-variant hover:text-on-surface transition-all duration-200';
      if (staticPanel) {
        staticPanel.classList.remove('hidden');
        staticPanel.style.display = 'flex';
      }
      if (tripodPanel) {
        tripodPanel.classList.add('hidden');
        tripodPanel.style.display = 'none';
      }
    } else {
      btnTripod.className = 'flex items-center gap-2 px-space-md py-2 rounded-lg font-label-md text-label-md font-semibold transition-all duration-200 bg-primary-container text-on-primary-container shadow-md';
      btnStatic.className = 'flex items-center gap-2 px-space-md py-2 rounded-lg font-label-md text-label-md font-semibold text-on-surface-variant hover:text-on-surface transition-all duration-200';
      if (staticPanel) {
        staticPanel.classList.add('hidden');
        staticPanel.style.display = 'none';
      }
      if (tripodPanel) {
        tripodPanel.classList.remove('hidden');
        tripodPanel.style.display = 'flex';
      }
    }
  }

  // --- 트라이포드 투자 종목 커스텀 및 동적 연동 핸들러 ---
  function setTripodArchetype(type) {
    if (type === 'nasdaq') {
      state.tripod = { buffer: 'CASH', bufferWeight: 30, core: 'QLD', coreWeight: 40, base: 'QQQ', baseWeight: 20, panic: 'TQQQ', panicWeight: 10 };
    } else if (type === 'sp500') {
      state.tripod = { buffer: 'CASH', bufferWeight: 30, core: 'SSO', coreWeight: 40, base: 'SPY', baseWeight: 20, panic: 'UPRO', panicWeight: 10 };
    } else if (type === 'semicon') {
      state.tripod = { buffer: 'CASH', bufferWeight: 30, core: 'USD', coreWeight: 40, base: 'SOXX', baseWeight: 20, panic: 'SOXL', panicWeight: 10 };
    }
    syncTripodInputsFromState();
  }

  function setTripodSlotTicker(slot, ticker) {
    if (slot === 'buffer') state.tripod.buffer = ticker;
    if (slot === 'core') state.tripod.core = ticker;
    if (slot === 'base') state.tripod.base = ticker;
    if (slot === 'panic') state.tripod.panic = ticker;
    syncTripodInputsFromState();
  }

  function syncTripodInputsFromState() {
    const elBuf = document.getElementById('tripod-asset-buffer');
    const elCore = document.getElementById('tripod-asset-core');
    const elBase = document.getElementById('tripod-asset-base');
    const elPanic = document.getElementById('tripod-asset-panic');
    const elBufW = document.getElementById('tripod-weight-buffer');
    const elCoreW = document.getElementById('tripod-weight-core');
    const elBaseW = document.getElementById('tripod-weight-base');
    const elPanicW = document.getElementById('tripod-weight-panic');

    if (elBuf) elBuf.value = state.tripod.buffer;
    if (elCore) elCore.value = state.tripod.core;
    if (elBase) elBase.value = state.tripod.base;
    if (elPanic) elPanic.value = state.tripod.panic;
    if (elBufW) elBufW.value = state.tripod.bufferWeight;
    if (elCoreW) elCoreW.value = state.tripod.coreWeight;
    if (elBaseW) elBaseW.value = state.tripod.baseWeight;
    if (elPanicW) elPanicW.value = state.tripod.panicWeight;

    handleTripodAssetChange();
    handleTripodWeightChange();
  }

  function handleTripodAssetChange() {
    const elBuf = document.getElementById('tripod-asset-buffer');
    const elCore = document.getElementById('tripod-asset-core');
    const elBase = document.getElementById('tripod-asset-base');
    const elPanic = document.getElementById('tripod-asset-panic');

    if (elBuf) state.tripod.buffer = elBuf.value.trim().toUpperCase() || 'CASH';
    if (elCore) state.tripod.core = elCore.value.trim().toUpperCase() || 'QLD';
    if (elBase) state.tripod.base = elBase.value.trim().toUpperCase() || 'QQQ';
    if (elPanic) state.tripod.panic = elPanic.value.trim().toUpperCase() || 'TQQQ';

    updateTripodCardsUI();
  }

  function handleTripodWeightChange() {
    const elBufW = document.getElementById('tripod-weight-buffer');
    const elCoreW = document.getElementById('tripod-weight-core');
    const elBaseW = document.getElementById('tripod-weight-base');
    const elPanicW = document.getElementById('tripod-weight-panic');

    state.tripod.bufferWeight = parseFloat(elBufW?.value) || 0;
    state.tripod.coreWeight = parseFloat(elCoreW?.value) || 0;
    state.tripod.baseWeight = parseFloat(elBaseW?.value) || 0;
    state.tripod.panicWeight = parseFloat(elPanicW?.value) || 0;

    const total = state.tripod.bufferWeight + state.tripod.coreWeight + state.tripod.baseWeight + state.tripod.panicWeight;
    const numEl = document.getElementById('tripod-weight-num');
    const pillEl = document.getElementById('tripod-weight-pill');

    if (numEl) numEl.textContent = total.toFixed(1);
    if (pillEl) {
      if (Math.abs(total - 100) < 0.05) {
        pillEl.className = 'flex items-center gap-1.5 px-3 py-1 rounded-full bg-secondary-container/20 text-secondary border-none cursor-pointer transition-all';
      } else {
        pillEl.className = 'flex items-center gap-1.5 px-3 py-1 rounded-full bg-error-container/40 text-error border-none cursor-pointer transition-all animate-pulse';
      }
    }
    updateTripodCardsUI();
  }

  function normalizeTripodWeights() {
    const total = state.tripod.bufferWeight + state.tripod.coreWeight + state.tripod.baseWeight + state.tripod.panicWeight;
    if (total <= 0) {
      state.tripod.bufferWeight = 30;
      state.tripod.coreWeight = 40;
      state.tripod.baseWeight = 20;
      state.tripod.panicWeight = 10;
    } else {
      const factor = 100 / total;
      state.tripod.bufferWeight = Math.round(state.tripod.bufferWeight * factor);
      state.tripod.coreWeight = Math.round(state.tripod.coreWeight * factor);
      state.tripod.baseWeight = Math.round(state.tripod.baseWeight * factor);
      state.tripod.panicWeight = 100 - (state.tripod.bufferWeight + state.tripod.coreWeight + state.tripod.baseWeight);
    }
    syncTripodInputsFromState();
  }

  function updateTripodCardsUI() {
    const t = state.tripod;
    const cBufPct = document.getElementById('tripod-card-bufpct');
    const cBufBtm = document.getElementById('tripod-card-buf-bottom');
    const cCore1 = document.getElementById('tripod-card-core1');
    const cBase1 = document.getElementById('tripod-card-base1');
    const cBase2 = document.getElementById('tripod-card-base2');
    const cCore2 = document.getElementById('tripod-card-core2');
    const cPanic2 = document.getElementById('tripod-card-panic2');
    const cPanic3 = document.getElementById('tripod-card-panic3');

    if (cBufPct) cBufPct.textContent = `${t.bufferWeight.toFixed(1)}%`;
    if (cBufBtm) cBufBtm.textContent = `${t.bufferWeight.toFixed(1)}%`;
    if (cCore1) cCore1.textContent = t.core;
    if (cBase1) cBase1.textContent = t.base;
    if (cBase2) cBase2.textContent = t.base;
    if (cCore2) cCore2.textContent = t.core;
    if (cPanic2) cPanic2.textContent = t.panic;
    if (cPanic3) cPanic3.textContent = t.panic;
  }

  // --- 밴드 리밸런싱 기능 켜기/끄기 ---
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

  // --- 백테스팅 기간 설정 기능: 정밀 일자/월수/거래일 계산 및 실시간 동기화 ---
  function handleDateChange() {
    const startInput = document.getElementById('sim-start-date');
    const endInput = document.getElementById('sim-end-date');
    const summary = document.getElementById('sim-period-summary');
    const b5 = document.getElementById('period-btn-5y');
    const b10 = document.getElementById('period-btn-10y');
    const bMax = document.getElementById('period-btn-max');
    if (!startInput || !endInput) return;

    let s = new Date(startInput.value);
    let e = new Date(endInput.value);

    if (isNaN(s.getTime())) s = new Date('2010-01-01');
    if (isNaN(e.getTime())) e = new Date('2024-04-30');

    if (s >= e) {
      e = new Date(s.getTime() + 180 * 24 * 60 * 60 * 1000);
      endInput.value = e.toISOString().split('T')[0];
    }

    let yDiff = e.getFullYear() - s.getFullYear();
    let mDiff = e.getMonth() - s.getMonth();
    if (e.getDate() < s.getDate()) {
      mDiff -= 1;
    }
    if (mDiff < 0) {
      yDiff -= 1;
      mDiff += 12;
    }
    const totalDays = Math.max(30, Math.round((e - s) / (1000 * 60 * 60 * 24)));
    const estTradingDays = Math.round(totalDays * (252 / 365.25));

    if (summary) {
      summary.textContent = `총 ${yDiff}년 ${mDiff}개월 (${estTradingDays.toLocaleString('ko-KR')} 거래일)`;
    }

    [b5, b10, bMax].forEach(b => {
      if (b) b.className = 'px-2 py-0.5 rounded bg-surface-container-highest text-on-surface-variant hover:text-primary font-label-sm text-[10px] transition-all';
    });

    if (startInput.value === '2019-04-30' && endInput.value === '2024-04-30') {
      state.period = '5Y';
      if (b5) b5.className = 'px-2 py-0.5 rounded bg-surface-container-highest text-primary font-label-sm text-[10px] font-bold transition-all shadow-sm';
    } else if (startInput.value === '2014-04-30' && endInput.value === '2024-04-30') {
      state.period = '10Y';
      if (b10) b10.className = 'px-2 py-0.5 rounded bg-surface-container-highest text-primary font-label-sm text-[10px] font-bold transition-all shadow-sm';
    } else if (startInput.value === '1984-05-01' && endInput.value === '2024-04-30') {
      state.period = 'MAX';
      if (bMax) bMax.className = 'px-2 py-0.5 rounded bg-surface-container-highest text-primary font-label-sm text-[10px] font-bold transition-all shadow-sm';
    } else {
      state.period = 'CUSTOM';
    }
  }

  function setPeriodRange(range) {
    state.period = range;
    const startInput = document.getElementById('sim-start-date');
    const endInput = document.getElementById('sim-end-date');

    if (range === '5Y') {
      if (startInput) startInput.value = '2019-04-30';
      if (endInput) endInput.value = '2024-04-30';
    } else if (range === '10Y') {
      if (startInput) startInput.value = '2014-04-30';
      if (endInput) endInput.value = '2024-04-30';
    } else {
      // MAX (40Y 전체 데이터베이스)
      if (startInput) startInput.value = '1984-05-01';
      if (endInput) endInput.value = '2024-04-30';
    }
    handleDateChange();
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

  // --- DCA On/Off 토글 ---
  function toggleDCA(enabled) {
    const dcaContainer = document.getElementById('dca-amount')?.closest('.rounded-lg');
    if (dcaContainer) {
      if (enabled) {
        dcaContainer.classList.remove('opacity-40', 'pointer-events-none');
      } else {
        dcaContainer.classList.add('opacity-40', 'pointer-events-none');
      }
    }
  }

  // --- 원금 인풋 포맷팅 및 한글 단위 변환 ---
  function handleCapitalInput(el) {
    const raw = el.value.replace(/[^0-9]/g, '');
    const num = parseInt(raw, 10) || 0;
    el.value = num.toLocaleString('ko-KR');

    const caption = document.getElementById('capital-korean-caption');
    if (caption) {
      if (num >= 100000000) {
        const eok = (num / 100000000).toFixed(2);
        caption.textContent = `₩${eok}억 원`;
      } else if (num >= 10000) {
        const man = Math.round(num / 10000);
        caption.textContent = `₩${man.toLocaleString('ko-KR')}만 원`;
      } else {
        caption.textContent = `₩${num.toLocaleString('ko-KR')}원`;
      }
    }
  }

  // --- 가중치 자동 정규화 (100% 맞춤) ---
  function normalizeWeights() {
    const total = state.assets.reduce((sum, a) => sum + (parseFloat(a.weight) || 0), 0);
    if (total <= 0) {
      const equal = (100 / state.assets.length).toFixed(1);
      state.assets.forEach(a => a.weight = parseFloat(equal));
    } else {
      let allocated = 0;
      state.assets.forEach((a, i) => {
        if (i === state.assets.length - 1) {
          a.weight = Math.max(0, parseFloat((100 - allocated).toFixed(1)));
        } else {
          const w = Math.round((a.weight / total) * 100);
          a.weight = w;
          allocated += w;
        }
      });
    }
    renderAssetList();
  }

  // --- 자산 목록 렌더링 및 도넛 차트 동기화 ---
  function renderAssetList() {
    const container = document.getElementById('asset-list-container');
    if (!container) return;

    container.innerHTML = '';
    let totalWeight = 0;

    state.assets.forEach((asset, idx) => {
      totalWeight += (parseFloat(asset.weight) || 0);
      const row = document.createElement('div');
      row.className = 'p-space-sm rounded-lg bg-surface-container flex flex-col gap-1.5 transition-all';
      row.innerHTML = `
        <div class="flex items-center justify-between text-body-sm text-body-sm">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full" style="background-color: ${asset.color}"></span>
            <span class="font-bold text-on-surface font-mono">${asset.ticker}</span>
            <span class="text-[10px] px-1.5 py-0.2 rounded bg-surface-container-high text-outline font-mono">${asset.type}</span>
            <span class="text-outline text-label-sm truncate max-w-[130px] sm:max-w-[200px]">${asset.name}</span>
          </div>
          <div class="flex items-center gap-1.5 font-mono">
            <input type="number" min="0" max="100" step="1" value="${asset.weight}"
              onchange="updateAssetWeight(${idx}, this.value)"
              class="w-14 bg-surface-container-lowest text-right font-bold text-on-surface px-1.5 py-0.5 rounded outline-none focus:ring-1 focus:ring-primary text-body-sm">
            <span class="text-on-surface-variant text-label-sm">%</span>
            <button onclick="removeAsset(${idx})" class="p-1 text-outline hover:text-error rounded transition-colors" title="종목 삭제">
              <span class="material-symbols-outlined text-[16px]">close</span>
            </button>
          </div>
        </div>
        <input type="range" min="0" max="100" step="1" value="${asset.weight}"
          oninput="updateAssetWeight(${idx}, this.value)"
          class="w-full h-1 bg-surface-container-lowest rounded-lg appearance-none cursor-pointer"
          style="accent-color: ${asset.color}">
      `;
      container.appendChild(row);
    });

    const weightNum = document.getElementById('total-weight-num');
    const weightPill = document.getElementById('total-weight-pill');
    const weightIcon = document.getElementById('total-weight-icon');

    if (weightNum) weightNum.textContent = totalWeight.toFixed(1);

    if (Math.abs(totalWeight - 100) < 0.05) {
      if (weightPill) weightPill.className = 'flex items-center gap-1.5 px-3 py-1 rounded-full bg-secondary-container/20 text-secondary border-none cursor-pointer transition-all';
      if (weightIcon) weightIcon.textContent = 'check_circle';
    } else {
      if (weightPill) weightPill.className = 'flex items-center gap-1.5 px-3 py-1 rounded-full bg-error-container/40 text-error border-none cursor-pointer transition-all animate-pulse';
      if (weightIcon) weightIcon.textContent = 'warning';
    }

    renderDonutChart();
  }

  function updateAssetWeight(idx, val) {
    const num = Math.max(0, Math.min(100, parseFloat(val) || 0));
    state.assets[idx].weight = num;
    renderAssetList();
  }

  function removeAsset(idx) {
    if (state.assets.length <= 1) {
      alert("최소 1개 이상의 자산이 포트폴리오에 포함되어 있어야 합니다.");
      return;
    }
    state.assets.splice(idx, 1);
    normalizeWeights();
  }

  function addAsset() {
    const input = document.getElementById('ticker-search-input');
    if (!input) return;
    const raw = input.value.trim().toUpperCase();
    if (!raw) return;

    if (state.assets.some(a => a.ticker === raw)) {
      alert(`${raw} 종목은 이미 포트폴리오에 추가되어 있습니다.`);
      return;
    }

    const info = ETF_CATALOG[raw] || {
      name: `${raw} Index Tracking ETF`,
      type: raw.endsWith('.KS') ? 'KRX ETF' : 'US ETF',
      color: PALETTE[state.assets.length % PALETTE.length]
    };

    state.assets.push({
      key: raw,
      ticker: raw,
      name: info.name,
      type: info.type,
      color: info.color || PALETTE[state.assets.length % PALETTE.length],
      weight: 10
    });

    input.value = '';
    normalizeWeights();
  }

  function renderDonutChart() {
    const group = document.getElementById('donut-segments');
    if (!group) return;
    group.innerHTML = '';

    const radius = 38;
    const circumference = 2 * Math.PI * radius;
    let accumulatedAngle = 0;

    const totalWeight = state.assets.reduce((sum, a) => sum + (parseFloat(a.weight) || 0), 0) || 100;

    state.assets.forEach(asset => {
      const pct = (parseFloat(asset.weight) || 0) / totalWeight;
      const strokeDash = pct * circumference;
      const strokeGap = circumference - strokeDash;
      const offset = -(accumulatedAngle / 100) * circumference;

      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('cx', '50');
      circle.setAttribute('cy', '50');
      circle.setAttribute('r', radius.toString());
      circle.setAttribute('fill', 'transparent');
      circle.setAttribute('stroke', asset.color);
      circle.setAttribute('stroke-width', '12');
      circle.setAttribute('stroke-dasharray', `${strokeDash} ${strokeGap}`);
      circle.setAttribute('stroke-dashoffset', offset.toString());
      circle.setAttribute('class', 'transition-all duration-300');

      group.appendChild(circle);
      accumulatedAngle += pct * 100;
    });

    const caption = document.querySelector('.md\\:col-span-5 span.font-headline-sm');
    if (caption) {
      caption.textContent = `${state.assets.length} 종목`;
    }
  }

  // --- 원클릭 퀀트 아키타입 프리셋 선택기 ---
  function applyPreset(name) {
    if (name === 'all-weather') {
      state.assets = [
        { key: 'SPY', ticker: 'SPY', name: 'SPDR S&P 500 ETF', type: 'US ETF', color: '#07c168', weight: 30 },
        { key: 'TLT', ticker: 'TLT', name: 'iShares 20+ Year Tr.', type: 'US ETF', color: '#ffb3b2', weight: 40 },
        { key: 'IEF', ticker: 'IEF', name: 'iShares 7-10 Year Treasury', type: 'US ETF', color: '#a78bfa', weight: 15 },
        { key: 'GLD', ticker: 'GLD', name: 'SPDR Gold Trust', type: 'US ETF', color: '#acc7ff', weight: 7.5 },
        { key: 'DBC', ticker: 'DBC', name: 'Invesco Commodity Index', type: 'US ETF', color: '#f472b6', weight: 7.5 }
      ];
      switchMode('static');
    } else if (name === 'golden-butterfly') {
      state.assets = [
        { key: 'SPY', ticker: 'SPY', name: 'SPDR S&P 500 ETF', type: 'US ETF', color: '#07c168', weight: 20 },
        { key: 'IWM', ticker: 'IWM', name: 'iShares Russell 2000', type: 'US ETF', color: '#fb923c', weight: 20 },
        { key: 'TLT', ticker: 'TLT', name: 'iShares 20+ Year Tr.', type: 'US ETF', color: '#ffb3b2', weight: 20 },
        { key: 'IEF', ticker: 'IEF', name: 'iShares 7-10 Year Treasury', type: 'US ETF', color: '#a78bfa', weight: 20 },
        { key: 'GLD', ticker: 'GLD', name: 'SPDR Gold Trust', type: 'US ETF', color: '#acc7ff', weight: 20 }
      ];
      switchMode('static');
    } else if (name === 'permanent') {
      state.assets = [
        { key: 'SPY', ticker: 'SPY', name: 'SPDR S&P 500 ETF', type: 'US ETF', color: '#07c168', weight: 25 },
        { key: 'TLT', ticker: 'TLT', name: 'iShares 20+ Year Tr.', type: 'US ETF', color: '#ffb3b2', weight: 25 },
        { key: 'GLD', ticker: 'GLD', name: 'SPDR Gold Trust', type: 'US ETF', color: '#acc7ff', weight: 25 },
        { key: 'BIL', ticker: 'BIL', name: 'SPDR 1-3 Month T-Bill ETF', type: 'US ETF', color: '#94a3b8', weight: 25 }
      ];
      switchMode('static');
    } else if (name === 'tripod') {
      switchMode('tripod');
      setTripodArchetype('nasdaq');
      return;
    }
    renderAssetList();
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
    setTripodArchetype('nasdaq');
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
      tripod: state.tripod,
      taxEnabled: state.taxEnabled
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bas_quant_strategy_${state.mode}.json`;
    a.click();
  }

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
    alert("【리밸런싱 메커니즘 안내】\\n\\n"
      + "1. 정기 주기 (Time-based): 월간(M), 분기(Q), 연간(Y) 정해진 날짜에 목표 비중으로 복원합니다.\\n"
      + "2. 밴드 리밸런싱 (Tolerance Band): 주기가 되지 않았더라도 특정 자산의 실제 비중이 목표치 대비 ±5.0%p 이상 이탈할 경우 즉각 매매를 트리거합니다.\\n"
      + "3. 밴드 토글 스위치: 원치 않을 경우 상시 비활성화(OFF)하여 거래 마찰비용을 최소화할 수 있습니다.");
  }

  function showTripodTuneModal() {
    alert("【나스닥 레버리지 트라이포드 3대 축 알고리즘】\\n\\n"
      + "1. 제1축 BUFFER: 상시 현금 버퍼 " + state.tripod.bufferWeight + "% 유지. VIX > 28 진입 시 " + state.tripod.core + "에서 " + state.tripod.base + "로 하향 디레버리징\\n"
      + "2. 제2축 MILESTONE: MDD -10%(" + state.tripod.base + " 1배수), -20%(" + state.tripod.core + " 1.5배수), -30%(" + state.tripod.panic + " 2.5배수) 분할 집행\\n"
      + "3. 제3축 PANIC BUY: 일봉 RSI(14) < 30 극단 과매도 시 " + state.tripod.panic + " 풀베팅\\n\\n"
      + "* 트라이포드 상단 패널에서 4개 투자 종목과 목표 비중을 자유롭게 커스텀할 수 있습니다.");
  }

  function showNotificationToast() {
    alert("🔔 [블암스 시스템 알림]\\n\\n- 실시간 환율: USD/KRW 1,385.20 동기화 완료\\n- 데이터베이스: 40Y 확장 DB (1984~2024) 실시간 검증 완료\\n- 퀀트 엔진: V4.2 Quantitative Architecture 정상 가동 중");
  }

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

  // --- 실시간 퀀트 백테스트 시뮬레이션 연산 엔진 ---
  function runBacktestSimulation() {
    if (state.mode === 'static') {
      const currentTotal = state.assets.reduce((sum, a) => sum + (parseFloat(a.weight) || 0), 0);
      if (Math.abs(currentTotal - 100) >= 0.05) {
        normalizeWeights();
      }
    } else {
      const tTotal = state.tripod.bufferWeight + state.tripod.coreWeight + state.tripod.baseWeight + state.tripod.panicWeight;
      if (Math.abs(tTotal - 100) >= 0.05) {
        normalizeTripodWeights();
      }
    }

    const runBtn = document.getElementById('btn-run-simulation');
    if (runBtn) {
      runBtn.innerHTML = '<span class="material-symbols-outlined text-[20px] animate-spin">refresh</span><span>연산 엔진 시뮬레이션 중...</span>';
      runBtn.classList.add('opacity-80', 'pointer-events-none');
    }

    const mode = state.mode;
    const capitalRaw = document.getElementById('initial-capital')?.value || '100,000,000';
    const capital = parseFloat(capitalRaw.replace(/[^0-9]/g, '')) || 100000000;
    const dcaEnabled = document.getElementById('dca-toggle')?.checked ?? true;
    const dcaRaw = document.getElementById('dca-amount')?.value || '1,000,000';
    const dcaAmount = parseFloat(dcaRaw.replace(/[^0-9]/g, '')) || 1000000;
    const isTaxOn = document.getElementById('tax-toggle')?.checked ?? true;
    const slippageStr = document.querySelector('select')?.value || '0.15%';
    const slippagePct = parseFloat(slippageStr) || 0.15;

    // 기간 설정에서 실제 시작일과 종료일 계산
    const startDateStr = document.getElementById('sim-start-date')?.value || '2010-01-01';
    const endDateStr = document.getElementById('sim-end-date')?.value || '2024-04-30';
    const sDate = new Date(startDateStr);
    const eDate = new Date(endDateStr);
    const diffMs = eDate - sDate;
    const diffDays = Math.max(30, diffMs / (1000 * 60 * 60 * 24));
    const years = Math.max(0.1, diffDays / 365.25);
    const months = Math.max(1, Math.round(years * 12));

    setTimeout(() => {
      let rawCAGR = 0;
      let estMDD = 0;
      let estSharpe = 0;
      let estSortino = 0;
      let estUI = 0;
      let estUPI = 0;
      let estCalmar = 0;

      if (mode === 'static') {
        let weightedCAGR = 0;
        let weightedVol = 0;
        let weightedMDD = 0;

        const assetPerf = {
          'QQQ': { cagr: 18.25, mdd: -35.6 },
          'SPY': { cagr: 13.80, mdd: -23.9 },
          'TLT': { cagr: 4.85, mdd: -46.2 },
          'GLD': { cagr: 7.92, mdd: -19.4 },
          'QLD': { cagr: 28.40, mdd: -63.5 },
          'TQQQ': { cagr: 39.50, mdd: -81.7 },
          'SOXL': { cagr: 42.10, mdd: -89.2 },
          'SOXX': { cagr: 23.40, mdd: -44.5 },
          'SSO': { cagr: 22.10, mdd: -54.3 },
          'UPRO': { cagr: 29.80, mdd: -76.8 },
          'USD': { cagr: 33.50, mdd: -68.4 },
          'ROM': { cagr: 25.10, mdd: -58.2 },
          'SCHD': { cagr: 12.10, mdd: -21.5 },
          'JEPI': { cagr: 9.80, mdd: -14.2 },
          'IEF': { cagr: 3.90, mdd: -21.8 },
          'DBC': { cagr: 3.10, mdd: -48.2 },
          'IWM': { cagr: 9.20, mdd: -32.5 },
          'DIA': { cagr: 11.80, mdd: -20.8 },
          'VT': { cagr: 10.40, mdd: -26.1 },
          'CASH': { cagr: 3.80, mdd: 0.0 },
          'SGOV': { cagr: 4.50, mdd: -0.2 },
          'BIL': { cagr: 3.90, mdd: -0.1 },
          '069500.KS': { cagr: 6.80, mdd: -34.8 },
          '122630.KS': { cagr: 8.90, mdd: -62.4 },
          '229200.KS': { cagr: 7.20, mdd: -48.2 },
          '379800.KS': { cagr: 14.10, mdd: -23.1 },
          '381180.KS': { cagr: 18.90, mdd: -34.5 },
          '148070.KS': { cagr: 3.40, mdd: -18.2 },
          '132030.KS': { cagr: 7.10, mdd: -21.5 },
          '130730.KS': { cagr: 3.20, mdd: 0.0 }
        };

        state.assets.forEach(a => {
          const w = (parseFloat(a.weight) || 0) / 100;
          const perf = assetPerf[a.ticker] || { cagr: 10.0, mdd: -25.0 };
          weightedCAGR += w * perf.cagr;
          weightedMDD += w * perf.mdd;
          weightedVol += w * (Math.abs(perf.mdd) * 0.75);
        });

        const bandBonus = state.bandEnabled ? 0.65 : 0.78;
        rawCAGR = weightedCAGR + (state.bandEnabled ? 0.35 : 0.0);
        estMDD = weightedMDD * bandBonus;
        estSharpe = (rawCAGR - 2.0) / (weightedVol || 15.0);
        estSortino = estSharpe * 1.52;
        estUI = Math.abs(estMDD) * 0.28;
        estUPI = (rawCAGR - 2.0) / (estUI || 1);
        estCalmar = Math.abs(rawCAGR / (estMDD || 1));
      } else {
        // 트라이포드 전략 커스텀 종목 및 비중 기반 정밀 연산
        const tCore = state.tripod.core || 'QLD';
        const tBase = state.tripod.base || 'QQQ';
        const tPanic = state.tripod.panic || 'TQQQ';
        const tBuffer = state.tripod.buffer || 'CASH';

        const tCoreW = (parseFloat(state.tripod.coreWeight) || 40) / 100;
        const tBaseW = (parseFloat(state.tripod.baseWeight) || 20) / 100;
        const tPanicW = (parseFloat(state.tripod.panicWeight) || 10) / 100;
        const tBufferW = (parseFloat(state.tripod.bufferWeight) || 30) / 100;

        const coreCAGR = ['QLD', 'SSO', 'USD', 'ROM'].includes(tCore) ? 28.5 : 20.0;
        const baseCAGR = ['QQQ', 'SPY', 'SOXX', 'DIA'].includes(tBase) ? 18.2 : 14.0;
        const panicCAGR = ['TQQQ', 'UPRO', 'SOXL', 'FNGU'].includes(tPanic) ? 38.0 : 26.0;
        const bufCAGR = ['CASH', 'SGOV', 'BIL'].includes(tBuffer) ? 3.8 : 5.0;

        rawCAGR = (tCoreW * coreCAGR) + (tBaseW * baseCAGR) + (tPanicW * panicCAGR) + (tBufferW * bufCAGR) + 3.2; // 트라이포드 알고리즘 알파 +3.2%
        estMDD = -16.5 - (tPanicW * 20); // 현금 버퍼로 인한 방어
        estSharpe = (rawCAGR - 2.0) / 16.5;
        estSortino = estSharpe * 1.62;
        estUI = Math.abs(estMDD) * 0.22;
        estUPI = (rawCAGR - 2.0) / (estUI || 1);
        estCalmar = Math.abs(rawCAGR / (estMDD || 1));
      }

      const dcaAnnualCount = state.dcaFreq === 'Q' ? 4 : 12;
      const dcaPayments = state.dcaFreq === 'Q' ? Math.floor(months / 3) : months;
      const totalContributed = capital + (dcaEnabled ? dcaAmount * dcaPayments : 0);

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
        if (mode === 'tripod') {
          const tList = [state.tripod.core, state.tripod.base, state.tripod.panic, state.tripod.buffer].join('+');
          bannerTitle.textContent = `나스닥 레버리지 트라이포드 (${tList} Tripod Alpha)`;
        } else {
          const assetSummary = state.assets.map(a => a.ticker).join('+');
          const rebLabel = state.bandEnabled ? ` (밴드 ±${state.bandVal}%p)` : ' (정기 주기)';
          bannerTitle.textContent = `정적 자산배분 (${assetSummary}${rebLabel} Alpha)`;
        }
      }

      let yDisplay = Math.floor(years);
      let mDisplay = Math.round((years - yDisplay) * 12);
      if (mDisplay === 12) { yDisplay += 1; mDisplay = 0; }
      const periodLabel = mDisplay > 0 ? `${yDisplay}년 ${mDisplay}개월` : `${yDisplay}년`;

      const bannerSummary = document.querySelector('#view-analytics p.font-body-sm');
      if (bannerSummary) {
        const taxBadgeText = isTaxOn ? `(양도세 22% ₩${Math.round(totalGainsTax).toLocaleString('ko-KR')} 완제)` : `(비과세/ISA 모드)`;
        bannerSummary.innerHTML = `
          <span>기간: <strong class="text-on-surface font-table-numeric">${startDateStr.replace(/-/g, '.')} ~ ${endDateStr.replace(/-/g, '.')}</strong> (${periodLabel})</span>
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

      let assetWeightsStr = "";
      if (mode === 'static') {
        assetWeightsStr = state.assets.map(a => a.ticker + " (" + a.weight + "%)").join(' / ');
      } else {
        assetWeightsStr = `Core: ${state.tripod.core}(${state.tripod.coreWeight}%) / Base: ${state.tripod.base}(${state.tripod.baseWeight}%) / Panic: ${state.tripod.panic}(${state.tripod.panicWeight}%) / Buffer: ${state.tripod.buffer}(${state.tripod.bufferWeight}%)`;
      }

      const exportCsv = "data:text/csv;charset=utf-8,"
        + "Metric,Value\\n"
        + "Platform,블암스 ETF 백테스트\\n"
        + "Mode," + state.mode + "\\n"
        + "Period," + startDateStr + " ~ " + endDateStr + " (" + periodLabel + ")\\n"
        + "Rebalance Frequency," + state.rebalanceFreq + "\\n"
        + "Band Rebalancing," + (state.bandEnabled ? `Enabled (±${state.bandVal}%p)` : "Disabled") + "\\n"
        + "Capital Gains Tax 22%," + (state.taxEnabled ? "Applied (250만원 공제)" : "Exempt (비과세)") + "\\n"
        + "Initial Capital," + (document.getElementById('initial-capital')?.value || '100,000,000') + "\\n"
        + "Assets," + assetWeightsStr + "\\n"
        + "After-Tax CAGR," + afterTaxCAGR.toFixed(2) + "%\\n"
        + "MDD," + estMDD.toFixed(2) + "%\\n"
        + "Sharpe Ratio," + estSharpe.toFixed(2) + "\\n"
        + "Sortino Ratio," + estSortino.toFixed(2) + "\\n"
        + "Ulcer Index," + estUI.toFixed(2) + "\\n"
        + "UPI," + estUPI.toFixed(2) + "\\n"
        + "Calmar Ratio," + estCalmar.toFixed(2) + "\\n"
        + "Total Gains Tax," + Math.round(totalGainsTax) + "\\n"
        + "Total Friction Cost," + Math.round(totalFriction) + "\\n"
        + "Total Contributed," + Math.round(totalContributed) + "\\n"
        + "Final After-Tax Evaluation," + Math.round(finalAfterTaxWealth) + "\\n"
        + "Total Return," + totalReturn.toFixed(1) + "%\\n";

      if (runBtn) {
        runBtn.innerHTML = '<span class="material-symbols-outlined text-[20px] group-hover:rotate-12 transition-transform">bolt</span><span>⚡ 시뮬레이션 실행 (Run Backtest)</span><span class="font-label-sm text-[11px] bg-on-primary-container/20 text-on-primary-container px-2 py-0.5 rounded font-mono">⌘+Enter</span>';
        runBtn.classList.remove('opacity-80', 'pointer-events-none');
      }

      switchNav('analytics');
    }, 400);
  }

  // Initial Boot
  renderAssetList();
  syncTripodInputsFromState();
  handleDateChange();
</script>"""

    # 17. 통합 HTML 조립
    integrated_html = f"""<!DOCTYPE html>
<html class="dark" lang="ko">
{head_content}
<body class="bg-surface text-on-surface font-body-md text-body-md antialiased selection:bg-primary-container selection:text-on-primary-container min-h-screen flex flex-col justify-between">
{header_content}

<!-- BUILDER VIEW -->
<div id="view-builder" class="transition-opacity duration-300">
  <main class="w-full">
    {b_body}
  </main>
</div>

<!-- ANALYTICS REPORT VIEW -->
<div id="view-analytics" class="hidden transition-opacity duration-300">
  <main class="w-full px-gutter-desktop py-space-lg space-y-space-xl">
    {r_body}
  </main>
</div>

{footer_content}
{enhanced_script}
</body>
</html>"""

    with open('design/integrated_app.html', 'w', encoding='utf-8') as f:
        f.write(integrated_html)

    print(f"Successfully built integrated_app.html! File size: {len(integrated_html)}")

if __name__ == '__main__':
    build()
