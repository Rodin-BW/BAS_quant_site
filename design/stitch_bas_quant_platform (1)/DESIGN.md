---
name: Quant Precision
colors:
  surface: '#0f131d'
  surface-dim: '#0f131d'
  surface-bright: '#353944'
  surface-container-lowest: '#0a0e18'
  surface-container-low: '#171b26'
  surface-container: '#1c1f2a'
  surface-container-high: '#262a35'
  surface-container-highest: '#313540'
  on-surface: '#dfe2f1'
  on-surface-variant: '#c1c6d6'
  inverse-surface: '#dfe2f1'
  inverse-on-surface: '#2c303b'
  outline: '#8b909f'
  outline-variant: '#414754'
  surface-tint: '#acc7ff'
  primary: '#acc7ff'
  on-primary: '#002f67'
  primary-container: '#478fff'
  on-primary-container: '#00285b'
  inverse-primary: '#005bbe'
  secondary: '#44e184'
  on-secondary: '#00391a'
  secondary-container: '#07c168'
  on-secondary-container: '#004823'
  tertiary: '#ffb3b2'
  on-tertiary: '#680013'
  tertiary-container: '#ff525e'
  on-tertiary-container: '#5b0010'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d7e2ff'
  primary-fixed-dim: '#acc7ff'
  on-primary-fixed: '#001a40'
  on-primary-fixed-variant: '#004491'
  secondary-fixed: '#66fe9d'
  secondary-fixed-dim: '#44e184'
  on-secondary-fixed: '#00210d'
  on-secondary-fixed-variant: '#005229'
  tertiary-fixed: '#ffdad9'
  tertiary-fixed-dim: '#ffb3b2'
  on-tertiary-fixed: '#410008'
  on-tertiary-fixed-variant: '#92001f'
  background: '#0f131d'
  on-background: '#dfe2f1'
  surface-variant: '#313540'
typography:
  display-lg:
    fontFamily: Hanken Grotesk
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.03em
  display-lg-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.025em
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Hanken Grotesk
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Hanken Grotesk
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Hanken Grotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Hanken Grotesk
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-sm:
    fontFamily: Hanken Grotesk
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0.005em
  kpi-numeric:
    fontFamily: Hanken Grotesk
    fontSize: 26px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.02em
  table-numeric:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: -0.01em
  label-md:
    fontFamily: Hanken Grotesk
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-desktop: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.875rem
  space-lg: 1.25rem
  space-xl: 2rem
---

## Brand & Style

This design system is tailored for institutional-grade quantitative portfolio engineering, systematic backtesting, and retail-accessible algorithmic wealth management. It synthesizes the intuitive, ultra-polished fluidity of contemporary Korean consumer fintech (Toss) with the disciplined, analytical density of global quant analytics suites (Snowball, Koyfin).

The interface communicates absolute mathematical authority, rapid latency, and crystalline legibility. Every pixel must feel intentional and grounded:
- **Style Archetype:** Modern High-Density FinTech / Engineered Dark Canvas.
- **Aesthetic Tenets:** Muted deep-navy surfaces, sub-pixel hairline dividers (`rgba(255, 255, 255, 0.08)`), vibrant single-purpose optical accents, and zero extraneous decorative noise.
- **Emotional Target:** Uncompromising reliability, executive calm, computational rigor, and surgical control during market volatility.

## Colors

The palette leverages an engineered deep obsidian-navy base rather than pure neutral blacks to preserve organic depth across complex analytical overlays.

- **Background & Canvas:**
  - `canvas-base`: `#0B0F19` (Deep Obsidian Navy)
  - `surface-card`: `#111827` (Tailwind Slate-900 equivalent)
  - `surface-elevated`: `#1E293B` (Tailwind Slate-800 equivalent)
  - `surface-subtle`: `rgba(255, 255, 255, 0.04)`

- **Accent & State Tokens:**
  - `accent-primary` (`#3182F6`): Signal Toss Blue. Applied to primary calls-to-action, active segmented toggles, interactive chart crosshairs, and benchmark traces.
  - `semantic-positive` (`#05C168`): Emerald Green. Used exclusively for positive returns, alpha generation, upward delta badges, and favorable tail risk.
  - `semantic-negative` (`#F04452`): Crimson Red. Reserved strictly for drawdowns (MDD), losses, negative Sharpe ratios, and tail risk anomalies.
  - `semantic-warning` (`#F59E0B`): Amber. Highlights tax liability thresholds, transaction drag, rebalancing slippage, and high portfolio turnover warnings.

- **Borders & Scaffolding:**
  - `border-hairline`: `rgba(255, 255, 255, 0.07)`
  - `border-active`: `rgba(49, 130, 246, 0.45)`
  - `border-subtle`: `rgba(255, 255, 255, 0.12)`

## Typography

The type scale prioritizes numerical legibility and scanning speed across dense tabular matrices.

- **Primary Sans (`Hanken Grotesk`):** Chosen for its geometric discipline, razor-sharp counters, and clean rendering on dark pixels. Used for all headings, body narrative, labels, and KPI metrics.
- **Numerical Rules:** All financial metrics, delta percentages, timestamps, and ticker symbols enforce open-type tabular lining numerals (`font-feature-settings: "tnum" 1, "cv05" 1`).
- **Monospace Integration (`JetBrains Mono`):** Applied strictly to dense data grid cells, formula breakdowns, ISIN/ticker identifiers, execution timestamps, and code-based algorithm scripts.

