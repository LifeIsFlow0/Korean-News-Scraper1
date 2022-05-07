from selenium import webdriver
import time
import pandas as pd
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

#뉴스 csv파일 df_News Dataframe으로 로드
df_News = pd.read_csv("News.csv", index_col=0)

#뉴스 Dataframe을 'date'column을 기준으로 내림차순 정렬
df_News_sort = df_News.sort_values(by=["PublishDate"], ascending=[False])

#아주경제는 네이버 뉴스에서 지원이 안 됨. 순서대로 중앙일보, 데일리안
#중앙일보025 + "&date={date}&page={i}"
#데일리안119 date ex. 20220506
urls = ['https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid=025',
        'https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid=119']

#웹 드라이버
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.implicitly_wait(2)

#중앙일보, 데일리안 네이버 뉴스 페이지 방문
for url in urls:

    try:
        #page가 있으면 저장
        for i in range(1, 50):
            #visit url
            driver.get(url + f"&date={date}&page={i}")

            #
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            headline_links = soup.find("ul", {"class": "type06_headline"}).find_all('a')


            for headline_link in headline_links:  # 카테고리 별 기사 url 가져오기
                newsNew = headline_link.select('img')
                # print(newsNew)
                for line in newsNew:
                    if news0 != line['alt']:  # 앞서 가져온 기사와 같은지 확인
                        news0 = line['alt']
                        #print(news0)


                # print('\n\n')

            try:
                type_links = soup.find("ul", {"class": "type06"}).find_all('a')

                for type_link in type_links:

                    newsNew = type_link.select('img')
                    for line in newsNew:
                        if news0 != line['alt']:  # 앞서 가져온 기사와 같은지 확인
                            news0 = line['alt']
                            print(news0)
            except:
                pass

    except:
        #저장된 naver 기사 제목과 비교.
        #맞으면 naver 기사 링크로 들어가서 댓글 더보기 누르기 > 그 다음은 반복
        #news
        for line in df_News_sort:
            if line.loc['Newspaper'] == "ajunews":
                continue

            for naver_url in naver_urls:
