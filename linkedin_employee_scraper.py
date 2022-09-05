from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pandas as pd
import json

path = "pathtoyourchromedriver\chromedriver.exe"
# download the chromedriver.exe from https://chromedriver.storage.googleapis.com/index.html?path=106.0.5249.21/

driver = webdriver.Chrome(path)

# Login
def login():
    login = open('login.txt') # this is your linkedin account login, store in a seperate text file. I recommend creating a fake account so your real one dosen't get flagged or banned
    line = login.readlines()

    email = line[0]
    password = line[1]

    driver.get("https://www.linkedin.com/login")
    time.sleep(1)

    eml = driver.find_element(by=By.ID, value="username")
    eml.send_keys(email)
    passwd = driver.find_element(by=By.ID, value="password")
    passwd.send_keys(password)
    loginbutton = driver.find_element(by=By.XPATH, value="//*[@id=\"organic-div\"]/form/div[3]/button")
    loginbutton.click()
    time.sleep(3)


# Return all profiles urls of M&A employees of a certain company
def getProfileURLs(companyName):
    time.sleep(1)
    driver.get("https://www.linkedin.com/company/" + companyName + "/people/?keywords=M%26A%2CMergers%2CAcquisitions")
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    source = BeautifulSoup(driver.page_source)

    visibleEmployeesList = []
    visibleEmployees = source.find_all('a', class_='app-aware-link')
    for profile in visibleEmployees:
        if profile.get('href').split('/')[3] ==  'in':
            visibleEmployeesList.append(profile.get('href'))

    invisibleEmployeeList = []
    invisibleEmployees = source.find_all('div', class_='artdeco-entity-lockup artdeco-entity-lockup--stacked-center artdeco-entity-lockup--size-7 ember-view')
    for invisibleguy in invisibleEmployees:
        title = invisibleguy.findNext('div', class_='lt-line-clamp lt-line-clamp--multi-line ember-view').contents[0].strip('\n').strip('  ')
        invisibleEmployeeList.append(title)

        # A profile can either be visible or invisible
        profilepiclink = ""
        visibleProfilepiclink = invisibleguy.find('img', class_='lazy-image ember-view')
        invisibleProfilepicLink = invisibleguy.find('img', class_='lazy-image ghost-person ember-view')
        if visibleProfilepiclink == None:
            profilepiclink = invisibleProfilepicLink.get('src')
        else:
            profilepiclink = visibleProfilepiclink.get('src')

        if profilepiclink not in invisibleEmployees:
            invisibleEmployeeList.append(profilepiclink)
    return (visibleEmployeesList[5:], invisibleEmployeeList)

# Testing spreadsheet of urls
# profilesToSearch = pd.DataFrame(columns=["ProfileID", "Title", "ProfilePicLink"])
# company = 'apple'
# searchable = getProfileURLs(company)
#
# for profileId in searchable[0]:
#     profilesToSearch.loc[len(profilesToSearch.index)] = [profileId, "", ""]
# for i in range(0, len(searchable[1]), 2):
#     profilesToSearch.loc[len(profilesToSearch.index)] = ["", searchable[1][i], searchable[1][i+1]]

# parses a type 2 job row
def parseType2Jobs(alltext):
    jobgroups = []
    company = alltext[16][:len(alltext[16]) // 2]
    totalDurationAtCompany = alltext[20][:len(alltext[20]) // 2]

    # get rest of the jobs in the same nested list
    groups = []
    count = 0
    index = 0
    for a in alltext:
        if a == '' or a == ' ':
            count += 1
        else:
            groups.append((count, index))
            count = 0
        index += 1

    numJobsInJoblist = [g for g in groups if g[0] == 21 or g[0] == 22 or g[0] == 25 or g[0] == 26]
    for i in numJobsInJoblist:
        # full time/part time case
        if 'time' in alltext[i[1] + 5][:len(alltext[i[1] + 5]) // 2].lower().split('-'):
            jobgroups.append((alltext[i[1]][:len(alltext[i[1]]) // 2], alltext[i[1] + 8][:len(alltext[i[1] + 8]) // 2]))
        else:
            jobgroups.append((alltext[i[1]][:len(alltext[i[1]]) // 2], alltext[i[1] + 4][:len(alltext[i[1] + 4]) // 2]))
    return ('type2job', company, totalDurationAtCompany, jobgroups)

# parses a type 1 job row
def parseType1Job(alltext):
    jobtitle = alltext[16][:len(alltext[16]) // 2]
    company = alltext[20][:len(alltext[20]) // 2]
    duration = alltext[23][:len(alltext[23]) // 2]
    return ('type1job', jobtitle, company, duration)

# returns linkedin profile information
def returnProfileInfo(employeeLink, companyName):
    url = employeeLink
    driver.get(url)
    time.sleep(2)
    source = BeautifulSoup(driver.page_source, "html.parser")

    profile = []
    profile.append(companyName)
    info = source.find('div', class_='mt2 relative')
    name = info.find('h1', class_='text-heading-xlarge inline t-24 v-align-middle break-words').get_text().strip()
    title = info.find('div', class_='text-body-medium break-words').get_text().lstrip().strip()
    profile.append(name)
    profile.append(title)
    time.sleep(1)
    experiences = source.find_all('li', class_='artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column')

    for x in experiences[1:]:
        alltext = x.getText().split('\n')
        print(alltext)
        startIdentifier = 0
        for e in alltext:
            if e == '' or e == ' ':
                startIdentifier+=1
            else:
                break
        # jobs, educations, certifications
        if startIdentifier == 16:
            # education
            if 'university' in alltext[16].lower().split(' ') or 'college' in alltext[16].lower().split(' ') or 'ba' in alltext[16].lower().split(' ') or 'bs' in alltext[16].lower().split(' '):
                profile.append(('education', alltext[16][:len(alltext[16])//2], alltext[20][:len(alltext[20])//2]))

            # certifications
            elif 'issued' in alltext[23].lower().split(' '):
                profile.append(('certification', alltext[16][:len(alltext[16])//2], alltext[20][:len(alltext[20])//2]))

        elif startIdentifier == 12:
            # Skills
            if (alltext[16] == '' or alltext[16] == ' ') and len(alltext) > 24:
                profile.append(('skill', alltext[12][:len(alltext[12])//2]))

    # experiences
    url = driver.current_url + '/details/experience/'
    driver.get(url)
    time.sleep(2)
    source = BeautifulSoup(driver.page_source, "html.parser")
    time.sleep(1)
    exp = source.find_all('li')
    for e in exp[13:]:
        row = e.getText().split('\n')
        if row[:16] == ['', '', '', '', '', '', ' ', '', '', '', '', '', '', '', '', '']:
            if 'yrs' in row[20].split(' '):
                profile.append(parseType2Jobs(row))
            else:
                profile.append(parseType1Job(row))

    return profile

if __name__ == "__main__":
    companies = ['apple'] #, 'microsoft', 'amazon', 'tesla-motors', 'google', 'nvidia', 'berkshire-hathaway', 'meta', 'unitedhealth-group'
    login()
    employees = {}
    for company in companies:
        searchable = getProfileURLs(company)
        for employee in searchable[0]:
            employees[employee] = returnProfileInfo(employee, company)
    with open('m&a.json', 'w') as f:
        json.dump(employees, f)
    time.sleep(10)
    driver.quit()
