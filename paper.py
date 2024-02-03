import argparse
import random
import pandas as pd
from datetime import datetime, timedelta, time
import os
import platform
import yfinance as yf

def comma_separated_strings(value):
    # This will split the string by comma and strip spaces, then return the list of strings (tickers)
    return [ticker.strip() for ticker in value.split(',')]

# Setup command line arguments
parser = argparse.ArgumentParser(
    description='Stock Analysis Tool',
    epilog="""Example commands:
    python stockanalysis.py --day Monday --random 5 --balance 10000 --fee 0.1
      Run the script for Monday, picking 5 random stocks, with a starting balance of $10,000 and a trading fee of $0.10 per trade.
    
    python stockanalysis.py --day Friday --random 15 --balance 20000
      Run the script for Friday, picking 15 random stocks, with a starting balance of $20,000 and the default trading fee.

    python stockanalysis.py --tickers aapl,meta --day monday
      Run the script with the tickers AAPL and META for Monday ($15,000 starting balance, $0.01 trading fee per trade).

    python stockanalysis.py --live
      This will only work if you have run the script previously to completion for a txt file to be made such as 'Tuesday.txt' which would contain data like 'tuesday,starttime,endtime'.
      This is because it will test against the last 1 day the best method evaluated so far.
      
    python stockanalysis.py
      Run the script with default settings (Tuesday, 10 random stocks, $15,000 starting balance, $0.01 trading fee per trade).""",
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument('--day', type=str, help='Day of the week to analyze', default='Tuesday')  # Default day is Tuesday
parser.add_argument('--random', type=int, help='Number of random stocks to pick', default=10)  # Default is 10 random stocks
parser.add_argument('--balance', type=int, help="User's starting balance", default=15000)  # $15,000 starting by default
parser.add_argument('--fee', type=float, help="Exchange fee per transaction (in dollars)", default=0.01)  # $0.01 fee per trade
parser.add_argument('--tickers', type=comma_separated_strings, help="Comma-separated list of ticker symbols to analyze", default=None) # Like --tickers aapl,meta,msft
parser.add_argument('--live', action='store_true', help="Fetch the last 1 day's data for the tickers")

# Parse arguments
args = parser.parse_args()

# Define the folder path
folder_path = 'ticker_data'

# Use the arguments
weekday_chosen = args.day.capitalize()
num_random_stocks = args.random
starting_balance = args.balance
# Fee per transaction (Buy/Sell)
trading_fee_per_trade = args.fee

# Ensure the day is valid
if weekday_chosen not in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
    raise ValueError("Invalid day. Please enter a valid weekday (e.g., Tuesday).")

# Define all available ticker symbols
all_tickers = ["AAPL", "BAC", "DIS", "INTC", "MMM", "NKE", "PG", "T", "UBER", "XOM", "ABBV", "CMCSA", "GOOGL", "JNJ", "MO", "ORCL", "PYPL", "TM", "VZ", "ABT", "CSCO", "HSBC", "JPM", "MRK", "PEP", "RTX", "TMUS", "WFC", "AMZN", "CVX", "IBM", "KO", "NIO", "PFE", "SONY", "TSLA", "WMT"]

# After parsing, check if custom tickers are provided
if args.tickers:
    tickers = args.tickers  # Use the custom list of tickers
else:
    # Select random stocks if the number specified is less than the total available
    if num_random_stocks < len(all_tickers):
        tickers = random.sample(all_tickers, num_random_stocks)
    else:
        tickers = all_tickers

# Initialize variables to track the worst times and their loss
worst_buy_time = None
worst_sell_time = None
lowest_total_profit = float('inf')  # Initialize with a very large number for tracking the worst performance

# Function to generate all time combinations
def generate_time_combinations(start_time, end_time, increment):
    times = []
    current_time = start_time
    while current_time <= end_time:
        times.append(current_time)
        current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=increment)).time()
    return times

# Generate all valid buy and sell time combinations within 9:30 to 15:55
buy_times = generate_time_combinations(time(9, 30), time(15, 50), 5)
sell_times = generate_time_combinations(time(9, 35), time(15, 55), 5)

# Number of days you can trade in a year
number_of_trading_days = 252

