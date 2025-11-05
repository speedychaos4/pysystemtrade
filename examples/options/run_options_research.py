"""Run an options research workflow using the pysystemtrade staging framework.

This script provides a reusable entry point for experimenting with option trend
following and reversal strategies.  It demonstrates how to adapt the existing
system stages to an options dataset and produce a compact research report.

Expected CSV schema
-------------------
The workflow expects a tidy CSV file containing at least the following
columns (additional fields will be used if present):

```
    date              - ISO formatted date of the observation
    instrument        - Instrument identifier (e.g. SPX_20231215_C04000)
    option_price      - Mark or settlement premium per option contract
    underlying_price  - Price of the underlying asset
    implied_vol       - Annualised implied volatility (as a decimal)

Optional columns:
    delta, gamma, vega, theta, realized_vol
```

The script aggregates data per instrument and exposes analysis functions over
`pandas.Series` so researchers can plug their own data sources in by exporting
CSV files with the described schema.

Example usage
-------------
```
python examples/options/run_options_research.py \
    --data-path data/options_demo.csv \
    --base-currency USD \
    --fast-window 5 --slow-window 21 --vol-window 30
```
"""
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence

import numpy as np
import pandas as pd

from sysdata.config.configdata import Config
from sysdata.sim.sim_data import simData
from systems.basesystem import System
from systems.stage import SystemStage


@dataclass(frozen=True)
class OptionInstrumentMeta:
    """Metadata describing an option contract used by the workflow."""

    instrument: str
    underlying: str
    expiry: Optional[pd.Timestamp]
    strike: Optional[float]
    option_type: Optional[str]
    multiplier: float = 1.0
    currency: str = "USD"


