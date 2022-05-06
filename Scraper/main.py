# newspaper3k, selenium, webdriver, webdriver_manager인가 webdrivermanager, requests, urllib, beautifulsoup4 라이브러리 추가

from newspaper import Article
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
import time

from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# 스크래퍼 클래스
class Scraper:

    def __init__(self):  # 솔직히 __init__은 클래스에 있어야 할 것 같아서 그냥 넣어봄
        pass

    def joongang(JAList):  # 중앙일보 스크래핑 함수. 아래 주석들은 코드 작성 과정에서 메모한 것. 지워도 됨
        # 중앙일보 정치 카테고리에서 기사 스크래핑하는 코드
        # 중앙일보는 <ul class: "story_list"> -> <a href = "url">
        # 위 html 코드에서 url(최신기사 url이다)을 가져와 기사 제목, 작성자, 처음 업로드 일자, 본문(text와 html)을 가져옴
        # print는 가져온 결과 확인하려고 넣음. count도

        # 앞으로 해야할 것 : 1) 페이지 또는 더보기 누르면서 새로운 기사 업로드
        #             (처음만 오래 돌려서 다 넣으면 다음은 F5 할 때 최신화된 기사만 다운받으면 되니까. 한번만)
        #            2) DB에 바로 저장 << Django와 연동해서 바로 넣는 방법으로 해보고 비효율적이면 말고))
        #           3) 이미지 파일 뒤에 /_ir50_/ 붙는거 바꾸기.
        #          (newspaper3k 라이브러리 열어서 그 부분 수정 후에 새로 넣으면 안될까.... 일단 찾아보기)
        Newspaper = 'joongang'
        dfNewsList = []
        dfLDList = []
        # JAList 는 중앙일보 카테고리를 리스트로 만든 것
        for category in JAList:  # 중앙일보 카테고리를 하나씩 대입
            html = urlopen("https://www.joongang.co.kr/" + category)  # 중앙일보에서 해당 카테고리 url
            bsObject = BeautifulSoup(html, "html.parser")  # url 화면을 html로 가져오기
            news0 = ''  # 기사 url이 3~4개 반복적으로 나오더라. 기사 당 한 번만 데이터를 긇어오려고 선언함
            count = 0  # 카테고리 당 가져오는 기사 개수 카운트

            for link in bsObject.find("ul", {"class": "story_list"}).find_all('a'):  # 카테고리 별 기사 url 가져오기
                newsNew = link.get('href')  # 개별 기사 url 저장됨

                if news0 != newsNew:  # 앞서 가져온 기사와 같은지 확인
                    news0 = newsNew  # 다른 기사이므로 news0을 새로운 기사 url로 갱신

                    a = Article(news0, keep_article_html=True, language='ko')  # newspaper3k 라이브러리 전용 html 로드

                    # newspaper3k 라이브러리 전용~~~
                    a.download()
                    a.parse()

                    article_html = a.article_html  # 기사 본문 html 코드 (기사 템플릿 html 파일에 넣을 코드?)
                    title = a.title  # 기사 제목
                    author = a.authors[0]  # 기사를 작성한 기자
                    publish_date = a.publish_date  # 기사를 처음 업로드한 시간
                    text = a.text  # 기사 본문 텍스트 정보만 (키워드 분석 전용 데이터)

                    # -----------------------------------------------------------------------------
                    # csv 로 데이터 저장
                    dfNewsList.append([title, author, publish_date, article_html, text, category, Newspaper])

                    # 데이터가 잘 저장되었는지 확인
                    '''print(article_html)
                    print('-------------------------------------------------------')
                    print(title)
                    print(author)
                    print(publish_date)
                    print(text)'''
                    count = count + 1  # 기사 카운트



                    # --------------------------------------------------------------
                    # 여기부터 호불호 데이터
                    html_LD = urlopen(news0)  # 호불호 데이터 스크래핑을 위한 개별 뉴스 url 로드 (bs4 라이브러리 전용)
                    bsObject_LD = BeautifulSoup(html_LD, "html.parser")  # bs4 라이브러리 전용 기사 전문 html 가져오기

                    LDlist = ['like', 'dislike']  # 딕셔너리로 변환을 위한 리스트
                    LD = {}  # 호불호 데이터 저장을 위한 딕셔너리
                    # 너무 길어서 변수 LDList로 선언. 호불호 데이터가 포함된 태그 저장

                    # -------------------------------------------------------------------
                    LDList = bsObject_LD.find('div', {"class": "empathy_wrap"}).find_all('span', {"class": "count"})

                    # 리스트 LD에 호불호 데이터 저장
                    for i in range(len(LDList)):
                        LD[LDlist[i]] = int(LDList[i].text)

                    #--------------------------------------------------------------------
                    # 호불호 데이터 csv 로 저장
                    dfLDList.append([LD['like'], LD['dislike']])

                    # 호불호 데이터가 잘 저장이 되었는지 확인
                    # print(LD)



                if count == 10:  # 뉴스는 10개씩만 test...
                    break

            # --------------------------------------------------------------
            # 여기부터 댓글 스크래핑
            # 중앙일보는 댓글 스크래핑이 막혀서 넘어감

            driver = webdriver.Chrome()
            driver.implicitly_wait(2)
            driver.get(url)

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

        # print(count)
        # csv 파일에 데이터 쓰기
        df_news = pd.DataFrame(dfNewsList, columns = ['Title', 'Author', 'PublishDate', 'BodyHTML', 'Text', 'Category', 'Newspaper'])
        #df_comment = pd.DataFrame(df)
        df_LD = pd.DataFrame(dfLDList, columns = ['Likes', 'Dislikes'])
        df_news.to_csv('News.csv', encoding = 'utf-8')
        df_LD.to_csv('LikeDislike.csv', encoding = 'utf-8')

        # 작업이 완료했는지 확인하기 위함
        #### 데이터 저장이 잘 되었는지, 데이터 자료값이 맞는지 확인
        end = 1
        return end


