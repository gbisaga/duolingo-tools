from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.select import Select
import time
import re
import requests
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--language', help=f"language to pull for")
args = parser.parse_args()

headless = True
chromeDriverLocation = './chromedriver.exe'
users = [ "AlcidesRon1" ] #"studentMic174665" "AliahCholi"
eventsByUser = {}
countByUser = {}
topN = 10
userinfo = {}
language = args.language

print(f'looking for {users}')

opts = ChromeOptions()
opts.set_headless(headless)
browser = Chrome(executable_path=chromeDriverLocation, options=opts)
browser.implicitly_wait(30)

baseurl = f'https://events.duolingo.com' + (f"?language={language}" if language != None else "")
print(baseurl)

browser.get(baseurl)

els = browser.find_elements_by_css_selector('a[href*="/event/"]')
totalCount = 0
matchCount = 0
maxCount = 0
for el in els:
    totalCount += 1
    if maxCount > 0 and totalCount > maxCount: break

    # https://events.duolingo.com/event/89d3b1db-1e06-4141-bb1c-8076e562ae35
    href = el.get_attribute("href")
    matches = re.match(r'.*/([-0-9a-fA-F]*)$', href)
    if matches:
        uuid = matches.group(1)
        # print(f' => {uuid}')
        url = f'https://events-login.duolingo.com/api/2/events/{uuid}/rsvps'
        r = requests.get(url)
        detail = None
        if r.status_code == 200:
            results = json.loads(r.text)
            rsvps = results["results"]
            detailurl = f'https://events-login.duolingo.com/api/2/events/{uuid}'
            detailresp = requests.get(detailurl)
            if detailresp.status_code == 200:
                detail = json.loads(detailresp.text)

        if len(users) > 0:
            hasthem = False
            for rsvp in rsvps:
                username = rsvp["username"]
                if username in users:
                    hasthem = True
                    if hasthem and detail != None:
                        start_date = detail["start_date"]

                        print(f'{start_date}: {href}')
                        matchCount += 1

        for rsvp in rsvps:
            username = rsvp["username"]
            if username not in eventsByUser:
                countByUser[username] = 0
                eventsByUser[username] = []
            eventsByUser[username].append(detail)
            countByUser[username] += 1

countByUserList = sorted(list(countByUser.items()), key=lambda x:x[1], reverse=True)

print(f'top {topN} users found in {totalCount} events')

cnt = 0
for u in countByUserList:
    cnt += 1
    if cnt > topN: break
    print(f' {u[0]}: {u[1]}')
    for event in eventsByUser[u[0]]:
        print(f'   {event["start_date"]}')

browser.close()