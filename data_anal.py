import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import os

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

print(operation_data.head())
print(network_df.head())

for _, row in network_df.iterrows():
    g.add_edge(row["from_station"], row["to_station"], weight=row["mileage"])

plt.figure(figsize=(12, 12))
pos = nx.spring_layout(g)
nx.draw(g, pos, node_size=50, font_size=8, edge_color="skyblue")
plt.title("high speed railway network")
#plt.show()

degree_dict = dict(g.degree())
degree_series = pd.Series(degree_dict)

plt.figure(figsize=(10, 6))
degree_series.hist(bins=30, color="lightblue", edgecolor="black")
plt.title("degree bunpu")
plt.xlabel('number of station connection')
plt.ylabel('num of station')
#plt.show()

avg_path_length = nx.average_shortest_path_length(g)
print(f"average path length: {avg_path_length:.2f}")

density = nx.density(g)
print(f"network density: {density:.4f}")

clustering_coeff = nx.average_clustering(g)
print(f"average clustering coef: {clustering_coeff: .4f}")
