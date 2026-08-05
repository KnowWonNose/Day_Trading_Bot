# -------------------------------
# Import Libraries
# -------------------------------
import pandas as pd
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
                'PYPL', 'NFLX', 'INTC', 'INTU', 'CSCO', 'PEP', 'TMO', 'NEE', 'LLY', 'ORCL',
                'MRK', 'ABT', 'CRM', 'AMGN', 'MDT', 'QCOM', 'TXN', 'LOW', 'UNP', 'UPS',
                'BA', 'CAT', 'GS', 'SPGI', 'DE', 'MMM', 'GE', 'LMT', 'RTX', 'HON'
        ]
    
    if option == 2:
        return ['BTC-USD']
    
    else:
        return ['AAPL']  # Test with a single stock
    #'ETH-USD' #'BTC-USD'
# INTC



def Get_Stock_Data(symbol, timeframe='1wk', period='10y'):
    df = yf.download(
        tickers=symbol,
        interval=timeframe,
        period=period,    # or for specifice range:  start="2021-01-01", end="2023-05-01",
        auto_adjust=True, #this was normally false
        progress=False
    )

    df.dropna(inplace=True)

    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA50'] = df['Close'].ewm(span=40, adjust=False).mean()
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA50'] = df['Close'].rolling(50).mean()

    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    df['ATR'] = df['TR'].rolling(14).mean()
    return df
    # df = yf.download(
    # tickers=symbol,
    # interval=timeframe,
    # period=period,
    # auto_adjust=True,
    # progress=False
    # )

    # df.dropna(inplace=True)

    # # Moving averages
    # df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    # df['EMA50'] = df['Close'].ewm(span=40, adjust=False).mean()

    # df['MA20'] = df['Close'].rolling(20).mean()
    # df['MA50'] = df['Close'].rolling(50).mean()

    # # ATR
    # df['H-L'] = df['High'] - df['Low']
    # df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    # df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))

    # df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    # df['ATR'] = df['TR'].ewm(alpha=1/14, adjust=False).mean()

    # return df



def generate_signals(df):
    df['signal'] = 0
    df.loc[(df['EMA20'] > df['MA20']) & (df['EMA50'] > df['MA50']), 'signal'] = 1
    df.loc[df['EMA20'] < df['MA20'], 'signal'] = -1
    df.loc[df['EMA50'] < df['MA50'], 'signal'] = -1 

    # df.loc[(df['EMA20'] > df['MA20'] + (df['EMA20']/70)) & (df['EMA50'] > df['MA50'] + (df['EMA50']/90)), 'signal'] = 1
    # df.loc[df['EMA20'] < df['MA20'] - (df['EMA20']/100), 'signal'] = -1
    # df.loc[df['EMA50'] < df['MA50'] - (df['EMA50']/70), 'signal'] = -1 

    return df


# -------------------------------
# 1. Fetch Historical Data
# -------------------------------

allBuysDates = []
allSellsDates = []
eachCompaniesTotalProfit = []
orderedCompaniesProfit = []
grandProfit = 0.0
number_of_trades = 0
number_of_current_trades = 0
buyToday = []
sellToday = []
number_of_trades = 0

allStocks = Get_Stock_Symbols(1)

for symbol in allStocks:
    
    investment = 1   # Amount to invest per trade
    stop_loss_pct = 0.15  # 15%
    cooldown_days = 5

    profit = totalCompanyProfit = position = 0.0
    cooldown_counter = 0

    data = Get_Stock_Data(symbol)
    data = generate_signals(data)

    for i in range(1, len(data)): #each day of trading?
    
        # -------------------------------
        # On Cooldown?
        # -------------------------------
        if cooldown_counter > 0:
            cooldown_counter -= 1
            continue  # Skip trading during cooldown



        signal = float(data['signal'].iloc[i])
        close_price = float(data['Close'].iloc[i].item())

        # -------------------------------
        # BUY?
        # -------------------------------
        # if data.index[i].date() == date(2021,8,23):
        #         print("found it")
        #         # print(data[['EMA20', 'MA20', 'EMA50', 'MA50']])
        #         print(data.loc['2021-08-23', ['EMA20', 'MA20', 'EMA50', 'MA50']])
        #         print("fodsfsgdund it")
        if signal == 1 and position == 0.0:     #if buy signal and no currently held stock
            # print(any(data.index.date == date(2021, 8, 23)))
            
            # if data.index[i].date() == date(2021,8,23):
            #     print("found it")
            #     print( data['EMA20'], data['EMA50'], data['MA20'], data['MA50'])
            position = investment / close_price
            entry_price = close_price
            profit = 0.0
            print(f"Day {data.index[i].date()} - BUY @ {entry_price:.2f}")

            allBuysDates.append(data.index[i].date())

            if data.index[i].date() == date.today():
                # print(symbol, data.index[i].date())
                buyToday.append(symbol)
            

        # -------------------------------
        # HOLD POSITION (Check Stop Loss)
        # -------------------------------
        elif position > 0.0:
            # Check for stop loss within the candle
            stop_loss_price = entry_price * (1 - stop_loss_pct)
            low_price = float(data['Low'].iloc[i].item())

            # If price dipped below stop loss, sell at stop loss price
            if low_price <= stop_loss_price:
                trade_return = position * stop_loss_price  # assume stop executed at stop-loss price
                position = 0.0
                number_of_trades += 1
                profit = (trade_return - investment) / investment * 100
                totalCompanyProfit += profit
                print(f"Day {data.index[i].date()} - STOP LOSS HIT @ {stop_loss_price:.2f} ({profit:.2f}%)")
                allSellsDates.append(data.index[i].date())
                if data.index[i].date() == date.today():
                    sellToday.append(symbol)
                cooldown_counter = cooldown_days
                continue  # skip further checks for this candle

            # Else normal sell signal
            elif signal == -1:
                trade_return = position * close_price
                position = 0.0
                number_of_trades += 1
                profit = (trade_return - investment) / investment * 100
                totalCompanyProfit += profit
                print(f"Day {data.index[i].date()} - SELL @ {close_price:.2f} ({profit:.2f}%)")
                if data.index[i].date() == date.today():
                    sellToday.append(symbol)
                allSellsDates.append(data.index[i].date())


    # Close remaining position at end
    if position > 0.0:
        trade_return = position * close_price
        position = 0.0
        number_of_trades += 1
        number_of_current_trades += 1
        profit = (trade_return - investment) / investment * 100
        totalCompanyProfit += profit
        print(f"Current day {data.index[i].date()} - SELL @ {close_price:.2f} ({profit:.2f}%)")

   



    
    eachCompaniesTotalProfit.append(symbol + ": \t" + f"{totalCompanyProfit : .2f}%")
    grandProfit += totalCompanyProfit
    orderedCompaniesProfit.append(f"{totalCompanyProfit : .2f}")




