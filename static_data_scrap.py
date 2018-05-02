import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time, re
from selenium.webdriver.support.ui import Select
import lxml.html
import psycopg2
from bs4 import BeautifulSoup

conn = psycopg2.connect(database='loads',user='prashant', password='12345', port=5432)
cursor = conn.cursor()

path_to_chromedriver = 'C:/Users/prash/Desktop/WebScrap/selenium/chromedriver' 

driver = webdriver.Chrome(executable_path = path_to_chromedriver)
driver.implicitly_wait(10) 
driver.maximize_window()
url = 'http://tis.nhai.gov.in/tollplazasonmap?language=en'
driver.get(url) 
embed = driver.find_element_by_tag_name('embed') 
driver.switch_to.frame(embed) 
element = driver.find_element_by_id('tollstation') 
driver.execute_script("arguments[0].click();", element)

WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='txtFrom']"))).send_keys("mumbai, India",Keys.RETURN)
WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='txtTo']"))).send_keys("delhi, India",Keys.RETURN)
select = Select(driver.find_element_by_id("ddlTravelOption"))
select.select_by_visible_text("4 to 6 Axle")
element2 = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,"//*[@id='showstation']/p[7]/a")))

driver.execute_script("arguments[0].click();", element2)
time.sleep(60)
html_source = driver.page_source
soup = BeautifulSoup(driver.page_source, 'html.parser')

tbody1 = soup('table' ,{"class":"tollinfotbl"})[0].find('tr')
td_list = tbody1.find_all('td')
distance = td_list[2].text
query = "INSERT INTO routeinfo (distance) VALUES (%s);"
data = (distance)
cursor.execute(query, ([data]))

tbody = soup('table' ,{"class":"tollinfotbl"})[0].find_all('tr')[3:]
for row in tbody[:-1]:
	cols = row.findChildren(recursive=False)
	cols = [ele.text for ele in cols]
	if cols:
		serial_no = str(cols[0])
		Toll_plaza = str(cols[1])
		cost_raw = str(cols[2])

		compiled = re.compile('^(\d+)\s*\(', flags=re.IGNORECASE | re.DOTALL)
		match = re.search(compiled, cost_raw)
		if match:
			cost = match.group(1)
		query = "INSERT INTO routes (serial_no,Toll_plaza, cost) VALUES (%s, %s, %s);"
		data = (serial_no, Toll_plaza, cost)
		cursor.execute(query, data)
conn.commit()
driver.quit()

