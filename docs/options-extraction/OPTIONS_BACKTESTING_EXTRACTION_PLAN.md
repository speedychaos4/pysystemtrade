# Options Backtesting Platform - Extraction Plan
## Based on pysystemtrade CTA Framework

---

## Executive Summary

This document outlines a comprehensive plan to extract reusable components from the pysystemtrade CTA trend following framework and adapt them to build a flexible options strategies backtesting platform. The goal is to create a research tool that supports trend following, mean reversion, and volatility-based options strategies with the ability to plug in custom data.

**Estimated Reusability: 65-70% of the core backtesting infrastructure**

---

## Table of Contents

1. [Core Architecture to Extract](#core-architecture)
2. [Components Analysis](#components-analysis)
3. [Options-Specific Extensions](#options-extensions)
4. [Implementation Roadmap](#implementation-roadmap)
5. [File Structure](#file-structure)
6. [Data Requirements](#data-requirements)
7. [Quick Start Guide](#quick-start)

---

## Core Architecture to Extract {#core-architecture}

### 1. System/Stage Pipeline (100% Reusable)

**Files to Extract:**
- `/systems/basesystem.py` - Main System orchestrator
- `/systems/stage.py` - SystemStage base class
- `/systems/system_cache.py` - Intelligent caching system

**Why:** The pipeline architecture is asset-class agnostic and provides:
- Clean separation of concerns
- Composable stages
- Intelligent caching for performance
- Easy testing and debugging

**Modifications Needed:** None - use as-is

---

### 2. Configuration System (100% Reusable)

**Files to Extract:**
- `/sysdata/config/configdata.py` - Config class
- `/sysdata/config/defaults.py` - Default parameters
- `/sysdata/config/fill_config_dict_with_defaults.py` - Config merging

**Why:** Provides parameter-driven system that allows:
- YAML/dict/list-based configuration
- Hierarchical defaults (private > backtest > defaults)
- Zero-code changes for strategy variations

**Modifications Needed:** None - use as-is

---

### 3. Data Abstraction Layer (80% Reusable)

**Files to Extract:**
- `/sysdata/base_data.py` - Base data interface
- `/sysdata/sim/sim_data.py` - Simulation data base class
- `/sysdata/csv/csv_sim_futures_data.py` - CSV backend (as template)

**Why:** Clean separation between storage and system logic:
- Multi-source support (CSV, database, API)
- System doesn't care about data source
- Easy to swap backends

**Modifications Needed:**
- Create `optionsSimData` class inheriting from `simData`
- Add methods for:
  - `get_option_chain(underlying, date)`
  - `get_greeks(option_code, date)`
  - `get_implied_volatility(option_code, date)`
  - `get_underlying_price(underlying, date)`

---

### 4. Trading Rules Framework (90% Reusable)

**Files to Extract:**
- `/systems/trading_rules.py` - TradingRule class
- `/systems/forecasting.py` - Rules stage

**Why:** Flexible rule definition system:
- Function + data + parameters = rule
- Dynamic data resolution from system
- Easy to add new rules
- Supports parameter variations

**Modifications Needed:**
- Rules will reference options data methods (e.g., `data.get_iv`, `data.get_delta`)
- Add options-specific rule functions (covered in Extensions section)

---

### 5. Position Sizing (50% Reusable)

**Files to Extract:**
- `/systems/positionsizing.py` - Base PositionSizing stage
- `/sysquant/estimators/vol.py` - Volatility estimation

**Why:** Core position sizing logic is valuable:
- Risk-based sizing
- Volatility targeting
- Buffer management

**Modifications Needed:**
- Create `OptionsPositionSizing` that inherits from `PositionSizing`
- Replace volatility-based sizing with Greeks-based sizing:
  - Use delta-adjusted notional exposure
  - Account for gamma risk
  - Size based on vega exposure for vol strategies
- Override `get_subsystem_position()` method

---

### 6. Portfolio Construction (70% Reusable)

**Files to Extract:**
- `/systems/portfolio.py` - Portfolio stage
- `/sysquant/optimisation/` - Portfolio optimization tools
- `/sysquant/estimators/correlations.py` - Correlation estimation

**Why:** Portfolio logic is largely asset-agnostic:
- Instrument weighting
- Diversification multiplier
- Portfolio optimization
- Buffering

**Modifications Needed:**
- Correlations should be based on delta-adjusted returns
- Add portfolio-level Greeks aggregation
- Consider options expiration in position management

---

### 7. P&L and Performance Analytics (85% Reusable)

**Files to Extract:**
- `/systems/accounts/` - All account modules
- `/systems/accounts/curves/account_curve.py` - Performance metrics
- `/systems/accounts/pandl_calculators/` - P&L calculation

**Why:** Excellent performance analytics:
- Sharpe ratio, Sortino, Calmar
- Drawdown analysis
- Net/Gross/Costs breakdown
- Per-rule attribution
- Extensible to pandas Series

**Modifications Needed:**
- Add options-specific cost models:
  - Bid/ask spreads (typically wider for options)
  - Pin risk costs
  - Assignment/exercise costs
- Add Greeks-based risk metrics to stats

---

### 8. Quantitative Tools (90% Reusable)

**Files to Extract:**
- `/sysquant/estimators/vol.py` - Volatility estimation
- `/sysquant/estimators/correlations.py` - Correlation
- `/sysquant/estimators/covariance.py` - Covariance
- `/syscore/pandas/` - Pandas utilities
- `/syscore/dateutils.py` - Date utilities

**Why:** High-quality quantitative libraries:
- Robust volatility estimation
- Exponential weighting
- Correlation matrices
- Pandas helpers

**Modifications Needed:** Minimal - mostly use as-is

---

### 9. Caching System (100% Reusable)

**Files to Extract:**
- `/systems/system_cache.py` - Caching decorators and logic

**Why:** Critical for performance:
- Automatic result caching
- Decorators: `@input`, `@output`, `@diagnostic`
- Picklable for persistence
- 10-100x speedup on large backtests

**Modifications Needed:** None - use as-is

---

### 10. Utilities (100% Reusable)

**Files to Extract:**
- `/syscore/objects.py` - Object utilities
- `/syscore/genutils.py` - General utilities
- `/syscore/exceptions.py` - Custom exceptions
- `/syscore/fileutils.py` - File utilities
- `/syslogging/` - Logging framework

**Why:** Well-designed utility libraries that work across asset classes

**Modifications Needed:** None - use as-is

---

## Components Analysis {#components-analysis}

### Direct Extraction (Use As-Is)

| Component | Files | Lines | Complexity | Value |
|-----------|-------|-------|------------|-------|
| System/Stage | basesystem.py, stage.py | ~500 | Medium | Critical |
| Config | configdata.py | ~300 | Low | High |
| Caching | system_cache.py | ~400 | Medium | High |
| TradingRule | trading_rules.py | ~500 | Medium | High |
| Utilities | syscore/* | ~2000 | Low | Medium |
| Logging | syslogging/* | ~1000 | Medium | Medium |

**Total: ~4,700 lines - Direct reuse**

---

### Adaptation Required (Modify)

| Component | Files | Lines | Modifications | Effort |
|-----------|-------|-------|---------------|--------|
| Data Layer | sim_data.py | ~600 | Add options methods | Medium |
| PositionSizing | positionsizing.py | ~800 | Greeks-based sizing | High |
| Portfolio | portfolio.py | ~1200 | Greeks aggregation | Medium |
| Accounts | accounts/* | ~2000 | Options costs | Medium |
| Rawdata | rawdata.py | ~500 | Add Greeks calculation | High |

**Total: ~5,100 lines - Adaptation needed**

---

### New Development (Build from Scratch)

| Component | Purpose | Estimated Lines | Effort |
|-----------|---------|-----------------|--------|
| OptionsData | Options chain, Greeks | ~800 | High |
| Greeks Calculator | Black-Scholes, vol surface | ~600 | High |
| Options Rules | IV rank, skew, theta | ~1000 | Medium |
| Risk Stage | Delta/gamma hedging | ~500 | Medium |
| Expiration Handler | Roll management | ~400 | Medium |

**Total: ~3,300 lines - New development**

---

## Options-Specific Extensions {#options-extensions}

### 1. OptionsRawData Stage (NEW)

**Purpose:** Calculate Greeks and options-specific metrics

**Location:** `systems/options/rawdata.py`

**Key Methods:**
```python
class OptionsRawData(RawData):
    def daily_delta(self, option_code) -> pd.Series:
        """Delta of option position"""

    def daily_gamma(self, option_code) -> pd.Series:
        """Gamma of option position"""

    def daily_vega(self, option_code) -> pd.Series:
        """Vega of option position"""

    def daily_theta(self, option_code) -> pd.Series:
        """Theta decay"""

    def daily_implied_vol(self, option_code) -> pd.Series:
        """Implied volatility"""

    def iv_rank(self, underlying_code, window=252) -> pd.Series:
        """IV rank over window"""

    def iv_percentile(self, underlying_code, window=252) -> pd.Series:
        """IV percentile over window"""

    def put_call_skew(self, underlying_code, days_to_exp=30, delta=0.25) -> pd.Series:
        """Measure skew between puts and calls"""

    def term_structure(self, underlying_code) -> pd.DataFrame:
        """Volatility term structure"""
```

**Base on:** `/systems/rawdata.py`

---

### 2. Options Trading Rules (NEW)

**Purpose:** Options-specific signal generation

**Location:** `systems/provided/options_rules/`

**Rules to Implement:**

#### A. Volatility-Based Rules
```python
def iv_rank_signal(iv_rank, high_threshold=80, low_threshold=20):
    """
    Signal based on IV rank
    - Sell premium when IV rank > high_threshold
    - Buy premium when IV rank < low_threshold
    """

def iv_expansion_signal(iv, vol_lookback=30):
    """
    Trend following on IV itself
    Uses EWMAC-style crossover on IV
    """

def mean_reversion_iv(iv, z_score_window=60, entry_threshold=2.0):
    """
    Mean reversion when IV deviates from historical mean
    """
```

#### B. Trend-Following Rules (Directional Options)
```python
def delta_adjusted_ewmac(underlying_price, vol, delta, Lfast=16, Lslow=64):
    """
    EWMAC signal adjusted for option delta
    """

def breakout_with_iv_filter(price, lookback=40, iv_rank=None, min_iv_rank=50):
    """
    Breakout strategy that only trades when IV is elevated
    """
```

#### C. Skew/Structure Rules
```python
def put_call_skew_signal(skew, entry_threshold=0.1):
    """
    Trade based on put/call skew anomalies
    """

def term_structure_signal(term_structure):
    """
    Trade based on volatility term structure shape
    (contango vs backwardation)
    """
```

#### D. Greeks-Based Rules
```python
def theta_decay_signal(theta, delta, min_theta_per_delta=0.05):
    """
    Signal for theta harvesting strategies
    Positive when theta/delta ratio is favorable
    """

def gamma_scalping_signal(gamma, realized_vol, implied_vol):
    """
    Signal for gamma scalping
    Positive when realized > implied
    """
```

---

### 3. OptionsPositionSizing Stage (MODIFIED)

**Purpose:** Size positions based on Greeks rather than price volatility

**Location:** `systems/options/positionsizing.py`

**Key Methods:**
```python
class OptionsPositionSizing(PositionSizing):
    def get_subsystem_position(self, option_code):
        """
        Override to use delta-adjusted sizing
        Position = (Target $ Risk / Delta / Price / Contract Multiplier)
        """

    def get_delta_adjusted_exposure(self, option_code):
        """
        Calculate notional exposure accounting for delta
        """

    def get_vega_exposure(self, option_code):
        """
        Calculate vega exposure for vol trading strategies
        """

    def get_gamma_risk(self, option_code):
        """
        Calculate gamma risk for risk management
        """

    def get_max_theta_exposure(self):
        """
        Limit total theta exposure across portfolio
        """
```

**Base on:** `/systems/positionsizing.py`

---

### 4. OptionsRisk Stage (NEW)

**Purpose:** Manage portfolio-level Greeks and hedging

**Location:** `systems/options/risk.py`

**Key Methods:**
```python
class OptionsRisk(SystemStage):
    @property
    def name(self):
        return "optionsRisk"

    def portfolio_delta(self) -> pd.Series:
        """Aggregate delta across all positions"""

    def portfolio_gamma(self) -> pd.Series:
        """Aggregate gamma across all positions"""

    def portfolio_vega(self) -> pd.Series:
        """Aggregate vega across all positions"""

    def portfolio_theta(self) -> pd.Series:
        """Aggregate theta across all positions"""

    def delta_hedging_trades(self) -> dict:
        """
        Calculate hedge trades needed to neutralize delta
        Returns dict of {instrument: hedge_quantity}
        """

    def get_hedged_positions(self) -> dict:
        """
        Get positions including dynamic hedges
        """
```

---

### 5. OptionsAccount Stage (MODIFIED)

**Purpose:** P&L calculation with options-specific costs

**Location:** `systems/options/accounts.py`

**Key Modifications:**
```python
class OptionsAccount(Account):
    def _calculate_option_costs(self, option_code, trades):
        """
        Options have different cost structure:
        - Wider bid/ask spreads (% of premium)
        - Commissions per contract
        - Assignment/exercise fees
        - Pin risk adjustment
        """

    def greeks_over_time(self) -> pd.DataFrame:
        """
        Track portfolio Greeks over time
        Returns DataFrame with delta, gamma, vega, theta columns
        """

    def theta_pnl_attribution(self) -> pd.Series:
        """
        P&L attributed to theta decay
        """

    def gamma_pnl_attribution(self) -> pd.Series:
        """
        P&L attributed to gamma scalping
        """

    def vega_pnl_attribution(self) -> pd.Series:
        """
        P&L attributed to volatility changes
        """
```

**Base on:** `/systems/accounts/accounts_stage.py`

---

### 6. Data Classes (NEW)

**Purpose:** Options-specific data objects

**Location:** `sysobjects/options/`

**Classes to Create:**

```python
class optionContract:
    """
    Represents a single option contract
    Attributes: underlying, strike, expiry, right (call/put), multiplier
    """

class optionChain:
    """
    Represents full options chain for an underlying at a date
    Methods: get_by_delta(), get_atm(), get_by_strike()
    """

class optionGreeks:
    """
    Container for Greeks
    Attributes: delta, gamma, vega, theta, rho
    """

class optionPrices:
    """
    Option price data with bid/ask/mid
    """
```

**Base on:** `/sysobjects/instruments.py`, `/sysobjects/adjusted_prices.py`

---

## Implementation Roadmap {#implementation-roadmap}

### Phase 1: Core Infrastructure (Week 1-2)

**Goal:** Set up base system that can run a simple backtest

**Tasks:**
1. ✅ Extract and adapt System/Stage architecture
   - Copy `/systems/basesystem.py`
   - Copy `/systems/stage.py`
   - Copy `/systems/system_cache.py`

2. ✅ Extract configuration system
   - Copy `/sysdata/config/configdata.py`
   - Copy config defaults structure

3. ✅ Extract utilities
   - Copy `/syscore/*` utilities
   - Copy `/syslogging/*` logging

4. ✅ Set up project structure
   - Create directory structure (see File Structure section)
   - Set up dependencies

5. ⚠️ Create basic data layer
   - Create `optionsSimData` base class
   - Implement CSV data loader for options
   - Define data schema (see Data Requirements)

**Deliverable:** Can instantiate System with empty stages and load options data

---

### Phase 2: Data & Greeks (Week 3-4)

**Goal:** Calculate Greeks and options metrics

**Tasks:**
1. ⚠️ Implement Greeks calculation
   - Black-Scholes model
   - Handle American options (binomial tree or approximation)
   - Vol surface interpolation

2. ⚠️ Create OptionsRawData stage
   - Implement all Greeks methods
   - IV rank/percentile calculation
   - Skew calculation

3. ⚠️ Create options data objects
   - `optionContract`
   - `optionChain`
   - `optionGreeks`

4. ✅ Unit tests for Greeks
   - Validate against known values
   - Test edge cases (deep ITM/OTM)

**Deliverable:** System can calculate and cache all Greeks for options chain

---

### Phase 3: Signal Generation (Week 5-6)

**Goal:** Implement options trading rules

**Tasks:**
1. ✅ Extract TradingRule framework
   - Copy `/systems/trading_rules.py`
   - Copy `/systems/forecasting.py`

2. ⚠️ Implement basic options rules
   - IV rank signal
   - IV mean reversion
   - Delta-adjusted EWMAC

3. ⚠️ Implement forecast scaling/capping
   - Extract `/systems/forecast_scale_cap.py`
   - Adapt for options if needed

4. ⚠️ Implement forecast combination
   - Extract `/systems/forecast_combine.py`

5. ✅ Test signal generation
   - Verify signals make sense
   - Check correlation between rules

**Deliverable:** System generates forecasts for options strategies

---

### Phase 4: Position Sizing (Week 7-8)

**Goal:** Size positions using Greeks

**Tasks:**
1. ⚠️ Create OptionsPositionSizing stage
   - Inherit from PositionSizing
   - Implement delta-adjusted sizing
   - Implement vega-based sizing for vol strategies

2. ⚠️ Add position constraints
   - Max Greeks per position
   - Max notional exposure
   - Handle expiration rollovers

3. ⚠️ Implement buffering
   - Extract buffering logic
   - Adapt for options (wider buffers due to illiquidity)

4. ✅ Test position sizing
   - Verify Greeks-based exposure matches targets
   - Test edge cases (deep ITM)

**Deliverable:** System sizes options positions appropriately

---

### Phase 5: Portfolio & Risk (Week 9-10)

**Goal:** Portfolio construction and Greeks aggregation

**Tasks:**
1. ⚠️ Extract and adapt Portfolio stage
   - Copy `/systems/portfolio.py`
   - Modify for delta-adjusted weights
   - Add Greeks aggregation

2. ⚠️ Create OptionsRisk stage
   - Portfolio Greeks calculation
   - Risk limits checking
   - Delta hedging logic (optional)

3. ⚠️ Add correlation estimation
   - Extract `/sysquant/estimators/correlations.py`
   - Use delta-adjusted returns for correlation

4. ⚠️ Test portfolio construction
   - Verify weights sum to 1
   - Check portfolio Greeks

**Deliverable:** System constructs multi-strategy options portfolio with risk management

---

### Phase 6: P&L & Performance (Week 11-12)

**Goal:** Calculate P&L and performance metrics

**Tasks:**
1. ⚠️ Extract and adapt Account stage
   - Copy `/systems/accounts/*`
   - Modify cost models for options
   - Add Greeks tracking

2. ⚠️ Implement options cost model
   - Bid/ask spreads (function of premium)
   - Per-contract commissions
   - Assignment costs

3. ⚠️ Add performance attribution
   - Theta P&L
   - Gamma P&L
   - Vega P&L
   - Delta P&L

4. ⚠️ Extract performance analytics
   - Copy `/systems/accounts/curves/`
   - Add options-specific metrics

5. ✅ Test P&L calculation
   - Verify against manual calculation
   - Check Greeks P&L attribution adds up

**Deliverable:** System calculates accurate P&L with full performance analytics

---

### Phase 7: Strategy Examples & Testing (Week 13-14)

**Goal:** Create example strategies and comprehensive tests

**Tasks:**
1. ⚠️ Create example strategies
   - Iron Condor (premium selling)
   - Covered call (yield enhancement)
   - Straddle (long vol)
   - Call/put spreads (directional)

2. ⚠️ Create pre-built systems
   - Similar to `/systems/provided/futures_chapter15/`
   - Document configuration options

3. ⚠️ Integration tests
   - End-to-end backtest
   - Compare results with manual calculations

4. ⚠️ Documentation
   - API documentation
   - Example notebooks
   - Configuration guide

**Deliverable:** Fully functional options backtesting platform with examples

---

### Phase 8: Advanced Features (Week 15+)

**Goal:** Add advanced capabilities

**Tasks:**
1. ⚠️ Dynamic hedging
   - Implement delta-hedging strategy
   - Gamma hedging

2. ⚠️ Optimization
   - Extract `/sysquant/optimisation/`
   - Adapt for options portfolios

3. ⚠️ Vol surface modeling
   - Implement SVI or similar
   - Arbitrage-free interpolation

4. ⚠️ Advanced rules
   - Calendar spreads
   - Volatility arbitrage
   - Dispersion trading

5. ⚠️ Live trading support (optional)
   - Order generation
   - Execution simulation
   - Broker integration

**Deliverable:** Production-ready platform with advanced features

---

## File Structure {#file-structure}

```
options_backtester/
│
├── systems/
│   ├── basesystem.py              # [EXTRACTED] System orchestrator
│   ├── stage.py                   # [EXTRACTED] SystemStage base
│   ├── system_cache.py            # [EXTRACTED] Caching
│   ├── trading_rules.py           # [EXTRACTED] TradingRule class
│   ├── forecasting.py             # [EXTRACTED] Rules stage
│   ├── forecast_scale_cap.py      # [EXTRACTED] Scaling/capping
│   ├── forecast_combine.py        # [EXTRACTED] Rule combination
│   ├── positionsizing.py          # [EXTRACTED] Base position sizing
│   ├── portfolio.py               # [ADAPTED] Portfolio construction
│   ├── buffering.py               # [EXTRACTED] Position buffering
│   │
│   ├── options/                   # [NEW] Options-specific stages
│   │   ├── __init__.py
│   │   ├── rawdata.py             # OptionsRawData stage
│   │   ├── positionsizing.py      # OptionsPositionSizing stage
│   │   ├── risk.py                # OptionsRisk stage
│   │   └── accounts.py            # OptionsAccount stage
│   │
│   ├── accounts/                  # [ADAPTED] P&L calculation
│   │   ├── accounts_stage.py
│   │   ├── curves/
│   │   │   ├── account_curve.py
│   │   │   └── stats_dict.py
│   │   └── pandl_calculators/
│   │       └── pandl_generic_costs.py
│   │
│   └── provided/                  # [MIXED] Pre-built systems & rules
│       ├── options_rules/         # [NEW] Options rules library
│       │   ├── iv_signals.py
│       │   ├── skew_signals.py
│       │   ├── greeks_signals.py
│       │   └── directional.py
│       │
│       └── example_systems/       # [NEW] Example strategies
│           ├── iron_condor.py
│           ├── covered_call.py
│           └── vol_trading.py
│
├── sysdata/
│   ├── base_data.py               # [EXTRACTED] Base data interface
│   ├── sim/
│   │   └── sim_data.py            # [EXTRACTED] Simulation data base
│   │
│   ├── options/                   # [NEW] Options data layer
│   │   ├── __init__.py
│   │   ├── options_sim_data.py    # optionsSimData base class
│   │   ├── csv_options_data.py    # CSV data loader
│   │   └── options_data_api.py    # API data loader (future)
│   │
│   └── config/                    # [EXTRACTED] Configuration
│       ├── configdata.py
│       ├── defaults.py
│       └── fill_config_dict_with_defaults.py
│
├── sysobjects/
│   ├── options/                   # [NEW] Options domain objects
│   │   ├── __init__.py
│   │   ├── contract.py            # optionContract
│   │   ├── chain.py               # optionChain
│   │   ├── greeks.py              # optionGreeks
│   │   └── prices.py              # optionPrices
│   │
│   └── instruments.py             # [EXTRACTED] Base instrument class
│
├── sysquant/
│   ├── estimators/                # [EXTRACTED] Quantitative estimators
│   │   ├── vol.py
│   │   ├── correlations.py
│   │   └── covariance.py
│   │
│   ├── optimisation/              # [EXTRACTED] Portfolio optimization
│   │   ├── weights.py
│   │   └── portfolio_optimiser.py
│   │
│   └── options/                   # [NEW] Options quant tools
│       ├── __init__.py
│       ├── black_scholes.py       # BS model & Greeks
│       ├── vol_surface.py         # Vol surface interpolation
│       └── american_options.py    # American options pricing
│
├── syscore/                       # [EXTRACTED] Core utilities
│   ├── objects.py
│   ├── genutils.py
│   ├── exceptions.py
│   ├── constants.py
│   ├── dateutils.py
│   ├── fileutils.py
│   └── pandas/
│       ├── pdutils.py
│       ├── strategy_functions.py
│       └── frequency.py
│
├── syslogging/                    # [EXTRACTED] Logging framework
│   ├── logger.py
│   └── logger_utils.py
│
├── examples/                      # [NEW] Example notebooks & scripts
│   ├── notebooks/
│   │   ├── 01_basic_options_backtest.ipynb
│   │   ├── 02_iv_rank_strategy.ipynb
│   │   ├── 03_covered_call.ipynb
│   │   └── 04_iron_condor.ipynb
│   │
│   └── scripts/
│       ├── simple_strategy.py
│       └── multi_strategy_portfolio.py
│
├── data/                          # Sample data
│   ├── options_prices/
│   │   └── SPY_options.csv
│   ├── underlying_prices/
│   │   └── SPY_prices.csv
│   └── vol_surface/
│       └── SPY_iv_surface.csv
│
├── tests/                         # Test suite
│   ├── test_greeks.py
│   ├── test_rules.py
│   ├── test_position_sizing.py
│   └── test_pnl.py
│
├── docs/                          # Documentation
│   ├── api/
│   ├── user_guide/
│   └── examples/
│
├── configs/                       # Example configurations
│   ├── simple_iv_rank.yaml
│   ├── iron_condor.yaml
│   └── covered_call.yaml
│
├── requirements.txt               # Python dependencies
├── setup.py                       # Package setup
└── README.md                      # Main documentation
```

---

## Data Requirements {#data-requirements}

### Required Data for Options Backtesting

#### 1. Options Price Data

**CSV Format:** `data/options_prices/{UNDERLYING}_options.csv`

```csv
date,underlying,strike,expiry,right,bid,ask,mid,volume,open_interest
2020-01-02,SPY,320.0,2020-01-17,C,5.20,5.30,5.25,1250,5430
2020-01-02,SPY,320.0,2020-01-17,P,2.10,2.15,2.125,890,3210
2020-01-02,SPY,325.0,2020-01-17,C,3.10,3.20,3.15,980,4120
...
```

**Required Fields:**
- `date` - Trading date
- `underlying` - Underlying symbol
- `strike` - Strike price
- `expiry` - Option expiration date
- `right` - 'C' for Call, 'P' for Put
- `bid` - Bid price
- `ask` - Ask price
- `mid` - Mid price (or calculated as (bid+ask)/2)
- `volume` - Trading volume (optional, for filtering)
- `open_interest` - Open interest (optional, for filtering)

#### 2. Underlying Price Data

**CSV Format:** `data/underlying_prices/{UNDERLYING}_prices.csv`

```csv
date,open,high,low,close,volume
2020-01-02,320.50,322.10,319.80,321.45,95234567
2020-01-03,321.50,323.20,321.00,322.95,87654321
...
```

**Required Fields:**
- `date` - Trading date
- `close` - Closing price (minimum requirement)
- `open`, `high`, `low` - Optional but useful
- `volume` - Optional

#### 3. Implied Volatility Data (Optional but Recommended)

**CSV Format:** `data/vol_surface/{UNDERLYING}_iv_surface.csv`

```csv
date,expiry,delta,strike,implied_vol
2020-01-02,2020-01-17,0.25,315.0,0.145
2020-01-02,2020-01-17,0.50,320.0,0.125
2020-01-02,2020-01-17,0.75,325.0,0.115
2020-01-02,2020-02-21,0.25,314.0,0.155
...
```

**Required Fields:**
- `date` - Trading date
- `expiry` - Option expiration
- `delta` - Option delta (for organizing surface)
- `strike` - Strike price
- `implied_vol` - Implied volatility (annualized)

**Alternative:** Calculate IV from option prices using Black-Scholes

#### 4. Interest Rates (Optional)

**CSV Format:** `data/interest_rates/rates.csv`

```csv
date,rate
2020-01-02,0.0175
2020-01-03,0.0175
...
```

**Note:** If not provided, can use constant rate from config

#### 5. Dividends (Optional but Important for Equity Options)

**CSV Format:** `data/dividends/{UNDERLYING}_dividends.csv`

```csv
ex_date,amount
2020-03-15,1.25
2020-06-15,1.30
...
```

### Data Loader Implementation

```python
class csvOptionsSimData(optionsSimData):
    def __init__(self,
                 options_price_dir="data/options_prices",
                 underlying_price_dir="data/underlying_prices",
                 vol_surface_dir="data/vol_surface"):
        self.options_price_dir = options_price_dir
        self.underlying_price_dir = underlying_price_dir
        self.vol_surface_dir = vol_surface_dir

    def get_option_chain(self, underlying, date):
        """Load full options chain for underlying at date"""

    def get_option_price(self, option_code, start_date, end_date):
        """Load price series for specific option"""

    def get_underlying_price(self, underlying, start_date, end_date):
        """Load underlying price series"""

    def get_implied_vol(self, option_code, start_date, end_date):
        """Load or calculate IV series"""

    def get_vol_surface(self, underlying, date):
        """Load volatility surface"""
```

---

## Quick Start Guide {#quick-start}

### Installation

```bash
# Clone repository
git clone <repo_url>
cd options_backtester

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Dependencies

```
# requirements.txt
pandas>=1.3.0
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.4.0
seaborn>=0.11.0
PyYAML>=5.4.0
pytest>=6.2.0
jupyter>=1.0.0
```

### Minimal Example

```python
# examples/simple_strategy.py

from systems.basesystem import System
from systems.options.rawdata import OptionsRawData
from systems.forecasting import Rules
from systems.forecast_scale_cap import ForecastScaleCap
from systems.forecast_combine import ForecastCombine
from systems.options.positionsizing import OptionsPositionSizing
from systems.portfolio import Portfolios
from systems.options.accounts import OptionsAccount

from sysdata.config.configdata import Config
from sysdata.options.csv_options_data import csvOptionsSimData

# Load data
data = csvOptionsSimData()

# Load configuration
config = Config("configs/simple_iv_rank.yaml")

# Build system
system = System(
    stage_list=[
        OptionsRawData(),
        Rules(),
        ForecastScaleCap(),
        ForecastCombine(),
        OptionsPositionSizing(),
        Portfolios(),
        OptionsAccount()
    ],
    data=data,
    config=config
)

# Run backtest
positions = system.portfolio.get_actual_position("SPY_C_320_2020-01-17")
pnl = system.accounts.portfolio()
stats = pnl.stats()

print(stats)
```

### Example Configuration

```yaml
# configs/simple_iv_rank.yaml

# Instruments (options)
instruments:
  - SPY_OPTIONS
  - QQQ_OPTIONS

# Trading rules
trading_rules:
  iv_rank_high:
    function: systems.provided.options_rules.iv_signals.sell_high_iv_rank
    other_args:
      high_threshold: 80
      window: 252

  iv_rank_low:
    function: systems.provided.options_rules.iv_signals.buy_low_iv_rank
    other_args:
      low_threshold: 20
      window: 252

# Forecast combination
forecast_weights:
  iv_rank_high: 0.5
  iv_rank_low: 0.5

forecast_div_multiplier: 1.0

# Position sizing
percentage_vol_target: 20.0
notional_trading_capital: 100000
base_currency: USD

# Options-specific
max_delta_per_position: 0.50
max_vega_per_position: 50.0
max_theta_per_day: -100.0

# Costs
options_bid_ask_spread_pct: 0.05  # 5% of premium
commission_per_contract: 0.65
```

---

## Key Differences from Futures System

### 1. Data Complexity
- **Futures:** Single price series per instrument
- **Options:** Entire chain (multiple strikes/expirations) per underlying

### 2. Position Sizing
- **Futures:** Volatility-based (forecast / volatility)
- **Options:** Greeks-based (delta-adjusted notional)

### 3. Risk Management
- **Futures:** Single volatility metric
- **Options:** Delta, gamma, vega, theta

### 4. Costs
- **Futures:** Fixed per-contract + spread
- **Options:** % of premium + per-contract + wider spreads

### 5. Expiration
- **Futures:** Roll management
- **Options:** Expiration requires closing or rolling positions

### 6. Signals
- **Futures:** Price-based (trend, breakout, carry)
- **Options:** IV-based, skew-based, Greeks-based + directional

---

## Summary Statistics

### Code Reuse Breakdown

| Category | Lines of Code | Reuse % | Effort |
|----------|---------------|---------|--------|
| **Direct Reuse** | 4,700 | 100% | Minimal |
| **Adaptation** | 5,100 | 60% | Medium |
| **New Development** | 3,300 | 0% | High |
| **Total** | **13,100** | **~70%** | **~14 weeks** |

### Component Status

| Component | Status | Priority | Week |
|-----------|--------|----------|------|
| System/Stage | ✅ Extract | Critical | 1 |
| Config | ✅ Extract | Critical | 1 |
| Utilities | ✅ Extract | High | 1 |
| Data Layer | ⚠️ Adapt | Critical | 2 |
| Greeks Calc | ⚠️ New | Critical | 3 |
| RawData Stage | ⚠️ New | Critical | 4 |
| Trading Rules | ⚠️ New | High | 5-6 |
| Position Sizing | ⚠️ Adapt | High | 7-8 |
| Portfolio | ⚠️ Adapt | High | 9-10 |
| Accounts | ⚠️ Adapt | High | 11-12 |
| Examples | ⚠️ New | Medium | 13-14 |

### Expected Outcomes

**After Phase 7 (Week 14):**
- ✅ Fully functional options backtesting platform
- ✅ Support for IV-based, directional, and Greeks-based strategies
- ✅ Portfolio construction with risk management
- ✅ Comprehensive performance analytics
- ✅ Example strategies and documentation

**Advanced Features (Week 15+):**
- Dynamic hedging
- Portfolio optimization
- Advanced vol surface modeling
- Live trading support

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Set up development environment**
3. **Start Phase 1** - Extract core infrastructure
4. **Define data schema** in detail
5. **Create GitHub repository** for project

---

## Questions to Resolve

1. **Data Source:** Where will options data come from?
   - Historical data provider (paid)
   - Free sources (limited)
   - Own data collection

2. **Options Types:**
   - Start with European or American?
   - Equity options only or include futures options?

3. **Greeks Calculation:**
   - Use Black-Scholes or more sophisticated model?
   - Calculate or use provided Greeks?

4. **Hedging:**
   - Include dynamic hedging in Phase 1 or later?
   - Delta-neutral strategies from the start?

5. **Target Strategies:**
   - Priority: IV rank, covered calls, iron condors?
   - Directional or neutral first?

---

## Conclusion

This extraction plan provides a clear roadmap to build a sophisticated options backtesting platform leveraging 65-70% of the battle-tested pysystemtrade infrastructure. The modular architecture ensures:

- **Rapid development** through code reuse
- **Flexibility** to add new strategies
- **Robustness** from proven components
- **Extensibility** for future enhancements

The estimated 14-week timeline to a production-ready system is aggressive but achievable given the high code reuse and clear architecture.

**Ready to start extracting!**
