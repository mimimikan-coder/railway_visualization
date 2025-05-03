import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import os
from flask import Flask, jsonify


g = nx.Graph()
script_dir = os.path.dirname(__file__)

ope_path = os.path.normpath(os.path.join(script_dir, "..", "high_speed_trains_operation_data.csv"))
del_path = os.path.normpath(os.path.join(script_dir, "..", "railway_stations_delay_data.csv"))
junc_path = os.path.normpath(os.path.join(script_dir, "..", "junction_stations_data.csv"))
dis_path = os.path.normpath(os.path.join(script_dir, "..", "adjacent_railway_stations_mileage_data.csv"))

operation_data = pd.read_csv(ope_path)
delay_data = pd.read_csv(del_path)
junction_data = pd.read_csv(junc_path)
distance_data = pd.read_csv(dis_path)

operation_data["scheduled_arrival_time"] = pd.to_datetime(operation_data["scheduled_arrival_time"], errors="coerce")
operation_data["scheduled_departure_time"] = pd.to_datetime(operation_data["scheduled_departure_time"])

network_df = pd.merge(distance_data, junction_data, left_on="from_station", right_on="station_name", how="left")
network_df = pd.merge(network_df, junction_data, left_on="to_station", right_on="station_name", how="left")
network_df = network_df[["from_station", "to_station", "mileage"]]

for _, row in network_df.iterrows():
    g.add_edge(row["from_station"], row["to_station"], weight=row["mileage"])

degree_dict = dict(g.degree())
degree_series = pd.Series(degree_dict)

avg_path_length = nx.average_shortest_path_length(g)
density = nx.density(g)
clustering_coeff = nx.average_clustering(g)

def calcDegreeCentrality(G):
    deg_dict = nx.degree_centrality(G)
    deg_df = pd.DataFrame(deg_dict.items(), columns=["station_name", "degree_centrality"])
    return deg_df

def calcBetweenCentrality(G):
    betweenness_dict = nx.betweenness_centrality(G)
    betweenness_df = pd.DataFrame(betweenness_dict.items(), columns=["station_name", "betweenness_centrality"])
    return betweenness_df

def calcClosenessCentrality(G):
    closeness_dict = nx.closeness_centrality(G)
    closeness_df = pd.DataFrame(closeness_dict.items(), columns=["station_name", "closeness_centrality"])
    return closeness_df

def calcAllCentrality(G):
    deg = calcDegreeCentrality(G)
    between = calcBetweenCentrality(G)
    close = calcClosenessCentrality(G)

    centrality_df = deg.merge(between, on="station_name").merge(close, on="station_name")
    return centrality_df