class OptionsCSVData(simData):
    """Load option chain observations from a CSV file.

    The loader keeps an in-memory dictionary of per-instrument data frames.  All
    public accessors return copies to ensure that calling code cannot mutate the
    original cache and accidentally poison other experiments.
    """

    def __init__(
        self,
        csv_path: Path,
        base_currency: str = "USD",
        start_date: Optional[pd.Timestamp] = None,
        end_date: Optional[pd.Timestamp] = None,
        metadata_overrides: Optional[Mapping[str, Mapping[str, object]]] = None,
    ) -> None:
        super().__init__()
        self._base_currency = base_currency
        self._raw_frames: Dict[str, pd.DataFrame] = {}
        self._metadata: Dict[str, OptionInstrumentMeta] = {}
        self._load_from_csv(
            csv_path=csv_path,
            start_date=start_date,
            end_date=end_date,
            metadata_overrides=metadata_overrides or {},
        )

    # ------------------------------------------------------------------
    # simData API
    def get_instrument_list(self) -> List[str]:
        return sorted(self._raw_frames.keys())

    def get_raw_price(self, instrument_code: str) -> pd.DataFrame:
        frame = self._raw_frames.get(instrument_code)
        if frame is None:
            raise KeyError(f"Unknown instrument '{instrument_code}'")
        series = frame["option_price"].copy()
        series.name = "option_price"
        return series.to_frame()

    def get_option_frame(self, instrument_code: str) -> pd.DataFrame:
        frame = self._raw_frames.get(instrument_code)
        if frame is None:
            raise KeyError(f"Unknown instrument '{instrument_code}'")
        return frame.copy()

    def get_underlying_price(self, instrument_code: str) -> pd.Series:
        frame = self.get_option_frame(instrument_code)
        series = frame["underlying_price"].copy()
        series.name = "underlying_price"
        return series

    def get_implied_vol(self, instrument_code: str) -> pd.Series:
        frame = self.get_option_frame(instrument_code)
        if "implied_vol" not in frame:
            raise KeyError("implied_vol column not found in data")
        series = frame["implied_vol"].copy()
        series.name = "implied_vol"
        return series

    def get_greek(self, instrument_code: str, greek: str) -> pd.Series:
        frame = self.get_option_frame(instrument_code)
        if greek not in frame:
            raise KeyError(f"{greek} column not found in data")
        series = frame[greek].copy()
        series.name = greek
        return series

    def get_realized_vol(self, instrument_code: str, window: int) -> pd.Series:
        frame = self.get_option_frame(instrument_code)
        if "realized_vol" in frame:
            realized = frame["realized_vol"].copy()
            realized.name = "realized_vol"
            return realized
        # Compute realised vol from underlying returns if not supplied
        underlying = frame["underlying_price"].pct_change()
        realized = underlying.rolling(window).std() * math.sqrt(252)
        realized.name = "realized_vol"
        return realized

    def get_fx_for_instrument(self, instrument_code: str, base_currency: str):
        # The demo loader assumes that all instruments are already denominated in
        # the base currency.  Returning a constant FX series keeps compatibility
        # with the parent class.
        index = self.get_option_frame(instrument_code).index
        fx_series = pd.Series(1.0, index=index, name=f"{instrument_code}_fx")
        return fx_series

    # ------------------------------------------------------------------
    # Helpers specific to this workflow
    def get_metadata(self, instrument_code: str) -> OptionInstrumentMeta:
        try:
            return self._metadata[instrument_code]
        except KeyError as exc:
            raise KeyError(f"Missing metadata for '{instrument_code}'") from exc

    def _load_from_csv(
        self,
        csv_path: Path,
        start_date: Optional[pd.Timestamp],
        end_date: Optional[pd.Timestamp],
        metadata_overrides: Mapping[str, Mapping[str, object]],
    ) -> None:
        frame = pd.read_csv(csv_path)
        if "date" not in frame.columns or "instrument" not in frame.columns:
            raise ValueError(
                "CSV must contain at least 'date' and 'instrument' columns"
            )

        frame["date"] = pd.to_datetime(frame["date"])
        frame = frame.sort_values(["instrument", "date"])  # stable ordering
        if start_date is not None:
            frame = frame[frame["date"] >= pd.Timestamp(start_date)]
        if end_date is not None:
            frame = frame[frame["date"] <= pd.Timestamp(end_date)]

        grouped = frame.groupby("instrument")
        for instrument, instrument_frame in grouped:
            instrument_frame = instrument_frame.set_index("date")
            instrument_frame = instrument_frame.asfreq("B").interpolate()
            self._raw_frames[instrument] = instrument_frame
            self._metadata[instrument] = self._derive_metadata(
                instrument, instrument_frame, metadata_overrides.get(instrument, {})
            )

    def _derive_metadata(
        self,
        instrument: str,
        frame: pd.DataFrame,
        overrides: Mapping[str, object],
    ) -> OptionInstrumentMeta:
        def _coerce_float(value: Optional[object]) -> Optional[float]:
            try:
                return float(value) if value is not None else None
            except (TypeError, ValueError):
                return None

        inferred = OptionInstrumentMeta(
            instrument=instrument,
            underlying=overrides.get("underlying", instrument.split("_")[0]),
            expiry=pd.to_datetime(overrides.get("expiry"))
            if overrides.get("expiry")
            else None,
            strike=_coerce_float(overrides.get("strike")),
            option_type=(overrides.get("option_type") or "").upper() or None,
            multiplier=float(overrides.get("multiplier", 1.0)),
            currency=str(overrides.get("currency", self._base_currency)),
        )
        return inferred


class OptionsFeatureEngineering(SystemStage):
    name = "features"

    def __init__(self, fast_window: int = 5, slow_window: int = 21, vol_window: int = 30) -> None:
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.vol_window = vol_window

    # ------------------------------------------------------------------
    def option_price(self, instrument: str) -> pd.Series:
        return self.parent.data.get_raw_price(instrument)["option_price"]

    def underlying_price(self, instrument: str) -> pd.Series:
        return self.parent.data.get_underlying_price(instrument)

    def implied_vol(self, instrument: str) -> pd.Series:
        return self.parent.data.get_implied_vol(instrument)

    def realized_vol(self, instrument: str) -> pd.Series:
        return self.parent.data.get_realized_vol(
            instrument_code=instrument, window=self.vol_window
        )

    def delta(self, instrument: str) -> Optional[pd.Series]:
        try:
            return self.parent.data.get_greek(instrument, "delta")
        except KeyError:
            return None

    def underlying_returns(self, instrument: str) -> pd.Series:
        return self.underlying_price(instrument).pct_change().fillna(0.0)

    def option_returns(self, instrument: str) -> pd.Series:
        return self.option_price(instrument).pct_change().fillna(0.0)

    def trend_indicator(self, instrument: str) -> pd.Series:
        prices = self.underlying_price(instrument)
        fast = prices.rolling(self.fast_window).mean()
        slow = prices.rolling(self.slow_window).mean()
        trend = fast - slow
        return trend.fillna(0.0)

    def volatility_spread(self, instrument: str) -> pd.Series:
        implied = self.implied_vol(instrument)
        realized = self.realized_vol(instrument)
        spread = implied - realized
        return spread.fillna(0.0)

    def zscore(self, series: pd.Series, window: int) -> pd.Series:
        rolling_mean = series.rolling(window).mean()
        rolling_std = series.rolling(window).std(ddof=0)
        zed = (series - rolling_mean) / rolling_std.replace(0, np.nan)
        return zed.fillna(0.0)


