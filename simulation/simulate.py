# function liblary

import pandas as pd
import networkx as nx
import numpy as np
import os
from pyvis.network import Network
from collections import defaultdict
import json
import matplotlib.colors as mcolors
from networkx.algorithms.community import greedy_modularity_communities

def calc_parameter(G):
    avg_path_length = nx.average_shortest_path_length(G)
    density = nx.density(G)
    clustering_coeff = nx.average_clustering(G)

    return avg_path_length, density, clustering_coeff

def get_graph_data(G):
    communities = list(greedy_modularity_communities(G))
    print(f"Num of Community: {len(communities)}")

    pos = nx.spring_layout(G, seed=42)
    pos = {node: (x, y*1.5) for node, (x, y) in pos.items()}

    degree_dict = dict(G.degree())
    threshold = sorted(degree_dict.values(), reverse=True)[int(len(degree_dict) * 0.1)] 
    labels = {node: node for node, degree in degree_dict.items() if degree >= threshold}

    colors = list(mcolors.TABLEAU_COLORS.values())
    for i, comm in enumerate(communities):
        nx.draw_networkx_nodes(G, pos, nodelist=list(comm), node_color=colors[i % len(colors)], label=f"Community {i+1}")

    nodes = []
    colors = list(mcolors.TABLEAU_COLORS.values())
    for node in G.nodes():
        comm_id = next((i for i, comm in enumerate(communities) if node in comm), -1)
        nodes.append({
            "id": node,
            "x": pos[node][0],
            "y": pos[node][1],
            "color": colors[comm_id % len(colors)] if comm_id != -1 else "#888",
            "label": node if degree_dict[node] >= threshold else "",  
            "degree": degree_dict[node]
        })

    edges = [{"source": u, "target": v, "weight": G[u][v]["weight"]} for u, v in G.edges()]

    degrees = list(degree_dict.values())
    degree_counts = np.bincount(degrees)
    degree_distribution = [
        {"degree": k, "count": int(count)}
        for k, count in enumerate(degree_counts)
        if count > 0
    ]

    return {
        "nodes": nodes, 
        "edges": edges, 
        "num_communities": len(communities), 
        "graph_id":"Network Graph", 
        "degree_distribution": degree_distribution
    }

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

    layout = nx.spring_layout(G, seed=42)
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

    layout = nx.spring_layout(G, seed=42)
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

    layout = nx.spring_layout(G, seed=42)
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


