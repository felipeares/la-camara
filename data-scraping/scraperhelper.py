import time
from datetime import datetime
from pytz import timezone
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from pyvirtualdisplay import Display

"""
GLOBALS
"""
print_times = True

path_to_chrome = './drivers/chromedriver'

date_started = str(datetime.now(timezone('America/Santiago')).strftime("%Y-%m-%d %H:%M:%S"))
start_clock = time.perf_counter()
last_milestone = start_clock

query_regex = re.compile(r"[a-z/:._?=]", re.IGNORECASE)

output = {
    'date_started': date_started,
    'date_finished': '', # saved at the end
    'execution_time': '', # saved at the end
    'description': '', #saved if promted
    'structure': {}, #saved if promted
    'file_name': '', # saved on file saved
    'error_size': 0, # saved on file saved
    'data': [] # saved on file saved
}

"""
Set the debug printing
"""
def setPrintTimeTo(should_print = True):
     global print_times
     print_times =  should_print
"""
Print a new message and seconds since last printed message
"""
def pt(message):
    global last_milestone
    print(message + ': ' + str(round(time.perf_counter() - last_milestone, 2)) + ' seconds')
    last_milestone = time.perf_counter()

"""
Save description and output structure
"""
def setOutputDescription(description = '', structure = {}):
    global last_milestone
    output['description'] = description
    output['structure'] = structure
    if print_times: pt('setOutputDescription')

"""
Init the commonly used options for Selenium
"""
def initSeleniumOptions():
    opts = Options()
    opts.add_argument('--no-sandbox') 
    opts.add_argument("--disable-setuid-sandbox")
    opts.add_argument("--disable-flash-3d")
    opts.add_argument("--disable-flash-stage3d")
    opts.add_argument("--kiosk")
    if print_times: pt('initSeleniumOptions')
    return opts

"""
Init the Browser Driver
"""
def initBrowser(set_page_load_timeout = 180):
    browser = webdriver.Chrome(executable_path=path_to_chrome, chrome_options=initSeleniumOptions())
    browser.set_page_load_timeout(set_page_load_timeout)
    if print_times: pt('initBrowser')
    return browser

"""
Wait for changes in an element attribute/text
"""
def waitForChangesInAttribute(browser, css_selector, first_value, attribute = '', text = False, exception_max = 10, wait = 0.1):
    while True:
        exception_counter = 0
        try:
            if text:
                new_value = browser.find_element_by_css_selector(css_selector).text
            else:
                new_value = browser.find_element_by_css_selector(css_selector).get_attribute(attribute)
            
            if new_value == first_value:
                time.sleep(wait)
            else:
                return new_value
                break
        except StaleElementReferenceException:
            if exception_counter > exception_max:
                return first_value
                break
            else:
                exception_counter = exception_counter + 1
                time.sleep(wait)

"""
Close Browser
"""
def closeSeleniumBrowser(browser):
    try:
        browser.close()
        browser.quit()
        if print_times: pt('Close Browser')
    except WebDriverException:
        if print_times: pt('Close Browser WebDriverException ERROR')
    except:
        if print_times: pt('Close Browser WILDCARD ERROR')

"""
Init the screenless display
"""
def initDisplay(height = 800, width = 1280):
    display = Display(visible=0, size=(height, width))
    display.start()
    if print_times: pt('initDisplay')
    return display

"""
Get the element in a specific tag. I does not exist return ''
"""
def getElementTextWithException(element_parent, tag):
    try:
        ret = element_parent.find_element_by_tag_name(tag).text
    except NoSuchElementException:
        ret = ''
    except:
        ret = ''
    finally:
        return ret
    
"""
Get the element parameters by tag parent
"""
def getElementParamsForParentWithTag(element_parent, tag):
    return getQueryParametersElementChild(element_parent.find_element_by_tag_name(tag))
    
"""
Get the query parameters from a url
"""
def getQueryParametersFromUrl(url):
    return query_regex.sub('',url).split('&')

"""
Get the query parameters from the first child <a> element
"""
def getQueryParametersElementChild(el):
    try:
        ret = getQueryParametersFromUrl(el.find_element_by_tag_name('a').get_attribute('href'))
    except NoSuchElementException:
        ret = ['','','','','']
    except:
        ret = ['','','','','']
    finally:
        return ret
    
"""
Get the link href from the first child <a> element
"""
def getLinkFromElementChild(el):
    for a in el.find_elements_by_tag_name('a'):
        return a.get_attribute('href')
    return ''
    
"""
Get the text of a element which contains a given text, excluding that given text
"""
def getRestOfTheTextForElementWith(parent_element, xpath, containing, exclude = True):
    elements = parent_element.find_elements_by_xpath(xpath + "[.//*[contains(text(),'" + containing + "')]]");
    if len(elements)>0:
        if exclude:
            return elements[0].text.replace(containing, '')
        else:
            return elements[0].text
    else:
        return ''
    

"""
Get the element which contains a given text
"""
def getElementWithText(parent_element, xpath, containing):
    elements = parent_element.find_elements_by_xpath(xpath + "[contains(text(),'" + containing + "')]");
    if len(elements)>0:
        return elements[0]
    else:
        return False


"""
Save to file output and errors
"""
def saveToFile(name, output_data, errors = []):
    global start_clock
    global output
    
    output['data'] = output_data
    output['date_finished'] = str(datetime.now(timezone('America/Santiago')).strftime("%Y-%m-%d %H:%M:%S"))
    output['execution_time'] = str(round(time.perf_counter() - start_clock))
    output['file_name'] = name
    output['error_size'] = len(errors)
    
    with open('data/' + name + '.json', 'w') as outfile:
        json.dump(output, outfile)
    with open('data/errors/' + name + '.json', 'w') as outfile:
        json.dump(errors, outfile)
    if print_times: pt('saveToFile')
    
"""
Get a List of indexes saved
"""
def getSavedIndexes(saved, index_name):
    out = []
    for d in saved:
        out.append(d[index_name])
    return out
