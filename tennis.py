from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.support.ui import Select
import threading
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

import time
import datetime





def fillform(id, value, driver):
	elem = driver.find_element_by_id(id)
	elem.clear()
	elem.send_keys(value)



def reserve(tomorrow, reserveid, starttime, endtime):
	# read username and password
	file_object = open("account.txt", "r")
	username = ''
	password = ''
	url = ''
	for line in file_object:
		strs = line.split('=')
		strs = list(map(lambda s: s.strip(), strs))
		if strs[0] == 'username':
			username = strs[1]
		elif strs[0] == 'password':
			password = strs[1]
		elif strs[0] == 'url':
			url = strs[1]

	# incognito mode
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument("--incognito")
	chrome_options.add_argument("--disable-dev-shm-usage")
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('--no-sandbox')

	print("Read account information successfully")
	# open chrome
	driver = webdriver.Chrome(chrome_options=chrome_options)
	driver.implicitly_wait(15)
	driver.get(url)

	print("open new url successfully")
	fillform('UserName', username, driver)
	fillform('password', password, driver)
	submit = driver.find_element_by_id('submit-sign-in')
	submit.submit()
	print("login successfully")

	elems = driver.find_elements_by_id('reserve')
	elems[reserveid].click() # weekend # 10 court 1 11 weekend 12 court 2 13 weekend

	elem = driver.find_element_by_id('resv-date')
	elem.click()

	daystr = str(tomorrow.day);
	datetofind = "//*[contains(text(), '" + daystr + "')]"

	datepick = driver.find_elements_by_xpath(datetofind)
	for ch in datepick:
		if(ch.text == daystr):
			ch.click()
			break

	time.sleep(3)

	start = driver.find_element_by_id('SelStartTime')
	select = Select(start)
	select.select_by_visible_text(starttime)

	end = driver.find_element_by_id('SelEndTime')
	select = Select(end)
	select.select_by_visible_text(endtime)

	submit = driver.find_element_by_id('submit-new-reservation')
	submit.submit()

	success = driver.find_elements_by_xpath("//*[contains(text(), 'A reservation already exists during this time period.')]")
	if(len(success) == 1):
		print(starttime + " " + endtime + " not available")
	else:
		print(starttime + " " + endtime + " booked")
	driver.quit()


def runReserve():
	thread_list = []

	tomorrow = datetime.date.today() + datetime.timedelta(days=1)

	weekno = tomorrow.weekday()

	# datepickertag = 'ui-datepicker-week-end'

	if weekno < 5:
	    t = threading.Thread(target=reserve, args=(tomorrow, 10, '7:00 PM', '8:00 PM'))
	    thread_list.append(t)
	    t = threading.Thread(target=reserve, args=(tomorrow, 12, '8:00 PM', '9:00 PM'))
	    thread_list.append(t)
	    # reserve(tomorrow, 10, '7:00 PM', '8:00 PM')
	    # reserve(tomorrow, 12, '8:00 PM', '9:00 PM')
	else:
		t = threading.Thread(target=reserve, args=(tomorrow, 11, '7:00 PM', '8:00 PM'))
		thread_list.append(t)
		t = threading.Thread(target=reserve, args=(tomorrow, 13, '8:00 PM', '9:00 PM'))
		thread_list.append(t)
		# reserve(tomorrow, 11, '7:00 PM', '8:00 PM')
		# reserve(tomorrow, 13, '8:00 PM', '9:00 PM')

	for thread in thread_list:
		thread.start()
	for thread in thread_list:
		thread.join()

def printTest():
	 print "time:"

scheduler = BackgroundScheduler()
# method is trigger everyday at 12:01 am
scheduler.add_job(runReserve,
				  'cron',
				  day_of_week='mon-sun',
				  hour=20, minute=50,
				  end_date='2018-10-30'
				  )
# scheduler.add_job(printTest,'interval', seconds=2)

scheduler.start()

# while True:
#     time.sleep(1)
