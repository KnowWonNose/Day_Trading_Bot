# -------------------------------
# Import Libraries
# -------------------------------
import pandas as pd
from pandas.tseries.offsets import DateOffset
from io import StringIO
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import requests
from datetime import date, timedelta
import smtplib
from email.mime.text import MIMEText

# -------------------------------
# Define Functions
# -------------------------------

def Get_Stock_Symbols(option):

    if option == 0:
                
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        html = requests.get(url, headers=headers).text
        table = pd.read_html(StringIO(html))[0]
        allStocks = table['Symbol'].tolist()
        allStocks = [s.replace(".", "-") for s in allStocks]
        allStocks.extend(['BTC-USD', 'ETH-USD', '^GSPC', 'CCJ'])  # Add Bitcoin to the list
        print("Grabbing", len(allStocks), "stocks from S&P500")
        return allStocks

    if option == 1:
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'BRK-B', 'TSLA', 'JPM', 'JNJ',
                'V', 'WMT', 'UNH', 'HD', 'DIS', 'BAC', 'XOM', 'VZ', 'ADBE', 'CMCSA',
                 'NFLX', 'INTU', 'CSCO', 'PEP', 'TMO', 'NEE', 'LLY', 'ORCL',
                'MRK', 'ABT', 'CRM', 'AMGN', 'MDT', 'QCOM', 'TXN', 'LOW', 'UNP', 'UPS',
                'BA', 'CAT', 'GS', 'SPGI', 'DE', 'MMM', 'GE', 'LMT', 'RTX', 'HON',
        ]
    
    if option == 2:
        return ['MSFT']
    
    else:
        return ['HON']  # Test with a single stock
    #'ETH-USD' #'BTC-USD'
# INTC



def Get_Stock_Data(symbol, timeframe='1d', period='10y'):
    # df = yf.download(
    #     tickers=symbol,
    #     interval=timeframe,
    #     period=period,    # or for specifice range:  start="2021-01-01", end="2023-05-01",
    #     auto_adjust=True, #this was normally false
    #     progress=False
    # )

    # if isinstance(df.columns, pd.MultiIndex):
    #     df.columns = df.columns.get_level_values(0)

    # df.dropna(inplace=True)

    # df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    # df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    # df['MA20'] = df['Close'].rolling(20).mean()
    # df['MA50'] = df['Close'].rolling(50).mean()

    # df['H-L'] = df['High'] - df['Low']
    # df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    # df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
    # df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    # df['ATR'] = df['TR'].rolling(14).mean()
    # return df
    df = yf.download(
        tickers=symbol,
        interval=timeframe,
        period=period,
        # start="2001-01-01",
        # end="2014-01-01",   # end is exclusive
        auto_adjust=False,
        progress=False,
        multi_level_index=False
    )

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.dropna(inplace=True)

    # Moving averages
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()

    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA50'] = df['Close'].rolling(50).mean()
    df['MA100'] = df['Close'].rolling(100).mean()

    # ATR
    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))

    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    df['ATR'] = df['TR'].ewm(alpha=1/14, adjust=False).mean()

    # RSI
    delta = df['Close'].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()

    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    df.dropna(inplace=True)


    # Then keep only the last 5 years
    cutoff = df.index.max() - DateOffset(years=5)
    df = df[df.index >= cutoff]

    return df

def generate_signals(df):


    
    df['signal'] = 0
    # ---------------------------------------------------------------------------------------------------------
    # IMPORTANT PART OF THE CODE IS HERE, THIS IS WHERE I DECIDE TO BUY AND SELL BASED ON THE MOVING AVERAGES
    # df.loc[(df['EMA20'] > df['MA20']) & (df['EMA50'] > df['MA50']), 'signal'] = 1
    # df.loc[df['EMA20'] < df['MA20'], 'signal'] = -1
    # df.loc[df['EMA50'] < df['MA50'], 'signal'] = -1 
    # ---------------------------------------------------------------------------------------------------------

