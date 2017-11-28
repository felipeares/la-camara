# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import time
import json
import re
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from pyvirtualdisplay import Display

# start time clock, globals and helper
is_screenless = False
path_to_chrome = './drivers/chromedriver'
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
opts.add_argument("--kiosk");
pt('Browser Options')

# start browser
browser = webdriver.Chrome(executable_path=path_to_chrome, chrome_options=opts)
browser.set_page_load_timeout(180)
pt('Start Browser')

# init output List
mociones = []
page_errors = []

#GO!
regex = re.compile(r"[a-z/:._?=]", re.IGNORECASE)
try:
    browser.get('https://www.camara.cl/pley/pley_mocmen.aspx?prmID=31')
    pt('Get Site')
    page_number = browser.find_element_by_css_selector('#detail .pages ul li.current').text
    
    # FOR LOOP STARTS HERE!!
    subcount = 1
    while True:
        pt('Get Motions: Page ' + str(subcount))
        subcount = subcount + 1
    
        rows = browser.find_elements_by_css_selector('#detail table.tabla tbody tr')
        rows.pop(0)
        for row in rows:
            columns = row.find_elements_by_css_selector('td')
            links = regex.sub('',columns[3].find_element_by_tag_name('a').get_attribute('href')).split('&')
            mocion = {
                    "numero":columns[0].text,
                    "fecha":columns[1].text,
                    "titulo":columns[2].text,
                    "boletin":columns[3].text,
                    "prmid":links[0],
                    "prmbL":links[1]
            }
            mociones.append(mocion)
        
        next_buttons = browser.find_elements_by_css_selector('#detail .pages ul li.next a')
        if len(next_buttons) > 0:
            browser.execute_script(next_buttons[0].get_attribute('href').replace('javascript:',''))
            exception_counter = 0
            while True:
                try:
                    new_page_number = browser.find_element_by_css_selector('#detail .pages ul li.current').text
                    if new_page_number == page_number:
                        time.sleep(0.1)
                    else:
                        page_number = new_page_number
                        break
                except StaleElementReferenceException:
                    if exception_counter > 10:
                        break
                    else:
                        exception_counter = exception_counter + 1
                        time.sleep(0.1)
        else:
            break
    
except TimeoutException as ex:
    pprint(ex)
    pt('PAGE TimeoutException ERROR')
except NoSuchElementException as ex:
    pprint(ex)
    pt('PAGE NoSuchElementException ERROR')
except WebDriverException as ex:
    pprint(ex)
    pt('PAGE WebDriverException ERROR')



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
with open('data/mociones.simple.1418.json', 'w') as outfile:
    json.dump(mociones, outfile)
    
# save errors
with open('data/errors/mociones.simple.1418.json', 'w') as outfile:
    json.dump(page_errors, outfile)
pt('Save to File')