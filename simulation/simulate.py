import pandas as pd
import networkx as nx
import numpy as np
import os
from pyvis.network import Network
from collections import defaultdict
import json

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
    a = 0.3
    b = 0.5
    c = 0.2
    centrality_df["score"] = (
        a*centrality_df["degree_centrality"]+
        b*centrality_df["betweenness_centrality"]+
        c*centrality_df["closeness_centrality"]
    )
    return centrality_df

def SIS_simulation(G, initial_infected, steps=50, beta=0.3, gamma=0.1):
    infected = {node: "S" for node in G.nodes}
    infected[initial_infected] = "I"

    history = []
    for step in range(steps):
        new_infected = infected.copy()

        for node in G.nodes:
            if infected[node] == "I":                     # delay
            
                for neighbor in G.neighbors(node):
                    if infected[neighbor] == "S" and np.random.rand() < beta:
                        new_infected[neighbor] = "I"      # transmission
                    
                if np.random.rand() < gamma:
                    new_infected[neighbor] = "S"                    # cured
        #print(list(infected.keys())[0], node)
        infected = new_infected.copy()
        history.append(infected)

    return history


def SIR_simulation(G, initial_infected, immune_nodes, steps=50, beta=0.3, gamma=0.1):
    infected = {}
    for node in G.nodes:
        if node in immune_nodes:
            infected[node] = "R"
        else:
            infected[node] = "S"

    for node in initial_infected:
        if node not in immune_nodes:
            infected[node] = "I"

    history = []
    for step in range(steps):
        new_infected = infected.copy()
        for node in G.nodes:
            if infected[node] == "I":
                for neighbor in G.neighbors(node):
                    if infected[neighbor] == "S" and np.random.rand() < beta:
                        new_infected[neighbor] = "I"
                if np.random.rand() < gamma:
                    new_infected[node] = "R"

        infected = new_infected
        history.append(infected.copy())

    return history    

def SIR_simulation_network(G, initial_infected, immune_nodes, steps=50, beta=0.3, gamma=0.1):
    infected = {}
    for node in G.nodes:
        if node in immune_nodes:
            infected[node] = "R"
        else:
            infected[node] = "S"

    for node in initial_infected:
        if node not in immune_nodes:
            infected[node] = "I"

    history = []
    for step in range(steps):
        new_infected = infected.copy()
        for node in G.nodes:
            if infected[node] == "I":
                for neighbor in G.neighbors(node):
                    if infected[neighbor] == "S" and np.random.rand() < beta:
                        new_infected[neighbor] = "I"
                if np.random.rand() < gamma:
                    new_infected[node] = "R"

        infected = new_infected
        history.append(infected.copy())

    data = {
        "nodes": [{"id": str(n)} for n in G.nodes()],
        "links": [{"source": str(u), "target": str(v)} for u, v in G.edges()],
        "history": history
    }
    with open("data/network_data.json", "w") as f:
        json.dump(data, f)


def multiple_sim(G, initial_infected, immune_nodes=[], beta=0.3, gamma=0.1, steps=50, trials=100):
    infection_count = defaultdict(int)

    for trial in range(trials):
        history = SIR_simulation(
            G,
            initial_infected = initial_infected,
            immune_nodes=immune_nodes,
            beta=beta,
            gamma=gamma,
            steps=steps
        )

        for state in history:
            for node, status in state.items():
                if status == "I":
                    infection_count[node] += 1

    sorted_nodes = sorted(infection_count.items(), key=lambda x: x[1], reverse=True)
    top10_nodes = [node for node, count in sorted_nodes[:10]]

    return top10_nodes, infection_count

def infected_count(history):
    counts = []
    for state in history:
        counts.append(sum(1 for status in state.values() if status == "I"))
    return counts

def select_nodes(G, initial_infected, candidate_nodes, k=10, trials=20, steps=50, beta=0.3, gamma=0.1):
    selected = []
    available = candidate_nodes.copy()

    for _ in range(k):
        best_node = None
        best_result = float("inf")

        for node in available:
            trial_immune = selected + [node]
            total_infected = 0

            for trial in range(trials):
                history = SIR_simulation(
                    G,
                    initial_infected=initial_infected,
                    immune_nodes=trial_immune,
                    beta=beta,
                    gamma=gamma,
                    steps=steps
                )

                total_infected += sum(
                    sum(1 for status in step.values() if status == "I")
                    for step in history
                )

            avg_infected = total_infected / trials

            if avg_infected < best_result:
                best_result = avg_infected
                best_node = node

        selected.append(best_node)
        available.remove(best_node)

    return selected



