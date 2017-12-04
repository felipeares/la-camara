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
        'Detalle de las mociones (Proyectos de Ley) creadas por los Diputados',
        {
            'type': 'Dictionary',
            'elements': [
                {'type': 'String','name': 'legislatura','description': '' },
                {'type': 'String','name': 'fecha','description': '' },
                {'type': 'String','name': 'estado','description': '' },
                {'type': 'String','name': 'boletin','description': '' },
                {'type': 'String','name': 'materia','description': '' },
                {'type': 'String','name': 'iniciativa','description': '' },
                {'type': 'String','name': 'origen','description': '' },
                {'type': 'String','name': 'prmid','description': '' },
                {'type': 'String','name': 'descripcion','description': '' },
                {
                    'type': 'Dictionary','name': 'hitos', 'description': '', 
                    'elements': [
                        {'type': 'String','name': 'fecha','description': '' },
                        {'type': 'String','name': 'sesios','description': '' },
                        {'type': 'String','name': 'etapa','description': '' },
                        {'type': 'String','name': 'sub_etapa','description': '' },
                        {'type': 'String','name': 'documento_link','description': '' }
                    ]
                },
                {
                    'type': 'Dictionary','name': 'informes', 'description': '', 
                    'elements': [
                        {'type': 'String','name': 'fecha','description': '' },
                        {'type': 'String','name': 'estapa','description': '' },
                        {'type': 'String','name': 'informe','description': '' },
                        {'type': 'String','name': 'documento_link','description': '' }
                    ]
                },
                {
                    'type': 'Dictionary','name': 'oficios', 'description': '', 
                    'elements': [
                        {'type': 'String','name': 'fecha','description': '' },
                        {'type': 'String','name': 'numero','description': '' },
                        {'type': 'String','name': 'etapa','description': '' },
                        {'type': 'String','name': 'oficio','description': '' },
                        {'type': 'String','name': 'documento_link','description': '' }
                    ]
                },
                {
                    'type': 'Dictionary','name': 'autores', 'description': '', 
                    'elements': [
                        {'type': 'String','name': 'nombre_diputado','description': '' },
                        {'type': 'List','name': 'region','description': '' },
                        {'type': 'String','name': 'distrito','description': '' },
                        {'type': 'String','name': 'partido','description': '' },
                        {'type': 'String','name': 'tipo','description': '' }
                    ]
                }
            ]
        }
)

scraperhelper.setPrintTimeTo(True)
browser = scraperhelper.initBrowser()

# input file
mociones = json.load(open('./data/mociones.simple.1418.json'))
scraperhelper.pt('Get Motions from file')

# saved files
output_saved = json.load(open('./data/mociones.extended.1418.json'))
errors_saved = json.load(open('./data/errors/mociones.extended.1418.json'))
indexes_saved = scraperhelper.getSavedIndexes(output_saved['data'], 'prmid')
scraperhelper.pt('Get saved files')

# output lists
data = output_saved['data']
errors = errors_saved


