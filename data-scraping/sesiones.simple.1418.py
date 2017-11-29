# -*- coding: utf-8 -*-
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

import imp
import scraperhelper
imp.reload(scraperhelper)

scraperhelper.setOutputDescription(
        'Lista de todas las sesiones de la cámara de Diputados para el período 2014-2018',
        {
            'type': 'Dictionary',
            'elements': [
                {'type': 'String', 'name': 'fecha', 'description': ''},
                {'type': 'String', 'name': 'sesion', 'description': ''},
                {'type': 'String', 'name': 'estado', 'description': ''},
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
try:
    browser.get('https://www.camara.cl/trabajamos/sala_sesiones.aspx')
    scraperhelper.pt('Get First Site')
    
    option_selected = browser.find_element_by_css_selector('#ctl00_mainPlaceHolder_ddlLegislaturas option[selected]').get_attribute('value')
    scraperhelper.pt('Get Handy Elements')
    
    while int(option_selected) > 45:   
        scraperhelper.pt('Get year id: ' + str(option_selected) + ' ----------')
        page_number = browser.find_element_by_css_selector('#detail .pages ul li.current').text
        
        subcount = 1
        while True:
            scraperhelper.pt('Get Sessions: Page ' + str(subcount))
            subcount = subcount + 1
            
            rows = browser.find_elements_by_css_selector('#detail table.tabla tbody tr')
            for row in rows:
                try:
                    columns = row.find_elements_by_css_selector('td')
                    prmid = scraperhelper.getQueryParametersFromUrl(columns[1].find_element_by_tag_name('a').get_attribute('href'))
                    sesion = {
                            "fecha":columns[0].text,
                            "sesion":columns[1].text,
                            "estado":columns[2].text,
                            "prmid":prmid[0]
                    }
                    data.append(sesion)
                except StaleElementReferenceException:
                    print('ERROR!! -----')
            
            next_buttons = browser.find_elements_by_css_selector('#detail .pages ul li.next a')
            if len(next_buttons) > 0:
                browser.execute_script(next_buttons[0].get_attribute('href').replace('javascript:',''))
                page_number = scraperhelper.waitForChangesInAttribute(browser, '#detail .pages ul li.current', page_number, text = True)
            else:
                break
        
        # Get next option
        select = browser.find_element_by_id('ctl00_mainPlaceHolder_ddlLegislaturas')
        for option in select.find_elements_by_tag_name('option'):
            if int(option.get_attribute('value')) == int(option_selected) - 1:
                option.click()
                break
        scraperhelper.pt('New option clicked')
        
        # Wait till loaded
        option_selected = scraperhelper.waitForChangesInAttribute(browser, '#ctl00_mainPlaceHolder_ddlLegislaturas option[selected]', option_selected, attribute = 'value')
        scraperhelper.pt('New page loaded')
            
    
except TimeoutException as ex:
    scraperhelper.pt('PAGE TimeoutException ERROR')
except NoSuchElementException as ex:
    scraperhelper.pt('PAGE NoSuchElementException ERROR')
except StaleElementReferenceException as ex:
    scraperhelper.pt('PAGE StaleElementReferenceException ERROR')
except WebDriverException as ex:
    scraperhelper.pt('PAGE WebDriverException ERROR')

scraperhelper.closeSeleniumBrowser(browser)
scraperhelper.saveToFile('sesiones.simple.1418', data, errors)