# stock-intraday-5-minute-trading
Stock analysis using 5 minute intraday trading. 

Basically just runs against whatever tickers you have set with the starting balance - yahoo finance only offers 60 day history at a time for 5 minute but I used that to calculate a good trade window for each day of the week.

- minutes after market open and how long to hold for in minutes.
  ```
      strategies = {
        0: {'wait_after_opening': 95, 'hold_duration_before_selling': 60},
        1: {'wait_after_opening': 0, 'hold_duration_before_selling': 50},
        2: {'wait_after_opening': 55, 'hold_duration_before_selling': 90},
        3: {'wait_after_opening': 35, 'hold_duration_before_selling': 5},
        4: {'wait_after_opening': 0, 'hold_duration_before_selling': 55}
    }
  ```

  Example output

```
  Running strategy for TM, Allocated Cash: $270.27
[*********************100%%**********************]  1 of 1 completed
2023-12-05 Tuesday - Buy: 1.0 shares at $187.70, Sell: 1.0 shares at $188.63, Profit: $0.93
2023-12-06 Wednesday - Buy: 1.0 shares at $192.03, Sell: 1.0 shares at $191.48, Loss: $-0.55
2023-12-07 Thursday - Buy: 1.0 shares at $188.63, Sell: 1.0 shares at $188.15, Loss: $-0.48
2023-12-08 Friday - Buy: 1.0 shares at $186.36, Sell: 1.0 shares at $187.05, Profit: $0.69
2023-12-11 Monday - Buy: 1.0 shares at $187.35, Sell: 1.0 shares at $187.21, Loss: $-0.14
2023-12-12 Tuesday - Buy: 1.0 shares at $184.76, Sell: 1.0 shares at $184.37, Loss: $-0.39
2023-12-13 Wednesday - Buy: 1.0 shares at $183.74, Sell: 1.0 shares at $183.16, Loss: $-0.58
2023-12-14 Thursday - Buy: 1.0 shares at $183.15, Sell: 1.0 shares at $183.03, Loss: $-0.12
2023-12-15 Friday - Buy: 1.0 shares at $182.81, Sell: 1.0 shares at $181.59, Loss: $-1.22
2023-12-18 Monday - Buy: 1.0 shares at $182.96, Sell: 1.0 shares at $183.39, Profit: $0.43
2023-12-19 Tuesday - Buy: 1.0 shares at $184.80, Sell: 1.0 shares at $184.47, Loss: $-0.33
2023-12-20 Wednesday - Buy: 1.0 shares at $182.09, Sell: 1.0 shares at $182.13, Profit: $0.04
2023-12-21 Thursday - Buy: 1.0 shares at $180.00, Sell: 1.0 shares at $180.28, Profit: $0.28
2023-12-22 Friday - Buy: 1.0 shares at $178.06, Sell: 1.0 shares at $178.93, Profit: $0.87
2023-12-26 Tuesday - Buy: 1.0 shares at $178.53, Sell: 1.0 shares at $179.85, Profit: $1.32
2023-12-27 Wednesday - Buy: 1.0 shares at $180.44, Sell: 1.0 shares at $180.52, Profit: $0.08
2023-12-28 Thursday - Buy: 1.0 shares at $181.55, Sell: 1.0 shares at $181.51, Loss: $-0.04
2023-12-29 Friday - Buy: 1.0 shares at $183.13, Sell: 1.0 shares at $183.68, Profit: $0.55
2024-01-02 Tuesday - Buy: 1.0 shares at $182.15, Sell: 1.0 shares at $181.78, Loss: $-0.37
2024-01-03 Wednesday - Buy: 1.0 shares at $181.80, Sell: 1.0 shares at $181.75, Loss: $-0.05
2024-01-04 Thursday - Buy: 1.0 shares at $184.10, Sell: 1.0 shares at $184.11, Profit: $0.01
2024-01-05 Friday - Buy: 1.0 shares at $186.00, Sell: 1.0 shares at $188.03, Profit: $2.03
2024-01-08 Monday - Buy: 1.0 shares at $187.02, Sell: 1.0 shares at $187.44, Profit: $0.42
2024-01-09 Tuesday - Buy: 1.0 shares at $186.53, Sell: 1.0 shares at $185.82, Loss: $-0.71
2024-01-10 Wednesday - Buy: 1.0 shares at $190.60, Sell: 1.0 shares at $192.16, Profit: $1.56
2024-01-11 Thursday - Buy: 1.0 shares at $195.62, Sell: 1.0 shares at $194.91, Loss: $-0.71
2024-01-12 Friday - Buy: 1.0 shares at $195.06, Sell: 1.0 shares at $195.64, Profit: $0.58
2024-01-16 Tuesday - Buy: 1.0 shares at $195.29, Sell: 1.0 shares at $195.36, Profit: $0.07
2024-01-17 Wednesday - Buy: 1.0 shares at $193.57, Sell: 1.0 shares at $194.02, Profit: $0.45
2024-01-18 Thursday - Buy: 1.0 shares at $199.14, Sell: 1.0 shares at $199.79, Profit: $0.65
2024-01-19 Friday - Buy: 1.0 shares at $200.10, Sell: 1.0 shares at $199.14, Loss: $-0.96
2024-01-22 Monday - Buy: 1.0 shares at $200.44, Sell: 1.0 shares at $201.14, Profit: $0.70
2024-01-23 Tuesday - Buy: 1.0 shares at $200.68, Sell: 1.0 shares at $201.52, Profit: $0.84
2024-01-24 Wednesday - Buy: 1.0 shares at $200.78, Sell: 1.0 shares at $201.61, Profit: $0.83
2024-01-25 Thursday - Buy: 1.0 shares at $199.48, Sell: 1.0 shares at $199.64, Profit: $0.16
2024-01-26 Friday - Buy: 1.0 shares at $197.24, Sell: 1.0 shares at $197.63, Profit: $0.39


Daily profit is total profit divided by days traded: $9.553108761950236
Then to calculate yearly profit we can multiply the profit per day by 252 possible trading days: $2407.3834080114593
Based on this evaluation, you could possibly expect an account balance of $12407.38 after 12 months.

IMPORTANT: This does not account for compounding (Using the updated daily balance to calculate potentially more profit)
This also does not account for API fees/Exchange fees for each transaction
With 2 trades per day (A buy & A sell) across 252 days for 14 stocks that would be 7056 trades
```
