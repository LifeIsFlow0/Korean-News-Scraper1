from selenium import webdriver
import time
import pandas as pd
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

#뉴스 csv파일 df_News Dataframe으로 로드
df_News = pd.read_excel("News_sort.xlsx", index_col=0)

#뉴스 Dataframe을 'date'column을 기준으로 내림차순 정렬
df_News_sort = df_News.sort_values(by=["PublishDate"], ascending=[False])

#아주경제는 네이버 뉴스에서 지원이 안 됨. 순서대로 중앙일보, 데일리안
#중앙일보025 + "&date={date}&page={i}"
#데일리안119 date ex. 20220506
urls = ['https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid=025',
        'https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid=119']
naver_urls = []
news0=''

#기사 날짜 데이터 추출
df_date = df_News['PublishDate']

#기사 날짜 데이터 최신날짜 추출
date = df_date[0][0:4] + df_date[0][5:7] + df_date[0][8:10]
#print(date)

#df_date에서 가장 오래된 날짜 추출
last_index = df_date.shape[0] - 1
date_last = df_date.iloc[last_index][0:4] + df_date.iloc[last_index][5:7] + df_date.iloc[last_index][8:10]
#print(date_last)

#웹 드라이버
'''driver = webdriver.Chrome(ChromeDriverManager().install())
driver.implicitly_wait(2)'''
process = 0
NB = ['joongang', 'dailian']
#중앙일보, 데일리안 네이버 뉴스 페이지 방문
for url in urls:

    # page가 있으면 저장
    for i in range(1, 2):

        # visit url
        #driver.get(urls[key] + f"&date={date}&page=1")

        # 파싱
        #html = driver.page_source
        html = urlopen(url + f"&date={date}&page=1")
        soup = BeautifulSoup(html, 'html.parser')

        headline_links = soup.find("ul", {"class": "type06_headline"}).find_all('a')

        for headline_link in headline_links:  # 카테고리 별 기사 url 가져오기

            link = headline_link.get('href')  # link 저장
            newsNew = headline_link.select('img')
            # print(newsNew)

            # image 태그에 있는 alt 속성 값 저장(기사 제목)
            for line in newsNew:
                if news0 != line['alt']:  # 앞서 가져온 기사와 같은지 확인
                    news0 = line['alt']
                    naver_urls.append([news0, link])

            # print('\n\n')

        try:  # 없는 경우도 있움
            type_links = soup.find("ul", {"class": "type06"}).find_all('a')

            for type_link in type_links:
                newsNew = type_link.select('img')
                link = headline_link.get('href')

                url_index = link.find('article/') + 7
                comment_link = link[:url_index] + '/comment' + link[url_index:]
                for line in newsNew:
                    if news0 != line['alt']:  # 앞서 가져온 기사와 같은지 확인
                        news0 = line['alt']
                        naver_urls.append([news0, comment_link])
        except:
            pass

    # 저장된 naver 기사 제목과 비교.
    # 맞으면 naver 기사 링크로 들어가서 댓글 더보기 누르기 > 그 다음은 반복
    # 해당 신문사만 dataframe 만들기
    df_News_key = df_News_sort.iloc[NB[process]]

    # 날짜 데이터 형태에 맞게 정리
    date_value = date[0:4] + '-' + date[4:6] + '-' + date[6:8]
    for line in df_News_key[df_News_key['PublishDate'].str.contains(date_value)]:
        for naver_url in naver_urls:
            if naver_url[0] == line['Title']:

                driver = webdriver.Chrome(ChromeDriverManager().install())
                driver.implicitly_wait(2)
                driver.get(naver_url[1])

                while True:
                    try:
                        더보기 = driver.find_element_by_css_selector('a.u_cbox_btn_more')
                        더보기.click()
                        time.sleep(1)
                    except:
                        break

                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                comment = soup.find_all('span', {"class": "u_cbox_contents"})

                # comment
                for line in comment:
                    print(line.string + '\n')
    process += 1