# really good
    # df.loc[(df['EMA20'] > df['MA20'] + (df['EMA20']/30)) & (df['EMA50'] > df['MA50'] + (df['EMA50']/90)), 'signal'] = 1
    # df.loc[df['EMA20'] < df['MA20'] - (df['EMA20']/100), 'signal'] = -1
    # df.loc[df['EMA50'] < df['MA50'] - (df['EMA50']/70), 'signal'] = -1 


    # really good
    # df.loc[(df['EMA20'] > df['MA20'] + (df['EMA20']/70)) & (df['EMA50'] > df['MA50'] + (df['EMA50']/90)), 'signal'] = 1
    # df.loc[df['EMA20'] < df['MA20'] - (df['EMA20']/100), 'signal'] = -1
    # df.loc[df['EMA50'] < df['MA50'] - (df['EMA50']/70), 'signal'] = -1 


    # df.loc[(df['MA20'] < df['EMA20']) & (df['EMA20'] < df['EMA50']) & (df['EMA50'] < df['MA50']), 'signal'] = 1

    # df.loc[(df['RSI'] > 80), 'signal'] = -1
    
    # df.loc[(df['RSI'] < 20), 'signal'] = 1
    
    df.loc[(df['EMA20'] > df['MA20'] + 1) &
    (df['EMA50'] > df['MA50']), 'signal'] = 1
    

    df.loc[(df['EMA20'] < df['MA20']) &
    (df['EMA50'] < df['MA50']), 'signal'] = -1


    # df.loc[(df['MA100'] > df['MA20']), 'signal'] = 1


    
    # date = "2022-06-30"

    # print(df.loc[:date].tail(10)[['Close','EMA20','EMA50','MA20','MA50']])


    # print(df.loc[date, [
    #     'Close',
    #     'EMA20',
    #     'EMA50',
    #     'MA20',
    #     'MA50',
    #     'MA100',
    #     'ATR',
      
    # ]])

    return df

#THIS DECIDES WHAT STOCKS TO BUY AND SELL, this parameter is the options as shown with the Get_Stock_Symbols function. 
# 0 = S&P500, 1 = my list of 50 stocks, 2 = BTC-USD, else = AAPL
allStockSymbols = Get_Stock_Symbols(2)

portfolio_history = []
numberOfCurrentPositions = 0
totalBuys = 0
totalSells = 0
maxNumberOfCurrentPositions = 0
all_percent_returns = []  # List to keep track of all percent returns for each trade
all_data = {}

wallet = Starting_wallet = 10000  # Starting wallet amount

# Load every stock first
for symbol in allStockSymbols:

    data = generate_signals(Get_Stock_Data(symbol))

    if len(data) == 0:
        print("Skipping", symbol, "- no data")
        continue

    all_data[symbol] = {
        "data": data,
        "position": None, #if in position, this will be the price we bought at, otherwise None
        "investment": 0,  # Amount invested in this stock
        "total_company_trades": 0  # Total trades made for this stock
    }

for current_day in range(len(all_data[allStockSymbols[0]]["data"])):  # FOR EACH DAY/WEEK 


# ---------------------------NO STOP LOSS YET---------------------------

    #SELLING STOCKS FIRST
    for symbol in allStockSymbols: #for each stock
        stock = all_data[symbol]

        if current_day >= len(stock["data"]): # check if stock data exists for the current day
            # print(f"Current day {current_day} - No data available for {symbol}")
            continue

        

        stockCurrentDay = stock["data"].iloc[current_day]

        

        if stock["position"] is not None:  # if we own it

            sell_price = stockCurrentDay["Close"]   #price if we sold
            percent_return = (sell_price - stock["position"]) / stock["position"]   # calculate percent profit/loss

            if stockCurrentDay["signal"] == -1 or percent_return < -0.15:  # if the signal is to sell or we hit the stop loss, sell it

                # Sell the stock
                if percent_return < -0.15:
                    percent_return = -0.15  # cap the loss at -15%
                profit = percent_return * stock["investment"]  # calculate dollar profit/loss from the trade
                wallet += stock["investment"] + profit  # Add profit/loss to wallet
                print(f"Current day {stock['data'].index[current_day].date()} - SELL {symbol} @ {sell_price:.2f} | Profit: ${profit:.2f} | Return: {percent_return:.2%}")  # print the date, price we sold at, and profit and percent made
                stock["position"] = None  # Reset position
                stock["investment"] = 0  # Reset investment
                numberOfCurrentPositions -= 1
                totalSells += 1  #keep track of how many trades we have made in total
                all_percent_returns.append(percent_return)  #keep track of all percent returns for each trade
                continue

    #BUYING STOCKS SECOND
    for symbol in allStockSymbols: #for each stock
        stock = all_data[symbol]

        if current_day >= len(stock["data"]): # check if stock data exists for the current day
            continue

        stockCurrentDay = stock["data"].iloc[current_day]
        if stock["position"] is None and stockCurrentDay["signal"] == 1 and numberOfCurrentPositions < 15: #if we don't own it and the signal is to buy

            # Buy the stock
            # --------------------------------------------------------------------------------
            # IMPORTANT PART OF THE CODE IS HERE, THIS IS WHERE I DECIDE HOW MUCH TO INVEST IN A STOCK

            #
            # stock["investment"] =  wallet / (len(allStockSymbols) - numberOfCurrentPositions)  # divides wallet by the number of stocks we don't own to determine how much to invest in this stock
            
            stock["investment"] =  wallet  # divides wallet by the number of stocks we don't own to determine how much to invest in this stock
             #divides wallet by the number of stocks we don't own to determine how much to invest in this stock
            # I should probably invest more and base it off the usual max positions I will ever hold
            # The current method under-invests because it reserves money for stocks that may never trigger.
            #
            #       Idea:
            #   what if whatever is in the wallet is put into the s&p 500 and when money is needed we remove what we need?
#           -  -------------------------------------------------------------------------------

            wallet -= stock["investment"]  #subtract the amount we invested from the wallet
            stock["position"] = stockCurrentDay["Close"] #save the price we bought at
            print(f"Current day {stock['data'].index[current_day].date()} - BUY {symbol} @ {stock['position']:.2f}")    #print the date and price we bought at
        
            stock["total_company_trades"] += 1  #increment the total trades for this stock
            numberOfCurrentPositions += 1  #increment the number of current trades we have
            totalBuys += 1  #keep track of how many trades we have made in total



    # I want to track the maximum number of trades that were open at any point in time.
    if maxNumberOfCurrentPositions < numberOfCurrentPositions:
        maxNumberOfCurrentPositions = numberOfCurrentPositions


    # weekly profit and loss graph at the end of the code 
    current_value = wallet
    for stock in all_data.values():
        if stock["position"] is not None and current_day < len(stock["data"]):
            current_price = stock["data"].iloc[current_day]["Close"]
            current_value += stock["investment"] * (current_price / stock["position"])
    portfolio_history.append(current_value)
            

    # #End of day summary
    # print(f"wallet: ${wallet:.2f} | # of Trades not sold: {numberOfCurrentPositions}")


#-------------------------------END OF SIMULATION--------------------------------

# this was an auto complete print and needs to be checked for accuracy
#selling everything, your new net value is:

portfolio_value = wallet

for stock in all_data.values():
    if stock["position"] is not None:
        last_price = stock["data"]["Close"].iloc[-1]
        portfolio_value += stock["investment"] * (
            last_price / stock["position"]
        )

print("\n\n\n----- FINAL RESULTS -----\n")

print(f"Portfolio value if sold today: ${portfolio_value:.2f}")
print(f"wallet: ${wallet:.2f} | # of Trades not sold: {numberOfCurrentPositions}\n")

print(f"Total percent return (portfolio value): {((portfolio_value - Starting_wallet) / Starting_wallet) * 100:.2f}%\n(this is the total percent profit which needs to beat the s&p 500 over the same time period)")
# print(f"avg trade return: {((wallet - Starting_wallet) / Starting_wallet) * 100 / totalBuys:.2f}% ") This is wrong because it doesn't account for the trades that are still open and not sold yet. also idk if compounding affects it
print(f"avg percent return = {sum(all_percent_returns) / len(all_percent_returns) * 100:.2f}%")  # Format percent returns for printing
print(f"Total # of trades buys: {totalBuys}")
print(f"Total # of trades sells: {totalSells}")
print(f"Max # of trades open at any point in time: {maxNumberOfCurrentPositions}")




# GRAPH OF PORTFOLIO VALUE OVER TIME
plt.plot(portfolio_history)
plt.title("Portfolio Value")
plt.ylabel("$")
plt.xlabel("Weeks")
plt.show()

# THIS is somthing ai gave me that might help my graph look better, Not my main focus rn
# peak = portfolio_history[0]
# max_drawdown = 0

# for value in portfolio_history:
#     if value > peak:
#         peak = value

#     drawdown = (value - peak) / peak

#     if drawdown < max_drawdown:
#         max_drawdown = drawdown

# print(f"Max Drawdown: {max_drawdown:.2%}")








# compare against S&P 500 correctly

# For a fair comparison, download:
#   ^GSPC

# with the same:
#   interval='1wk'
#   period='10y'

# Then calculate:
#   SP500_return = (end_price - start_price) / start_price

# Your strategy needs to beat:
#   S&P 500 return
#   + lower drawdown
#   + reasonable trade count