# main 함수
'''JAlist = ['politics', 'money', 'society', 'world', 'culture', 'sports', 'lifestyle', 'people']  # 중앙일보 카테고리 리스트
scrap = Scraper
scrap.joongang(JAlist)'''

#동적페이지 추출- request, beautifulsoup
'''url = "https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid=025"

#웹 드라이브
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.implicitly_wait(2)
driver.get(url)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
naver_title = soup.find_all('a', {"class": "nclicks(cnt_flashart)"})
if naver_title == :
    print(i)'''

#url = "https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid=025&date=20220506&page=1"

'''driver = webdriver.Chrome(ChromeDriverManager().install())
driver.implicitly_wait(2)
driver.get(url)

while True:
    try:
        더보기 = driver.find_element_by_css_selector('a.u_cbox_btn_more')
        더보기.click()
        time.sleep(1)
    except:
        break

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
comment = soup.find_all('span', {"class": "u_cbox_contents"})'''
'''
url = "https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid=469"

html = urlopen(url)  # 중앙일보에서 해당 카테고리 url
bsObject = BeautifulSoup(html, "html.parser")  # url 화면을 html로 가져오기

pagelist = bsObject.find("div", {"class" : "paging"})

links = bsObject.find("ul", {"class": "type13 firstlist"}).find_all('a')

news0 = ''  # 기사 url이 3~4개 반복적으로 나오더라. 기사 당 한 번만 데이터를 긇어오려고 선언함
for link in links:  # 카테고리 별 기사 url 가져오기
    newsNew = link.select('img')
    #print(newsNew)
    for line in newsNew:
        if news0 != line['alt']:  # 앞서 가져온 기사와 같은지 확인
            news0 = line['alt']
            print(news0)

for i in range(1,len(pagelist) + 1):

    url = "https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid=469&date=20220506&page=" + str(i)

    html = urlopen(url)  # 중앙일보에서 해당 카테고리 url
    bsObject = BeautifulSoup(html, "html.parser")  # url 화면을 html로 가져오기



    headline_links = bsObject.find("ul", {"class": "type06_headline"}).find_all('a')
    type_links = bsObject.find("ul", {"class": "type06"}).find_all('a')

    for headline_link, type_link in zip(headline_links, type_links):  # 카테고리 별 기사 url 가져오기
        newsNew = headline_link.select('img')
        #print(newsNew)
        for line in newsNew:
            if news0 != line['alt']:  # 앞서 가져온 기사와 같은지 확인
                news0 = line['alt']
                print(news0)
        #print('\n\n')
        newsNew = type_link.select('img')
        for line in newsNew:
            if news0 != line['alt']:  # 앞서 가져온 기사와 같은지 확인
                news0 = line['alt']
                print(news0)

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.implicitly_wait(2)
    driver.get(url)'''

