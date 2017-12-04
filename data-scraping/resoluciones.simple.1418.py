# -*- coding: utf-8 -*-
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import imp
import scraperhelper
imp.reload(scraperhelper)

scraperhelper.setOutputDescription(
        'Lista de todos los proyectos de resolución de la cámara de Diputados para el período 2014-2018',
        {
            'type': 'Dictionary',
            'elements': [
                {'type': 'String', 'name': 'ingreso', 'description': ''},
                {'type': 'String', 'name': 'numero', 'description': ''},
                {'type': 'String', 'name': 'titulo', 'description': ''},
                {'type': 'String', 'name': 'estado', 'description': ''},
                {'type': 'String', 'name': 'documento_link', 'description': ''},
                {'type': 'String', 'name': 'prmid', 'description': ''}
            ]
        }
)

scraperhelper.setPrintTimeTo(True)
browser = scraperhelper.initBrowser()

# output lists
data = []
errors = []

# main script GO!
page = 1
try:
    browser.get('https://www.camara.cl/trabajamos/presolucion.aspx')
    browser.execute_script("__doPostBack('ctl00$mainPlaceHolder$lblistadogral','')")
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'ctl00_mainPlaceHolder_pnlResultados')))
    scraperhelper.pt('Get First Site and load list')
    
    page_number = browser.find_element_by_css_selector('#detail .pages ul li.current').text
    while True:
        for tr in browser.find_elements_by_css_selector('#main table.tabla tbody tr'):
            cols = tr.find_elements_by_tag_name('td')
            if len(cols) > 5: 
                res = {
                    "ingreso": cols[0].text,
                    "numero": cols[1].text,
                    "titulo": cols[2].text,
                    "estado": cols[3].text,
                    "documento_link": scraperhelper.getLinkFromElementChild(cols[4]),
                    "prmid": scraperhelper.getQueryParametersElementChild(cols[5])[0]
                }
                data.append(res)
            
        next_buttons = browser.find_elements_by_css_selector('.pages ul li.next a')
        if len(next_buttons) > 0:
            page = page + 1
            browser.execute_script(next_buttons[0].get_attribute('href').replace('javascript:',''))
            page_number = scraperhelper.waitForChangesInAttribute(browser, '.pages ul li.current', page_number, text = True)
            scraperhelper.pt('Loading Page ' + str(page))
        else:
            break
            
    
except TimeoutException as ex:
    scraperhelper.pt('PAGE TimeoutException ERROR')
except NoSuchElementException as ex:
    scraperhelper.pt('PAGE NoSuchElementException ERROR')
except StaleElementReferenceException as ex:
    scraperhelper.pt('PAGE StaleElementReferenceException ERROR')
except WebDriverException as ex:
    scraperhelper.pt('PAGE WebDriverException ERROR')

scraperhelper.closeSeleniumBrowser(browser)
scraperhelper.saveToFile('resoluciones.simple.1418', data, errors)