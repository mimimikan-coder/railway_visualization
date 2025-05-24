from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os
import pandas as pd
import networkx as nx
from simulation.simulate import *
import json

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

sis_history = SIS_simulation(g, initial_station)
history = SIR_simulation(g, initial_infected=[initial_station], immune_nodes=[])
history_immunity = SIR_simulation(g, initial_infected=[initial_station], immune_nodes=top10)

sis_infected = infected_count(sis_history)
infected = infected_count(history)
infected_immunity = infected_count(history_immunity)

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("railway_visualization/index.html")

# draw network graphs
@app.route("/network")
def network():
    data = get_graph_data(g)
    return jsonify(data)

@app.route("/network-parameter")
def network_parameter():
    a, d, c = calc_parameter(g)
    data = {
        "avarage_path_length": a,
        "density": d,
        "clustering_coef": c
    }
    return jsonify(data)

@app.route("/network-graph")
def network_graph():
    return render_template("railway_visualization/graph.html")

# simulation modules
@app.route("/simulation")
def get_simulation_data():
    data = {
        "steps":list(range(len(infected))),
        "infected":infected,
        "infected_immunity": infected_immunity,
        "infected_sis": sis_infected
    }
    return jsonify(data)

@app.route("/simulation/multiple_simulation")
def run_multiple_sim():
    top10_nodes, counts = multiple_sim(g, initial_infected=[initial_station], immune_nodes=[])
    return jsonify({
        "top10_nodes": top10_nodes
    })

@app.route("/simulation/SIRwith_immunity", methods=["POST"])
def run_SIRwith_immunity():
    nodes = request.json.get("immune_nodes", [])
    res = SIR_simulation(g, initial_infected=[initial_station], immune_nodes=nodes, steps=50)

    infected_countA = infected_count(res)
    return jsonify({
        "infected_counts": infected_countA
    })

@app.route("/simulation/best_node")
def get_best_node():
    best_nodes = select_nodes(g, initial_infected=[initial_station], candidate_nodes=list(g.nodes), k=10, trials=5, steps=20)

    return jsonify({
        "best_nodes": best_nodes
    })

@app.route("/simulation/optimal_immunity", methods=["POST"])
def run_optimal_simulation():
    nodes = request.json.get("bests", [])
    res = SIR_simulation(g, initial_infected=[initial_station], immune_nodes=nodes, steps=50)
    
    count = infected_count(res)
    return jsonify({
        "infected_count": count
    })

@app.route("/network-animation")
def animation_home():
    return render_template("railway_visualization/network.html")

@app.route("/network-data")
def network_data():
    with open ("data/network_data.json") as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == "__main__":      # localhost 5000
    app.run(debug=True)

# 最尤ノードの選択　貪欲法　中心性の視覚化(統計図)　遅延駅10駅(毎度計算？)＋最尤10駅のリスト表示
# シミュのアニメーション画面でどのノードを初期感染点にするかを選べるようにする
# 遅延駅、未遅延駅のタイムステップごとのグラフを横(下)に表示

"""
中心性、平均パス長などの表示→レポート作成、社団構造の可視化
"""