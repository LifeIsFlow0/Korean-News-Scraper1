from selenium import webdriver
import time
import pandas as pd
import requests
from urllib.request import urlopen
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


df_News_sort = df_News.sort_values(by=["date"], ascending=[False])

#아주경제는 네이버 뉴스에서 지원이 안 됨. 순서대로 중앙일보, 데일리안
urls = ['https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid=025',
        'https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid=119']

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.implicitly_wait(2)

for url in urls:
    driver.get(url)