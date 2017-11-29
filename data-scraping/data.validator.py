# -*- coding: utf-8 -*-
import json
# from pprint import pprint

def getBlankFields(input_list, field, validator = '', is_list = False, input_id = 'prmid'):
    returned_list = []
    count = 0
    for rep in input_list:
        if is_list:
            if len(rep[field]) == validator:
                returned_list.append(rep[input_id])
                count = count + 1
        else:
            if rep[field] == validator:
                returned_list.append(rep[input_id])
                count = count + 1
    print(str(round(100*count/len(input_list),2)) + '%')
    return returned_list

def getBlankFields2Degree(input_list, field, field2, validator = '', is_list = False, input_id = 'prmid'):
    returned_list = []
    count = 0
    for rep in input_list:
        if is_list:
            if len(rep[field][field2]) == validator:
                returned_list.append(rep[input_id])
                count = count + 1
        else:
            if rep[field][field2] == validator:
                returned_list.append(rep[input_id])
                count = count + 1
    print(str(round(100*count/len(input_list),2)) + '%')
    return returned_list

loaded = json.load(open('./data/sesiones.simple.1418.json'))

#empty_fields = getBlankFields(loaded, 'comite_parlamentario')
empty_fields = getBlankFields(loaded, 'prmid', validator = 0, is_list = True)
#empty_fields = getBlankFields2Degree(loaded, 'comisiones', 'permanentes', validator = 0, is_list = True)

print(str(' '.join(map(str, empty_fields))))