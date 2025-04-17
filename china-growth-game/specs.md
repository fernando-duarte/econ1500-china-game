# Augmented Open-Economy Solow Model Simulation for China (1980–2024)

## Model Description

### Variables:
- **GDP (Y)**: Economic output measured in billion USD.
- **Capital Stock (K)**: Accumulated stock of physical capital (factories, infrastructure).
- **Labor Force (L)**: Total active workforce in millions.
- **Human Capital (H)**: Represents education and skill level, normalized initially to 1.
- **Total Factor Productivity (A)**: Efficiency and technology level in production, normalized initially to 1.
- **Net Exports (NX)**: Difference between exports and imports (billion USD).
- **Savings Rate (s)**: Proportion of GDP saved annually.
- **Openness Ratio**: Total trade (exports + imports) as a percentage of GDP.
- **FDI Ratio**: Foreign Direct Investment inflows as a percentage of GDP.
- **Population Growth (n)**: Annual growth rate of the labor force.
- **Human Capital Growth (η)**: Annual growth rate of human capital.

### Parameters (Optimized):
- **Capital Share (α)**: 0.30
- **Depreciation Rate (δ)**: 0.10
- **Baseline TFP Growth (g)**: 0.005
- **Openness Impact on TFP (θ)**: 0.1453
- **FDI Impact on TFP (φ)**: 0.10
- **Savings Rate (s)**: 0.20
- **Interest Rate Sensitivity (β)**: -90

## Initial Conditions (1980):
- GDP: 306.2 billion USD
- Capital Stock: 800 billion USD
- Labor Force: 600 million
- Human Capital: 1 (normalized)
- TFP: 1 (normalized)
- Net Exports: 3.6 billion USD

## Model Equations:
1. **Production Function**:
\[ Y(t) = A(t) K(t)^\alpha [L(t)H(t)]^{1-\alpha} \]

2. **Capital Accumulation**:
\[ K(t+1) = (1 - \delta) K(t) + sY(t) + NX(t) \]

3. **Human Capital Growth**:
\[ H(t+1) = H(t)(1 + \eta) \]

4. **Labor Force Growth**:
\[ L(t+1) = L(t)(1 + n) \]

5. **TFP Growth (with openness and FDI)**:
\[ A(t+1) = A(t)\left[1 + g + \theta \frac{X(t)+M(t)}{Y(t)} + \phi \frac{FDI(t)}{Y(t)}\right] \]

6. **Net Foreign Investment (NFI)** (assumed equal to NX for simplicity):
\[ NX(t) = \beta(r_t - r_t^*) \]

## Step-by-Step Annual Update Instructions:
**Step 1: Compute GDP:**
Using capital, labor, human capital, and productivity:
\[ Y(t) = A(t) K(t)^\alpha (L(t)H(t))^{1-\alpha} \]

**Step 2: Update Capital:**
Depreciate existing capital and add new investment (savings plus net exports):
\[ K(t+1) = (1-\delta)K(t) + sY(t) + NX(t) \]

**Step 3: Update Labor Force:**
\[ L(t+1) = L(t)(1+n) \]

**Step 4: Update Human Capital:**
\[ H(t+1) = H(t)(1+\eta) \]

**Step 5: Update Productivity (TFP):**
\[ A(t+1) = A(t)\left[1+g+\theta \frac{X(t)+M(t)}{Y(t)}+\phi \frac{FDI(t)}{Y(t)}\right] \]

**Step 6: Update Net Exports:**
Adjust net exports based on interest rate differential (assumed constant for simplicity):
\[ NX(t) = \beta(r_t - r_t^*) \]

## Model Simulation Results
The attached tables and plots compare the simulated model outcomes to actual historical data for China (1980–2024), demonstrating the accuracy and applicability of the model. For detailed numerical results, refer to the provided simulation tables and comparison analyses.

