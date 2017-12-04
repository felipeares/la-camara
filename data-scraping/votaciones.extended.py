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
        'Detalle de todas votaciones para el período 2014-2018',
        {
            'type': 'Dictionary',
            'elements': [                
                {'type': 'String','name': 'prmid','description': '' },
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
scraperhelper.pt('Get sessions from file')

# output lists
data = []
errors = []

# main script GO!
counting = 0
for session in sessions_data['data']:
    for voting in session['votaciones']:
        counting = counting + 1
        saved = False
        try:
            # Go to 'Detale Votaciones'
            browser.get('https://www.camara.cl/trabajamos/sala_votacion_detalle.aspx?prmId=' + voting['votacion_prmid'])
            
            vote = {
                "prmid": voting['votacion_prmid'],
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
            scraperhelper.pt('Loaded Voting ' + voting['votacion_prmid'])
            if not saved:
                errors.append(voting['votacion_prmid'])
                print('----------- WITH ERROR! -------------')

scraperhelper.closeSeleniumBrowser(browser)
scraperhelper.saveToFile('votaciones.extended.1418', data, errors)
