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
        'Recarga de votaciones con error para el período 2014-2018',
        {
            'type': 'Dictionary',
            'elements': [                
                {'type': 'String','name': 'boletin','description': '' },
                {'type': 'String','name': 'fecha','description': '' },
                {'type': 'String','name': 'materia','description': '' },
                {'type': 'String','name': 'articulo','description': '' },
                {'type': 'String','name': 'sesion','description': '' },
                {'type': 'String','name': 'tramite','resultado': '' },
                {'type': 'String','name': 'tipo','description': '' },
                {'type': 'String','name': 'quorum','description': '' },
                {'type': 'String','name': 'resultado','description': '' },
                {'type': 'List','name': 'favor','description': '' },
                {'type': 'List','name': 'contra','description': '' },
                {'type': 'List','name': 'abstencion','description': '' },
                {'type': 'List','name': 'articulo_quinto','description': '' },
                {'type': 'List','name': 'pareos','description': '' },
            ]
        }
)

scraperhelper.setPrintTimeTo(True)
browser = scraperhelper.initBrowser()

# input file
sessions_data = json.load(open('./data/sesiones.extended.1418.json'))
saved_data = json.load(open('./data/votaciones.extended.1418.json'))
errors_data = json.load(open('./data/errors/votaciones.extended.1418.json'))
scraperhelper.pt('Get files')

# output lists
data = []
errors = []


# preload data
for d in saved_data['data']:
    data.append(d)
scraperhelper.pt('Preload Data - ' + str(len(saved_data['data'])))

# main script GO!
counting = 0
for votacion_prmid in errors_data:
    counting = counting + 1
    saved = False
    try:
        # Go to 'Detale Votaciones'
        browser.get('https://www.camara.cl/trabajamos/sala_votacion_detalle.aspx?prmId=' + votacion_prmid)
        
        vote = {
            "boletin": '',
            "fecha": '',
            "materia": '',
            "articulo": '',
            "sesion": '',
            "tramite": '',
            "tipo": '',
            "quorum": '',
            "resultado": '',
            "favor": [],
            "contra": [],
            "abstencion": [],
            "articulo_quinto": [],
            "pareos": []
        }
        
        
        for el in browser.find_elements_by_css_selector('#detail .stress'):            
            try:
                h2 = el.find_element_by_tag_name('h2').text
            except NoSuchElementException as ex:
                h2 = 'SIN TITULO'
            
            
            if 'A favor' in h2:
                for a in el.find_elements_by_css_selector('#ctl00_mainPlaceHolder_dtlAFavor td a'):
                    vote['favor'].append(scraperhelper.getQueryParametersFromUrl(a.get_attribute('href'))[0])
            elif 'En contra' in h2:
                for a in el.find_elements_by_css_selector('#ctl00_mainPlaceHolder_dtlEncontra td a'):
                    vote['contra'].append(scraperhelper.getQueryParametersFromUrl(a.get_attribute('href'))[0])
            elif 'Abstención' in h2:
                for a in el.find_elements_by_css_selector('#ctl00_mainPlaceHolder_dtlAbstencion td a'):
                    vote['abstencion'].append(scraperhelper.getQueryParametersFromUrl(a.get_attribute('href'))[0])
            elif 'Artículo 5°' in h2:
                for a in el.find_elements_by_css_selector('table td a'):
                    vote['articulo_quinto'].append(scraperhelper.getQueryParametersFromUrl(a.get_attribute('href'))[0])
            elif 'Pareos' in h2:
                for a in el.find_elements_by_css_selector('#ctl00_mainPlaceHolder_dtlPareos td a'):
                    vote['pareos'].append(scraperhelper.getQueryParametersFromUrl(a.get_attribute('href'))[0])
            else:
                vote['boletin'] = h2.replace('Boletín ','')
                vote['fecha'] = scraperhelper.getRestOfTheTextForElementWith(el, './p', 'Fecha:').strip()
                vote['materia'] = scraperhelper.getRestOfTheTextForElementWith(el, './p', 'Materia:').strip()
                vote['articulo'] = scraperhelper.getRestOfTheTextForElementWith(el, './p', 'Artículo:').strip()
                vote['sesion'] = scraperhelper.getRestOfTheTextForElementWith(el, './p', 'Sesión:').strip()
                vote['tramite'] = scraperhelper.getRestOfTheTextForElementWith(el, './p', 'Trámite:').strip()
                vote['tipo'] = scraperhelper.getRestOfTheTextForElementWith(el, './p', 'Tipo de votació:').strip()
                vote['quorum'] = scraperhelper.getRestOfTheTextForElementWith(el, './p', 'Quorum:').strip()
                vote['resultado'] = scraperhelper.getRestOfTheTextForElementWith(el, './p', 'Resultado:').strip()
                if h2 == 'SIN TITULO':
                    vote['materia'] = el.find_element_by_tag_name('h3').text
        
        data.append(vote)
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
        scraperhelper.pt('Loaded Voting ' + votacion_prmid)
        if not saved:
            errors.append(votacion_prmid)
            print('----------- WITH ERROR! -------------')

scraperhelper.closeSeleniumBrowser(browser)
scraperhelper.saveToFile('votaciones.extended.1418', data, errors)


