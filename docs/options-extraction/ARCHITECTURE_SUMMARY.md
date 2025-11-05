# pysystemtrade Architecture - Executive Summary

## Repository Overview
- **Purpose:** Open-source systematic futures trading engine for backtesting and live trading
- **Size:** ~592 Python files across 16 main modules
- **Version:** 1.8.2 (Nov 2024)
- **Author:** Rob Carver (implementations of "Systematic Trading" framework)
- **Production Ready:** Yes - actively used for live Interactive Brokers trading

---

## Architecture at a Glance

### The Core System (Pipeline Architecture)
```
Data Input → [Pipeline of SystemStages] → P&L Analysis → Performance Metrics

Example pipeline flow:
RawData → Rules → ForecastScaleCap → ForecastCombine → PositionSizing → Portfolio → Account → Results
```

### Key Insight: Component Composition
Everything is a **SystemStage** - discrete components that:
- Process data independently
- Access parent system via `self.parent`
- Have clearly defined inputs/outputs
- Can be tested in isolation
- Chain together to form processing pipeline

---

## The 7 Core Processing Stages

| # | Stage | Function | Key Output |
|---|-------|----------|-----------|
| 1 | **RawData** | Calculate volatility, prepare prices | `daily_prices()`, `daily_volatility()` |
| 2 | **Rules** | Execute trading rules on all instruments | `raw_forecast()` for each rule |
| 3 | **ForecastScaleCap** | Scale forecasts, cap to [-20,20] range | `capped_forecast()` |
| 4 | **ForecastCombine** | Combine rules with weights + FDM | `combined_forecast()` |
| 5 | **PositionSizing** | Convert forecast to contract count | `subsystem_position()` |
| 6 | **Portfolio** | Apply instrument weights + IDM | `notional_position()`, `actual_position()` |
| 7 | **Account** | Calculate P&L and performance metrics | `portfolio()`, `stats()` |

---

## What Makes It Powerful

### 1. **Configuration-Driven (Zero Code Changes)**
All parameters live in YAML config or Python dict:
- Trading rules & parameters
- Instrument list & weights
- Position sizing targets
- Cost models
- Optimization settings

Example: Change `forecast_scalars` dict and get different backtest instantly

### 2. **Intelligent Caching**
- Avoids recalculating same forecasts
- Decorators (`@input`, `@output`, `@diagnostic`) manage cache
- Picklable for persistence
- Speeds up large backtests by 10-100x

### 3. **Flexible Data Abstraction**
Three layers of separation:
```
Storage (CSV, MongoDB, Arctic, IB)
    ↓ (hidden by)
Data Objects (futuresSimData, customData)
    ↓ (exposed as)
System Interface (simData methods)
```
Swap storage backends without touching system code

### 4. **Rich Performance Analytics**
P&L calculated as:
- Gross (before costs)
- Net (after costs)  
- Per-rule contribution
- Per-instrument breakdown
- Per-subsystem aggregation

Statistics include: Sharpe, drawdown, skewness, kurtosis, calmar ratio, etc.

### 5. **Built-in Diversification Logic**
- **Forecast Diversification Multiplier (FDM):** Boosts forecast when rules agree
- **Instrument Diversification Multiplier (IDM):** Increases when portfolio diversified
- Both estimated from correlation structure

### 6. **Production-Ready Components**
- Position buffering (reduce turnover)
- Capital multiplier (compound trading)
- Cost modeling (slippage, commissions, spread)
- Order execution framework
- Interactive Brokers integration

---

## The System Class: Hub of Everything

```python
system = System(
    stage_list=[RawData(), Rules(), ForecastScaleCap(), ...],
    data=csvFuturesSimData(),
    config=Config("config.yaml")
)

# Access stages dynamically
system.rules.get_raw_forecast("EDOLLAR", "ewmac8")
system.portfolio.get_notional_position("CORN")
system.accounts.portfolio().stats()
```

**Key Methods:**
- `.get_instrument_list()` - Available instruments
- `.[stage_name].*()` - Access any stage's methods
- `.cache` - Inspect cached results

---

## Data Pipeline Flow