allBuysDates = sorted(allBuysDates)
allSellsDates = sorted(allSellsDates)

# Define your range
start_date = date(2024, 10, 27)
end_date = date(2025, 10, 27)

# print(type(allBuysDates[0]))
# print(type(end_date))
bought = 0
maxBought = 0

# Iterate through each day
current = start_date
while current <= end_date:
    if current in allBuysDates:
        # print("i bought")
        bought += 1
    elif current in allSellsDates:
        bought -= 1

    if bought > maxBought:
        maxBought = bought


    current += timedelta(days=1)
    

# print(maxBought)
# # If you want them back as strings:
# sorted_strings = [d.strftime("%Y-%m-%d") for d in sorted_dates]
# print(sorted_strings)



# allBuysDates





print("\n----- FINAL RESULTS -----")
print(f"Initial balance: ${(number_of_trades * investment):,.2f}")
print(f"Final profit:   ${grandProfit * investment + number_of_trades * investment:,.2f}")
print(f"Profit/Loss:     ${grandProfit * investment / 100:,.2f}")
print(f"Return:           {grandProfit:.2f}%")
print(f"Number of trades: {number_of_trades}")
print(f"avg profit per company: {grandProfit / len(allStocks):.2f}%")
print(f"Trades not finished: {number_of_current_trades}")




# print('\n'.join(eachCompaniesTotalProfit))

# orderedCompaniesProfit.sort(key = float)
# print('\n'.join(orderedCompaniesProfit))


# orderedCompaniesProfit = [float(x) for x in orderedCompaniesProfit if x != "0.00"]

# print(f" percents adds up to : {sum(orderedCompaniesProfit)}%")

print("Stocks to buy today:")
for stock in buyToday:
    print(stock)

print("\n Stocks to sell today:")
for stock in sellToday:
    print(stock)


# -------------------------------
# 6. Plot Price and Signals
# -------------------------------
plt.figure(figsize=(14,7))
plt.plot(data['Close'], label='Price', color='blue')
plt.plot(data['EMA20'], label='EMA20', color='red')
plt.plot(data['EMA50'], label='EMA50', color='purple')
plt.plot(data['MA20'], label='MA20', color='green', linestyle='--')
plt.plot(data['MA50'], label='MA50', color='black', linestyle='--')

buy_signals = data[data['signal'] == 1]
sell_signals = data[data['signal'] == -1]
plt.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='green', label='Buy', s=100)
plt.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='red', label='Sell', s=10)

plt.title(f"{symbol} Backtest: EMA + MA Strategy + Stop Loss ({stop_loss_pct*100:.1f}% & {cooldown_days}-day cooldown)")
plt.xlabel("Time")
plt.ylabel("Price (USD)")
plt.legend()
plt.show()



if buyToday != []:

    # === Replace these with your info ===
    phone_number = "5132187957"  # your 10-digit number
    carrier_gateway = "vtext.com"  # e.g. AT&T: txt.att.net, Verizon: vtext.com
    to_number = f"{phone_number}@{carrier_gateway}"

    from_email = "njmcclorey@gmail.com"
    app_password = "qwuk vyuu rujh cobz"  # use an App Password (see below)

    msg = MIMEText("Stocks to buy today:\n" + '\n'.join(buyToday))
    msg["From"] = from_email
    msg["To"] = to_number
    msg["Subject"] = ""  # SMS doesn't need a subject

    # Send the email (which becomes an SMS)
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(from_email, app_password)
        server.send_message(msg)

    print("✅ Text message sent!")