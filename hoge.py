from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os
import pandas as pd
import networkx as nx
from simulation.simulate import *
import json
from networkx.algorithms.community import greedy_modularity_communities
from simulation.simulate import *
import matplotlib.pyplot as plt

# read CSV
script_dir = os.path.dirname(__file__)

path = os.path.normpath(os.path.join(script_dir, "./data", "centrality_score.csv"))
score_data = pd.read_csv(path)
stations = score_data["station_name"]
score_data = score_data["score"]

ope_path = os.path.normpath(os.path.join(script_dir, "./data", "high_speed_trains_operation_data.csv"))
del_path = os.path.normpath(os.path.join(script_dir, "./data", "railway_stations_delay_data.csv"))
junc_path = os.path.normpath(os.path.join(script_dir, "./data", "junction_stations_data.csv"))
dis_path = os.path.normpath(os.path.join(script_dir, "./data", "adjacent_railway_stations_mileage_data.csv"))
top10_path = os.path.normpath(os.path.join(script_dir, "./data", "centrality_score.csv"))

operation_data = pd.read_csv(ope_path)
delay_data = pd.read_csv(del_path)
junction_data = pd.read_csv(junc_path)
distance_data = pd.read_csv(dis_path)
top10_data = pd.read_csv(top10_path)

# make graph
g = nx.Graph()
for _, row in distance_data.iterrows():
    g.add_edge(row["from_station"], row["to_station"], weight=row["mileage"])

centrality = nx.degree_centrality(g)
plt.bar(centrality.keys(), centrality.values(), color='#3B82F6')
plt.xlabel('Node', fontsize=12)
plt.ylabel('Degree Centrality', fontsize=12)
plt.title('Node Centrality', fontsize=14)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# communities = list(greedy_modularity_communities(g))
# degree_centrality = nx.degree_centrality(g)
# results = []

# for i, community in enumerate(communities):
#     community_nodes = list(community)
#     sorted_nodes = sorted(
#         community_nodes,
#         key= lambda node: degree_centrality[node]
#     )
#     top_nodes = sorted_nodes[:10]
#     results.append(top_nodes)

# for i, result in enumerate(results):
#     print(i)
#     print(result)

# initial_station = "Yimianpobei Railway Station"
# SIR_simulation_network(g, initial_infected=[initial_station], immune_nodes=[])

# layout = nx.spring_layout(g, seed=42)

# nodes = []
# for n in range(len(stations)):
#     nodes.append({
#         "id": n,
#         "x": layout[stations[n]][0],
#         "y": layout[stations[n]][1],
#         "centrality": score_data[n],
#         "name": stations[n]
#     })

# with open("data/centrality_nodes.json", "w", encoding="utf-8") as f:
#     json.dump({"nodes": nodes}, f, ensure_ascii=False, indent=2)