## Layout & Spacing

This design system uses a strict 12-column adaptive grid configured for high-density information architecture.

- **Breakpoints:**
  - **Mobile (< 768px):** 4 columns, `margin: 1rem`, `gutter: 0.75rem`. KPI cards horizontal carousel, charts full width with horizontal pinch-to-zoom.
  - **Tablet (768px - 1199px):** 8 columns, `margin: 1.5rem`, `gutter: 1rem`. Side-by-side KPI pairs, 2-column tabular breakdowns.
  - **Desktop (1200px+):** 12 columns, `margin: 2rem`, `gutter: 1.5rem`. Split dashboard layout: Left 8-col analytical chart canvas; Right 4-col real-time stats, factor exposures, and rebalancing control drawer.
- **Rhythm & Padding:** Strict 4px base multiplier. Component inner padding adheres strictly to `space-sm` (8px) for badges and micro-inputs, `space-md` (14px) for list items and table rows, and `space-lg` (20px) for container cards.

## Elevation & Depth

To maintain high data density without visual clutter, traditional drop shadows are minimized in favor of tonal layering and low-contrast optical borders.

- **Layer 0 (Canvas Base):** Pure `#0B0F19` backdrop.
- **Layer 1 (Cards & Data Grids):** Solid `#111827` surface framed with a hairline outline `border: 1px solid rgba(255, 255, 255, 0.07)`.
- **Layer 2 (Overlays & Segmented Surfaces):** `#1E293B` background with subtle ambient elevation: `box-shadow: 0 4px 16px -2px rgba(0, 0, 0, 0.45)`.
- **Layer 3 (Modals & Tooltips):** Blended glassmorphism over dark navy (`background: rgba(17, 24, 39, 0.85); backdrop-filter: blur(12px)`), bounded by `rgba(255, 255, 255, 0.12)`.
- **Active Focus & Glow:** Interactive selections (e.g., active chart tabs or focused input fields) utilize an ambient radial halo: `0 0 0 1px #3182F6, 0 0 12px rgba(49, 130, 246, 0.25)`.

## Shapes

The geometry strikes a modern balance between consumer friendliness (Toss-style approachable radiuses) and technical rigor:
- **Base Components (Inputs, Segmented Controls, Badges):** `rounded-md` (8px / `0.5rem`).
- **Cards & Data Modules:** `rounded-lg` (16px / `1rem`) creates distinct, polished analytical panels.
- **Pill Elements:** Full rounded pills (`9999px`) are strictly reserved for status indicators (e.g., "LIVE", "BACKTEST COMPLETE") and asset-class classification chips (e.g., "US ETF", "KR ETF").

## Components

### 1. KPI Metric Cards
- **Architecture:** Compact container (`surface-card`, 16px corner radius, hairline boundary).
- **Structure:** Metric Title (Label-md, muted slate-400) + Informational Info-Icon tooltip top-right. Numeric primary value (`kpi-numeric`) centered/bottom with explicit tabular numerals.
- **Trend Tag:** Compact pill badge on bottom row displaying positive (`#05C168` on `rgba(5, 193, 104, 0.1)`) or negative (`#F04452` on `rgba(240, 68, 82, 0.1)`) delta with direction arrow.

### 2. Analytical Chart Containers & Tabs
- **Header Structure:** Title + unified Segmented Pill Bar containing metrics: `[ CAGR | MDD | Ulcer Index | Sharpe | Sortino | UPI | Calmar | Tax & Cost ]`.
- **Active Tab:** Solid slate-800 or Toss Blue pill fill, crisp white text, micro glow.
- **Inactive Tab:** Transparent background, muted text (`#94A3B8`), subtle hover shift to `rgba(255, 255, 255, 0.05)`.
- **Crosshair Tooltip:** Glassmorphic slate-900 box (`backdrop-filter: blur(8px)`), monospaced values, colored legend bullet points.

### 3. High-Density Data Tables
- **Row Rhythm:** Fixed 40px row height for optimal data scanning. Alternating subtle zebra striping (`rgba(255, 255, 255, 0.015)` optional, default transparent with `border-bottom: 1px solid rgba(255, 255, 255, 0.05)`).
- **Alignment:** Text/Tickers left-aligned, Asset Class badges centered, all financial return figures strictly right-aligned with `JetBrains Mono`.

### 4. Asset Class Badges
- **Form:** Pill shape (`rounded-full`), padding `2px 8px`, `label-sm`.
- **US ETF:** Blue tint (`color: #60A5FA; background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.2)`).
- **KR ETF:** Teal tint (`color: #2DD4BF; background: rgba(20, 184, 166, 0.12); border: 1px solid rgba(20, 184, 166, 0.2)`).

### 5. Buttons & Controls
- **Primary Action:** Solid Toss Blue (`#3182F6`), hover `#2272EB`, active press transform scale `0.98`.
- **Secondary Action:** Ghost/Outline button with hairline border (`rgba(255, 255, 255, 0.1)`), hovering to slate-800.
- **Toggles:** 44px x 24px track, deep navy-slate background when unselected, `#3182F6` when enabled. 20px circular white thumb with swift 150ms cubic-bezier transition.

### 6. Input Fields
- Dark input fields (`#0B0F19`) nested within cards, bounded by 1px slate-700. Active focus state triggers blue halo border with zero label displacement. Numerical inputs include right-aligned unit affixes (e.g., `USD`, `%`, `bps`).