# # read CSV
# script_dir = os.path.dirname(__file__)

# ope_path = os.path.normpath(os.path.join(script_dir, "./data", "high_speed_trains_operation_data.csv"))
# del_path = os.path.normpath(os.path.join(script_dir, "./data", "railway_stations_delay_data.csv"))
# junc_path = os.path.normpath(os.path.join(script_dir, "./data", "junction_stations_data.csv"))
# dis_path = os.path.normpath(os.path.join(script_dir, "./data", "adjacent_railway_stations_mileage_data.csv"))

# operation_data = pd.read_csv(ope_path)
# delay_data = pd.read_csv(del_path)
# junction_data = pd.read_csv(junc_path)
# distance_data = pd.read_csv(dis_path)

# # make graph
# g = nx.Graph()
# for _, row in distance_data.iterrows():
#     g.add_edge(row["from_station"], row["to_station"], weight=row["mileage"])

# # set station list
# delay_stations = delay_data["station_name"].unique().tolist()

# delay_info = operation_data.groupby("station_name")["arrival_delay"].mean().to_dict()
# nx.set_node_attributes(g, delay_info, "delay")

# initial_station = 'Yimianpobei Railway Station'

# top10, counts_list = multiple_sim(g, [initial_station])
# print(top10)

# history = SIR_simulation(g, initial_infected=[initial_station])
# history_immunity = SIR_simulation(g, initial_infected=[initial_station], immune_nodes=top10)
# infected = infected_count(history)
# infected_immunity = infected_count(history_immunity)




"""
# SIR sim with top node
pd.set_option("display.max_columns", 5)
df = calcAllCentrality(g)
top_10 = df.sort_values(by="score", ascending=False).head(10)
#df.to_csv("./centrality_score.csv")
top_nodes = top_10["station_name"].tolist()

beta = 0.3
gamma = 0.1
steps = 50
infected = {node: "S" for node in g.nodes}
infected[initial_station] = "I"
for node in top_nodes:
    infected[node] = "R"

history = []
for step in range(steps):
    new_infected = infected.copy()
    for node in g.nodes:
        if infected[node] == "I":
            for neighbor in g.neighbors(node):
                if infected[neighbor] == "S" and np.random.rand()<beta:
                    new_infected[neighbor] = "I"

            if np.random.rand() < gamma:
                new_infected[node] = "R"

    infected = new_infected
    history.append(infected.copy())
result = []
for step, state in enumerate(history):
    scount = list(state.values()).count("S")
    icount = list(state.values()).count("I")
    rcount = list(state.values()).count("R")

    result.append({
        "step":step, 
        "S": scount,
        "I": icount,
        "R": rcount
    })
print(pd.DataFrame(result))
"""


"""
# SIR simulation
infected = {node: "S" for node in g.nodes}
infected[initial_station] = "I"

beta = 0.3
gamma = 0.1
steps = 50

history = []
for step in range(steps):
    new_infected = infected.copy()

    for node in g.nodes:
        if infected[node] == "I":
            for neighbor in g.neighbors(node):
                if infected[neighbor] == "S" and np.random.rand() < beta:
                    new_infected[neighbor] = "I"

            if np.random.rand() < gamma:
                new_infected[node] = "R"

    infected = new_infected
    history.append(infected.copy())

result = []
for step, state in enumerate(history):
    scount = list(state.values()).count("S")
    icount = list(state.values()).count("I")
    rcount = list(state.values()).count("R")

    result.append({
        "step":step, 
        "S": scount,
        "I": icount,
        "R": rcount
    })
print(pd.DataFrame(result))
"""

"""for station in delay_stations:
    infected[station] = 1                   # 2row added
"""

"""
# simurate SIS model
# initialize constant
beta = 0.3
gamma = 0.1
steps = 50


# set delay station parameter
infected = {node: 0 for node in g.nodes}
infected[initial_station] = 1

history = []
for step in range(steps):
    new_infected = infected.copy()

    for node in g.nodes:
        if infected[node] == 1:                     # delay
            
            for neighbor in g.neighbors(node):
                if infected[neighbor] == 0 and np.random.rand() < beta:
                    new_infected[neighbor] = 1      # transmission
                    
            if np.random.rand() < gamma:
                new_infected[neighbor] = 0                    # cured
    #print(list(infected.keys())[0], node)
    infected = new_infected.copy()
    history.append(infected)

print("SIS simulation completed")
"""


# Delay駅のみでいいのか？遅れていない駅も込で計算しないといけないのでは？
# 終わったらやること　　Flaskでフロントエンドとつなげる　リアルタイム可視化　拡散マップ（ネットワーク図アニメーション）

