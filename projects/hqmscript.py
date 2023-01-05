# momentum strategy - invest in stocks that have increased the most
# Goal select the 50 stocks with the highest price momentum
# Vlad Petrea

# imports
import numpy as np  # for numerical computing
import pandas as pd  # data science for tabular data
import requests  # http requests
from scipy import stats  # calculate percentile scores
import xlsxwriter  # format and save excel files
from statistics import mean

# import list of stocks and api token
stocks = pd.read_csv('Stocks_in_SP_500.csv')

from secrets import IEX_CLOUD_API_TOKEN


# batch api call
# chunk stocks into gorups of 100
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i: i + n]


symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))

# build Pandas dataframe
hqm_columns = [
    'Ticker',
    'Price',
    'Number of shares to buy',
    'one year price return',
    'one year return percentile',
    'six month price return',
    'six month return percentile',
    'three month price return',
    'three month return percentile',
    'one month price return',
    'one month return percentile',
    'HQM score'
]

hqm_dataframe = pd.DataFrame(columns=hqm_columns)  # creates data frame with hqm columns
for symbol_string in symbol_strings:
    batch_api_call_url = f'https://cloud.iexapis.com/v1/stock/market/batch?symbols={symbol_string}&types=previous,stats&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        hqm_dataframe = hqm_dataframe.append(
            pd.Series(
                [
                    symbol,
                    data[symbol]['previous']['close'],
                    'N/A',
                    data[symbol]['stats']['year1ChangePercent'],
                    'N/A',
                    data[symbol]['stats']['month6ChangePercent'],
                    'N/A',
                    data[symbol]['stats']['month3ChangePercent'],
                    'N/A',
                    data[symbol]['stats']['month1ChangePercent'],
                    'N/A',
                    'N/A'
                ],
                index=hqm_columns),
            ignore_index=True
        )

# list of time periods
time_periods = [
    'one year',
    'six month',
    'three month',
    'one month'
]
# calculate percentile scores
for row in hqm_dataframe.index:
    for time_period in time_periods:
        change_col = f'{time_period} price return'
        percentile_col = f'{time_period} return percentile'
        hqm_dataframe.loc[row, percentile_col] = stats.percentileofscore(hqm_dataframe[change_col], hqm_dataframe.loc[row, change_col])/100

# calculate HQM score which is arithmetic mean of the 4 momentum percentiles previously calculated
# loop over all the rows and for each row add all the momentum percentiles to a list and add the mean of that list into the hqm score col
for row in hqm_dataframe.index:
    momentum_percentiles = []
    for time_period in time_periods:
        momentum_percentiles.append(hqm_dataframe.loc[row, f'{time_period} return percentile'])
    hqm_dataframe.loc[row, 'HQM score'] = mean(momentum_percentiles)

# #remove low HQM stocks
hqm_dataframe.sort_values('HQM score', ascending = False, inplace = True)  # sorts dataframe by HQM score returns in decending order in place
hqm_dataframe = hqm_dataframe[:50]  # take the first 50 rows
hqm_dataframe.reset_index(inplace = True, drop = True)  # reset index in place


# calculating number of shares to buy
def calculate_shares():
    global portfolio_size
    portfolio_size = input('Enter size of portfolio:')

    try:
        float(portfolio_size)
    except ValueError:
        print('that is not a number!')
        portfolio_size = input('Enter the size of your portfolio:')


calculate_shares()

position_size = float(portfolio_size)/len(hqm_dataframe.index)
for i in range(len(hqm_dataframe)):
    hqm_dataframe.loc[i, 'Number of shares to buy'] = position_size // hqm_dataframe.loc[i, 'Price']


# format excel output

writer = pd.ExcelWriter('hqm_strat.xlsx', engine= 'xlsxwriter')
hqm_dataframe.to_excel(writer, sheet_name='hqm_strat', index=False)

# make formats
background_color = '0a0a23'
font_color = 'ffffff'

string_template = writer.book.add_format(
    {
        'font_color': font_color,
        'bg_color': background_color,
        'border': 1
    }
)

dollar_template = writer.book.add_format(
    {
        'num_format': '$0.00',
        'font_color': font_color,
        'bg_color': background_color,
        'border': 1
    }
)

integer_template = writer.book.add_format(
    {
        'num_format': '0',
        'font_color': font_color,
        'bg_color': background_color,
        'border': 1
    }
)

percent_template = writer.book.add_format(
    {
        'num_format': '%00.0',
        'font_color': font_color,
        'bg_color': background_color,
        'border': 1
    }
)

column_formats = {
    'A': ['Ticker', string_template],
    'B': ['Price', dollar_template],
    'C': ['Number of shares to buy', integer_template],
    'D': ['one year Price returns', percent_template],
    'E': ['one year return percentile', percent_template],
    'F': ['six month price return', percent_template],
    'G': ['six month return percentile', percent_template],
    'H': ['three month price return', percent_template],
    'I': ['three month return percentile', percent_template],
    'J': ['one month price return', percent_template],
    'K': ['one month return percentile', percent_template],
    'L': ['HQM score', percent_template]
}

for column in column_formats.keys():
    writer.sheets['hqm_strat'].set_column(f'{column}:{column}', 25, column_formats[column][1])
    writer.sheets['hqm_strat'].write(f'{column}1', column_formats[column][0], column_formats[column][1])

writer.save()