class OptionsForecastStage(SystemStage):
    name = "forecasts"

    def __init__(self, trend_weight: float = 0.6, reversal_weight: float = 0.4, z_window: int = 20) -> None:
        self.trend_weight = trend_weight
        self.reversal_weight = reversal_weight
        self.z_window = z_window

    # ------------------------------------------------------------------
    def _feature_stage(self) -> OptionsFeatureEngineering:
        return self.parent.features

    def trend_signal(self, instrument: str) -> pd.Series:
        trend = self._feature_stage().trend_indicator(instrument)
        return self._feature_stage().zscore(trend, self.z_window)

    def reversal_signal(self, instrument: str) -> pd.Series:
        spread = self._feature_stage().volatility_spread(instrument)
        return -self._feature_stage().zscore(spread, self.z_window)

    def composite_signal(self, instrument: str) -> pd.Series:
        trend = self.trend_signal(instrument)
        reversal = self.reversal_signal(instrument)
        weighted = self.trend_weight * trend + self.reversal_weight * reversal
        return weighted.clip(-3, 3)


class OptionsPositionSizingStage(SystemStage):
    name = "positions"

    def __init__(
        self,
        notional_per_instrument: float = 1_000_000.0,
        max_leverage: float = 5.0,
    ) -> None:
        self.notional_per_instrument = notional_per_instrument
        self.max_leverage = max_leverage

    # ------------------------------------------------------------------
    def _forecast_stage(self) -> OptionsForecastStage:
        return self.parent.forecasts

    def _feature_stage(self) -> OptionsFeatureEngineering:
        return self.parent.features

    def target_notional(self, instrument: str) -> pd.Series:
        signal = self._forecast_stage().composite_signal(instrument)
        target = signal / 3.0 * self.notional_per_instrument
        return target

    def option_contracts(self, instrument: str) -> pd.Series:
        target_notional = self.target_notional(instrument)
        prices = self._feature_stage().option_price(instrument)
        metadata = self.parent.data.get_metadata(instrument)
        # Avoid division by zero for illiquid contracts
        contracts = target_notional / (prices.replace(0, np.nan) * metadata.multiplier)
        contracts = contracts.clip(lower=-self.max_leverage, upper=self.max_leverage)
        return contracts.fillna(0.0)


class OptionsPortfolioStage(SystemStage):
    name = "portfolio"

    def _position_stage(self) -> OptionsPositionSizingStage:
        return self.parent.positions

    def _feature_stage(self) -> OptionsFeatureEngineering:
        return self.parent.features

    def daily_pnl(self, instrument: str) -> pd.Series:
        contracts = self._position_stage().option_contracts(instrument)
        prices = self._feature_stage().option_price(instrument)
        metadata = self.parent.data.get_metadata(instrument)
        returns = prices.diff().fillna(0.0)
        pnl = contracts.shift(1).fillna(0.0) * returns * metadata.multiplier
        pnl.name = f"{instrument}_pnl"
        return pnl

    def cumulative_pnl(self, instrument: str) -> pd.Series:
        return self.daily_pnl(instrument).cumsum()

    def portfolio_summary(self) -> pd.DataFrame:
        rows = []
        for instrument in self.parent.data.get_instrument_list():
            daily = self.daily_pnl(instrument)
            ann_pnl = daily.sum() * 252 / len(daily.index.unique())
            ann_vol = daily.std(ddof=0) * math.sqrt(252)
            sharpe = ann_pnl / ann_vol if ann_vol > 0 else 0.0
            rows.append(
                dict(
                    instrument=instrument,
                    total_pnl=daily.sum(),
                    annualised_pnl=ann_pnl,
                    annualised_vol=ann_vol,
                    sharpe=sharpe,
                )
            )
        return pd.DataFrame(rows).set_index("instrument")


