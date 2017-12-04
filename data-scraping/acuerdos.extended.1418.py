# -*- coding: utf-8 -*-
import json

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
        'Detalle de todos los acuerdos para el período 2014-2018',
        {
            'type': 'Dictionary',
            'elements': [
                {'type': 'String','name': 'periodo','description': '' },
                {'type': 'String','name': 'ingreso','description': '' },
                {'type': 'String','name': 'numero','description': '' },
                {'type': 'String','name': 'acuerdo_prmid','description': '' },
                {'type': 'String','name': 'titulo','description': '' },
                {'type': 'String','name': 'estado','description': '' },
                {
                    'type': 'Dictionary','name': 'autores', 'description': '', 
                    'elements': [
                        {'type': 'String','name': 'nombre_diputado','description': '' },
                        {'type': 'String','name': 'prmid_diputado','description': '' },
                        {'type': 'String','name': 'partido','description': '' },
                        {'type': 'String','name': 'calidad','description': '' }
                    ]
                },
                {
                    'type': 'Dictionary','name': 'resumen', 'description': '', 
                    'elements': [
                        {'type': 'String','name': 'despacho','description': '' },
                        {'type': 'String','name': 'numero','description': '' },
                        {'type': 'String','name': 'destinatario','description': '' },
                        {'type': 'String','name': 'entrega','description': '' },
                        {'type': 'String','name': 'documento_link','description': '' }
                    ]
                }
            ]
        }
)

scraperhelper.setPrintTimeTo(True)
browser = scraperhelper.initBrowser()

# input file
sesiones = json.load(open('./data/sesiones.extended.1418.json'))
scraperhelper.pt('Get input file')

# saved files
output_saved = json.load(open('./data/acuerdos.extended.1418.json'))
errors_saved = json.load(open('./data/errors/acuerdos.extended.1418.json'))
indexes_saved = scraperhelper.getSavedIndexes(output_saved['data'], 'acuerdo_prmid')
scraperhelper.pt('Get saved files')

# output lists
data = output_saved['data']
errors = errors_saved

# main script GO!
all_count = len(sesiones['data'])
counting = 0
for session in sesiones['data']:
    for acuerdo in session['acuerdos']:
        if acuerdo['acuerdo_prmid'] not in indexes_saved:
            if acuerdo['acuerdo_prmid'] in errors_saved:
                errors.remove(acuerdo['acuerdo_prmid'])
            
            saved = False
            counting = counting + 1
            try:
                ac = {
                    "periodo": '',
                    "ingreso": '',
                    "numero": '',
                    "acuerdo_prmid": acuerdo['acuerdo_prmid'],
                    "titulo": '',
                    "estado": '',
                    "autores": [],
                    "resumen": []
                }
                
                # Go to 'Proyectos de Ley'
                browser.get('https://www.camara.cl/trabajamos/pacuerdo_detalle.aspx?prmid=' + acuerdo['acuerdo_prmid'])
                 
                try:
                    ac['titulo'] = browser.find_element_by_css_selector('h3.caption').text
                except NoSuchElementException as ex:
                    ac['titulo'] = ''
                
                for tr in browser.find_elements_by_css_selector('.wrapperDataGroup table.tabla tr'):
                    if 'Período legislativo:' in tr.text:
                        ac['periodo'] = tr.text.replace('Período legislativo:','').strip()
                    elif 'Ingreso:' in tr.text:
                        ac['ingreso'] = tr.text.replace('Ingreso:','').strip()
                    elif 'Número:' in tr.text:
                        ac['numero'] = tr.text.replace('Número:','').strip()
                    elif 'Estado:' in tr.text:
                        ac['estado'] = tr.text.replace('Estado:','').strip()
                   
                
                # Autores
                page_number = browser.find_element_by_css_selector('.pages ul li.current').text
                while True:
                    for tr in browser.find_elements_by_css_selector('#ctl00_mainPlaceHolder_pnlAutores table.tabla tbody tr'):
                        cols = tr.find_elements_by_tag_name('td')
                        if len(cols) > 2: 
                            autor = {
                                "nombre_diputado": cols[0].text,
                                "prmid_diputado": scraperhelper.getQueryParametersElementChild(cols[0])[0],
                                "partido": cols[1].text,
                                "calidad": cols[2].text
                            }
                            ac['autores'].append(autor)
                        
                    next_buttons = browser.find_elements_by_css_selector('.pages ul li.next a')
                    if len(next_buttons) > 0:
                        browser.execute_script(next_buttons[0].get_attribute('href').replace('javascript:',''))
                        page_number = scraperhelper.waitForChangesInAttribute(browser, '.pages ul li.current', page_number, text = True)
                    else:
                        break
                
                # Resumen
                browser.execute_script("__doPostBack('ctl00$mainPlaceHolder$btnResumen','')")
                try:
                    WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.ID, 'ctl00_mainPlaceHolder_pnlResumen')))
                    for tr in browser.find_elements_by_css_selector('#ctl00_mainPlaceHolder_pnlResumen table.tabla tbody tr'):
                       cols = tr.find_elements_by_tag_name('td')
                       if len(cols) > 4: 
                            res = {
                                "despacho": cols[0].text,
                                "numero": cols[1].text,
                                "destinatario": cols[2].text,
                                "entrega": cols[3].text,
                                "documento_link": scraperhelper.getLinkFromElementChild(cols[4])
                            }
                            ac['resumen'].append(res) 
                except TimeoutException as ex:
                    ac['resumen'] = []
                
                data.append(ac)
                saved = True
                            
                    
            except TimeoutException as ex:
                scraperhelper.pt('PAGE TimeoutException ERROR')
            except NoSuchElementException as ex:
                scraperhelper.pt('PAGE NoSuchElementException ERROR')
            except StaleElementReferenceException as ex:
                scraperhelper.pt('PAGE StaleElementReferenceException ERROR')
            except WebDriverException as ex:
                scraperhelper.pt('PAGE WebDriverException ERROR')
            
            finally:
                scraperhelper.pt('Loaded Agreenment ' + acuerdo['acuerdo_prmid'] + ' ' + str(counting) + '/' + str(all_count))
                if not saved:
                    errors.append(acuerdo['acuerdo_prmid'])
                    print('----------- WITH ERROR! -------------')


scraperhelper.closeSeleniumBrowser(browser)
scraperhelper.saveToFile('acuerdos.extended.1418', data, errors)