# main script GO!
all_count = len(mociones)
counting = 0
for mocion in mociones:
    if mocion['prmid'] not in indexes_saved:
        if mocion['prmid'] in errors_saved:
            errors.remove(mocion['prmid'])
        
        saved = False
        counting = counting + 1
        try:
            moc = {
                "legislatura": '',
                "fecha": '',
                "estado": '',
                "boletin": '',
                "materia": '',
                "iniciativa": '',
                "origen": '',
                "prmid": mocion['prmid'],
                "descripcion": '',
                "hitos": [],
                "informes": [],
                "oficios": [],
                "autores": [],
            }
            
            # Go to 'Proyectos de Ley'
            browser.get('https://www.camara.cl/pley/pley_detalle.aspx?prmID=' + mocion['prmid'])
             
            try:
                moc['descripcion'] = browser.find_element_by_css_selector('h3.caption').text
            except NoSuchElementException as ex:
                moc['descripcion'] = ''
            
            for tr in browser.find_elements_by_css_selector('.wrapperDataGroup table.tabla tr'):
                if 'Legislatura:' in tr.text:
                    moc['legislatura'] = tr.text.replace('legislatura:','').strip()
                elif 'Fecha de ingreso:' in tr.text:
                    moc['fecha'] = tr.text.replace('Fecha de ingreso:','').strip()
                elif 'Estado:' in tr.text:
                    moc['estado'] = tr.text.replace('Estado:','').strip()
                elif 'Numero de boletín:' in tr.text:
                    moc['boletin'] = tr.text.replace('Numero de boletín:','').strip()
                elif 'Materia:' in tr.text:
                    moc['materia'] = tr.text.replace('Materia:','').strip()
                elif 'Iniciativa:' in tr.text:
                    moc['iniciativa'] = tr.text.replace('Iniciativa:','').strip()
                elif 'Cámara de origen:' in tr.text:
                    moc['origen'] = tr.text.replace('Cámara de origen:','').strip()
            
            # Hitos
            for tr in browser.find_elements_by_css_selector('table#ctl00_mainPlaceHolder_grvtramitacion tbody tr'):
                cols = tr.find_elements_by_tag_name('td')
                if len(cols) > 4: 
                    hito = {
                        "fecha": cols[0].text,
                        "sesion": cols[1].text,
                        "etapa": cols[2].text,
                        "sub_etapa": cols[3].text,
                        "documento_link": scraperhelper.getQueryParametersElementChild(cols[4])[0]
                    }
                moc['hitos'].append(hito)
            
            # Informes
            browser.execute_script("__doPostBack('ctl00$mainPlaceHolder$btnInformes','')")
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'ctl00_mainPlaceHolder_pnlInformes')))
            for tr in browser.find_elements_by_css_selector('table#ctl00_mainPlaceHolder_grvinformes tbody tr'):
               cols = tr.find_elements_by_tag_name('td')
               if len(cols) > 3: 
                    informe = {
                        "fecha": cols[0].text,
                        "etapa": cols[1].text,
                        "informe": cols[2].text,
                        "documento_link": scraperhelper.getQueryParametersElementChild(cols[3])[0]
                    }
                    moc['informes'].append(informe) 
            
            # Oficios
            browser.execute_script("__doPostBack('ctl00$mainPlaceHolder$btnOficios','')")
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'ctl00_mainPlaceHolder_pnlOficios')))
            for tr in browser.find_elements_by_css_selector('table#ctl00_mainPlaceHolder_grvoficios tbody tr'):
               cols = tr.find_elements_by_tag_name('td')
               if len(cols) > 4: 
                    oficio = {
                        "fecha": cols[0].text,
                        "numero": cols[1].text,
                        "etapa": cols[2].text,
                        "oficio": cols[3].text,
                        "documento_link": scraperhelper.getQueryParametersElementChild(cols[4])[0]
                    }
                    moc['oficios'].append(oficio) 
            
            # Autores
            browser.execute_script("__doPostBack('ctl00$mainPlaceHolder$btnAutores','')")
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'ctl00_mainPlaceHolder_pnlAutores')))
            for tr in browser.find_elements_by_css_selector('table#ctl00_mainPlaceHolder_grvAutores tbody tr'):
               cols = tr.find_elements_by_tag_name('td')
               if len(cols) > 3: 
                    autor = {
                        "nombre_diputado": cols[0].text,
                        "region": cols[1].text,
                        "distrito": cols[2].text,
                        "partido": cols[3].text
                    }
                    moc['autores'].append(autor) 
            
            
            data.append(moc)
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
            scraperhelper.pt('Loaded Motion ' + mocion['prmid'] + ' ' + str(counting) + '/' + str(all_count))
            if not saved:
                errors.append(mocion['prmid'])
                print('----------- WITH ERROR! -------------')


scraperhelper.closeSeleniumBrowser(browser)
scraperhelper.saveToFile('mociones.extended.1418', data, errors)