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
        'Detalle de todas las sesiones de la cámara de Diputados para el período 2014-2018',
        {
            'type': 'Dictionary',
            'elements': [
                {
                    'type': 'Dictionary','name': 'ordenes', 'description': '', 
                    'elements': [
                        {'type': 'String','name': 'boletin','description': '' },
                        {'type': 'String','name': 'proyecto','description': '' },
                        {'type': 'String','name': 'pley_prmid','description': '' },
                        {'type': 'String','name': 'origen','description': '' },
                        {'type': 'String','name': 'reglamentaria','description': '' },
                        {'type': 'String','name': 'informantes','description': '' },
                        {
                            'type': 'Dictionary','name': 'informes','description': '',
                            'elements': [
                                {'type': 'String','name': 'fecha','description': '' },
                                {'type': 'String','name': 'estapa','description': '' },
                                {'type': 'String','name': 'informe','description': '' },
                                {'type': 'String','name': 'link','description': '' }
                            ]
                        }
                    ]
                },
                {
                    'type': 'Dictionary','name': 'asistencia', 'description': '', 
                    'elements': [
                        {'type': 'String','name': 'diputado_prmid','description': '' },
                        {'type': 'String','name': 'partido_prmid','description': '' },
                        {'type': 'String','name': 'asistencia','description': '' },
                        {'type': 'String','name': 'observacion','description': '' },
                        {'type': 'String','name': 'ingreso','description': '' }
                    ]
                },
                {
                    'type': 'Dictionary','name': 'intervenciones', 'description': '', 
                    'elements': [
                        {'type': 'String','name': 'diputado_prmid','description': '' },
                        {'type': 'String','name': 'partido_prmid','description': '' },
                        {'type': 'String','name': 'etapa','description': '' },
                        {'type': 'String','name': 'detalle','description': '' },
                        {'type': 'String','name': 'documento','description': '' },
                        {'type': 'String','name': 'duracion','description': '' }
                    ]
                },
                {
                    'type': 'Dictionary','name': 'votaciones', 'description': '', 
                    'elements': [
                        {'type': 'String','name': 'boletin','description': '' },
                        {'type': 'String','name': 'materia','description': '' },
                        {'type': 'String','name': 'artículo','description': '' },
                        {'type': 'String','name': 'tipo','description': '' },
                        {'type': 'String','name': 'votacion_prmid','description': '' }
                    ]
                },
                {
                    'type': 'Dictionary','name': 'acuerdos', 'description': '', 
                    'elements': [
                        {'type': 'String','name': 'ingreso','description': '' },
                        {'type': 'String','name': 'numero','description': '' },
                        {'type': 'String','name': 'acuerdo_prmid','description': '' },
                        {'type': 'String','name': 'titulo','description': '' },
                        {'type': 'String','name': 'estado','description': '' },
                        {'type': 'String','name': 'documento_lnk','description': '' }
                    ]
                }
            ]
        }
)

scraperhelper.setPrintTimeTo(True)
browser = scraperhelper.initBrowser()

# input file
sessions_data = json.load(open('./data/sesiones.simple.1418.json'))
scraperhelper.pt('Get sessions from file')

# output lists
data = []
errors = []

# main script GO!

for session in sessions_data['data']:
    try:
        scraperhelper.pt('Get Session ' + session['prmid'])
        
        sesion = {
            "fecha": session['fecha'],
            "sesion": session['sesion'],
            "estado": session['estado'],
            "prmid": session['prmid'],
            "ordenes": [],
            "asistencia": [],
            "intervenciones": [],
            "votaciones": []
        }
        
        # Go to 'Ordenes del día'
        browser.get('https://www.camara.cl/trabajamos/sesion_ordendia.aspx?prmid=' + session['prmid'])
        for el in browser.find_elements_by_css_selector('#detail .stress'):
            table = el.find_elements_by_tag_name('td')
            if(len(table)>0):
                boletin = {
                    "boletin": el.find_element_by_tag_name('h2').text.replace('Boletín ',''),
                    "proyecto": table[0].text.replace('ver detalle',''),
                    "pley_prmid": scraperhelper.getQueryParametersFromUrl(table[0].find_element_by_tag_name('a').get_attribute('href'))[0],
                    "origen": table[1].text,
                    "reglamentaria": table[2].text,
                    "informantes": table[3].text,
                    "informes": []
                }
                
                infs = table[4].find_elements_by_css_selector('tbody tr')
                for tr in infs:
                    cols = tr.find_elements_by_tag_name('td')
                    if(len(cols)>0):
                        inf = {
                            "fecha": cols[0].text,
                            "etapa": cols[1].text,
                            "informe": cols[2].text,
                            "link": scraperhelper.getQueryParametersFromUrl(cols[2].find_element_by_tag_name('a').get_attribute('href'))[0]
                        }
                        boletin["informes"].append(inf)
            else:
                boletin = {
                    "boletin": el.find_element_by_tag_name('h2').text.replace('Boletín ',''),
                    "proyecto": '',
                    "pley_prmid": '',
                    "origen": '',
                    "reglamentaria": '',
                    "informantes": '',
                    "informes": []
                }
                        
            sesion['ordenes'].append(boletin)
        
        
        
        # Go to 'Asistencia'
        # browser.get('https://www.camara.cl/trabajamos/sesion_asistencia.aspx?prmid=' + session['prmid'])
        
        
        
        
        # Go to 'Intevenciones'
        # browser.get('https://www.camara.cl/trabajamos/sesion_intervenciones.aspx?prmid=' + session['prmid'])
        
        
        
        
        
        # Go to 'Votaciones'
        # browser.get('https://www.camara.cl/trabajamos/sesion_votaciones.aspx?prmid=' + session['prmid'])
        
        
        
        
        
        # Go to 'Acuerdos'
        # browser.get('https://www.camara.cl/trabajamos/sesion_pacuerdo.aspx?prmid=' + session['prmid'])
        
        
        
        
        data.append(sesion)
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
# scraperhelper.saveToFile('sesiones.extended.1418', data, errors)