#신문사 별 카테고리
JAlist = ['politics', 'money', 'society', 'sports',
          'culture', 'lifestyle', 'world', 'people']
HKlist = ['News/Politics', 'News/Economy', 'News/Society', 'Sports',
          'News/Culture', 'News/Enter', 'News/World', 'News/People', 'News/Life', 'News/Local']
AJlist = ['politics', 'economy', 'society', 'cultureentertainment/sports',
          'cultureentertainment/culture', 'cultureentertainment/entertainment']
DAILIlist = ['politics', 'economy', 'society', 'sports',
             'lifeCulture', 'entertainment', 'world', 'itScience']

#신문사 별 Dataframe으로 만들 리스트 선언
dfJANewsList = []
dfJA_LDList = []
dfHKNewsList = []
dfHK_LDList = []
dfAJNewsList = []
dfAJ_LDList = []
dfDAILINewsList = []
dfDAILI_LDList = []

idNews = 0
for category in JAlist:  # 중앙일보 카테고리를 하나씩 대입
    html = urlopen("https://www.joongang.co.kr/" + category)  # 중앙일보에서 해당 카테고리 url
    bsObject = BeautifulSoup(html, "html.parser")  # url 화면을 html로 가져오기
    news0 = ''  # 기사 url이 3~4개 반복적으로 나오더라. 기사 당 한 번만 데이터를 긇어오려고 선언함
    count = 0  # 카테고리 당 가져오는 기사 개수 카운트

    for link in bsObject.find("ul", {"class": "story_list"}).find_all('a'):  # 카테고리 별 기사 url 가져오기
        newsNew = link.get('href')  # 개별 기사 url 저장됨

        if news0 != newsNew:  # 앞서 가져온 기사와 같은지 확인
            news0 = newsNew  # 다른 기사이므로 news0을 새로운 기사 url로 갱신

            a = Article(news0, keep_article_html=True, language='ko')  # newspaper3k 라이브러리 전용 html 로드

            # newspaper3k 라이브러리 전용~~~
            a.download()
            a.parse()

            article_html = a.article_html  # 기사 본문 html 코드 (기사 템플릿 html 파일에 넣을 코드?)
            title = a.title  # 기사 제목
            author = a.authors[0]  # 기사를 작성한 기자
            publish_date = a.publish_date  # 기사를 처음 업로드한 시간
            text = a.text  # 기사 본문 텍스트 정보만 (키워드 분석 전용 데이터)

            # -----------------------------------------------------------------------------
            # csv 로 데이터 저장하기 위한 리스트
            dfJANewsList.append([idNews, title, author, publish_date, article_html, text, category, 'joongang'])

            # 데이터가 잘 저장되었는지 확인
            '''print(article_html)
            print('-------------------------------------------------------')
            print(title)
            print(author)
            print(publish_date)
            print(text)'''

            # --------------------------------------------------------------
            # 여기부터 호불호 데이터
            html_LD = urlopen(news0)  # 호불호 데이터 스크래핑을 위한 개별 뉴스 url 로드 (bs4 라이브러리 전용)
            bsObject_LD = BeautifulSoup(html_LD, "html.parser")  # bs4 라이브러리 전용 기사 전문 html 가져오기

            LDlist = []  # 호불호 데이터 저장을 위한 리스트

            # -------------------------------------------------------------------
            LD = bsObject_LD.find('div', {"class": "empathy_wrap"}).find_all('span', {"class": "count"})
            #print(LD)

            # 리스트 LD에 호불호 데이터 저장
            for i in LD:
                LDlist.append(i.text)

            # --------------------------------------------------------------------
            # 호불호 데이터 csv 로 저장
            dfJA_LDList.append([idNews, LDlist[0], LDlist[1]])

            # 호불호 데이터가 잘 저장이 되었는지 확인
            #print(LDlist)

            # News 총 개수 저장
            idNews += 1

