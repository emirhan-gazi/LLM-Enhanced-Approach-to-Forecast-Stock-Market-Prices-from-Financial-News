import requests
from bs4 import BeautifulSoup
import pandas as pd 
import datetime



def function_it_and_create_dataframe(news:list): 
    """
        args:
            news: list
                news type: [{'title': '...', 'link': '...', 'date': '...'}, ...]
        return: 
            pd.Dataframe
    """
    main_url = 'https://www.bloomberght.com'
    data = []
    for i in range(len(news)):
        urls = main_url + news[i]['link']
        response = requests.get(urls)
        soup = BeautifulSoup(response.content, 'html.parser')
        article_containers = soup.find_all('article', {'class': 'content'})
        last_text = ''
        for article in article_containers:
            for text in article.find_all('p'):
                last_text += text.text.strip() + " "

        data.append({'title': news[i]['title'], 'link': news[i]['link'], 'text': last_text, 'date': news[i]['date']})
    
    df = pd.DataFrame(data)
    return df


def convdate2datetime(date:str) -> datetime.datetime:
    """
        args:
            date: str
                date type: dd-mm-yyyy

        return:
            datetime.datetime

    """
    day = date.split('-')[0]
    month = date.split('-')[1]
    year = date.split('-')[2]

    return datetime.datetime.strptime(f'{day}-{month}-{year}', '%d-%m-%Y')

def convlist2datetime(date : list) -> datetime.datetime:
    """
        args:
            date: list
                date type: ['01', 'Ocak', '2021']

        return:
            datetime.datetime

    """

    day = date[0]
    month = date[1]
    year = date[2]

    if month == 'Ocak':
        month = '01'
    elif month == 'Şubat':
        month = '02'
    elif month == 'Mart':
        month = '03'
    elif month == 'Nisan':
        month = '04'
    elif month == 'Mayıs':
        month = '05'
    elif month == 'Haziran':
        month = '06'
    elif month == 'Temmuz':
        month = '07'
    elif month == 'Ağustos':
        month = '08'
    elif month == 'Eylül':
        month = '09'
    elif month == 'Ekim':
        month = '10'
    elif month == 'Kasım':
        month = '11'
    elif month == 'Aralık':
        month = '12'
    
    return convdate2datetime(f'{day}-{month}-{year}')


def get_news(initial:str, end:str):  
    """
        args:
            initial: str
                initial date type: dd-mm-yyyy
            end: str
                end date type: dd-mm-yyyy
        return:
            pd.core.frame.DataFrame
    """

    main_url = 'https://www.bloomberght.com/tum-ekonomi-haberleri'
    url = 'https://www.bloomberght.com/tum-ekonomi-haberleri'

    initial_Dt = convdate2datetime(initial)
    end_Dt = convdate2datetime(end)

    count = 1
    dfs = []
    while True:
        url = main_url + f"/{count}"
        response = requests.get(url)
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        news_containers = soup.find_all('div', {'class': 'widget-news-list type1'})
        news_time = news_containers[0].find_all('a')[1].find('span', {'class': 'date'}).text.strip().split(' ')[0:3] # news date
        news_time = convlist2datetime(news_time)
        if initial_Dt <= news_time <= end_Dt:
            print('In the process.......')
            news_containers = soup.find_all('div', {'class': 'widget-news-list type1'})
            articles = []
            for all_article in news_containers:
                for article in all_article.find_all('a'):
                    title = article.find('span', {'class': 'title'}).text.strip()
                    date = article.find('span', {'class': 'date'}).text.strip()
                    link = article['href']
                    articles.append({'title': title, 'link': link, 'date': date})

        

            df = function_it_and_create_dataframe(articles)
            dfs.append(df)

        elif news_time < initial_Dt: 
            break
        count +=1          
        

    return pd.concat(dfs)
