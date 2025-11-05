# pysystemtrade Repository Architecture Analysis

## Documentation Index

This comprehensive analysis of the pysystemtrade repository has been organized into two documents:

### 1. ARCHITECTURE_SUMMARY.md (Quick Reference - 8 min read)
**Start here for a quick understanding of the system**

- Repository overview and architecture at a glance
- The 7 core processing stages explained
- Key design patterns and why they matter
- Quick start workflow
- Configuration examples
- Pre-baked systems overview
- Reusability assessment for options platforms

**Use this when:** You want the "big picture" and key components explained quickly

**File:** `/home/user/ARCHITECTURE_SUMMARY.md`

---

### 2. pysystemtrade_architecture_analysis.md (Deep Dive - 25 min read)
**Comprehensive technical reference with code examples**

**Sections:**
1. Complete repository structure (all 16 modules)
2. Core backtesting architecture with code
3. Data handling architecture (3-layer model)
4. Signal generation & trading rules framework
5. Position sizing & risk management
6. Performance analytics & P&L calculation
7. System caching mechanism
8. Configuration & pre-baked systems
9. Quantitative components (estimators, optimization)
10. Production system components
11. Key design patterns explained
12. Main entry points for backtesting
13. Component reusability assessment for options platforms
14. Key files reference table
15. Typical backtest workflow
16. Extensibility examples

**Use this when:** You need implementation details, code examples, and understanding of each component

**File:** `/home/user/pysystemtrade_architecture_analysis.md`

---

## Quick Navigation Guide

### I want to understand...

**...the overall system architecture**
→ Read: ARCHITECTURE_SUMMARY.md, sections "Architecture at a Glance" and "The 7 Core Processing Stages"

**...how to run a backtest**
→ Read: ARCHITECTURE_SUMMARY.md section "Quick Start Workflow"  
→ Or: pysystemtrade_architecture_analysis.md section 12 "Main Entry Points"

**...the data pipeline**
→ Read: ARCHITECTURE_SUMMARY.md section "Data Pipeline Flow"  
→ Or: pysystemtrade_architecture_analysis.md section 3 "Data Handling Architecture"

**...the trading rules system**
→ Read: pysystemtrade_architecture_analysis.md section 4 "Signal Generation & Trading Rules Framework"

**...how P&L is calculated**
→ Read: pysystemtrade_architecture_analysis.md section 6 "Performance Analytics & P&L Calculation"

**...what's reusable for options**
→ Read: ARCHITECTURE_SUMMARY.md section "For Options Strategies Platform"  
→ Or: pysystemtrade_architecture_analysis.md section 13 "Component Reusability for Options Strategies Platform"

**...configuration examples**
→ Read: ARCHITECTURE_SUMMARY.md section "Configuration Example"  
→ Or: pysystemtrade_architecture_analysis.md section 8 "Configuration & Pre-baked Systems"

**...specific modules**
→ Read: pysystemtrade_architecture_analysis.md section 14 "Key Files Reference Table"

**...design patterns**
→ Read: ARCHITECTURE_SUMMARY.md section "Why This Architecture is Brilliant"  
→ Or: pysystemtrade_architecture_analysis.md section 11 "Key Design Patterns"

**...code examples**
→ Read: pysystemtrade_architecture_analysis.md sections 12-16 for code samples

---

## Key Takeaways

### Architecture Philosophy
pysystemtrade uses a **stage pipeline architecture** where:
- System is composed of discrete SystemStage objects
- Each stage has clearly defined inputs/outputs
- Stages are independent and testable
- Configuration-driven (zero code changes for most variations)
- Intelligent caching for performance

### The 7 Core Stages
1. **RawData** - Calculate volatility, prepare prices
2. **Rules** - Execute trading rules
3. **ForecastScaleCap** - Scale and cap forecasts
4. **ForecastCombine** - Combine rules with weights
5. **PositionSizing** - Convert forecast to contracts
6. **Portfolio** - Apply instrument weights
7. **Account** - Calculate P&L and statistics

### Design Strengths
- Modular and extensible
- Configuration-driven flexibility
- Rich performance analytics
- Multi-data-source support
- Production-ready
- Highly reusable framework

### Reusability for Options
- 60-70% directly reusable
- Minimal modifications needed for Greeks-based sizing
- Core architecture is asset-class agnostic
- P&L, portfolio, and quantitative components readily adaptable

---

## Repository Stats

- **Total Python Files:** ~592
- **Main Modules:** 16
- **Core Backtesting Files:** ~80
- **Data Abstraction Layers:** 3
- **Pre-baked Systems:** 3+ complete examples
- **Trading Rules Library:** 8+ pre-built rules
- **Quantitative Tools:** 15+ estimators/optimizers
- **Lines of Code:** ~50,000+ (excluding tests)

---

## Module Quick Reference

### Core Engine (`/systems/`)
**Main entry point:** `basesystem.py` (System class)
**Processing pipeline:** `rawdata.py` → `forecasting.py` → `forecast_scale_cap.py` → `forecast_combine.py` → `positionsizing.py` → `portfolio.py` → `accounts/`

