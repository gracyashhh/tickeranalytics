from selenium import webdriver
from time import sleep
import json
# from selenium.webdriver.common.action_chains import ActionChains
###OLD FASHION STUFF###
# from selenium.webdriver.chrome.options import Options
# options = Options()
# options.add_argument('--headless')
# options.add_argument('--disable-gpu')
from selenium.webdriver.chrome.options import Options
options = Options()
options.headless = True
driver=webdriver.Chrome("D:\chromedriver\chromedriver.exe",options=options)
driver.get('https://twitter.com/search?q=spac&src=typed_query&f=user')
driver.maximize_window()
sleep(3)
users=[]
for i in range(1,10):
    user1=driver.find_element_by_xpath(f'/html/body/div/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/section/div/div/div[{i}]/div/div/div/div[2]/div[1]/div[1]/a/div/div[2]/div/span')
    users.append(user1.text)
driver.execute_script("window.scrollTo(0, 4080)")
sleep(1)
driver.execute_script("window.scrollTo(4080, 1080+4080)")
sleep(3)
for i in range(1,10):
    user1=driver.find_element_by_xpath(f'/html/body/div/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/section/div/div/div[{i}]/div/div/div/div[2]/div[1]/div[1]/a/div/div[2]/div/span')
    users.append(user1.text)
data={}
for k in range(len(users)):
    driver.get('https://twitter.com/'+users[k])
    sleep(2)
    bio=driver.find_element_by_xpath('/html/body/div/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/div')
    data[users[k]]=bio.text
with open('userbio.json', 'w') as f:
    json.dump(data, f,indent=4)
