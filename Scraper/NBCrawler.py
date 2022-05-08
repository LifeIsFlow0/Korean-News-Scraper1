from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time

#신문사마다 네이버에서 할당받은 id
presses = ['011', '025', '119']

#구독자 수 int로 저장할 리스트
subscribe_list = []

for press in presses:
    # 웹 드라이버 선언
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.implicitly_wait(2)

    # visit url
    driver.get(f"https://media.naver.com/press/{press}")
    time.sleep(5)

    # 파싱
    html = driver.page_source

    # html = urlopen(url + f"&date={date}&page=1")
    soup = BeautifulSoup(html, 'html.parser')

    #subscribe = soup.select('.press_subscribe_badge::after')

    #값 가져오기
    subscribe = soup.find("span", {"class" : "press_subscribe_badge"}).find_all("em")
    #subscribe = soup.find_element_by_xpath('/html/body/div[2]/div/section[1]/header/div[4]/div/div[2]/div[2]/span/em')

    #결과 확인
    #Seoul_subscribe = subscribe[1].text
    #print(subscribe)
    subscribe = subscribe[0].string
    print(subscribe)

    #리스트에 저장
    subscribe_list.append(int(subscribe))

    #driver 종료
    driver.close()

#저장된 값 확인
print(subscribe_list)