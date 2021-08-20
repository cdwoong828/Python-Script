from selenium import webdriver
from bs4 import BeautifulSoup
import time

#options = webdriver.chromeOptions()
driver = webdriver.Chrome("/Users/daewoong/Documents/Python/chromedriver")
#driver = webdriver.Chrome(chromedriver, options=options)

driver.get("https://www.nsdi.go.kr/lxportal/?menuno=2971&redirect=http://data.nsdi.go.kr/dataset/20180918ds00006")
driver.find_element_by_name('j_username').send_keys('matt.choi828@gmail.com')
driver.find_element_by_name('j_password').send_keys('Qw8946qw!!')
driver.find_element_by_xpath('//*[@id="submit_b"]').click()
time.sleep(3)

html = driver.page_source # 페이지의 elements모두 가져오기
soup = BeautifulSoup(html, 'html.parser') # BeautifulSoup사용하기
notices = soup.select('#data_table_resource > tbody')

for i in range(1, 9):
    driver.find_element_by_xpath(f'//*[@id="data_table_resource"]/tbody/tr[{i}]/td[5]/ul/li/button').click()
    time.sleep(2)
