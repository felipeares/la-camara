# -*- coding: utf-8 -*-
import json

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

import imp
import scraperhelper
imp.reload(scraperhelper)

scraperhelper.setOutputDescription(
        'Detalle de todas las resoluciones para el período 2014-2018',
        {
            'type': 'Dictionary',
            'elements': [
                {'type': 'String','name': 'periodo','description': '' },
                {'type': 'String','name': 'ingreso','description': '' },
                {'type': 'String','name': 'numero','description': '' },
                {'type': 'String','name': 'res_prmid','description': '' },
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
                }
            ]
        }
)

scraperhelper.setPrintTimeTo(True)
browser = scraperhelper.initBrowser()

# input file
resoluciones = json.load(open('./data/resoluciones.simple.1418.json'))
scraperhelper.pt('Get input file')

# saved files
try:
    output_saved = json.load(open('./data/resoluciones.extended.1418.json'))
    errors_saved = json.load(open('./data/errors/resoluciones.extended.1418.json'))
    indexes_saved = scraperhelper.getSavedIndexes(output_saved['data'], 'res_prmid')
    data = output_saved['data']
    errors = errors_saved
except FileNotFoundError:
    output_saved = []
    errors_saved = []
    indexes_saved = []
    data = []
    errors = []
scraperhelper.pt('Get saved files')

# main script GO!
all_count = len(resoluciones['data'])
counting = 0
for res in resoluciones['data']:
    if res['prmid'] not in indexes_saved:
        if res['prmid'] in errors_saved:
            errors.remove(res['prmid'])
        
        saved = False
        counting = counting + 1
        try:
            ac = {
                "periodo": '',
                "ingreso": '',
                "numero": '',
                "res_prmid": res['prmid'],
                "titulo": '',
                "estado": '',
                "autores": []
            }
            
            # Go to 'Proyectos de Ley'
            browser.get('https://www.camara.cl/trabajamos/presolucion_detalle.aspx?prmID=' + res['prmid'])
             
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
            scraperhelper.pt('Loaded Resolution ' + res['prmid'] + ' ' + str(counting) + '/' + str(all_count))
            if not saved:
                errors.append(res['prmid'])
                print('----------- WITH ERROR! -------------')


scraperhelper.closeSeleniumBrowser(browser)
scraperhelper.saveToFile('resoluciones.extended.1418', data, errors)