### Data Layer (`/sysdata/`)
**Configuration:** `config/configdata.py`
**Data interfaces:** `sim/sim_data.py`, `sim/futures_sim_data.py`
**Storage backends:** `csv/`, `mongodb/`, `arctic/`, `parquet/`

### Domain Objects (`/sysobjects/`)
Core data structures for instruments, prices, contracts, FX, etc.

### Quantitative (`/sysquant/`)
Statistical estimators, portfolio optimization, risk calculations

### Production (`/sysproduction/`, `/sysexecution/`, `/sysbrokers/`)
Live trading, order execution, Interactive Brokers integration

### Utilities (`/syscore/`, `/syslogging/`)
Core utilities, logging, pandas helpers

---

## How to Use These Documents

### For Project Overview
1. Start with ARCHITECTURE_SUMMARY.md
2. Read sections in order: Overview → Architecture → Stages → Use Cases
3. Refer to ARCHITECTURE_SUMMARY.md section "File Locations Reference" for code exploration

### For Implementation Details
1. Reference ARCHITECTURE_SUMMARY.md for section numbers in detailed guide
2. Read relevant section in pysystemtrade_architecture_analysis.md
3. Look at code examples provided
4. Cross-reference with "Key Files Reference Table" (section 14)

### For Code Exploration
1. Use ARCHITECTURE_SUMMARY.md "Module Breakdown" to locate files
2. Use pysystemtrade_architecture_analysis.md "Key Files Reference Table" for line counts
3. Read detailed explanations in appropriate sections
4. Examples provided show typical usage patterns

### For Extension/Customization
1. Read section 11 "Key Design Patterns" to understand approach
2. Review section 15 "Typical Backtest Workflow" 
3. Study section 16 "Extensibility Examples"
4. Reference pre-baked systems in `/systems/provided/` as templates

---

## Document Statistics

| Document | Size | Lines | Read Time |
|----------|------|-------|-----------|
| ARCHITECTURE_SUMMARY.md | 12 KB | 416 | 8-10 min |
| pysystemtrade_architecture_analysis.md | 35 KB | 1074 | 20-30 min |
| **Total** | **47 KB** | **1490** | **30-40 min** |

---

## Repository Information

- **Repository:** https://github.com/robcarver17/pysystemtrade
- **Version Analyzed:** 1.8.2 (November 2024)
- **Author:** Rob Carver
- **License:** GNU v3
- **Production Status:** Active (used for live trading)
- **Language:** Python 3
- **Key Dependencies:** Pandas, NumPy, MongoDB, Arctic, IB-insync

---

## Analysis Methodology

This analysis was conducted through:
1. Complete directory structure exploration
2. Core file examination (System, SystemStage, Config classes)
3. Pipeline stage analysis (all 8+ stages)
4. Data layer documentation
5. Configuration system review
6. Trading rules framework analysis
7. P&L and performance analytics study
8. Design pattern identification
9. Reusability assessment for options platforms
10. Code example extraction from real files

Total files examined: ~150+
Documentation depth: Comprehensive with code examples

---

## Next Steps

### To Understand the System
1. Read ARCHITECTURE_SUMMARY.md completely
2. Pick one section from pysystemtrade_architecture_analysis.md that interests you
3. Run a simple backtest using the quick start guide
4. Explore the pre-baked systems in `/systems/provided/`

### To Customize
1. Copy pre-baked system as template
2. Modify config YAML or Python dict
3. Run backtest to see results
4. Iterate on parameters

### To Extend
1. Create custom SystemStage inheriting from base
2. Implement required methods
3. Add to System's stage_list
4. Update config with new parameters
5. Reference section 16 "Extensibility Examples"

### For Options Adaptation
1. Review section 13 "Component Reusability for Options Strategies Platform"
2. Identify which stages need modification
3. Review section 15 "Typical Backtest Workflow" to understand flow
4. Adapt RawData stage for Greeks
5. Extend PositionSizing for Greeks-based sizing
6. Adapt cost models for options
7. Extend Risk stage for Greeks hedging

---

## Document Versions

**Analysis Date:** November 5, 2024
**Repository State:** Commit ff41385 (small changes to algo)
**Branch:** claude/extract-trend-following-backtester-011CUpMGaE92ewucNm87aQ83

---

## Questions & Clarifications

These documents answer:
- What does pysystemtrade do?
- How is it architectured?
- What are the main components?
- How do you run a backtest?
- What's the data pipeline?
- How is risk/P&L calculated?
- What can be reused for options?
- Where is each component located?
- How extensible is the framework?
- What design patterns are used?

---

## Support Documentation Links

Within the repository:
- `/docs/introduction.md` - Getting started guide
- `/docs/backtesting.md` - Comprehensive backtesting guide
- `/docs/data.md` - Data handling details
- `/docs/production.md` - Production trading setup
- `/examples/` - Working code examples

Outside (author's resources):
- https://qoppac.blogspot.com/ - Author's technical blog
- https://www.systematicmoney.org/ - Systematic trading framework
- "Systematic Trading" book - Complete framework explanation

---

**Ready to explore pysystemtrade? Start with ARCHITECTURE_SUMMARY.md!**