# Define a function to clear the screen
def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def fetch_and_save_ticker_data(ticker, live=False):
    if live:
        # Adjust start and end date for live data fetching
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)  # Fetch data for the last day
    else:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=59)  # Existing logic for historical data

    # Fetch data using adjusted dates
    df = yf.download(ticker, start=start_date, end=end_date, interval='5m')
    
    # Ensure the ticker_data folder exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Save to CSV
    file_path = os.path.join(folder_path, f'{ticker}.csv')
    df.to_csv(file_path)

# Adjusted the clear_screen function to include current best and worst times and their profits
def update_screen():
    clear_screen()

    best_case_percentage_change = (highest_total_profit / number_of_unique_days / starting_balance) * 100  # Calculate percentage change
    worst_case_percentage_change = (lowest_total_profit / number_of_unique_days / starting_balance) * 100  # Calculate percentage change
    
    # Speculative balances calculations
    best_case_balance_without_compounding = starting_balance + (starting_balance * best_case_percentage_change / 100 * number_of_trading_days)
    worst_case_balance_without_compounding = starting_balance + (starting_balance * worst_case_percentage_change / 100 * number_of_trading_days)
    best_case_balance_with_compounding = starting_balance * ((1 + best_case_percentage_change / 100) ** number_of_trading_days)
    worst_case_balance_with_compounding = starting_balance * ((1 + worst_case_percentage_change / 100) ** number_of_trading_days)

    # ANSI color codes
    HEADER = '\033[92m'  # Green
    BLUE = '\033[94m'  # Blue
    RED = '\033[91m'  # Red
    YELLOW = '\033[93m'  # Yellow
    GREEN = '\033[0m' # Green
    ENDC = '\033[0m'  # Reset color

    # Header with basic information
    print(HEADER + "="*80 + ENDC)
    print(HEADER + "Stock Analysis Dashboard (One Day Trading)".center(80) + ENDC)
    print(HEADER + "="*80 + ENDC)
    print(YELLOW + f'Analyzing Day: {weekday_chosen}'.ljust(40) + f'Starting Balance: ${starting_balance}'.rjust(40) + ENDC)
    print(YELLOW + f'Number of Stocks: {len(tickers)}'.ljust(40) + f'Allocated per Stock: ${allocated_balance_per_stock:.2f}'.rjust(40) + ENDC)
    print("-"*80)

    # Best case scenario display
    print(BLUE + "Best Case Scenario".center(80) + ENDC)
    print(BLUE + f'Buy Time: {best_buy_time}'.ljust(40) + f'Sell Time: {best_sell_time}\n'.rjust(40) + ENDC)
    print(BLUE + f'Highest Total Change From {number_of_unique_days} {weekday_chosen}\'s: ${highest_total_profit:.2f}'.center(80) + ENDC)
    print(BLUE + f'Average Change per day: ${highest_total_profit / number_of_unique_days:.2f}'.center(80) + ENDC)
    print(BLUE + f'Percentage Change Per Day: {best_case_percentage_change:.2f}%\n'.center(80) + ENDC)
    print(YELLOW + "Speculative Future Balances Over 252 Trading Days".center(80) + ENDC)
    print(BLUE + f'Best Case Without Compounding: ${best_case_balance_without_compounding:.2f}'.center(80) + ENDC)
    print(BLUE + f'Best Case With Compounding: ${best_case_balance_with_compounding:.2f}'.center(80) + ENDC)
    print("-"*80)

    # Worst case scenario display (conditional)
    if worst_buy_time is not None and worst_sell_time is not None:
        print(RED + "Worst Case Scenario".center(80) + ENDC)
        print(RED + f'Buy Time: {worst_buy_time}'.ljust(40) + f'Sell Time: {worst_sell_time}\n'.rjust(40) + ENDC)
        print(RED + f'Lowest Total Change From {number_of_unique_days} {weekday_chosen}\'s: ${lowest_total_profit:.2f}'.center(80) + ENDC)
        print(RED + f'Average Change per day: ${lowest_total_profit / number_of_unique_days:.2f}'.center(80) + ENDC)
        print(RED + f'Percentage Change Per Day: {worst_case_percentage_change:.2f}%\n'.center(80) + ENDC)
        print(YELLOW + "Speculative Future Balances Over 252 Trading Days".center(80) + ENDC)
        print(RED + f'Worst Case Without Compounding: ${worst_case_balance_without_compounding:.2f}'.center(80) + ENDC)
        print(RED + f'Worst Case With Compounding: ${worst_case_balance_with_compounding:.2f}'.center(80) + ENDC)
        print(HEADER + "="*80 + ENDC)
    else:
        print(RED + "Worst Case Scenario: Data not available".center(80) + ENDC)
        print(HEADER + "="*80 + "\n" + ENDC)
    print(f"Notes:".center(80))
    print(f"This will make sure at least the buy and sell is made in the same day".center(80))
    print(f"The goal is to find the best trade window statistically".center(80))
    print(f"If the ticker already exists from previous runs you might want to delete it to get the latest 60 days".center(80))
    print(f"Tickers being used in this run: {tickers}".center(80))

