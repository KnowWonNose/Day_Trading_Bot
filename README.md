## 1. Stock Market Data

I don't think the stock info (MA, EMA, etc...) is perfectly accurate (at least not when compared to Robinhood)

line 50, need to see if its the imported data, my set parameters, or I am calculating it wrong

It does seem proportionally correct, but that could throw off the trading algorythm

## 2. Volitily + RA

UpdatedBot trades concurrently. it can do really well for specific stocks but it is struggling to find a good inputs that work for all of them

Maybe add RSI and trade differently based on volotility. certain stocks have different trends

Also, need to figure out how much to buy depending on how many stocks. Do I leave extra uninvested money in the s&p 500 like a bank and withdraw when i want to buy a specific stock?

## 3. Bias

I am investing in todays s&p 500. This knowledge was not known 20 years ago

should I make trades based on each the specific day's s&p 500?(that would take the bot longer and require more code) Or only invest in the top 100.... top 10?

Or I could only do the volatile ones like Tesla

Or I could look at todays largest volatile stocks and try to ride one if it goes past 90%. try to play safe and scrape the next 5%

## 3. Graphing

Graph at the end is for all trading, useful for testing individual stocks but it should be improved or changed

