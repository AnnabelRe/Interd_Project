import pandas as pd
import pickle
import requests
from bs4 import BeautifulSoup
from loguru import logger
from tqdm.contrib.concurrent import thread_map



url = "http://openinsider.com/screener?s={ticker}&o=&pl=&ph=&ll=&lh=&fd=0&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page={page_no}"

nasdaq = pd.read_excel("/Users/admin/Documents/Interd Project/data/ISIN_merge.xlsx") 
TICKERS = nasdaq['TICKER SYMBOL'].tolist()

import_length = 1000
downloads_count = int(len(TICKERS)/import_length)+1


def fetch_content(url: str) -> str:
    """Does exactly what it says"""
    try:
        re = requests.get(url).content.decode("utf8")
        return re
    except Exception as e:
        #logger.warning(f"Something went wrong with the URL:{url}\nError:{e}")
        return None


def process_content(content: bytes) -> pd.DataFrame:
    """Processes the extracted content and returns daatframe that holds the required info or no info at all"""
    soup = BeautifulSoup(content, "html.parser")

    # get header first
    table = soup.find("table", {"class": "tinytable"})
    #logger.info(f"Type of the Table:{type(table)}")

    if not table:
        #logger.warning(f"Found nothing, so we return an empty dataframe")
        return pd.DataFrame()

    # headers are in the "th" tag of the table, so we extract all th tags

    headers = [header.text for header in table.find_all("th")]
    rows = []

    for row in table.find_all("tr"):
        row_content = [r.text for r in row.find_all("td")]
        if row_content:
            rows.append(row_content)
    
    df = pd.DataFrame(rows, columns=headers)
    
    return df

def run_download(ticker: str) -> pd.DataFrame:   
    data = []
    for page in range(20):
        url_ = url.format(ticker=ticker, page_no=page)
        content = fetch_content(url_)
        if not content:
            break
        df = process_content(content)
        if df.empty:
            break
        df["original_Ticker"]= ticker
        data.append(df)
    if not data:
        return pd.DataFrame()
    return pd.concat(data)


def main(i):
    start_idx= 1000*i
    tickers_subset = TICKERS[start_idx:(start_idx+import_length)]
    #print(start_idx,(start_idx+import_length))
    dfs = thread_map(run_download,tickers_subset)
    dfs = pd.concat(dfs)
    return dfs


if __name__ == "__main__":       
    count = 0
    for count in range(count,downloads_count):
        data = main(count)
        name=str(count)
        file = open("/Users/admin/Documents/Interd Project/data/DD_download/results_" + name + ".pkl", 'wb')
        pickle.dump(data, file)
        file.close()
        count+=1



