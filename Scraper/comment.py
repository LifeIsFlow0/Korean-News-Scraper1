from selenium import webdriver
import time
import pandas as pd
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager



#아주경제는 네이버 뉴스에서 지원이 안 됨. 순서대로 중앙일보, 데일리안
#중앙일보025 + "&date={date}&page={i}"
#데일리안119 date ex. 20220506
urls = ['https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid=025&listType=title',
        'https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid=119&listType=title']



def CommentCrawl(url, Newspaper):
    # 뉴스 csv파일 df_News Dataframe으로 로드
    df_News = pd.read_excel("News_sort.xlsx", index_col=0)

    # 뉴스 Dataframe을 'date'column을 기준으로 내림차순 정렬
    df_News_sort = df_News.sort_values(by=["PublishDate"], ascending=[False])

    # 네이버 링크 저장
    naver_urls = []
    news0 = ''

    # 댓글 Data저장
    comment_list = []

    # 기사 날짜 데이터 추출
    df_date = df_News['PublishDate']

    # 기사 날짜 데이터 최신날짜 추출
    date = df_date[0][0:4] + df_date[0][5:7] + df_date[0][8:10]
    # print(date)

    # df_date에서 가장 오래된 날짜 추출
    last_index = df_date.shape[0] - 1
    date_last = df_date.iloc[last_index][0:4] + df_date.iloc[last_index][5:7] + df_date.iloc[last_index][8:10]
    # print(date_last)

    # 웹 드라이버
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.implicitly_wait(2)

    # visit url
    driver.get(url + f"&date={date}&page=1")
    driver.implicitly_wait(2)
    # 파싱
    html = driver.page_source
    # html = urlopen(url + f"&date={date}&page=1")
    soup = BeautifulSoup(html, 'html.parser')

    headline_links = soup.find_all("ul", {"class": "type02"})

    for headline_link in headline_links:  # 카테고리 별 기사 url 가져오기
        for line in headline_link.find_all('a'):
            newsNew = line.text
            link = line.get('href')  # link 저장
            # print(newsNew)

            url_index = link.find('article/') + 7
            comment_link = link[:url_index] + '/comment' + link[url_index:]
            print(comment_link)
            if news0 != newsNew:  # 앞서 가져온 기사와 같은지 확인
                news0 = newsNew

                # print(news0, link)
                naver_urls.append([newsNew, comment_link])

        # print('\n\n')

    try:  # 없는 경우도 있움
        type_links = soup.find("ul", {"class": "type06"})

        for line in headline_link.find_all('a'):
            newsNew = line.text
            link = line.get('href')  # link 저장
            # print(newsNew)

            url_index = link.find('article/') + 7
            comment_link = link[:url_index] + '/comment' + link[url_index:]
            print(comment_link)
            if news0 != newsNew:  # 앞서 가져온 기사와 같은지 확인
                news0 = newsNew

                # print(news0, link)
                naver_urls.append([newsNew, comment_link])
    except:
        pass

    df_naver = pd.DataFrame(naver_urls, columns=['title', 'url'])
    # print(df_naver)
    # 저장된 naver 기사 제목과 비교.
    # 맞으면 naver 기사 링크로 들어가서 댓글 더보기 누르기 > 그 다음은 반복
    # 해당 신문사만 dataframe 만들기
    df_News_key = df_News_sort[df_News_sort['Newspaper'].str.contains(Newspaper)]
    # print(df_News_key)
    # 날짜 데이터 형태에 맞게 정리
    date_value = date[0:4] + '-' + date[4:6] + '-' + date[6:8]

    # print(df_News_key[df_News_key['PublishDate'].str.contains(date_value)]['Title'])
    df_News_title = df_News_key[df_News_key['PublishDate'].str.contains(date_value)][['idNews', 'Title']]
    # print(df_News_title)

    for idxNews, Title in df_News_title.iterrows():
        # print(Title[1])
        for idxNaver, row in df_naver.iterrows():
            # print(row)
            if row[0] == Title[1]:

                driver = webdriver.Chrome(ChromeDriverManager().install())
                driver.implicitly_wait(2)
                driver.get(row[1])
                driver.implicitly_wait(2)

                while True:
                    try:
                        더보기 = driver.find_element_by_css_selector('a.u_cbox_btn_more')
                        더보기.click()
                        time.sleep(1)
                    except:
                        break

                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                comment_nick = soup.find_all('span', {"class": "u_cbox_nick"})
                comment_text = soup.find_all('span', {"class": "u_cbox_contents"})

                # comment
                for nick, text in zip(comment_nick, comment_text):
                    # print(nick.string + '\n')
                    # print(text.string + '\n')
                    comment_list.append([idxNews, nick.text, text.text])

                driver.close()
    df_comment = pd.DataFrame(comment_list, columns=['idNews', 'nick', 'text'])
    #print(comment_list)

    return df_comment


