import socket, time, requests
from bs4 import BeautifulSoup
import pandas as pd

def getStockCurrentPrice(stock_name:str)->tuple:
    """
        args:
            stock_name: str
                stock_name type: 'AKBNK'
        return:
            stock_code: str
            stock_price: float
            stock_daily_change: float
            stock_time: str
    """

    url = "https://borsa.doviz.com/hisseler"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")

    data = soup.find("tr", {"data-name":stock_name})
    if data is None:
        return None
    data = data.text
    data = data.split()
    stock_code = data[0]
    stock_price = float(data[-6].replace(",","."))
    stock_daily_change = float(data[-2].strip().removeprefix("%").replace(",","."))
    stock_time = data[-1]

    return stock_code, stock_price, stock_daily_change, stock_time

def getCurencyPrice(currency_name:str)->float:
    """
        args:
            currency_name: str
                currency_name type: 'USD'
        return:
            currency_price: float
    """

    url = "https://kur.doviz.com/"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")

    data = soup.find("span", {"data-socket-key": currency_name})

    if data is None:
        return "Hata"
    else:
        data = data.text
        if data[-5] == ",":
            data = data.replace(",",".")
            data = float(data)
        elif data[-3] == ",":
            data = data.replace(",",".")
            data = data.replace(".","")
            data = float(data) / 100
        
        return data

def getStockPriceTimeInterval(stock_market:str, initial_date:str, end_dat:str, frequency:str)->pd.Dataframe:
    """
        args:
            stock_market: str
                stock_market type: 'AKBNK'
            initial_date: str
                initial_date type: '01-01-2021'
            end_data: str
                end_data type: '01-01-2021'
            frequency: str
                frequency type: '1'
        return:
            pd.Dataframe
    """

    url = f"https://www.isyatirim.com.tr/_layouts/15/Isyatirim.Website/Common/Data.aspx/HisseTekil?"
    url += f"hisse={stock_market}&startdate={initial_date}&enddate={end_data}&frequency={frequency}.json"
    res = requests.get(url)
    result = res.json()
    
    return pd.DataFrame(result["value"])

    