from logging import error
import requests
from bs4 import BeautifulSoup
import pandas
import random
import time
from mongoengine import *



def GoodinfoCrawler(stock):

    stockname = str(stock)
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
    }
    res =  requests.get('https://goodinfo.tw/StockInfo/ShowBuySaleChart.asp?STOCK_ID='+ stockname +'&CHT_CAT=DATE=DATA&PERIOD=365' , headers = headers)

    res.encoding = 'utf-8'

    soup = BeautifulSoup(res.text, 'lxml')
    data = soup.select_one('#divBuySaleDetail')

    try:
        dfs = pandas.read_html(data.prettify())
    except:
        print(error)

    df = dfs[0]
    df.columns = ['Date', 'Close_price', 'Fluctuation', 'Fluctuation_ratio', 'Volume',
                'Foreign_buy', 'Foreign_sell', 'Foreign_buysell_subtract', 'Foreign_sharehold', 'Foreign_sharehold_ratio',
                'InvestmentTrust_buy', 'InvestmentTrust_sell', 'InvestmentTrust_buysell_subtract',
                'Dealer_buy', 'Dealer_sell', 'Dealer_buysell_subtract',
                'Foreign_InvestmentTrust_Dealer_totalbuy', 'Foreign_InvestmentTrust_Dealer_totalsell', 'Foreign_InvestmentTrust_Dealer_totalbuysell_subtract'
                ]
    df.insert(0, 'Stock_id', stock)
    df.insert(0, 'Sort_id', '0')
    cut_lenth = len(df)
    data_cut_times = cut_lenth // 19
    for i in range(0, data_cut_times-1):
        df = df.drop(index = [(i*20)+18,(i*20)+19], axis=0)

    df = df.astype(str)
    df = df.applymap(lambda x: x.replace('+', ''))
    df = df.applymap(lambda x: x.replace(',', ''))

    df.fillna(value=0, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['Sort_id'] = range(1, len(df)+1)
    df['Sort_id'] = df['Sort_id'].astype(int)
    df['Stock_id'] = df['Stock_id'].astype(str)


    delay_choices = [0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7]  # 延遲的秒數
    delay = random.choice(delay_choices)  # 隨機選取秒數
    time.sleep(delay)  # 延遲
    df_json = df.to_dict(orient='records')
    
    return df_json

















