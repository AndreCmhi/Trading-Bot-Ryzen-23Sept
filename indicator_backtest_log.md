# Trading Bot Report

Generated: 2026-06-12 10:17:38

## Current Runtime Settings
| Setting | Value |
| --- | --- |
| strategy_mode | SCALPING |
| min_score | 4 |
| auto_close_roi_percent | 3 |
| trailing_enabled | True |
| trailing_trigger_roi_percent | 2.5 |
| trailing_callback_roi_percent | 0.8 |
| fast_trailing_enabled | True |
| fast_trailing_trigger_roi_percent | 0.9 |
| fast_trailing_callback_roi_percent | 0.25 |
| hard_stop_roi_percent | -5 |
| max_trades_per_hour | 15 |
| max_symbol_trades_per_day | 2 |

## Overall Closed Trades
| Metric | Value |
| --- | --- |
| Closed trades | 0 |
| Open trades | 2 |
| Wins | 0 |
| Losses | 0 |
| Breakeven | 0 |
| Win rate | 0.00% |
| Total PnL | 0.00 |
| Average PnL | 0.0000 |
| Profit factor | 0.00 |
| Avg win | 0.0000 |
| Avg loss | 0.0000 |

## Last 20 Closed Trades
| Metric | Value |
| --- | --- |
| Closed trades | 0 |
| Win rate | 0.00% |
| Total PnL | 0.00 |

## Forward Test Since 2026-05-27 04:12:00
| Metric | Value |
| --- | --- |
| Closed trades | 0 |
| Wins | 0 |
| Losses | 0 |
| Breakeven | 0 |
| Win rate | 0.00% |
| Total PnL | 0.00 |

## Close Reason Performance
| Reason | Trades | Win Rate | Total PnL | Avg PnL |
| --- | --- | --- | --- | --- |

## Best Symbols
| Symbol | Trades | Win Rate | Total PnL | Avg PnL |
| --- | --- | --- | --- | --- |

## Worst Symbols
| Symbol | Trades | Win Rate | Total PnL | Avg PnL |
| --- | --- | --- | --- | --- |

## Indicator Backtest
| Bucket | Trades | Win Rate | Total PnL | Avg PnL |
| --- | --- | --- | --- | --- |

### VWAP Bias
| Bucket | Trades | Win Rate | Total PnL | Avg PnL |
| --- | --- | --- | --- | --- |

### EMA Bias
| Bucket | Trades | Win Rate | Total PnL | Avg PnL |
| --- | --- | --- | --- | --- |

### ADX Bucket
| Bucket | Trades | Win Rate | Total PnL | Avg PnL |
| --- | --- | --- | --- | --- |

### Recent Indicator Log
| Closed | Symbol | Side | PnL | Vol | VWAP | EMA | ADX | Confirm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Recommendation
- Forward-test only on Binance Testnet until at least 30 new closed trades after SCALPING patch.
- Pass condition: new closed trades >= 30, win rate > 55%, total PnL >= 0, no hard-stop cluster.
- Keep trend and pullback filters enabled; do not raise max trades per hour before pass condition.
