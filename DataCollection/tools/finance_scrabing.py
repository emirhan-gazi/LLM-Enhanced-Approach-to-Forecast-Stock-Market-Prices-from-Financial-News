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

def getStockPriceTimeInterval(stock_market:str, initial_date:str, end_date:str, frequency:str):
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
    url += f"hisse={stock_market}&startdate={initial_date}&enddate={end_date}&frequency={frequency}.json"
    res = requests.get(url)
    result = res.json()
    
    return result

def apply_change_status(change):
    if change > 1:
        return 2
    elif change < -1:
        return 0
    else:
        return 1

def get_stock_price_changes(stock_names, initial_date, end_date, frequency, save=False):
    datas = []
    for i in stock_names:
        data = getStockPriceTimeInterval(i, initial_date, end_date, frequency)
        datas.append(pd.DataFrame(data["value"]))
    
    new_dfs = []
    names = []
    for i in datas:
        df_tmp = i[["HGDG_HS_KODU", "HGDG_TARIH", "HGDG_KAPANIS", "HGDG_HACIM", "PD", "PD_USD", "DOLAR_BAZLI_AOF"]]
        name = df_tmp["HGDG_HS_KODU"].iloc[0]
        names.append(name)
        df_tmp = df_tmp.rename(columns={"HGDG_HS_KODU": "Stock_Code", "HGDG_TARIH": "Date", "HGDG_KAPANIS": "Last_Price", "HGDG_HACIM": "Volume", "PD": "PD", "PD_USD": "PD_USD", "DOLAR_BAZLI_AOF": "USD_Based_AOF"})
        changes_percentage = []
        for i in range(len(df_tmp["Last_Price"])):
            if i == 0:
                changes_percentage.append(0)
            else:
                changes_percentage.append(round(((df_tmp["Last_Price"].iloc[i] - df_tmp["Last_Price"].iloc[i-1]) / df_tmp["Last_Price"].iloc[i-1]) * 100, 2))
        df_tmp["Changes_Percentage"] = changes_percentage
        df_tmp["Change_Status"] = df_tmp["Changes_Percentage"].apply(apply_change_status)
        df_tmp = df_tmp.iloc[1:]
        if save:
            df_tmp.to_csv(f"stock_prices/{name}.csv", index=False) # Stock prices one by one
        new_dfs.append(df_tmp)

    dates = new_dfs[0]["Date"].values

    dfs_date = []
    for i in dates:
        df = pd.DataFrame()
        for j, n_df in enumerate(new_dfs):
            if i in n_df["Date"].values:
                df_tmp = n_df[n_df["Date"] == i][["Stock_Code","Change_Status","Date"]]
                df = pd.concat([df, df_tmp])
        df.to_csv(f"daily_changes/{i}.csv", index=False)
        dfs_date.append(df)

    actual_df = pd.concat(dfs_date)

    if save:
        actual_df.to_csv("actual_df.csv", index=False)
    
    return actual_df
        
    
