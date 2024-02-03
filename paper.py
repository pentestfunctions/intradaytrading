import os
import backtrader as bt
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Set display options
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

def clear_screen():
    if os.name == 'nt':
        _ = os.system('cls')  # For Windows
    else:
        _ = os.system('clear')  # For Mac and Linux

def fetch_data(ticker, start_date, end_date, interval='5m'):
    data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    if data.empty:
        raise ValueError(f"Failed to fetch data for {ticker}.")
    return data

def run_backtrader_for_ticker(start_date, end_date, start_cash, ticker, strategies, daily_profit_loss):
    print(f"\nRunning strategy for {ticker}, Allocated Cash: ${start_cash:.2f}")
    df = fetch_data(ticker, start_date, end_date, interval='5m')
    total_profit_loss = 0

    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    current_date = start_date_obj

    trading_days = set()
    while current_date <= end_date_obj:
        day_of_week = current_date.weekday()
        strategy = strategies.get(day_of_week)

        if strategy:
            wait_minutes = strategy['wait_after_opening']
            hold_minutes = strategy['hold_duration_before_selling']
            
            day_data = df[df.index.date == current_date.date()]
            
            if not day_data.empty:
                rows_to_skip_buy = int(wait_minutes / 5)
                rows_to_skip_sell = int(hold_minutes / 5)
                
                if len(day_data) > rows_to_skip_buy + rows_to_skip_sell:
                    buy_row = day_data.iloc[rows_to_skip_buy:rows_to_skip_buy + 1]
                    sell_row = day_data.iloc[rows_to_skip_buy + rows_to_skip_sell:rows_to_skip_buy + rows_to_skip_sell + 1]
                    
                    buy_price = buy_row['Open'].iloc[0]
                    sell_price = sell_row['Close'].iloc[0]
                    shares_bought = start_cash // buy_price
                    cost = shares_bought * buy_price
                    sell_amount = shares_bought * sell_price
                    profit_or_loss = sell_amount - cost
                    total_profit_loss += profit_or_loss
                    
                    # Accumulate daily profit/loss
                    daily_profit_loss[current_date.strftime('%A')] += profit_or_loss
                    
                    profit_loss_color = "\033[92m" if profit_or_loss > 0 else "\033[91m"
                    print(f"{current_date.strftime('%Y-%m-%d %A')} - Buy: {shares_bought} shares at ${buy_price:.2f}, Sell: {shares_bought} shares at ${sell_price:.2f}, {profit_loss_color}{'Profit' if profit_or_loss > 0 else 'Loss'}: ${profit_or_loss:.2f}\033[0m")
        if strategy and not day_data.empty:
            trading_days.add(current_date.date())
        current_date += timedelta(days=1)
    return trading_days

def main(start_cash, tickers, start_date, end_date):
    strategies = {
        0: {'wait_after_opening': 95, 'hold_duration_before_selling': 60},
        1: {'wait_after_opening': 0, 'hold_duration_before_selling': 50},
        2: {'wait_after_opening': 55, 'hold_duration_before_selling': 90},
        3: {'wait_after_opening': 35, 'hold_duration_before_selling': 5},
        4: {'wait_after_opening': 0, 'hold_duration_before_selling': 55}
    }

    all_trading_days = set()  # Initialize a set to aggregate trading days across all tickers

    daily_profit_loss = {day: 0 for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']}
    
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    # Iterate through the strategies and print each
    for day, strategy in strategies.items():
        print(f'{days_of_week[day]} Strategy:')
        print(f'Wait after opening: {strategy["wait_after_opening"]} minutes')
        print(f'Hold duration before selling: {strategy["hold_duration_before_selling"]} minutes')
        print()

    total_portfolio_profit_loss = 0
    cash_per_ticker = start_cash / len(tickers)

    print(f"Starting with ${start_cash:.2f}, allocating ${cash_per_ticker:.2f} per ticker.\n")

    for ticker in tickers:
        ticker_trading_days = run_backtrader_for_ticker(start_date, end_date, cash_per_ticker, ticker, strategies, daily_profit_loss)
        all_trading_days.update(ticker_trading_days)  # Aggregate trading days

    # Analyze the most and least profitable days
    most_profitable_day = max(daily_profit_loss, key=daily_profit_loss.get)
    least_profitable_day = min(daily_profit_loss, key=daily_profit_loss.get)

    final_balance = start_cash + sum(daily_profit_loss.values())

    final_balance_color = "\033[92m" if final_balance > start_cash else "\033[91m"
    print(f"\n{final_balance_color}Total Portfolio Balance: ${final_balance:.2f}\033[0m")
    print(f"Most Profitable Day: {most_profitable_day} with profit/loss of ${daily_profit_loss[most_profitable_day]:.2f}")
    print(f"Least Profitable Day: {least_profitable_day} with profit/loss of ${daily_profit_loss[least_profitable_day]:.2f}")

    # Calculate the annualized return percentage using approximate trading days
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    total_days = (end_date_obj - start_date_obj).days + 1
    weeks_in_period = total_days / 7
    trading_days_approx = len(all_trading_days)
    total_profit_loss = final_balance - start_cash
    annualized_return_percent = (total_profit_loss / start_cash) * (252 / trading_days_approx) * 100

    print(f"\nAnnualized Return: {annualized_return_percent:.2f}% based on {len(all_trading_days)} observed days")
    profit_per_day = final_balance - 10000
    print(f"Daily profit is total profit divided by days traded: ${profit_per_day / len(all_trading_days)}")
    print(f"Then to calculate yearly profit we can multiply the profit per day by 252 possible trading days: ${profit_per_day / len(all_trading_days) * 252}")
    # Calculate and print the expected account balance after 12 months
    expected_balance_after_12_months = start_cash * (1 + annualized_return_percent / 100)
    print(f"Based on this evaluation, you could possibly expect an account balance of ${expected_balance_after_12_months:.2f} after 12 months.")
    print(f"\nIMPORTANT: This does not account for compounding (Using the updated daily balance to calculate potentially more profit)\nThis also does not account for API fees/Exchange fees for each transaction")
    print(f"With 2 trades per day (A buy & A sell) across 252 days for 14 stocks that would be {7056} trades")

if __name__ == '__main__':
    clear_screen()
    start_cash = 10000
    tickers = ['AAPL', 'GOOGL', 'RTX', 'IBM', 'BAC', 'JPM', 'AMZN', 'UBER', 'TSLA', 'SONY', 'HSBC',
               'PG', 'DIS', 'PFE', 'KO', 'T', 'WMT', 'MRK', 'CSCO', 'ABT', 'NKE', 'PYPL', 'XOM',
               'CVX', 'INTC', 'PEP', 'ORCL', 'CMCSA', 'TMUS', 'VZ', 'ABBV', 'MMM', 'JNJ', 'WFC',
               'MO', 'NIO', 'TM']    
    start_date = '2024-01-03'
    end_date = '2024-02-03'
    main(start_cash, tickers, start_date, end_date)
