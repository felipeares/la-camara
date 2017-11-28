# -*- coding: utf-8 -*-
import time
import json
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from pyvirtualdisplay import Display

# search function
def searchin(prmid,value_non_blank,json_list):
    for rep in json_list:
        if prmid == rep['prmid']:
            if rep[value_non_blank] != '':
                return True
    return False

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
    
# get saved representatives 
loaded_historic = json.load(open('./data/diputados.extended.1014.json'))
loaded_oficios = json.load(open('./data/diputados.oficios.1418.json'))
pt('Get reps from file')

# init output List
diputados_extended = []
diputados_missed = []

# GO!
counter = 0
for rep in loaded_historic:
    counter = counter + 1
    if not searchin(rep['prmid'],'nombre',loaded_oficios):
        if rep['periodo'] == '2010-2014':
            print('------------- STARTING REP Nº ' + str(counter) + ' ----------------')
            
            rep_saved = False
            rep_extended = {
                "prmid":rep['prmid'],
                "nombre":rep['nombre'],
                "periodo":rep['periodo'],
                "oficios":[],
                "errors":[]
            }
            
            try:
                browser.get('https://www.camara.cl/camara/diputado_detalle_h.aspx?prmid='+str(rep['prmid']))
                pt('Get Current Rep Site')
                
                # Diligences
                div_id = 'ctl00_mainPlaceHolder_pnlOficios'
                browser.execute_script("__doPostBack('ctl00$mainPlaceHolder$btnOficiosH','')")
                time.sleep(2)
                WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, div_id)))
                
                try:
                    results = browser.find_element_by_css_selector('#' + div_id + ' .results').text
                    subcount = 1
                    while True:
                        pt('Get Diligences: Page ' + str(subcount))
                        subcount = subcount + 1
                        diligences = browser.find_elements_by_css_selector('#' + div_id + ' table.tabla tbody tr')
                        for dl in diligences:
                            try:
                                info = dl.find_elements_by_css_selector('td')
                                info_array = []
                                for inf in info:
                                    info_array.append(inf.text)
                                rep_extended['oficios'].append(info_array)
                            except StaleElementReferenceException:
                                rep_extended['errors'].append('Error on Page ' + str(subcount-1))
                                print('Error on Page ' + str(subcount-1))
                                break
                        
                        next_buttons = browser.find_elements_by_css_selector('#' + div_id + ' .pages ul li.next a')
                        if len(next_buttons) > 0:
                            browser.execute_script(next_buttons[0].get_attribute('href').replace('javascript:',''))
                            exception_counter = 0
                            while True:
                                try:
                                    new_results = browser.find_element_by_css_selector('#' + div_id + ' .results').text
                                    if new_results == results:
                                        time.sleep(0.1)
                                    else:
                                        results = new_results
                                        break
                                except StaleElementReferenceException:
                                    if exception_counter > 10:
                                        break
                                    else:
                                        exception_counter = exception_counter + 1
                                        time.sleep(0.1)
                                    
                            results = browser.find_element_by_css_selector('#' + div_id + ' .results').text
                        else:
                            break
                    
                    diputados_extended.append(rep_extended)
                    rep_saved = True
                except NoSuchElementException as ex:
                    pt('PAGE NoSuchElementException ERROR')
            
            except TimeoutException as ex:
                pt('PAGE TimeoutException ERROR')
            except WebDriverException as ex:
                pt('PAGE WebDriverException ERROR')
            except:
                pt('PAGE WILDCARD ERROR')
        
            if rep_saved:
                pt('Current Rep Saved')
            else:
                diputados_extended.append(rep_extended)
                diputados_missed.append(rep)
                pt('Current Rep NOT Saved')

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
with open('data/diputados.oficios.1014.json', 'w') as outfile:
    json.dump(diputados_extended, outfile)
    
# save errors
with open('data/errors/diputados.oficios.1014.json', 'w') as outfile:
    json.dump(diputados_missed, outfile)
pt('Save to File')