#중앙일보, 데일리안 네이버 뉴스 페이지 방문

'''print(urls[0])
url = urls[0]
# page가 있으면 저장
# visit url
driver.get(url + f"&date={date}&page=1")
driver.implicitly_wait(2)
# 파싱
html = driver.page_source
# html = urlopen(url + f"&date={date}&page=1")
soup = BeautifulSoup(html, 'html.parser')

headline_links = soup.find_all("ul", {"class": "type02"})

for headline_link in headline_links:  # 카테고리 별 기사 url 가져오기
    for line in headline_link.find_all('a'):
        newsNew = line.text
        link = line.get('href')  # link 저장
        # print(newsNew)

        url_index = link.find('article/') + 7
        comment_link = link[:url_index] + '/comment' + link[url_index:]
        print(comment_link)
        if news0 != newsNew:  # 앞서 가져온 기사와 같은지 확인
            news0 = newsNew

            # print(news0, link)
            naver_urls.append([newsNew, comment_link])

    # print('\n\n')

try:  # 없는 경우도 있움
    type_links = soup.find("ul", {"class": "type06"})

    for line in headline_link.find_all('a'):
        newsNew = line.text
        link = line.get('href')  # link 저장
        # print(newsNew)

        url_index = link.find('article/') + 7
        comment_link = link[:url_index] + '/comment' + link[url_index:]
        print(comment_link)
        if news0 != newsNew:  # 앞서 가져온 기사와 같은지 확인
            news0 = newsNew

            # print(news0, link)
            naver_urls.append([newsNew, comment_link])
except:
    pass

df_naver = pd.DataFrame(naver_urls, columns=['title', 'url'])
# print(df_naver)
# 저장된 naver 기사 제목과 비교.
# 맞으면 naver 기사 링크로 들어가서 댓글 더보기 누르기 > 그 다음은 반복
# 해당 신문사만 dataframe 만들기
df_News_key = df_News_sort[df_News_sort['Newspaper'].str.contains('joongang')]
# print(df_News_key)
# 날짜 데이터 형태에 맞게 정리
date_value = date[0:4] + '-' + date[4:6] + '-' + date[6:8]

# print(df_News_key[df_News_key['PublishDate'].str.contains(date_value)]['Title'])
df_News_title = df_News_key[df_News_key['PublishDate'].str.contains(date_value)][['idNews', 'Title']]
# print(df_News_title)

for idxNews, Title in df_News_title.iterrows():
    # print(Title[1])
    for idxNaver, row in df_naver.iterrows():
        # print(row)
        if row[0] == Title[1]:

            driver = webdriver.Chrome(ChromeDriverManager().install())
            driver.implicitly_wait(2)
            driver.get(row[1])
            driver.implicitly_wait(2)

            while True:
                try:
                    더보기 = driver.find_element_by_css_selector('a.u_cbox_btn_more')
                    더보기.click()
                    time.sleep(1)
                except:
                    break

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            comment_nick = soup.find_all('span', {"class": "u_cbox_nick"})
            comment_text = soup.find_all('span', {"class": "u_cbox_contents"})

            # comment
            for nick, text in zip(comment_nick, comment_text):
                # print(nick.string + '\n')
                # print(text.string + '\n')
                comment_list.append([idxNews, nick.text, text.text])

            driver.close()

print(comment_list)'''

#print(urls[1])
#url = urls[1]
# page가 있으면 저장

df_comment_JA = CommentCrawl(urls[0], 'joongang')
df_comment_DA = CommentCrawl(urls[1], 'dailian')

df_comment = pd.concat([df_comment_JA, df_comment_DA], ignore_index=True)
#Dataframe 저장
df_comment.to_csv('comment.csv', encoding='utf-8')
df_comment.to_excel('comment.xlsx', encoding='utf-8', sheet_name='comment')