### Input Data Required
1. **Price data** (daily OHLC minimum)
2. **Instrument metadata** (contract size, currency, costs)
3. **FX rates** (for multi-currency portfolio)
4. **Configuration** (all strategy parameters)

### Processing Flow
```
Raw price series
    ↓
Volatility calculation
    ↓
Rule evaluation (for each rule)
    ↓
Scale & cap forecasts
    ↓
Combine with weights
    ↓
Size positions (forecast / volatility)
    ↓
Weight by instrument allocation
    ↓
Calculate position changes
    ↓
Apply costs & slippage
    ↓
Calculate P&L
    ↓
Compute statistics
```

---

## Key Classes You Need to Know

### System Architecture
- **System** - Main orchestrator
- **SystemStage** - Base class for all processing stages
- **Config** - Parameter management (YAML/dict/list based)
- **simData** - Data access interface

### Trading Framework
- **TradingRule** - Container for rule function + parameters
- **Rules** - Stage that executes all trading rules
- **ForecastCombine** - Combines multiple rule forecasts

### Position Construction
- **PositionSizing** - Position from forecast
- **Portfolios** - Apply weights & diversification
- **Account** - P&L calculation

### Performance Analysis
- **accountCurve** - Extends pandas Series with stats
- **accountCurveGroup** - Aggregates multiple curves
- **pandlCalculation** - Core P&L math

### Quantitative Tools
- **estimators.vol** - Volatility calculation
- **estimators.correlations** - Correlation estimation
- **optimisation.portfolioOptimiser** - Weight optimization

---

## Configuration Example

```yaml
# instruments.yaml
instruments: [EDOLLAR, CORN, US10, CRUDE_W]

# rules
trading_rules:
  ewmac8:
    function: systems.provided.rules.ewmac.ewmac_forecast_with_defaults
    other_args: {Lfast: 8, Lslow: 32}
  ewmac32:
    function: systems.provided.rules.ewmac.ewmac_forecast_with_defaults
    other_args: {Lfast: 32, Lslow: 128}

# Combining rules
forecast_weights: {ewmac8: 0.5, ewmac32: 0.5}
forecast_div_multiplier: 1.1
forecast_scalars: {ewmac8: 5.3, ewmac32: 2.65}

# Portfolio
instrument_weights: {EDOLLAR: 0.4, CORN: 0.3, US10: 0.2, CRUDE_W: 0.1}
instrument_div_multiplier: 1.5

# Sizing
percentage_vol_target: 25.0
notional_trading_capital: 500000
base_currency: GBP

# Costs
cost_per_contract: 2.0
spread_cost_in_bps: 2.5
```

One config change (e.g., `forecast_weights: {ewmac8: 0.3, ewmac32: 0.7}`) creates entirely different backtest.

---

## Pre-baked Systems Ready to Use

### 1. Futures Chapter 15
- Location: `systems/provided/futures_chapter15/basesystem.py`
- Complete system from Rob Carver's book
- 4 rules: ewmac2_8, ewmac4_16, ewmac8_32, carry
- Drop-in ready: `system = futures_system()`

### 2. Rob's Production System
- Location: `systems/provided/rob_system/`
- More complex multi-rule setup
- Customized RawData stage
- Used for live trading

### 3. Example Systems
- `provided/example/simplesystem.py` - Minimal setup
- Multiple examples in `/examples/introduction/`
- Good templates for custom systems

---

## Quick Start Workflow

### Step 1: Load Data
```python
from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
data = csvFuturesSimData()  # Ships with sample data
```

### Step 2: Create Configuration
```python
from sysdata.config.configdata import Config
config = Config("systems.provided.futures_chapter15.futuresconfig.yaml")
```

### Step 3: Build System
```python
from systems.provided.futures_chapter15.basesystem import futures_system
system = futures_system(data, config)
```

### Step 4: Get Results
```python
positions = system.portfolio.get_notional_position("EDOLLAR")
pnl = system.accounts.pandl_for_subsystem("EDOLLAR")
stats = pnl.stats()  # Sharpe, drawdown, returns, etc.
```

---

## Module Breakdown