weekday_count = 0

# Initialize variables to track the best times and their profit
best_buy_time = None
best_sell_time = None
highest_total_profit = -float('inf')

number_of_unique_days = set()

# Brute-force search for the best buy and sell times
for buy_time in buy_times:
    for sell_time in sell_times:
        if sell_time <= buy_time:
            continue  # Skip invalid combinations where sell time is before or equal to buy time
        
        overall_profit_loss = 0  # Reset profit/loss for each combination
        allocated_balance_per_stock = starting_balance / len(tickers)
        
        # Repeat the trading strategy for each ticker, now with the current combination of buy and sell times
        for ticker in tickers:
            file_path = os.path.join(folder_path, f'{ticker}.csv')
            if not os.path.exists(file_path):
                print(f"Fetching data for {ticker}...")
                fetch_and_save_ticker_data(ticker, args.live)
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                df['Datetime_Obj'] = pd.to_datetime(df['Datetime']).dt.tz_localize(None)
                df['DayOfWeek'] = df['Datetime_Obj'].dt.day_name()
                df['Time'] = df['Datetime_Obj'].dt.time

                # Filter for the chosen weekday
                df_weekday = df[df['DayOfWeek'] == weekday_chosen]
                number_of_unique_days = df_weekday['Datetime_Obj'].dt.date.nunique()

                
                for date, group in df_weekday.groupby(df_weekday['Datetime_Obj'].dt.date):
                    within_time_frame = group[(group['Time'] >= buy_time) & (group['Time'] <= sell_time)]

                    if not within_time_frame.empty:
                        buy_price = within_time_frame.iloc[0]['Open']
                        sell_price = within_time_frame.iloc[-1]['Close']
                        shares_to_buy = allocated_balance_per_stock // buy_price

                        # Calculate profit or loss after subtracting the trading fee for both buy and sell transactions
                        profit_loss = (sell_price - buy_price) * shares_to_buy - (trading_fee_per_trade * 2)  # Subtract $0.02 total for the buy and sell
                        overall_profit_loss += profit_loss

                        # Update best and worst scenarios as before
                        if overall_profit_loss > highest_total_profit:
                            highest_total_profit = overall_profit_loss
                            best_buy_time = buy_time
                            best_sell_time = sell_time
                            update_screen()

                        elif overall_profit_loss < lowest_total_profit:  # Check if this combination is the worst so far
                            lowest_total_profit = overall_profit_loss
                            worst_buy_time = buy_time
                            worst_sell_time = sell_time
                            update_screen()
            else:
                print(f'File not found for ticker: {ticker}')

        # Check if this combination has the highest profit so far
        if overall_profit_loss > highest_total_profit:
            highest_total_profit = overall_profit_loss
            best_buy_time = buy_time
            best_sell_time = sell_time

# Save the best buy and sell times to a file named after the weekday
results_filename = f'{weekday_chosen}.txt'
with open(results_filename, 'w') as file:
    file.write(f'{weekday_chosen},{best_buy_time.strftime("%H:%M")},{best_sell_time.strftime("%H:%M")}')

# Print the best buy and sell times and the highest total profit
print(f'\nFinal Results for {weekday_chosen}:')
print(f'Best Buy Time: {best_buy_time}, Best Sell Time: {best_sell_time}, Highest Total Profit: {highest_total_profit:.2f}')
if worst_buy_time and worst_sell_time:
    print(f'Worst Buy Time: {worst_buy_time}, Worst Sell Time: {worst_sell_time}, Lowest Total Profit: {lowest_total_profit:.2f}')
