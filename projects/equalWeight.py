import numpy as np
import pandas as pd
import requests
import math

#pull sp500 tickers
stocks = pd.read_csv('sp_500_stocks.csv')

#symbol = 'AAPL'
#price = data['latestPrice']
#market_cap = data['marketCap']

#create columns for dataframe and make pd dataframe
my_columns = ['Ticker', 'Stock Price', 'Market Cap', 'Num of Shares']
# final_dataframe = pd.DataFrame(columns = my_columns)
#
# #loop through list of stocks and get info from api call
# for stock in stocks['Ticker'][:5]:
#     api_url = f'https://sandbox.iexapis.com/stable/stock/{stock}/quote/?token=Tpk_059b97af715d417d9f49f50b51b1c448'
#     data = requests.get(api_url).json()
#     final_dataframe = final_dataframe.append(
#         pd.Series(
#             [
#                 stock,
#                 data['latestPrice'],
#                 data['marketCap'],
#                 'N/A'
#             ],
#             index = my_columns
#         ),
#         ignore_index=True
#     )

#a function to split up the list of sp500
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
final_dataframe = pd.DataFrame(columns = my_columns)

for symbol_string in symbol_strings:
    batch_api_call = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote&token=Tpk_059b97af715d417d9f49f50b51b1c448'
    data = requests.get(batch_api_call).json()
    for symbol in symbol_string.split(','):
        final_dataframe = final_dataframe.append(
            pd.Series(
                [
                    symbol,
                    data[symbol]['quote']['latestPrice'],
                    data[symbol]['quote']['marketCap'],
                    'N/A'
                ],index = my_columns
            ),
            ignore_index = True
        )

#             symbol,
#             price,
#             market_cap,
#             'N/A'
#         ],
#         index = my_columns
#     ),
#     ignore_index = True
# )