#---------------------------------------------------------------------------------
#뉴스, 호불호 Dataframe 만들기
df_JANews = pd.DataFrame(dfJANewsList,
                         columns = ['idNews', 'Title', 'Author', 'PublishDate', 'BodyHTML', 'Text', 'Category', 'Newspaper'])
df_JALD = pd.DataFrame(dfJA_LDList, columns = ['idNews', 'Likes', 'Dislikes'])

#Dataframe 확인
print(df_JANews)
print(df_JALD)

'''for category in HKlist:  # 한국일보 카테고리를 하나씩 대입
    html = urlopen("https://www.hankookilbo.com/" + category)  # 한국일보에서 해당 카테고리 url
    bsObject = BeautifulSoup(html, "html.parser")  # url 화면을 html로 가져오기
    news0 = ''  # 기사 url이 3~4개 반복적으로 나오더라. 기사 당 한 번만 데이터를 긇어오려고 선언함
    count = 0  # 카테고리 당 가져오는 기사 개수 카운트

    for link in bsObject.find("ul", {"id" : "section-bottom-article-list"}).find_all('a'):  # 카테고리 별 기사 url 가져오기
        newsNew = link.get('href')  # 개별 기사 url 저장됨
        #print(newsNew)
        if news0 != newsNew:  # 앞서 가져온 기사와 같은지 확인
            news0 = newsNew  # 다른 기사이므로 news0을 새로운 기사 url로 갱신

            a = Article("https://www.hankookilbo.com" + news0, keep_article_html=True, language='ko')  # newspaper3k 라이브러리 전용 html 로드

            # newspaper3k 라이브러리 전용~~~
            a.download()
            a.parse()

            article_html = a.article_html  # 기사 본문 html 코드 (기사 템플릿 html 파일에 넣을 코드?)
            title = a.title  # 기사 제목
            author = a.authors  # 기사를 작성한 기자
            publish_date = a.publish_date  # 기사를 처음 업로드한 시간
            text = a.text  # 기사 본문 텍스트 정보만 (키워드 분석 전용 데이터)

            # -----------------------------------------------------------------------------
            # csv 로 데이터 저장
            dfHKNewsList.append([title, author, str(publish_date), article_html, text, category, 'hankook'])

            # 데이터가 잘 저장되었는지 확인
            print(article_html)
            print('-------------------------------------------------------')
            print(title)
            print(author)
            print(publish_date)
            print(text)
            
            # --------------------------------------------------------------
            # 여기부터 호불호 데이터
            html_LD = urlopen("https://www.hankookilbo.com" + news0)  # 호불호 데이터 스크래핑을 위한 개별 뉴스 url 로드 (bs4 라이브러리 전용)
            bsObject_LD = BeautifulSoup(html_LD, "html.parser")  # bs4 라이브러리 전용 기사 전문 html 가져오기

            LDlist = []  # 호불호 데이터 저장을 위한 리스트

            # -------------------------------------------------------------------
            LD = bsObject_LD.find('div', {"class": "empathy_wrap"}).find_all('span', {"class": "count"})
            # print(LD)

            # 리스트 LD에 호불호 데이터 저장
            for i in LD:
                LDlist.append(i.text)

            # --------------------------------------------------------------------
            # 호불호 데이터 csv 로 저장
            dfJA_LDList.append([LDlist[0], LDlist[1]])

            # 호불호 데이터가 잘 저장이 되었는지 확인
            # print(LDlist)

#--------------------------------------------------------------------------------
#뉴스, 호불호 Dataframe 만들기
df_HKNews = pd.DataFrame(dfHKNewsList,
                           columns=['Title', 'Author', 'PublishDate', 'BodyHTML', 'Text', 'Category', 'Newspaper'])
#df_HKLD = pd.DataFrame(dfHK_LDList, columns = ['Likes', 'Dislikes'])

#Dataframe 확인
print(df_HKNews)
#print(df_HKLD)'''