def run_options_research_workflow(
    data_path: Path,
    base_currency: str = "USD",
    start_date: Optional[pd.Timestamp] = None,
    end_date: Optional[pd.Timestamp] = None,
    fast_window: int = 5,
    slow_window: int = 21,
    vol_window: int = 30,
    trend_weight: float = 0.6,
    reversal_weight: float = 0.4,
    z_window: int = 20,
    notional_per_instrument: float = 1_000_000.0,
    max_leverage: float = 5.0,
) -> Dict[str, object]:
    """Execute the full options research workflow and return diagnostics."""

    options_data = OptionsCSVData(
        csv_path=Path(data_path),
        base_currency=base_currency,
        start_date=start_date,
        end_date=end_date,
    )

    config = Config(dict(parameters=dict(base_currency=base_currency)))

    stages: Sequence[SystemStage] = [
        OptionsFeatureEngineering(
            fast_window=fast_window,
            slow_window=slow_window,
            vol_window=vol_window,
        ),
        OptionsForecastStage(
            trend_weight=trend_weight,
            reversal_weight=reversal_weight,
            z_window=z_window,
        ),
        OptionsPositionSizingStage(
            notional_per_instrument=notional_per_instrument,
            max_leverage=max_leverage,
        ),
        OptionsPortfolioStage(),
    ]

    system = System(stage_list=list(stages), data=options_data, config=config)

    instrument_summaries = system.portfolio.portfolio_summary()
    cumulative_curves = {
        instrument: system.portfolio.cumulative_pnl(instrument)
        for instrument in options_data.get_instrument_list()
    }

    return {
        "system": system,
        "summary": instrument_summaries,
        "cumulative_pnl": cumulative_curves,
    }


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-path", type=Path, required=True, help="Path to the CSV dataset")
    parser.add_argument("--base-currency", default="USD", help="Base currency of the study")
    parser.add_argument("--start-date", type=pd.Timestamp, default=None, help="Optional start date filter")
    parser.add_argument("--end-date", type=pd.Timestamp, default=None, help="Optional end date filter")
    parser.add_argument("--fast-window", type=int, default=5, help="Fast moving average window")
    parser.add_argument("--slow-window", type=int, default=21, help="Slow moving average window")
    parser.add_argument("--vol-window", type=int, default=30, help="Lookback window for realised volatility")
    parser.add_argument("--trend-weight", type=float, default=0.6, help="Weight assigned to the trend signal")
    parser.add_argument("--reversal-weight", type=float, default=0.4, help="Weight assigned to the reversal signal")
    parser.add_argument("--z-window", type=int, default=20, help="Window used for z-score normalisation")
    parser.add_argument("--notional", type=float, default=1_000_000.0, help="Target notional per instrument")
    parser.add_argument("--max-leverage", type=float, default=5.0, help="Maximum leverage in contracts")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    diagnostics = run_options_research_workflow(
        data_path=args.data_path,
        base_currency=args.base_currency,
        start_date=args.start_date,
        end_date=args.end_date,
        fast_window=args.fast_window,
        slow_window=args.slow_window,
        vol_window=args.vol_window,
        trend_weight=args.trend_weight,
        reversal_weight=args.reversal_weight,
        z_window=args.z_window,
        notional_per_instrument=args.notional,
        max_leverage=args.max_leverage,
    )

    summary: pd.DataFrame = diagnostics["summary"]
    print("Options research summary (per instrument):")
    print(summary.round(4))

    cumulative_curves: Mapping[str, pd.Series] = diagnostics["cumulative_pnl"]
    for instrument, curve in cumulative_curves.items():
        print("\nCumulative PnL for", instrument)
        print(curve.tail(10).round(2))


if __name__ == "__main__":
    main()
