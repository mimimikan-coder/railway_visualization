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

top10 =  top10_data.sort_values("score", ascending=False).head(10)

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
@app.route("/simulation/multiple_simulation", methods=["POST"])
def run_multiple_sim():
    source = request.get_json().get("source")
    print(source)
    top10_nodes, counts = multiple_sim(g, initial_infected=[source], immune_nodes=[])
    return jsonify({
        "top10_nodes": top10_nodes
    })

@app.route("/simulation/centrality_top10")
def centrality_top10():
    print(top10)
    data = {
        "name":top10["station_name"].tolist(),
        "degree_centrality": top10["degree_centrality"].tolist(),
        "betweenness_centrality": top10["betweenness_centrality"].tolist(),
        "closeness_centrality": top10["closeness_centrality"].tolist(),
        "score": top10["score"].tolist()
    }
    return jsonify(data)

@app.route("/simulation/best_node", methods=["POST"])
def get_best_node():
    source = request.get_json().get("source")
    best_nodes = select_nodes(g, initial_infected=[source], candidate_nodes=list(g.nodes), k=10, trials=5, steps=20)

    return jsonify({
        "best_nodes": best_nodes
    })




# network.html
@app.route("/network-animation")
def animation_home():
    return render_template("railway_visualization/network.html")

@app.route("/network-data")
def network_data():
    with open ("data/network_data.json") as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/network/simulation", methods=["POST"])
def network_simulation():
    req = request.get_json()
    model = req.get("model")
    source = req.get("source")

    print(source)
    if not g.has_node(source):
        return jsonify({"error": "node not found"})
    
    if model == "SIR":
        result = SIR_simulation(g, initial_infected=[source], immune_nodes=[])
    elif model == "SIS":
        result = SIS_simulation(g, initial_infected=[source])
    
    print(result["links"][:10])
    return jsonify(result)

@app.route("/nodes")
def nodes():
    nodes = [{"id": node, "label":node} for node in g.nodes()]
    return jsonify(nodes)

if __name__ == "__main__":      # localhost 5000
    app.run(debug=True)