for category in AJlist:  # 아주경제 카테고리를 하나씩 대입
    for j in range(1, 7):
        html = urlopen("https://www.ajunews.com/" + category + "?page=" + str(j) + "&")  # 아주경제에서 해당 카테고리 url
        bsObject = BeautifulSoup(html, "html.parser")  # url 화면을 html로 가져오기
        news0 = ''  # 기사 url이 3~4개 반복적으로 나오더라. 기사 당 한 번만 데이터를 긇어오려고 선언함
        count = 0  # 카테고리 당 가져오는 기사 개수 카운트

        for link in bsObject.find("ul", {"class" : "news_list"}).find_all('a'):  # 카테고리 별 기사 url 가져오기
            newsNew = link.get('href')  # 개별 기사 url 저장됨
            #print(newsNew)
            if news0 != newsNew:  # 앞서 가져온 기사와 같은지 확인
                news0 = newsNew  # 다른 기사이므로 news0을 새로운 기사 url로 갱신

                a = Article("https:" + news0, keep_article_html=True, language='ko')  # newspaper3k 라이브러리 전용 html 로드

                # newspaper3k 라이브러리 전용~~~
                a.download()
                a.parse()

                article_html = a.article_html  # 기사 본문 html 코드 (기사 템플릿 html 파일에 넣을 코드?)
                title = a.title  # 기사 제목
                author = ''  # 기사를 작성한 기자
                publish_date = a.publish_date  # 기사를 처음 업로드한 시간
                text = a.text  # 기사 본문 텍스트 정보만 (키워드 분석 전용 데이터)

                # -----------------------------------------------------------------------------
                # csv 로 데이터 저장
                dfAJNewsList.append([idNews, title, author, str(publish_date), article_html, text, category, 'ajunews'])

                # 데이터가 잘 저장되었는지 확인
                '''print(article_html)
                print('-------------------------------------------------------')
                print(title)'''
                #print(author)
                '''print(publish_date)
                print(text)'''

                # --------------------------------------------------------------
                # 여기부터 호불호 데이터
                html_LD = urlopen("https:" + news0)  # 호불호 데이터 스크래핑을 위한 개별 뉴스 url 로드 (bs4 라이브러리 전용)
                bsObject_LD = BeautifulSoup(html_LD, "html.parser")  # bs4 라이브러리 전용 기사 전문 html 가져오기

                LDlist = []  # 호불호 데이터 저장을 위한 리스트

                # -------------------------------------------------------------------
                LD = bsObject_LD.find_all('em', {"id": "spanSum"})
                # print(LD)

                # 리스트 LD에 호불호 데이터 저장
                for i in LD:
                    LDlist.append(i.text)

                # --------------------------------------------------------------------
                # 호불호 데이터 csv 로 저장
                dfAJ_LDList.append([idNews, LDlist[0], LDlist[1]])

                # 호불호 데이터가 잘 저장이 되었는지 확인
                # print(LDlist)

                #News 총 개수 저장
                idNews += 1
#-------------------------------------------------------------------------------------
#뉴스, 호불호 Dataframe 만들기
df_AJNews = pd.DataFrame(dfAJNewsList,
                           columns=['idNews', 'Title', 'Author', 'PublishDate', 'BodyHTML', 'Text', 'Category', 'Newspaper'])
df_AJLD = pd.DataFrame(dfAJ_LDList, columns = ['idNews', 'Likes', 'Dislikes'])

#Dataframe 상태 확인
print(df_AJNews)
print(df_AJLD)