### Core Backtesting (`/systems/`)
- `basesystem.py` - Main System class
- `stage.py` - SystemStage base
- `forecasting.py` - Rules/signal generation
- `trading_rules.py` - Trading rule framework
- `forecast_scale_cap.py` - Scaling/capping
- `forecast_combine.py` - Rule combination
- `positionsizing.py` - Position sizing
- `portfolio.py` - Weighting/diversification
- `system_cache.py` - Result caching
- `accounts/` - P&L and performance analytics

### Data Layer (`/sysdata/`)
- `base_data.py` - Generic interface
- `sim/sim_data.py` - Simulation interface
- `sim/csv_futures_sim_data.py` - CSV backend
- `sim/db_futures_sim_data.py` - Database backend
- `config/configdata.py` - Configuration
- `csv/`, `mongodb/`, `arctic/` - Storage backends

### Domain Objects (`/sysobjects/`)
- `instruments.py` - Instrument definitions
- `adjusted_prices.py` - Back-adjusted prices
- `roll_calendars.py` - Futures roll management
- `spot_fx_prices.py` - FX rates

### Quantitative (`/sysquant/`)
- `estimators/vol.py` - Volatility
- `estimators/correlations.py` - Correlations
- `estimators/covariance.py` - Covariance
- `optimisation/` - Portfolio optimization
- `portfolio_risk.py` - Risk calculations

### Utilities (`/syscore/`)
- Pandas utilities (resampling, alignment)
- Date/time utilities
- Logging framework
- Object introspection

---

## Why This Architecture is Brilliant

### 1. **Separation of Concerns**
Each stage has one job, does it well, can be tested independently

### 2. **Extensibility**
Add new stages, rules, data sources without modifying existing code

### 3. **Reusability**
Framework is asset-class agnostic (works for stocks, bonds, options, etc.)

### 4. **Debuggability**
Can inspect intermediate results at each stage via cache
Clear flow of data through pipeline

### 5. **Performance**
Intelligent caching means large backtests stay fast
Can pickle cache for later reuse

### 6. **Flexibility**
100% parameter-driven - no code changes needed for most variations
YAML configs are readable and versionable

---

## For Options Strategies Platform

### Directly Reusable (60-70%)
- **System/Stage architecture** - Core framework
- **Config system** - Parameter management
- **Portfolio construction** - Weighting, diversification
- **P&L calculation** - Cost handling, statistics
- **Caching** - Result persistence
- **Quantitative tools** - Estimation, optimization
- **Data abstraction** - Multi-source support

### Requires Extension (30-40%)
- **RawData stage** - Add Greeks calculation
- **PositionSizing** - Use Greeks instead of volatility
- **Trading rules** - Greeks-based signals
- **Risk stage** - Delta/gamma/vega hedging
- **Cost models** - Options-specific spreads/gamma costs
- **Execution** - Leg-matched orders, roll management

### Estimated Total Reuse: 60-70% of codebase

---

## File Locations Reference

```
MAIN ENTRY POINT:
  /systems/basesystem.py - System class

TYPICAL PIPELINE:
  /systems/rawdata.py
  /systems/forecasting.py
  /systems/forecast_scale_cap.py
  /systems/forecast_combine.py
  /systems/positionsizing.py
  /systems/portfolio.py
  /systems/accounts/accounts_stage.py

CONFIGURATION:
  /sysdata/config/configdata.py

DATA SOURCES:
  /sysdata/sim/csv_futures_sim_data.py
  /sysdata/sim/db_futures_sim_data.py

TRADING RULES LIBRARY:
  /systems/provided/rules/ewmac.py
  /systems/provided/rules/carry.py
  /systems/provided/rules/breakout.py

PRE-BAKED SYSTEMS:
  /systems/provided/futures_chapter15/basesystem.py
  /systems/provided/rob_system/run_system.py

EXAMPLES:
  /examples/introduction/simplesystem.py
  /examples/introduction/asimpletradingrule.py
```

---

## Full Documentation

Complete analysis with code examples, architecture diagrams, and detailed component references is available in:
**`/home/user/pysystemtrade_architecture_analysis.md`**

This comprehensive guide includes:
- Detailed stage-by-stage breakdown
- Code examples for each component
- Configuration reference
- Entry points for backtesting
- Reusability assessment for options platforms
- Design pattern explanations
- Key files reference table

