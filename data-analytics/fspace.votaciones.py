# -*- coding: utf-8 -*-
import json
import numpy as np
from sklearn.cluster import KMeans

def getIndexOfRep(diputados_list, prmid):
    try:
        return diputados_list.index(prmid)
    except ValueError:
        return -1

# Get the data
votaciones = json.load(open('../data-scraping/data/votaciones.extended.1418.json'))
diputados = json.load(open('../data-scraping/data/diputados.extended.1418.json'))

# Index reps prmid with a 0-119 index
diputados_list = []
diputados_info = {}
for dip in diputados:
    diputados_list.append(dip['prmid'])
    diputados_info[dip['prmid']] = dip
    diputados_info[dip['prmid']]['index'] = diputados_list.index(dip['prmid'])


# Build matrix
all_against = 0
for votacion in votaciones['data']:
    if len(votacion['contra']) + len(votacion['abstencion']) == 0:
        all_against = all_against + 1


total = len(votaciones['data']) - all_against
votes_matrix = np.zeros( (120, total) ).astype(int)
counting = 0
for votacion in votaciones['data']:
    if len(votacion['contra']) + len(votacion['abstencion']) > 0:
        # print('Loading votacion ' + str(counting+1) + ' of ' + str(total))
        
        for prmid in votacion['favor']:
            index = getIndexOfRep(diputados_list, prmid)
            if index > -1:
                votes_matrix[index,counting] = 100
        
        for prmid in votacion['abstencion']:
            index = getIndexOfRep(diputados_list, prmid)
            if index > -1:
                votes_matrix[index,counting] = -50
        
        for prmid in votacion['contra']:
            index = getIndexOfRep(diputados_list, prmid)
            if index > -1:
                votes_matrix[index,counting] = -100
        
        counting = counting + 1

print()
clusters = 10
kmeans = KMeans(n_clusters=clusters, random_state=0).fit(votes_matrix)
predictions = kmeans.predict(votes_matrix)
clusters_list = []
clusters_partidos = []
for i in range(0,clusters):
    print('------ CLUSTER Nº ' + str(i) + ' -----------')
    cluster_prmids = []
    partidos_sum = {}
    prediction_index = 0
    for prediction in predictions:
        if prediction == i:
            cluster_prmids.append(diputados_list[prediction_index])
            partido = diputados_info[diputados_list[prediction_index]]['comite_parlamentario']
            if partido in partidos_sum:
                partidos_sum[partido] = partidos_sum[partido] + 1
            else:
                partidos_sum[partido] = 1
        prediction_index = prediction_index + 1
    
    clusters_list.append(cluster_prmids)
    
    clusters_partidos.append(partidos_sum)
    for key in partidos_sum:
        print(str(key) + ': ' + str(partidos_sum[key]))
        if key == 'Unión Demócrata Independiente':
            ultra_right_cluster = i

print()
print('Ultra right cluster: ' + str(ultra_right_cluster))
centers = kmeans.cluster_centers_
distances_to_ultra_right = []
for center in centers:
    distances_to_ultra_right.append(round(np.linalg.norm(center-centers[ultra_right_cluster])))


# Re-Order Clusters
while True:
    changes = False
    for dist_index in range(1,clusters) :
        if distances_to_ultra_right[dist_index-1] > distances_to_ultra_right[dist_index]:
            distances_to_ultra_right[dist_index], distances_to_ultra_right[dist_index-1] = distances_to_ultra_right[dist_index-1], distances_to_ultra_right[dist_index]
            clusters_list[dist_index], clusters_list[dist_index-1] = clusters_list[dist_index-1], clusters_list[dist_index]
            clusters_partidos[dist_index], clusters_partidos[dist_index-1] = clusters_partidos[dist_index-1], clusters_partidos[dist_index]
            centers[dist_index], centers[dist_index-1] = centers[dist_index-1], centers[dist_index].copy()
            changes = True
    
    if not changes:
        break
    
# Generate a distance-to-cluster-center matrix
clusters_center_ditance = []
c = 0
max_distance = 0
for cluster in clusters_list:
    distances = []
    for prmid in cluster:
        dist = round(np.linalg.norm(votes_matrix[diputados_list.index(prmid), :]-centers[c]))
        distances.append(dist)
        max_distance = max(max_distance, dist)
    clusters_center_ditance.append(distances)
    c = c + 1
    
# Generate cluster center distance matrix
clusters_center_distance_matrix = np.zeros( (clusters, clusters) )
for c1 in range(0,clusters):
    for c2 in range(0,clusters):
        clusters_center_distance_matrix[c1,c2] = (np.linalg.norm(centers[c1]-centers[c2]))
        
# Build a graph json ouput
graph_json = {
    "nodes": [],
    "links": []
}

max_distance = max_distance = max(max_distance, np.max(clusters_center_distance_matrix))

for c in range(0,clusters):
    # Create the cluster node 
    graph_json["nodes"].append({"id": ('c'+str(c)), "group": c, "n": 'Bloque '+str(c+1), "is_c": True, "p":clusters_partidos[c]})
    for i in range(0,len(clusters_list[c])):
        # Create the rep node
        graph_json["nodes"].append({"id": clusters_list[c][i], "group": c, "n":  diputados_info[clusters_list[c][i]]['nombre'], "is_c": False, "p":diputados_info[clusters_list[c][i]]['comite_parlamentario']})
        # Create the link
        graph_json["links"].append({"source": ('c'+str(c)), "target": clusters_list[c][i], "value": round(clusters_center_ditance[c][i]/max_distance, 2), "is_c_to_c": False})
    
    # Create the clusters links
    for c2 in range(c+1,clusters):
        graph_json["links"].append({"source": ('c'+str(c)), "target": ('c'+str(c2)), "value": round(np.asscalar(clusters_center_distance_matrix[c,c2])/max_distance, 2), "is_c_to_c": True})


# Save outputs
with open('../data-analytics/data/graph.clusters.json', 'w') as outfile:
    json.dump(graph_json, outfile)

with open('../data-analytics/data/clusters.votaciones.json', 'w') as outfile:
    json.dump(clusters_list, outfile)


            