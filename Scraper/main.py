# newspaper3k, selenium, webdriver, webdriver_manager인가 webdrivermanager, requests, urllib, beautifulsoup4 라이브러리 추가

from newspaper import Article
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

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
                    # 여기부터 댓글 스크래핑
                    # 중앙일보는 댓글 스크래핑이 막혀서 넘어감
                    '''
                    raw = requests.get(news0, headers={'User-Agent': 'Chrome'})
                    bsObject_comment = BeautifulSoup(raw, "html.parser")
                    print(bsObject_comment)
                    count = count + 1

                    commentLink = bsObject_comment.find('div', {"class": "comment_layout"})
                    print(commentLink)
                    if commentLink == None:
                        pass
                    else:
                        for commentList in bsObject_comment.find('div', {"class": "comment_layout"}).find_all('div'):
                            nickname = link.get('span', {"class": "comment_userid"})
                            commentBody = link.get('span', {"class": "comment_body"})
                            print(nickname.text())
                            print(commentBody.text())
                            '''


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

            # print(count)
        # csv 파일에 데이터 쓰기
        df_news = pd.DataFrame(dfNewsList, columns = ['Title', 'Author', 'PublishDate', 'BodyHTML', 'Text', 'Category', 'Newspaper'])
        df_LD = pd.DataFrame(dfLDList, columns = ['Likes', 'Dislikes'])
        df_news.to_csv('News.csv', encoding = 'utf-8')
        df_LD.to_csv('LikeDislike.csv', encoding = 'utf-8')

        # 작업이 완료했는지 확인하기 위함
        end = 'end'
        return end


# main 함수
JAlist = ['politics', 'money', 'society', 'world', 'culture', 'sports', 'lifestyle', 'people']  # 중앙일보 카테고리 리스트
scrap = Scraper
scrap.joongang(JAlist)
