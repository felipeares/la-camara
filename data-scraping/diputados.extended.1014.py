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
    
# get saved representatives 
diputados = json.load(open('./data/diputados.simple.all.json'))
pt('Get reps from file')

# init output List
diputados_extended = []
diputados_missed = []

# GO!
counter = 1
for rep in diputados:
    if rep['periodo'] == '2014-2018':
        page = 'https://www.camara.cl/camara/diputado_detalle.aspx?prmid='+str(rep['prmid'])
    elif rep['periodo'] == '2010-2014':
        page = 'https://www.camara.cl/camara/diputado_detalle_h.aspx?prmid='+str(rep['prmid'])
    
    if rep['periodo'] == '2010-2014':
        print('----- ' + rep['periodo'] + ' STARTING REP Nº ' + str(counter) + ' ----------------')
        print(page)
        counter = counter + 1
        
        rep_saved = False
        rep_extended = {
            "prmid":rep['prmid'],
            "nombre":rep['nombre'],
            "periodo":rep['periodo'],
            "nacimiento":'',
            "profesion":'',
            "telefono":'',
            "correo":'',
            "comuna":'',
            "distrito":'',
            "region":'',
            "periodos":[],
            "comite_parlamentario":'',
            "comisiones":{
                "permanentes":[],
                "investigadoras":[],
                "antiguas":[]
            },
            "mociones_prmid":[],
            "acuerdos_prmid":[],
            "grupos_interparlamentarios":[],
            "oficios":[],
            "familia":[],
            "actividad_laboral":[]
        }
        
        try:
            browser.get(page)
            pt('Get Current Rep Site')
            
            # Basic Info
            ficha = browser.find_element_by_css_selector('#ficha')
            rep_extended['nacimiento'] = ficha.find_element_by_css_selector('div.birthDate p').text
            rep_extended['profesion'] = ficha.find_element_by_css_selector('div.profession p').text
            
            summary = browser.find_elements_by_css_selector('#ficha .summary')
            location = summary[0].find_elements_by_css_selector('p')        
            rep_extended['comuna'] = location[0].text
            rep_extended['distrito'] = location[1].text
            rep_extended['region'] = location[2].text
            
            periods = summary[1].find_elements_by_css_selector('ul li')
            for pe in periods:
                rep_extended['periodos'].append(pe.text)
            
            commitees= summary[2].find_elements_by_css_selector('p')
            for co in commitees:
                rep_extended['comite_parlamentario'] = rep_extended['comite_parlamentario'] + co.text
            
            # rep_extended['telefono'] = ficha.find_element_by_css_selector('div.phones p').text.replace('Teléfono: ','')
            # rep_extended['correo'] = ficha.find_element_by_css_selector('li.email a').text
            pt('Get Basic Info')
            
            # Comissions
            regex = re.compile(r"[a-z/:._?=]", re.IGNORECASE)
            comissions = browser.find_element_by_css_selector('#ctl00_mainPlaceHolder_pnlComisiones')
            
            act_perm = comissions.find_elements_by_xpath("//h3[contains(text(),'actualmente')]/following-sibling::h4[contains(text(),'permanentes')]/following-sibling::ul[1]/li/a");
            for pe in act_perm:
                rep_extended['comisiones']['permanentes'].append(regex.sub('',pe.get_attribute('href')))
            
            act_inv = comissions.find_elements_by_xpath("//h3[contains(text(),'actualmente')]/following-sibling::h4[contains(text(),'investigadoras')]/following-sibling::ul[1]/li/a");
            for pe in act_inv:
                rep_extended['comisiones']['investigadoras'].append(regex.sub('',pe.get_attribute('href')))
            
            past = comissions.find_elements_by_xpath("//h3[contains(text(),'actualmente')]/following-sibling::h4[contains(text(),'investigadoras')]/following-sibling::ul[1]/li");
            for pe in past:
                rep_extended['comisiones']['antiguas'].append(pe.text)
            pt('Get Comissions')
            
            # Motions
            div_id = 'ctl00_mainPlaceHolder_pnlMociones'
            regex = re.compile(r"[a-z/:._?=]", re.IGNORECASE)
            browser.execute_script("__doPostBack('ctl00$mainPlaceHolder$btnMocionesH','')")
            time.sleep(2)
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, div_id)))
            subcount = 1
            while True:
                pt('Get Motions: Page ' + str(subcount))
                subcount = subcount + 1
                motions = browser.find_elements_by_css_selector('#' + div_id + ' table.tabla tbody tr td:nth-child(4) a')
                for mo in motions:
                    rep_extended['mociones_prmid'].append(regex.sub('',mo.get_attribute('href')))
                
                next_buttons = browser.find_elements_by_css_selector('#' + div_id + ' .pages ul li.next a')
                if len(next_buttons) > 0:
                    browser.execute_script(next_buttons[0].get_attribute('href').replace('javascript:',''))
                    time.sleep(2)
                    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, div_id)))
                else:
                    break
            
            # Agreements
            div_id = 'ctl00_mainPlaceHolder_pnlPAcuerdo'
            regex = re.compile(r"[a-z/:._?=]", re.IGNORECASE)
            browser.execute_script("__doPostBack('ctl00$mainPlaceHolder$btnSalaH','')")
            time.sleep(2)
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, div_id)))
            subcount = 1
            while True:
                pt('Get Agreements: Page ' + str(subcount))
                subcount = subcount + 1
                agreenments = browser.find_elements_by_css_selector('#' + div_id + ' table.tabla tbody tr td:nth-child(2) a')
                for agr in agreenments:
                    rep_extended['acuerdos_prmid'].append(regex.sub('',agr.get_attribute('href')))
                
                next_buttons = browser.find_elements_by_css_selector('#' + div_id + ' .pages ul li.next a')
                if len(next_buttons) > 0:
                    browser.execute_script(next_buttons[0].get_attribute('href').replace('javascript:',''))
                    time.sleep(2)
                    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, div_id)))
                else:
                    break
            
            # Groups
            div_id = 'ctl00_mainPlaceHolder_pnlGruposH'
            browser.execute_script("__doPostBack('ctl00$mainPlaceHolder$btnGruposH','')")
            time.sleep(2)
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, div_id)))
            subcount = 1
            while True:
                pt('Get Groups: Page ' + str(subcount))
                subcount = subcount + 1
                groups = browser.find_elements_by_css_selector('#' + div_id + ' table.tabla tbody tr td:nth-child(1)')
                for gr in groups:
                    rep_extended['grupos_interparlamentarios'].append(gr.text)
                
                next_buttons = browser.find_elements_by_css_selector('#' + div_id + ' .pages ul li.next a')
                if len(next_buttons) > 0:
                    browser.execute_script(next_buttons[0].get_attribute('href').replace('javascript:',''))
                    time.sleep(2)
                    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, div_id)))
                else:
                    break
            
            # Curriculum
            div_id = 'ctl00_mainPlaceHolder_pnlCurriculum'
            browser.execute_script("__doPostBack('ctl00$mainPlaceHolder$btnCurriculumH','')")
            time.sleep(2)
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, div_id)))
            curriculum = browser.find_element_by_css_selector('#' + div_id + '')
            family = curriculum.find_elements_by_xpath("//h3[contains(text(),'Antecedentes Familiares')]/following-sibling::ul[1]/li");
            for fa in family:
                rep_extended['familia'].append(fa.text)
            
            work = curriculum.find_elements_by_xpath("//h3[contains(text(),'Actividad Laboral')]/following-sibling::ul[1]/li");
            for wk in work:
                rep_extended['actividad_laboral'].append(wk.text)
            pt('Get Curriculum')
            
            diputados_extended.append(rep_extended)
            rep_saved = True
        
        except TimeoutException as ex:
            pprint(ex)
            pt('PAGE TimeoutException ERROR')
        except NoSuchElementException as ex:
            pprint(ex)
            pt('PAGE NoSuchElementException ERROR')
        except WebDriverException as ex:
            pprint(ex)
            pt('PAGE WebDriverException ERROR')
        
        
        if rep_saved:
            pt('Current Rep Saved')
        else:
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
with open('data/diputados.extended.1014.json', 'w') as outfile:
    json.dump(diputados_extended, outfile)
    
# save errors
with open('data/errors/diputados.extended.1014.json', 'w') as outfile:
    json.dump(diputados_missed, outfile)
pt('Save to File')
