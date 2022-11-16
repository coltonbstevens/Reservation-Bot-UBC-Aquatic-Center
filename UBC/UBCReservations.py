#! python3
# UBCReservations.py - Reserves time slots at the UBC aquatic center using the Selenium web driver.
import time
import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

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


username = input("Enter your CWL username:")
password = input("Enter your CWL password:")

# Event names from the website
eventList = ['25m Length Swim', 'Leisure Pool','25m Length Toonie Swim UBC Staff/Faculty',
             '25m Length Swim UBC Student Access','50m Length Swim','50m Length Swim UBC Student Access',
             '50m Length Swim Member/Student Access','25m Length Swim Member/Student Access',
             '50m Length Toonie Swim UBC Staff/Faculty']

# Locate and click the login button
loginButton = driver.find_element('xpath','//*[@id="topNav"]/div[1]/a')
loginButton.click()

# Locate and click the CWL button
CWLButton = driver.find_element('xpath','/html/body/div[1]/div[6]/div/div/div/div[2]/div[2]/div[1]/div/div[1]/p[4]/a/img')
CWLButton.click()

# Locate the username box and send the username
usernameBox = driver.find_element('id', 'username')
usernameBox.send_keys(username)

# Locate the password box and enter the password
passwordBox = driver.find_element('xpath','//*[@id="password"]')
passwordBox.send_keys(password)
passwordBox.send_keys(Keys.ENTER)

# Store the dates available for reservations
dates = WebDriverWait(driver,timeout=30).until(lambda d: d.find_elements('xpath','//h2[contains(text(),"202")]'))

# Store the classes available for reservations
table = WebDriverWait(driver,timeout=30).until(lambda d: d.find_element('xpath','//*[@id="classes"]'))
df = pd.read_html(str(table.get_attribute('outerHTML')))
df = df[0]

# Add the available classes to a list
y=[]
for i in range(len(df.values)):
    y.append(df.values[i][0])

# Convert the list to a pandas series
df_classes = pd.Series(y)

# Store the names of each class in a list
classes = []
for i in range(len(df_classes)):
    if df_classes[i][0].isdigit():
        classes.append(df_classes[i])
    else:
        if len(df_classes[i].split('|')) > 2:
            classes.append(df_classes[i].split('|')[0] + '| ' + df_classes[i].split('|')[2].split(' Aquatic Centre')[0].strip())
        else:
            classes.append(df_classes[i].split('|')[0] + '| ' + df_classes[i].split('|')[1].split(' Aquatic Centre')[0].strip())

# Convert the list of class names to a pandas dataframe
classes = pd.Series(classes)
classes = pd.DataFrame({"text":classes})

# Create a column for class type based on the number of characters in the string. Fill missing class types with the type from the previous row.
classes['type'] = np.where(classes['text'].apply(len)>14,"Event","Date")
classes = classes.pivot(columns='type').fillna(method='ffill')
classes.dropna(inplace=True)
classes.columns = classes.columns.get_level_values(1)

# Create columns for time, event, and category based on the regular patterns in the list of strings.
classes['Time'] = classes['Event'].str[-19::]
classes['Event'] = classes['Event'].str[:-19].str.strip()
classes[['Category','Event']] = classes['Event'].str.split('|',expand=True)
classes['Category'] = classes['Category'].str.strip()
classes['Event'] = classes['Event'].str.strip()

# Filter to classes in the list of events
classesFiltered = classes[(classes['Event'].isin(eventList)) & (classes['Category']=="REGISTER")]
eventsGrouped = classesFiltered.groupby(['Date','Event'])

# Filter to classes in the next week
classesFilteredNextWeek = classesFiltered[classesFiltered.Date.isin(classesFiltered.Date.drop_duplicates()[0:7])]

print("Events available in the next week:")
print(classesFilteredNextWeek[['Date', 'Event', 'Time']].to_string())

# Ask the user to input a date
while True:
    dateSelected = input("Select a date (e.g.,2022 Oct 7th):")
    if dateSelected in classesFilteredNextWeek.Date.drop_duplicates().values:
        break
    else:
        print(f"Please enter one of the following dates: {classesFilteredNextWeek.Date.drop_duplicates().values}")

# Filter classes to the inputted date
classesFilteredDay = classesFilteredNextWeek[classesFilteredNextWeek.Date==dateSelected]
print("Events available in the chosen day:")
print(classesFilteredDay[['Date', 'Event', 'Time']].to_string())

# Ask the user to input a time
while True:
    timeSelected = input("Select a time (e.g., 08:30 am):")
    if timeSelected in classesFilteredDay.Time.str[0:8].values:
        break
    else:
        print(f"Please enter one of the following time slots: {classesFilteredDay.Time.str[0:8].values}")

print(f"Reserving time slot...\n",classesFilteredDay[classesFilteredDay.Time.str[0:8]==timeSelected])

timesInNextWeek = classesFilteredNextWeek[classesFilteredNextWeek.Time.str[0:8]==timeSelected].reset_index()

timeIndex = timesInNextWeek[timesInNextWeek.Date==dateSelected].index[0]

# Select the class with the inputted time
a = WebDriverWait(driver,timeout=30).until(lambda d: d.find_elements('xpath',f"//*[contains(text(),'{timeSelected} -')]/../../../div[3]/div[2]/input"))
a[timeIndex].click()

# Locate and click the register button
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

# Locate and click the attendees button
nextAttendeesButton = WebDriverWait(driver,timeout=30).until(lambda d: d.find_element('xpath','//*[@id="event-attendees"]/div[3]/div/a'))
nextAttendeesButton.click()

# Locate and click the questionnaire button
nextQuestionnaireButton = WebDriverWait(driver,timeout=30).until(lambda d: d.find_element('xpath','//*[@id="main-content"]/div/div/div[2]/div[2]/a'))
nextQuestionnaireButton.click()

