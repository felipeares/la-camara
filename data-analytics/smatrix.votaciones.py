# -*- coding: utf-8 -*-
import json
import numpy as np
import matplotlib.pyplot as plt

# Search for rep
def getIndexOfRep(diputados_list, prmid):
    try:
        return diputados_list.index(prmid)
    except ValueError:
        return -1

# Soft Matrix Function
def myfunction( x ):
    return (x / np.max(x))*100

# Change columns/row
def changeIndexFromTo(from_index, to_index):
    global matrix_ordered
    global diputados_list_reordered
    
    # change list index position
    diputados_list_reordered[to_index], diputados_list_reordered[from_index] = diputados_list_reordered[from_index], diputados_list_reordered[to_index]

    # change columns position
    matrix_ordered[:,from_index], matrix_ordered[:,to_index] = matrix_ordered[:,to_index], matrix_ordered[:,from_index].copy()
    
    # change rows position
    matrix_ordered[from_index,:], matrix_ordered[to_index,:] = matrix_ordered[to_index,:], matrix_ordered[from_index,:].copy()

    
# Get the data
votaciones = json.load(open('../data-scraping/data/votaciones.extended.1418.json'))
clusters = json.load(open('../data-analytics/data/clusters.votaciones.json'))
diputados = json.load(open('../data-scraping/data/diputados.extended.1418.json'))

# Build the starter matrix
matrix = np.zeros( (120, 120) )
matrix_soften = np.zeros( (120, 120) )
matrix_ordered = np.zeros( (120, 120) )
matrix_concurrencies = np.zeros( (120, 120) )

# Build analytics matrix
# [favor, contra, abstencion, art5t0, pareos]
sumvotes = np.zeros( (len(votaciones['data'])+1, 5) )

# Index reps prmid with a 0-119 index
diputados_list = []
for cluster in clusters:
    for prmid in cluster:
        diputados_list.append(prmid)

# calculate concurrencies
total = len(votaciones['data'])
counting = 0
for votacion in votaciones['data']:
    print('Loading votacion ' + str(counting+1) + ' of ' + str(total))
    counting = counting + 1
    
    if len(votacion['contra']) + len(votacion['abstencion']) > 0:
        
        mergedlist = votacion['favor'] + votacion['contra'] + votacion['abstencion']
        rep_data_array = []
        
        # Load the data
        for i in range(0,120):
            if diputados_list[i] in mergedlist:
                rep_data_array.append({
                    "in": True,
                    "favor": diputados_list[i] in votacion['favor'],
                    "contra": diputados_list[i] in votacion['contra'],
                    "abstencion": diputados_list[i] in votacion['abstencion']
                })
            else:
                rep_data_array.append({"in": False})
        
        # Edit the matrix
        for i in range(0,120):
            if rep_data_array[i]["in"]:
                for j in range(i,120):
                    if rep_data_array[j]["in"]:
                        matrix_concurrencies[i,j] = matrix_concurrencies[i,j] + 1
                        
                        if rep_data_array[i]['favor'] and rep_data_array[j]['favor']:
                            matrix[i,j] = matrix[i,j] + 1
                        
                        elif rep_data_array[i]['contra'] and rep_data_array[j]['contra']:
                            matrix[i,j] = matrix[i,j] + 1
                        
                        elif rep_data_array[i]['abstencion'] and rep_data_array[j]['abstencion']:
                            matrix[i,j] = matrix[i,j] + 1
                        
                        elif rep_data_array[i]['favor'] and rep_data_array[j]['contra']:
                            matrix[i,j] = matrix[i,j] - 1
                            
                        elif rep_data_array[i]['contra'] and rep_data_array[j]['favor']:
                            matrix[i,j] = matrix[i,j] - 1
 
                    

# Divide matrix by matrix_concurrencies
for i in range(0,120):
    for j in range(i,120):
        if matrix_concurrencies[i,j] > 0:
            matrix_soften[i,j] = matrix[i,j]/matrix_concurrencies[i,j]
        else: 
            matrix_soften[i,j] = matrix[i,j]//1
        
        matrix_soften[j,i] = matrix_soften[i,j]
        

# Ordering
matrix_ordered = np.around(matrix_soften[:].copy(), decimals=2)
diputados_list_reordered = diputados_list[:].copy()
clusters = json.load(open('../data-analytics/data/clusters.votaciones.json'))

# Named Clusters
ticks_name = []
for cluster_index in range(0,len(clusters)):
    for prmid in clusters[cluster_index]:
        ticks_name.append(cluster_index)

ind = 0
for cluster in clusters:
    for prmid in cluster:
        changeIndexFromTo(getIndexOfRep(diputados_list,prmid), ind)
        ind = ind +  1


for rep in range(0,120):
    # get rep cluster
    rep_cluster = ticks_name[rep]
    # loop backward untill cluster changes and re-order lower-higher left-right
    while True:
        changes = False
        for i in range(1,rep - 1):
            if ticks_name[rep - i - 1] == rep_cluster:
                if matrix_ordered[rep,rep - i - 1] >  matrix_ordered[rep,rep - i]:
                    changes = True
                    changeIndexFromTo(rep - i - 1,rep - i)
            else:
                break
        if not changes:
            break
    
    # loop forward untill cluster changes and re-order higher-lower left-right
    while True:
        changes = False
        for i in range(1,120 - rep - 1):
            if ticks_name[rep + i + 1] == rep_cluster:
                if matrix_ordered[rep,rep + i + 1] >  matrix_ordered[rep,rep + i]:
                    changes = True
                    changeIndexFromTo(rep + i + 1,rep + i)
            else:
                break
        if not changes:
            break
        
plt.rcParams.update({'font.size': 4})
fig, ax = plt.subplots()
cax = ax.matshow(matrix_ordered, interpolation='nearest')
ax.grid(True)
plt.xticks(range(120), ticks_name, rotation=90);
plt.yticks(range(120), ticks_name);
plt.show()

# Build a graph json ouput
graph_json = {
    "nodes": [],
    "links": []
}

# Create a diputados array
diputados_info = {}
for rep in diputados:
    diputados_info[rep['prmid']] = rep

# Create the nodes and links
for i in range(0,120):
    # Create node
    rep = diputados_info[diputados_list_reordered[i]]
    graph_json["nodes"].append({"id": diputados_list_reordered[i], "group": ticks_name[i], "nombre": rep['nombre'], "partido": rep['comite_parlamentario']})
    
    # Create link for the rep
    for j in range(i+1,120):
        graph_json["links"].append({"source": diputados_list_reordered[i], "target": diputados_list_reordered[j], "value": np.asscalar(matrix_ordered[i,j])})

# Save outputs
with open('../data-analytics/data/graph.votaciones.json', 'w') as outfile:
    json.dump(graph_json, outfile)

np.savetxt("../data-analytics/data/prmidorder.votaciones.csv", diputados_list_reordered, delimiter=",", fmt="%s")
np.savetxt("../data-analytics/data/smatrixorder.votaciones.csv", matrix_ordered, delimiter=",")
np.savetxt("../data-analytics/data/sum.votaciones.csv", sumvotes, delimiter=",")