import argparse
import random
import pandas as pd
from datetime import datetime, timedelta, time
import os
import platform
import yfinance as yf

# Get the current time for the user (For progress updates)
current_users_time = datetime.now()
current_time_str = current_users_time.strftime("%Y-%m-%d %H:%M:%S")  # You can adjust the format as needed

def comma_separated_strings(value):
    # This will split the string by comma and strip spaces, then return the list of strings (tickers)
    return [ticker.strip() for ticker in value.split(',')]

# Setup command line arguments
parser = argparse.ArgumentParser(
    description='Stock Analysis Tool',
    epilog="""Example commands:
    python stockanalysis.py --day Monday --random 5 --balance 10000 --fee 0.1
      Run the script for Monday, picking 5 random stocks, with a starting balance of $10,000 and a trading fee of $0.10 per trade.

    python stockanalysis.py --day all --random 5 --balance 10000 --fee 0.1
      Run the script for all weekdays, picking 5 random stocks, with a starting balance of $10,000 and a trading fee of $0.10 per trade.
          
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

parser.add_argument('--day', type=str, help='Day of the week to analyze (you can specify all to run against all)', default='Tuesday')  # Default day is Tuesday
parser.add_argument('--random', type=int, help='Number of random stocks to pick', default=10)  # Default is 10 random stocks
parser.add_argument('--balance', type=int, help="User's starting balance", default=15000)  # $15,000 starting by default
parser.add_argument('--fee', type=float, help="Exchange fee per transaction (in dollars)", default=0.01)  # $0.01 fee per trade
parser.add_argument('--tickers', type=comma_separated_strings, help="Comma-separated list of ticker symbols to analyze", default=None) # Like --tickers aapl,meta,msft
parser.add_argument('--live', action='store_true', help="Fetch the last 1 day's data for the tickers")

# Parse arguments
args = parser.parse_args()

# Dictionary to store results for each day
daily_results = {}

# Define the folder path
folder_path = 'ticker_data'

# Use the arguments
weekday_chosen = args.day.capitalize()
num_random_stocks = args.random
starting_balance = args.balance
# Fee per transaction (Buy/Sell)
trading_fee_per_trade = args.fee

# Define weekdays to loop through if 'all' is specified
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

# Ensure the day is valid
if weekday_chosen not in valid_days and weekday_chosen.lower() != 'all':
    raise ValueError("Invalid day. Please enter a valid weekday (e.g., Tuesday) or 'all'.")

# Check if 'all' is specified or just a single day
if args.day.lower() == 'all':
    days_to_analyze = weekdays
else:
    if args.day.capitalize() not in valid_days:
        raise ValueError("Invalid day. Please enter a valid weekday (e.g., Tuesday).")
    days_to_analyze = [args.day.capitalize()]

# Define all available ticker symbols
all_tickers = [
    "AAPL", "BAC", "DIS", "INTC", "MMM", "NKE", "PG", "T", "UBER", "XOM",
    "ABBV", "CMCSA", "GOOGL", "JNJ", "MO", "ORCL", "PYPL", "TM", "VZ", "ABT",
    "CSCO", "HSBC", "JPM", "MRK", "PEP", "RTX", "TMUS", "WFC", "AMZN", "CVX",
    "IBM", "KO", "NIO", "PFE", "SONY", "TSLA", "WMT", "MSFT", "NFLX", "AMD",
    "NVDA", "FB", "BA", "LMT", "GILD", "BIIB", "MDT", "BMY", "GE", "DAL",
    "LUV", "AAL", "CAT", "DE", "GS", "MS", "C", "BLK", "SQ", "ZM", "SPOT",
    "ADBE", "CRM", "TMO", "UNH", "MCD", "V", "MA", "HD", "LOW", "SBUX"
]

ticker_details = {
    "AAPL": "Apple Inc. - A leading technology company known for its smartphones, computers, and software.",
    "BAC": "Bank of America Corp - A multinational banking and financial services corporation.",
    "DIS": "The Walt Disney Company - A diversified multinational mass media and entertainment conglomerate.",
    "INTC": "Intel Corporation - A leading semiconductor manufacturing company.",
    "MMM": "3M Company - A multinational conglomerate corporation operating in fields of industry, worker safety, health care, and consumer goods.",
    "NKE": "Nike, Inc. - A global marketer of athletic footwear, apparel, and equipment.",
    "PG": "Procter & Gamble Co. - A multinational consumer goods corporation.",
    "T": "AT&T Inc. - An American multinational conglomerate holding company and telecommunications giant.",
    "UBER": "Uber Technologies, Inc. - A technology company offering ride-hailing services, food delivery, and more.",
    "XOM": "Exxon Mobil Corporation - One of the world's largest publicly traded oil and gas companies.",
    "ABBV": "AbbVie Inc. - A biopharmaceutical company focused on developing treatments for severe conditions.",
    "CMCSA": "Comcast Corporation - A global media and technology company with two primary businesses: Comcast Cable and NBCUniversal.",
    "GOOGL": "Alphabet Inc. - The parent company of Google, overseeing various businesses, including Google's Internet services.",
    "JNJ": "Johnson & Johnson - A multinational corporation that develops medical devices, pharmaceuticals, and consumer packaged goods.",
    "MO": "Altria Group, Inc. - An American corporation and one of the world's largest producers and marketers of tobacco, cigarettes, and related products.",
    "ORCL": "Oracle Corporation - A multinational computer technology corporation specializing in database software and technology, cloud engineered systems, and enterprise software products.",
    "PYPL": "PayPal Holdings, Inc. - An American company operating an online payments system in the majority of countries that support online money transfers.",
    "TM": "Toyota Motor Corporation - A Japanese multinational automotive manufacturer.",
    "VZ": "Verizon Communications Inc. - An American multinational telecommunications conglomerate and a corporate component of the Dow Jones Industrial Average.",
    "ABT": "Abbott Laboratories - A multinational medical devices and health care company with a broad range of branded generic pharmaceuticals, medical devices, diagnostics, and nutrition products.",
    "CSCO": "Cisco Systems, Inc. - An American multinational technology conglomerate that develops, manufactures, and sells networking hardware, software, telecommunications equipment, and other high-technology services and products.",
    "HSBC": "HSBC Holdings plc - A British multinational banking and financial services holding company.",
    "JPM": "JPMorgan Chase & Co. - An American multinational investment bank and financial services holding company.",
    "MRK": "Merck & Co., Inc. - A leading global biopharmaceutical company known as MSD outside of the United States and Canada.",
    "PEP": "PepsiCo, Inc. - An American multinational food, snack, and beverage corporation.",
    "RTX": "Raytheon Technologies Corporation - An aerospace and defense company that provides advanced systems and services for commercial, military, and government customers worldwide.",
    "TMUS": "T-Mobile US, Inc. - A major wireless network operator in the United States.",
    "WFC": "Wells Fargo & Company - An American multinational financial services company.",
    "AMZN": "Amazon.com, Inc. - A multinational technology company focusing on e-commerce, cloud computing, digital streaming, and artificial intelligence.",
    "CVX": "Chevron Corporation - An American multinational energy corporation, one of the successor companies of Standard Oil.",
    "IBM": "International Business Machines Corporation - An American multinational technology and consulting company.",
    "KO": "The Coca-Cola Company - An American multinational beverage corporation.",
    "NIO": "NIO Inc. - A Chinese automobile manufacturer specializing in designing and developing electric vehicles.",
    "PFE": "Pfizer Inc. - An American multinational pharmaceutical and biotechnology corporation.",
    "SONY": "Sony Corporation - A Japanese multinational conglomerate corporation that is one of the leading manufacturers of electronic products.",
    "TSLA": "Tesla, Inc. - An American electric vehicle and clean energy company.",
    "WMT": "Walmart Inc. - An American multinational retail corporation that operates a chain of hypermarkets, discount department stores, and grocery stores.",
    "MSFT": "Microsoft Corporation - An American multinational technology company with a focus on computer software, consumer electronics, personal computers, and related services.",
    "NFLX": "Netflix, Inc. - An American content platform and production company offering subscription streaming service.",
    "AMD": "Advanced Micro Devices, Inc. - An American multinational semiconductor company that develops computer processors and related technologies.",
    "NVDA": "NVIDIA Corporation - An American multinational technology company incorporated in Delaware and based in Santa Clara, California. It designs graphics processing units (GPUs) for gaming and professional markets.",
    "FB": "Meta Platforms, Inc. (formerly Facebook, Inc.) - An American multinational technology conglomerate holding company and social media and social networking service.",
    "BA": "The Boeing Company - An American multinational corporation that designs, manufactures, and sells airplanes, rotorcraft, rockets, satellites, and telecommunications equipment.",
    "LMT": "Lockheed Martin Corporation - An American aerospace, defense, arms, security, and advanced technologies company.",
    "GILD": "Gilead Sciences, Inc. - A biopharmaceutical company that researches, develops, and commercializes drugs.",
    "BIIB": "Biogen Inc. - An American multinational biotechnology company specializing in the discovery, development, and delivery of therapies for the treatment of neurodegenerative diseases and autoimmune disorders.",
    "MDT": "Medtronic plc - A global leader in medical technology, services, and solutions.",
    "BMY": "Bristol Myers Squibb - An American multinational pharmaceutical company.",
    "GE": "General Electric Company - An American multinational conglomerate operating in sectors such as aviation, power, renewable energy, digital industry, and healthcare.",
    "DAL": "Delta Air Lines, Inc. - An American airline, one of the major airlines of the United States.",
    "LUV": "Southwest Airlines Co. - An American airline, the world's largest low-cost carrier.",
    "AAL": "American Airlines Group Inc. - An American airline holding company and the world's largest airline.",
    "CAT": "Caterpillar Inc. - An American Fortune 100 corporation which designs, develops, engineers, manufactures, markets, and sells machinery, engines, financial products, and insurance.",
    "DE": "Deere & Company - An American corporation that manufactures agricultural, construction, and forestry machinery.",
    "GS": "The Goldman Sachs Group, Inc. - An American multinational investment bank and financial services company.",
    "MS": "Morgan Stanley - An American multinational investment management and financial services company.",
    "C": "Citigroup Inc. - An American multinational investment bank and financial services corporation.",
    "BLK": "BlackRock, Inc. - An American multinational investment management corporation based in New York City.",
    "SQ": "Block, Inc. (formerly Square, Inc.) - An American financial services and digital payments company.",
    "ZM": "Zoom Video Communications, Inc. - An American communications technology company that provides videotelephony and online chat services.",
    "SPOT": "Spotify Technology S.A. - A Swedish audio streaming and media services provider.",
    "ADBE": "Adobe Inc. - An American multinational computer software company.",
    "CRM": "Salesforce, Inc. - An American cloud-based software company providing customer relationship management service.",
    "TMO": "Thermo Fisher Scientific Inc. - An American provisioner of scientific instrumentation, reagents and consumables, and software services.",
    "UNH": "UnitedHealth Group Incorporated - An American multinational managed healthcare and insurance company.",
    "MCD": "McDonald's Corporation - An American fast food company, known for its hamburgers, cheeseburgers, and french fries.",
    "V": "Visa Inc. - An American multinational financial services corporation.",
    "MA": "Mastercard Incorporated - An American multinational financial services corporation.",
    "HD": "The Home Depot, Inc. - The largest home improvement retailer in the United States.",
    "LOW": "Lowe's Companies, Inc. - An American retail company specializing in home improvement.",
    "SBUX": "Starbucks Corporation - An American multinational chain of coffeehouses and roastery reserves."
}

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

# Number of days you can trade in a year divded by 5 to represent each weekday
number_of_trading_days = 252 / 5

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

    best_average_change_per_day = highest_total_profit / number_of_unique_days
    worst_average_change_per_day = lowest_total_profit / number_of_unique_days
    best_case_percentage_change = (best_average_change_per_day / starting_balance) * 100  # Calculate percentage change
    worst_case_percentage_change = (worst_average_change_per_day / starting_balance) * 100

    # Speculative balances calculations
    best_case_balance_without_compounding = starting_balance + (starting_balance * best_case_percentage_change / 100 * number_of_trading_days)
    best_case_balance_with_compounding = starting_balance * ((1 + best_case_percentage_change / 100) ** number_of_trading_days)

    worst_case_balance_without_compounding = starting_balance + (starting_balance * worst_case_percentage_change / 100 * number_of_trading_days)

    # ANSI color codes
    HEADER = '\033[92m'  # Green
    BLUE = '\033[94m'  # Blue
    RED = '\033[91m'  # Red
    YELLOW = '\033[93m'  # Yellow
    GREEN = '\033[0m' # Green
    ENDC = '\033[0m'  # Reset color

    total_width = 100
    total_width_half = 50
    date_length = len(current_time_str)
    title = "Stock Analysis Dashboard (One Day Trading)"
    space_for_title = total_width - date_length
    centered_title = title.center(space_for_title)
    header_string = f"{HEADER}{centered_title}{current_time_str}{ENDC}"

    # Header with basic information
    print(HEADER + "="*total_width + ENDC)
    print(header_string)
    print(HEADER + "="*total_width + ENDC)
    print(YELLOW + f'Analyzing Day: {weekday_chosen}'.ljust(total_width_half) + f'Starting Balance: ${starting_balance}'.rjust(total_width_half) + ENDC)
    print(YELLOW + f'Number of Stocks: {len(tickers)}'.ljust(total_width_half) + f'Allocated per Stock: ${allocated_balance_per_stock:.2f}'.rjust(total_width_half) + ENDC)
    print("-"*total_width)

    # Best case scenario display
    print(BLUE + "Best Case Scenario".center(total_width) + ENDC)
    print(BLUE + f'Buy Time: {best_buy_time}'.ljust(total_width_half) + f'Sell Time: {best_sell_time}'.rjust(total_width_half) + ENDC)
    print(BLUE + f'Highest Total Change From {number_of_unique_days} {weekday_chosen}\'s: ${highest_total_profit:.2f}'.center(total_width) + ENDC)
    print(BLUE + f'Average Change per day: ${best_average_change_per_day:.2f}'.center(total_width) + ENDC)
    print(BLUE + f'Percentage Change Per Day: {best_case_percentage_change:.2f}%\n'.center(total_width) + ENDC)
    print(YELLOW + f"Speculative Future Balances Over 252 Trading Days (50 {weekday_chosen}\'s)".center(total_width) + ENDC)
    print(BLUE + f'Best Case Without Compounding: ${best_case_balance_without_compounding:.2f}'.center(total_width) + ENDC)
    print(BLUE + f'Best Case With Compounding: ${best_case_balance_with_compounding:.2f}'.center(total_width) + ENDC)
    print("-"*total_width)

    # Worst case scenario display (conditional)
    if worst_buy_time is not None and worst_sell_time is not None:
        print(RED + "Worst Case Scenario".center(total_width) + ENDC)
        print(RED + f'Buy Time: {worst_buy_time}'.ljust(total_width_half) + f'Sell Time: {worst_sell_time}\n'.rjust(total_width_half) + ENDC)
        print(RED + f'Lowest Total Change From {number_of_unique_days} {weekday_chosen}\'s: ${lowest_total_profit:.2f}'.center(total_width) + ENDC)
        print(RED + f'Average Change per day: ${worst_average_change_per_day:.2f}'.center(total_width) + ENDC)
        print(RED + f'Percentage Change Per Day: {worst_case_percentage_change:.2f}%\n'.center(total_width) + ENDC)
        print(YELLOW + f"Speculative Future Balances Over 252 Trading Days (50 {weekday_chosen}\'s)".center(total_width) + ENDC)
        print(RED + f'Worst Case Without Compounding (Investing start balance each day): ${worst_case_balance_without_compounding:.2f}'.center(total_width) + ENDC)
        print(HEADER + "="*total_width + ENDC)
    else:
        print(RED + "Worst Case Scenario: Data not available".center(total_width) + ENDC)
        print(HEADER + "="*total_width + "\n" + ENDC)
    print(f"Notes:".center(total_width))
    print(f"This will make sure at least the buy and sell is made in the same day".center(total_width))
    print(f"The goal is to find the best trade window statistically".center(total_width))
    print(f"If the ticker already exists from previous runs you might want to delete it to get the latest 60 days".center(total_width))
    print(HEADER + "="*total_width + "\n" + ENDC)
    print(f"Tickers being used in this run: {tickers}".center(total_width))

    # Loop through each ticker to print its details
    for ticker in tickers:
        print("-"*total_width)
        print([{ticker}], ticker_details.get(ticker, f"No hardcoded details available for {ticker}").center(total_width))
weekday_count = 0

# Initialize variables to track the best times and their profit
best_buy_time = None
best_sell_time = None
highest_total_profit = -float('inf')

number_of_unique_days = set()

# Brute-force search for the best buy and sell times
for weekday_chosen in days_to_analyze:
    # Reset variables for the current day's analysis
    highest_total_profit = -float('inf')
    lowest_total_profit = float('inf')
    best_buy_time = None
    best_sell_time = None
    worst_buy_time = None
    worst_sell_time = None

    overall_profit_loss = 0  # Reset profit/loss for the new day
    allocated_balance_per_stock = starting_balance / len(tickers)
    number_of_unique_days = 0  # Reset for each day
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

    # Store the day's results in the daily_results dictionary after the analysis is complete
    daily_results[weekday_chosen] = {
        'best_buy_time': best_buy_time,
        'best_sell_time': best_sell_time,
        'highest_total_profit': highest_total_profit,
        'worst_buy_time': worst_buy_time,
        'worst_sell_time': worst_sell_time,
        'lowest_total_profit': lowest_total_profit,
    }

# ANSI escape codes for colors
RED = '\033[91m'
GREEN = '\033[92m'
RESET = '\033[0m'  # Resets the color to default

# Print the results for each day
if args.day.lower() == 'all':
    
    # Initialize a variable to store the sum of highest profits
    total_highest_profit = 0

    # Iterate through the results to accumulate the highest profits
    for day, results in daily_results.items():
        total_highest_profit += results["highest_total_profit"]
    average_highest_profit_per_day = total_highest_profit / len(daily_results)

    for day, results in daily_results.items():
        print(f'\nFinal Results for {day}:')
        # Use green color for positive profit-related info
        print(GREEN + f'Best Buy Time: {results["best_buy_time"]}, Best Sell Time: {results["best_sell_time"]}, Highest Total Profit Per Day: {results["highest_total_profit"] / number_of_unique_days:.2f}' + RESET)
        if results["worst_buy_time"] and results["worst_sell_time"]:
            # Use red color for negative profit-related info
            print(RED + f'Worst Buy Time: {results["worst_buy_time"]}, Worst Sell Time: {results["worst_sell_time"]}, Lowest Total Profit: {results["lowest_total_profit"] / number_of_unique_days:.2f}' + RESET)
    print(50*"=")
    # Use green for total potential profit statement
    print(GREEN + f'\nTotal Potential Profit for the Week using each days strategy: {total_highest_profit / number_of_unique_days:.2f}' + RESET)
else:
    # Print the best buy and sell times and the highest total profit
    print(f'\nFinal Results for {weekday_chosen}:')
    print(f'Best Buy Time: {best_buy_time}, Best Sell Time: {best_sell_time}, Highest Total Profit Per Day: {highest_total_profit / number_of_unique_days:.2f}')
    if worst_buy_time and worst_sell_time:
        print(f'Worst Buy Time: {worst_buy_time}, Worst Sell Time: {worst_sell_time}, Lowest Total Profit: {lowest_total_profit / number_of_unique_days:.2f}')
    # Save the best buy and sell times to a file named after the weekday
    results_filename = f'{weekday_chosen}.txt'
    with open(results_filename, 'w') as file:
        file.write(f'{weekday_chosen},{best_buy_time.strftime("%H:%M")},{best_sell_time.strftime("%H:%M")}')
