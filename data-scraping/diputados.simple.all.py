#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from pyvirtualdisplay import Display

# start time clock, globals and helper
path_to_chrome = './drivers/chromedriver'
is_screenless = False
start_clock = time.perf_counter()
last_milestone = start_clock
def pt(message):
    global last_milestone
    print(message + ': ' + str(round(time.perf_counter() - last_milestone, 2)) + ' seconds')
    last_milestone = time.perf_counter()

# start display
if is_screenless:
    display_size = {'height': 800, 'width': 1280 }
    display = Display(visible=0, size=(display_size['width'], display_size['height']))
    display.start()
    pt('Display Start')

# browser options
opts = Options()
opts.add_argument('--no-sandbox')
opts.add_argument("--disable-setuid-sandbox")
opts.add_argument("--disable-flash-3d")
opts.add_argument("--disable-flash-stage3d")
opts.add_argument("user-agent=curl/7.35.0")
opts.add_argument("--kiosk");
opts.add_argument("--incognito")
pt('Browser Options')

# start browser
browser = webdriver.Chrome(executable_path=path_to_chrome, chrome_options=opts)
browser.set_page_load_timeout(180)
pt('Start Browser')

# SAVE REPRESENTATIVES
diputados = []

try:
    # CURRENT REPRESENTATIVES
    browser.get('https://www.camara.cl/camara/diputados.aspx')
    pt('Get Current Reps Site')
    
    content = browser.find_elements_by_css_selector('li.alturaDiputado h4 a')
    regex = re.compile(r"[a-z/:._?=]", re.IGNORECASE)
    for el in content:
        diputados.append({
                "prmid":str(regex.sub('',el.get_attribute('href').replace('*=',''))),
                "nombre":str(el.text.replace('SR. ','').replace('SRA. ','')),
                "periodo":"2014-2018"
        })
    pt('Get Current Reps Information')
    
    # HISTORIC REPRESENTATIVES
    browser.get('https://www.camara.cl/camara/galeria1014.aspx')
    pt('Get Historic Reps Site')
    
    content = browser.find_elements_by_css_selector('li.alturaDiputado h4 a')
    regex = re.compile(r"[a-z/:._?=]", re.IGNORECASE)
    for el in content:
        diputados.append({
                "prmid":str(regex.sub('',el.get_attribute('href'))),
                "nombre":str(el.text.replace('SR. ','').replace('SRA. ','')),
                "periodo":"2010-2014"
        })
    pt('Get Current Reps Information')
    
except TimeoutException as ex:
    pt('PAGE TimeoutException ERROR')
except WebDriverException:
    pt('PAGE WebDriverException ERROR')
    #restart browser
    browser = webdriver.Chrome(executable_path=path_to_chrome, chrome_options=opts)
    pt('RE-Start Browser')
except:
    pt('PAGE WILDCARD ERROR')


# close browser
try:
    browser.close()
    browser.quit()
    pt('Close Browser')
except WebDriverException:
    pt('Close Browser WebDriverException ERROR')
except:
    pt('Close Browser WILDCARD ERROR')
    
# save to file
if len(diputados) > 0:
    with open('data/diputados.simple.all.json', 'w') as outfile:
        json.dump(diputados, outfile)
    pt('Save to File')
else:
    print('Couldn`t save to file')