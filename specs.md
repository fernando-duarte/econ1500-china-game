# China's Growth Game: Saving, Trade, and Prosperity (1980–2025)

## Overview
- **Game Type**: Interactive economic simulation
- **Duration**: 50 minutes total
- **Participants**: 80 undergraduates divided into 10 teams (8 students per team)
- **Timeframe**: 1980–2025 (10 rounds, each representing 5 years: 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025)

## Game Flow and Timing
### Group Formation (3 minutes)
- Students form groups by proximity.
- Select one leader device per group.

### Group Naming (2 minutes)
- UI auto-generates a default, fun economic-themed group name (e.g., "The Prosperous Pandas").
- Students can generate alternative names or manually input their own.
- Explicit confirmation required for the chosen name.

### Gameplay (34 minutes)
- Rounds 1–2: 5 minutes each (for familiarization).
- Rounds 3–10: 4 minutes each (standard play).

### Discussion (8 minutes)
- Instructor-led reflection and analysis of strategies and outcomes.

## Prizes (Announced at Start)
### Categories
- Highest GDP Growth
- Highest Net Exports
- Best Balanced Economy (combination of GDP and Consumption)

### Suggested Prizes
- Gift cards, certificates, or economic-themed souvenirs.

## Student UI Components

### Dashboard (Always Visible)
- Current Year
- Group Name
- Countdown Timer (e.g., ⏳ TIME LEFT: 4:30)
- Economic Statistics:
  - GDP
  - Capital Stock
  - Consumption
  - Net Exports
  - Previous Round GDP Growth (%)
  - Current Ranking

### Breaking News (Event Announcements)
- Initial announcement without numeric details.
- Numeric impact explicitly revealed at the end of each affected round.

#### Events
- **2001**: China Joins WTO (Exports +25%, TFP +2% per year)
- **2008**: Global Financial Crisis (Exports -20%, GDP growth -3%)
- **2018**: US-China Trade War (Exports -10%)
- **2020**: COVID-19 Pandemic (GDP growth -4%)

### Decision Controls
- **Savings Rate Slider**: 1%–99%, default at 10%
- **Exchange Rate Policy Buttons**:
  - Undervalue (set exchange rate 20% lower than the market baseline)
  - Market-Based (set at baseline market exchange rate)
  - Overvalue (set exchange rate 20% higher than the market baseline)
- Explicit submit button with confirmation step

### Results Visualization
- GDP Growth (line chart)
- Trade Balance (bar graph)
- Consumption vs. Savings (pie chart)

+--------------------------------------------+
| Year: 2005                           ℹ️      |
| Your GDP:             $2,500 bn            |
| Your Capital Stock:   $1,800 bn            |
| Your Consumption:     $1,200 bn            |
| Your Net Exports:     +$200 bn             |
| GDP Growth (last round): 8%                |
| Ranking: #2 of 10 groups 🔥                |
+--------------------------------------------+
| ⏳ TIME LEFT: 3:45                          |
+--------------------------------------------+

BREAKING NEWS (2001): 🌎 China joins the WTO!

Decision Time!
---------------
Savings Rate: [ ▮▮▮▮▮▯▯▯▯▯▯ 45% ] 
(Choose from 1% to 99%)
---------------
Exchange Rate Policy:
🔵 [Undervalue]   ⚪ [Market-Based]   ⚪ [Overvalue]

[SUBMIT DECISIONS]

Results Visualizations:
- GDP Growth 📈
- Trade Balance 📊
- Consumption vs Savings 🥧


## Professor Dashboard
- Real-time leaderboard displaying:
  - GDP ranking
  - Net exports ranking
  - Balanced economy ranking
- Charts tracking overall class performance
- Controls explicitly provided to start subsequent rounds
- Capability to pause or restart the timer

## Technical Setup
- Students must connect to provided Wi-Fi.
- Each group selects exactly one leader device for decision submissions.
- All students may individually view progress but submissions are allowed only via the leader device.

## Comprehensive Economic Model

### Endogenous Variables
- GDP (Y)
- Capital Stock (K)
- Human Capital (H)
- Productivity (Total Factor Productivity, TFP, A)
- Net Exports (NX)
- Consumption (C)
- Investment (I)

### Exogenous Variables
- Labor Force Growth (n)
- Foreign Income Growth
- Domestic Interest Rate
- Foreign Interest Rate
- Openness Ratio
- FDI Ratio

### Student-Determined Variables (Exogenous, set by students each round)
- **Savings Rate (s)**: Chosen explicitly by students, no fixed default (initial suggested default at 10%)
- **Exchange Rate (e)**: Determined by students' choice each round:
  - Undervalue: 20% lower than the market baseline
  - Market-Based: Baseline market exchange rate
  - Overvalue: 20% higher than the market baseline

### Model Equations (Explicitly Defined)
- **Production**: \(Y(t) = A(t) \times K(t)^\alpha \times (L(t) \times H(t))^{(1-\alpha)}\)
- **Capital Accumulation**: \(K(t+1) = (1 - \delta) \times K(t) + s \times Y(t) + NX(t)\)
- **Labor Force Growth**: \(L(t+1) = L(t) \times (1+n)\)
- **Human Capital Growth**: \(H(t+1) = H(t) \times (1+\eta)\)
- **Productivity Growth**: \(A(t+1) = A(t) \times (1 + g + \theta \times openness\_ratio + \phi \times fdi\_ratio)\)
- **Net Exports**: \(NX(t) = \beta \times (domestic\_interest\_rate - foreign\_interest\_rate)\)

### Explicit Parameters
- \(\alpha = 0.3\)
- \(\delta = 0.1\)
- \(g = 0.005\)
- \(\theta = 0.1453\)
- \(\phi = 0.1\)
- \(\beta = -90\)
- \(n = 0.00717\)
- \(\eta = 0.02\)

### Explicit Exogenous Variables
- Foreign income growth: 3% per year.
- Domestic interest rate: 4% annually.
- Foreign interest rate: 8% annually.
- Openness ratio: starts at 0.1 and increases gradually.
- FDI ratio (post-1990): 0.02.

## Step-by-Step Computation (Explicitly Detailed)
- Each Round:
  1. Input current GDP, capital stock, labor force, human capital, and productivity values.
  2. Apply student-selected savings rate and exchange rate explicitly.
  3. Compute GDP explicitly using the production equation.
  4. Update capital stock explicitly with capital accumulation equation.
  5. Update labor force explicitly.
  6. Update human capital explicitly.
  7. Update productivity explicitly.
  8. Compute net exports explicitly.

## Prize Determination (Explicit Criteria)
- **Highest GDP Growth**: Highest GDP value in the final round.
- **Highest Net Exports**: Highest Net Export value in the final round.
- **Best Balanced Economy**: Highest combined GDP and consumption in the final round.

This specification provides thorough and explicit details designed to facilitate seamless implementation by any developer or system operator.

