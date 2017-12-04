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
                {'type': 'String','name': 'fecha','description': '' },
                {'type': 'String','name': 'sesion','description': '' },
                {'type': 'String','name': 'estado','description': '' },
                {'type': 'String','name': 'prmid','description': '' },
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
                        {'type': 'List','name': 'boletin_link','description': '' },
                        {'type': 'String','name': 'materia','description': '' },
                        {'type': 'String','name': 'artículo','description': '' },
                        {'type': 'String','name': 'tipo','description': '' },
                        {'type': 'String','name': 'tipo','resultado': '' },
                        {'type': 'String','name': 'votacion_prmid','description': '' },
                        {'type': 'String','name': 'favor','description': '' },
                        {'type': 'String','name': 'contra','description': '' },
                        {'type': 'String','name': 'abstencion','description': '' },
                        {'type': 'String','name': 'dispensados','description': '' }
                    ]
                },
                {
                    'type': 'Dictionary','name': 'acuerdos', 'description': '', 
                    'elements': [
                        {'type': 'String','name': 'ingreso','description': '' },
                        {'type': 'String','name': 'numero','description': '' },
                        {'type': 'String','name': 'acuerdo_prmid','description': '' },
                        {'type': 'String','name': 'titulo','description': '' },
                        {'type': 'String','name': 'estado','description': '' }
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
counting = 0
for session in sessions_data['data']:
    counting = counting + 1
    saved = False
    try:
        sesion = {
            "fecha": session['fecha'],
            "sesion": session['sesion'],
            "estado": session['estado'],
            "prmid": session['prmid'],
            "ordenes": [],
            "asistencia": [],
            "intervenciones": [],
            "votaciones": [],
            "acuerdos": []
        }
        
        # Go to 'Ordenes del día'
        browser.get('https://www.camara.cl/trabajamos/sesion_ordendia.aspx?prmid=' + session['prmid'])
        for el in browser.find_elements_by_css_selector('#detail .stress'):
            table = el.find_elements_by_tag_name('td')
            if(len(table)>0):
                boletin = {
                    "boletin": el.find_element_by_tag_name('h2').text.replace('Boletín ',''),
                    "proyecto": table[0].text.replace('ver detalle',''),
                    "pley_prmid": scraperhelper.getQueryParametersElementChild(table[0])[0],
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
                            "link": scraperhelper.getQueryParametersElementChild(cols[2])[0]
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
        # scraperhelper.pt('Orders Scraped')
        
        
        # Go to 'Asistencia'
        """
        browser.get('https://www.camara.cl/trabajamos/sesion_asistencia.aspx?prmid=' + session['prmid'])
        for tr in browser.find_elements_by_css_selector('#detail .col.detalle table.tabla tbody tr'):
            tds = tr.find_elements_by_tag_name('td')
            asistencia = {
                "diputado_prmid": scraperhelper.getQueryParametersElementChild(tds[0])[0],
                "partido_prmid": tds[1].text,
                "asistencia": tds[2].text,
                "observacion": tds[3].text,
                "ingreso": tds[4].text
            }
            sesion['asistencia'].append(asistencia)
        # scraperhelper.pt('Assistance Scraped')
        """
        browser.get('https://www.camara.cl/trabajamos/sesion_asistencia.aspx?prmid=' + session['prmid'])
        js_script = "return_scrap_array = []; $('#detail .col.detalle table.tabla tbody tr').each(function(index) { return_scrap_array.push($(this).find('td').get().map( (td) => [td.textContent, td.getElementsByTagName('a')[0] ? td.getElementsByTagName('a')[0].href : ''] ) )}); return JSON.stringify(return_scrap_array);"
        asist_array = json.loads(browser.execute_script(js_script))
        for asist in asist_array:
            asistencia = {
                "diputado_prmid": scraperhelper.getQueryParametersFromUrl(asist[0][1])[0],
                "partido_prmid": asist[1][0],
                "asistencia": asist[2][0],
                "observacion": asist[3][0],
                "ingreso": asist[4][0]
            }
            sesion['asistencia'].append(asistencia)
        
        # Go to 'Intervenciones'
        browser.get('https://www.camara.cl/trabajamos/sesion_intervenciones.aspx?prmid=' + session['prmid'])
        for tr in browser.find_elements_by_css_selector('#detail table#ctl00_mainPlaceHolder_grvIntervenciones tbody tr'):
            tds = tr.find_elements_by_tag_name('td')
            asistencia = {
                "diputado_prmid": scraperhelper.getQueryParametersElementChild(tds[1])[0],
                "partido_prmid": tds[2].text,
                "etapa": tds[3].text,
                "detalle": tds[4].text,
                "documento": tds[5].text,
                "duracion": tds[6].text
            }
            sesion['intervenciones'].append(asistencia)
        # scraperhelper.pt('Interventions Scraped')

        
        # Go to 'Votaciones'
        browser.get('https://www.camara.cl/trabajamos/sesion_votaciones.aspx?prmid=' + session['prmid'])
        for el in browser.find_elements_by_css_selector('#detail .stress'):            
            vote_link = scraperhelper.getElementWithText(el, './p/a', 'ver detalle de la votación')
            resume = el.find_elements_by_css_selector('div table.tabla tbody tr td')
            if len(resume) != 4:
                print(str(len(resume)))
                resume = ['']*4
            
            votacion = {
                "boletin": scraperhelper.getElementTextWithException(el,'h3'),
                "boletin_link": scraperhelper.getElementParamsForParentWithTag(el,'h3'),
                "materia": scraperhelper.getRestOfTheTextForElementWith(el, './p', 'Materia:').strip(),
                "artículo": scraperhelper.getRestOfTheTextForElementWith(el, './p', 'Artículo:').strip(),
                "tipo": scraperhelper.getRestOfTheTextForElementWith(el, './p', 'Tipo:').strip(),
                "resultado": scraperhelper.getRestOfTheTextForElementWith(el, './p', 'Resultado:').replace(' ver detalle de la votación','').strip(),
                "votacion_prmid": scraperhelper.getQueryParametersFromUrl(vote_link.get_attribute('href'))[0] if vote_link  else '',
                "favor": resume[0].text,
                "contra": resume[1].text,
                "abstencion": resume[2].text,
                "dispensados": resume[3].text
            }
            sesion['votaciones'].append(votacion)
            
        # scraperhelper.pt('Votes Scraped')
        
        # Go to 'Acuerdos'
        browser.get('https://www.camara.cl/trabajamos/sesion_pacuerdo.aspx?prmid=' + session['prmid'])
        for tr in browser.find_elements_by_css_selector('#detail table.tabla tbody tr'):
            tds = tr.find_elements_by_tag_name('td')
            acuerdo = {
                "ingreso": tds[0].text,
                "numero": tds[1].text,
                "acuerdo_prmid": scraperhelper.getQueryParametersElementChild(tds[1])[0],
                "titulo": tds[2].text,
                "estado": tds[3].text
            }
            sesion['acuerdos'].append(acuerdo)
        # scraperhelper.pt('Agreenments Scraped')        
        
        data.append(sesion)
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
        scraperhelper.pt('Loaded Session ' + session['prmid'])
        if not saved:
            errors.append(session['prmid'])
            print('----------- WITH ERROR! -------------')

scraperhelper.closeSeleniumBrowser(browser)
scraperhelper.saveToFile('sesiones.extended.1418', data, errors)