for category in DAILIlist:  # 데일리안 카테고리를 하나씩 대입
    for j in range(1, 6):
        html = urlopen("https://www.dailian.co.kr/" + category + "?page=" + str(j))  # 데일리안에서 해당 카테고리 url
        bsObject = BeautifulSoup(html, "html.parser")  # url 화면을 html로 가져오기
        news0 = ''  # 기사 url이 3~4개 반복적으로 나오더라. 기사 당 한 번만 데이터를 긇어오려고 선언함
        count = 0  # 카테고리 당 가져오는 기사 개수 카운트

        for link in bsObject.find("div", {"class" : "itemContainer"}).find_all('a'):  # 카테고리 별 기사 url 가져오기
            newsNew = link.get('href')  # 개별 기사 url 저장됨
            #print(newsNew)
            if news0 != newsNew:  # 앞서 가져온 기사와 같은지 확인
                news0 = newsNew  # 다른 기사이므로 news0을 새로운 기사 url로 갱신

                a = Article("https://www.dailian.co.kr" + news0, keep_article_html=True, language='ko')  # newspaper3k 라이브러리 전용 html 로드

                # newspaper3k 라이브러리 전용~~~
                a.download()
                a.parse()

                article_html = a.article_html  # 기사 본문 html 코드 (기사 템플릿 html 파일에 넣을 코드?)
                title = a.title  # 기사 제목
                author = ''  # 기사를 작성한 기자
                publish_date = a.publish_date  # 기사를 처음 업로드한 시간
                text = a.text  # 기사 본문 텍스트 정보만 (키워드 분석 전용 데이터)

                # -----------------------------------------------------------------------------
                # csv 로 데이터 저장
                dfDAILINewsList.append([idNews, title, author, str(publish_date), article_html, text, category, 'dailian'])

                # 데이터가 잘 저장되었는지 확인
                '''print(article_html)
                print('-------------------------------------------------------')
                print(title)
                print(author)
                print(publish_date)
                print(text)'''

                # --------------------------------------------------------------
                # 여기부터 호불호 데이터
                html_LD = urlopen("https://www.dailian.co.kr" + news0)  # 호불호 데이터 스크래핑을 위한 개별 뉴스 url 로드 (bs4 라이브러리 전용)
                bsObject_LD = BeautifulSoup(html_LD, "html.parser")  # bs4 라이브러리 전용 기사 전문 html 가져오기

                LDlist = []  # 호불호 데이터 저장을 위한 리스트

                # -------------------------------------------------------------------
                '''LD = bsObject_LD.find_all('div', {"class": "faceIcon"})
                #print(LD)

                # 리스트 LD에 호불호 데이터 저장
                for i in LD:
                    LDlist.append(i.text)'''
                LD_like = bsObject_LD.find('span', {"id" : "news_likes"}).text
                LD_dislike = bsObject_LD.find('span', {"id" : "news_hates"}).text
                #print([LD_like, LD_dislike])
                # --------------------------------------------------------------------

                # 호불호 데이터 csv 로 저장
                dfDAILI_LDList.append([idNews, LD_like, LD_dislike])

                # 호불호 데이터가 잘 저장이 되었는지 확인
                # print(LDlist)

                #News 총 개수 저장
                idNews += 1
#-------------------------------------------------------------------------------------
#뉴스, 호불호 Dataframe 만들기
df_DAILINews = pd.DataFrame(dfDAILINewsList,
                           columns=['idNews', 'Title', 'Author', 'PublishDate', 'BodyHTML', 'Text', 'Category', 'Newspaper'])
df_DAILILD = pd.DataFrame(dfDAILI_LDList, columns = ['idNews', 'Likes', 'Dislikes'])

#Dataframe 상태 확인
print(df_DAILINews)
print(df_DAILILD)

#Dataframe 합치기
df_News = pd.merge(df_JANews, df_AJNews).merge(df_DAILINews)
df_LD = pd.merge(df_JALD, df_AJLD).merge(df_DAILILD)

#합친 Dataframe 확인
print(df_News)
print(df_LD)

#Dataframe csv로 저장
df_News.to_csv('News.csv', mode='w', encoding='utf-8')
df_LD.to_csv('LikeDislike.csv', mode='w', encoding='utf-8')