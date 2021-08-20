import requests
from bs4 import BeautifulSoup


url = 'https://finance.naver.com/'

response = requests.get(url)
response.raise_for_status()
html = response.text
soup = BeautifulSoup(html, 'html.parser')
tbody = soup.select_one('#content > div.article > div.section > div.news_area > div.section_strategy')
trs = tbody.select('ul > li')
datas = []
for tr in trs:
    name = tr.select_one('span > a').get_text()
    #current_price = tr.select_one('td').get_text()
    # change_direction = tr['class'][0]
    # change_price = tr.select_one('td > span').get_text()
    datas.append([name])

print(datas[1][0])
