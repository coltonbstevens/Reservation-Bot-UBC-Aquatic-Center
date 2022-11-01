#! python3
# UBCReservations.py - Reserves time slots at the UBC aquatic center.
import time
import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup

from webdriver_manager.chrome import ChromeDriverManager

# Run to install the version of chromedriver that works with the installed version of Chrome
# import chromedriver_autoinstall as chromedriver
# chromedriver.install()

# Location of chromedriver
s=Service('/Users/coltonstevens/chromedriver')

driver = webdriver.Chrome(service=s)

# URL of UBC Aquatic Center
url='https://ubc.perfectmind.com/24063/Clients/BookMe4BookingPages/Classes?calendarId=177b4c03-533a-4d92-8b47-6dce1d39a5ae&widgetId=15f6af07-39c5-473e-b053-96653f77a406&embed=False'
driver.get(url)


"""username = input("Enter your CWL username:")
password = input("Enter your CWL password:")"""

username = 'colton04'
password = 'DvC6SiS58ryQ!'


eventList = ['25m Length Swim', 'Leisure Pool','25m Length Toonie Swim UBC Staff/Faculty',
             '25m Length Swim UBC Student Access','50m Length Swim','50m Length Swim UBC Student Access',
             '50m Length Swim Member/Student Access','25m Length Swim Member/Student Access',
             '50m Length Toonie Swim UBC Staff/Faculty']

loginButton = driver.find_element('xpath','//*[@id="topNav"]/div[1]/a')
loginButton.click()

CWLButton = driver.find_element('xpath','/html/body/div[1]/div[6]/div/div/div/div[2]/div[2]/div[1]/div/div[1]/p[4]/a/img')
CWLButton.click()


usernameBox = driver.find_element('id', 'username')

usernameBox.send_keys(username)

passwordBox = driver.find_element('xpath','//*[@id="password"]')
passwordBox.send_keys(password)
passwordBox.send_keys(Keys.ENTER)

dates = WebDriverWait(driver,timeout=30).until(lambda d: d.find_elements('xpath','//h2[contains(text(),"2022")]'))

table = WebDriverWait(driver,timeout=30).until(lambda d: d.find_element('xpath','//*[@id="classes"]'))
df = pd.read_html(str(table.get_attribute('outerHTML')))
df = df[0]

y=[]
for i in range(len(df.values)):
    y.append(df.values[i][0])

df_classes = pd.Series(y)

classes = []
for i in range(len(df_classes)):
    if df_classes[i][0].isdigit():
        classes.append(df_classes[i])
    else:
        if len(df_classes[i].split('|'))>2:
            classes.append(df_classes[i].split('|')[0] + '| ' + df_classes[i].split('|')[2].split(' Aquatic Centre')[0].strip())
        else:
            classes.append(df_classes[i].split('|')[0] + '| ' + df_classes[i].split('|')[1].split(' Aquatic Centre')[0].strip())

classes = pd.Series(classes)
classes = pd.DataFrame({"text":classes})
classes['type'] = np.where(classes['text'].apply(len)>14,"Event","Date")
classes = classes.pivot(columns='type').fillna(method='ffill')
classes.dropna(inplace=True)
classes.columns = classes.columns.get_level_values(1)

classes['Time'] = classes['Event'].str[-19::]
classes['Event'] = classes['Event'].str[:-19].str.strip()
classes[['Category','Event']] = classes['Event'].str.split('|',expand=True)
classes['Category'] = classes['Category'].str.strip()
classes['Event'] = classes['Event'].str.strip()

classesFiltered = classes[(classes['Event'].isin(eventList)) & (classes['Category']=="REGISTER")]
eventsGrouped = classesFiltered.groupby(['Date','Event'])

classesFilteredNextWeek = classesFiltered[classesFiltered.Date.isin(classesFiltered.Date.drop_duplicates()[0:7])]

print("Events available in the next week:")
print(classesFilteredNextWeek[['Date', 'Event', 'Time']].to_string())

while True:
    dateSelected = input("Select a date (e.g.,2022 Oct 7th):")
    if dateSelected in classesFilteredNextWeek.Date.drop_duplicates().values:
        break
    else:
        print(f"Please enter one of the following dates: {classesFilteredNextWeek.Date.drop_duplicates().values}")

classesFilteredDay = classesFilteredNextWeek[classesFilteredNextWeek.Date==dateSelected]
print("Events available in the chosen day:")
print(classesFilteredDay[['Date', 'Event', 'Time']].to_string())

while True:
    timeSelected = input("Select a time (e.g., 08:30 am):")
    if timeSelected in classesFilteredDay.Time.str[0:8].values:
        break
    else:
        print(f"Please enter one of the following time slots: {classesFilteredDay.Time.str[0:8].values}")

print(f"Reserving time slot...\n",classesFilteredDay[classesFilteredDay.Time.str[0:8]==timeSelected])

timesInNextWeek = classesFilteredNextWeek[classesFilteredNextWeek.Time.str[0:8]==timeSelected].reset_index()

timeIndex = timesInNextWeek[timesInNextWeek.Date==dateSelected].index[0]

"""html = driver.page_source
soup = BeautifulSoup(html,'html.parser')
table = soup.select_one("table[id='classes']")
table_df = pd.read_html(str(table))[0]
print(table_df)
print(table_df.columns)"""



a = WebDriverWait(driver,timeout=30).until(lambda d: d.find_elements('xpath',f"//*[contains(text(),'{timeSelected} -')]/../../../div[3]/div[2]/input"))
a[timeIndex].click()

registerButton = WebDriverWait(driver,timeout=30).until(lambda d: d.find_element('xpath','//*[@id="main-content"]/div/div/div[1]/div/section[2]/a'))
registerButton.click()

'''f len(driver.find_elements('xpath','//*[@id="main-content"]/div/div/div[1]/div/section[2]/a')) > 0:
    registerButton = WebDriverWait(driver,timeout=30).until(lambda d: d.find_element('xpath','//*[@id="main-content"]/div/div/div[1]/div/section[2]/a'))
    registerButton.click()
else:
    print("Time slot is full or unavailable for registration. Please try again")'''

#personButton = WebDriverWait(driver,timeout=30).until(lambda d: d.find_element('xpath','//*[@id="ParticipantsFamily_FamilyMembers_0__IsParticipating"]'))
#personButton.click()

time.sleep(1)

nextAttendeesButton = WebDriverWait(driver,timeout=30).until(lambda d: d.find_element('xpath','//*[@id="event-attendees"]/div[3]/div/a'))
nextAttendeesButton.click()

nextQuestionnaireButton = WebDriverWait(driver,timeout=30).until(lambda d: d.find_element('xpath','//*[@id="main-content"]/div/div/div[2]/div[2]/a'))
nextQuestionnaireButton.click()

