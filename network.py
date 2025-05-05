from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os
import pandas as pd
import networkx as nx
from simulation.simulate import *
import json
#from network.network_analyze import calcAllCentrality

# read CSV
script_dir = os.path.dirname(__file__)

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

# set station list
delay_stations = delay_data["station_name"].unique().tolist()

delay_info = operation_data.groupby("station_name")["arrival_delay"].mean().to_dict()
nx.set_node_attributes(g, delay_info, "delay")

initial_station = 'Yimianpobei Railway Station'
top10 =  list(top10_data.sort_values("score", ascending=False).head(10))

SIR_simulation_network(g, initial_infected=[initial_station], immune_nodes=top10)