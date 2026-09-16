import sys
import os

# ============================================================
# THÊM ĐƯỜNG DẪN src/ VÀO PYTHONPATH
# ============================================================
CURRENT_DIR = os.path.dirname(__file__)                 # web/
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))   # Youtube/
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
sys.path.append(SRC_PATH)
print("Đã thêm vào PYTHONPATH:", SRC_PATH)

# ============================================================
# IMPORT MODULE
# ============================================================
from flask import Flask, render_template, request, jsonify
import pickle
import networkx as nx
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from community_detection import run_leiden
from ic_model import independent_cascade
from lt_model import run_lt_on_community

# ============================================================
# FLASK APP
# ============================================================
app = Flask(__name__, template_folder="templates", static_folder="static")

GRAPH_PATH = os.path.join(PROJECT_ROOT, "data", "processed_data", "graph_full.pkl")
COMM_PATH  = os.path.join(PROJECT_ROOT, "data", "processed_data", "communities_filtered.pkl")
STATS_PATH = os.path.join(PROJECT_ROOT, "network_stats.json")

print("Đang load graph...")
with open(GRAPH_PATH, "rb") as f:
    G = pickle.load(f)

print("Load xong. Số node:", G.number_of_nodes())

@app.route("/")
def index():
    #Load communities mới nhất mỗi lần mở trang
    with open(COMM_PATH, "rb") as f:
        communities = pickle.load(f)

    comm_sizes = [len(c) for c in communities]
    return render_template("index.html", comm_sizes=comm_sizes)

# ============================================================
# VẼ NETWORK
# ============================================================
def draw_network(nodes, edges, seed, activated=None, filename="network.png"):
    plt.figure(figsize=(10, 8))
    G_sub = nx.Graph()
    G_sub.add_nodes_from(nodes)
    G_sub.add_edges_from(edges)

    pos = nx.spring_layout(G_sub)

    colors = []
    for n in G_sub.nodes():
        if activated and n in activated:
            if n == seed:
                colors.append("orange")  # seed
            else:
                colors.append("red")     # đã bị ảnh hưởng
        else:
            colors.append("green")       # chưa bị ảnh hưởng
    nx.draw(G_sub, pos, node_color=colors, node_size=20, edge_color="gray", with_labels=False)
    nx.draw_networkx_edges(G_sub, pos, edgelist=edges, edge_color="orange")

    plt.tight_layout()
    out_dir = os.path.join(CURRENT_DIR, "static", "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, filename)

    plt.savefig(out_path)
    plt.close()
    return f"/static/img/{filename}"

# ============================================================
# API: RUN IC
# ============================================================
@app.route("/run-ic", methods=["POST"])
def run_ic():
    data = request.json
    comm_idx = int(data.get("community_index", 0))
    raw_p = str(data.get("p", "0.1")).replace(",", ".")
    p = float(raw_p)

    with open(COMM_PATH, "rb") as f:
        communities = pickle.load(f)

    community = communities[comm_idx]

    # tạo subgraph cộng đồng
    subG = G.subgraph(community)

    # chọn seed node (degree cao nhất trong cộng đồng)
    seed = max(subG.nodes(), key=lambda n: subG.degree(n))

    # chạy IC trên subgraph
    activated, timeline, edges_activated = independent_cascade(subG, [seed], p=p)

    # vẽ network
    image_url = draw_network(
        list(subG.nodes())[:5000],
        edges_activated[:5000],
        seed,
        activated,
        filename="ic_network.png"
    )

    return jsonify({
        "community_index": comm_idx,
        "community_size": len(subG.nodes()),
        "seed": seed,
        "activated_count": len(activated),
        "timeline": timeline,
        "image_url": image_url
    })


# ============================================================
# API: RUN LT
# ============================================================
@app.route("/run-lt", methods=["POST"])
def run_lt():
    try:
        data = request.json
        comm_idx = int(data.get("community_index", 0))
        raw_threshold = str(data.get("threshold", "0.5")).replace(",", ".")
        threshold = float(raw_threshold)

        if threshold < 0 or threshold > 1:
            return jsonify({"error": "Threshold phải nằm trong khoảng 0 đến 1."}), 400

        with open(COMM_PATH, "rb") as f:
            communities = pickle.load(f)

        if comm_idx < 0 or comm_idx >= len(communities):
            return jsonify({"error": "Cộng đồng được chọn không tồn tại."}), 400

        community = communities[comm_idx]
        valid_nodes = [n for n in community if n in G]
        if not valid_nodes:
            return jsonify({"error": "Cộng đồng không có node hợp lệ trong graph."}), 400

        # tạo subgraph cộng đồng
        subG = G.subgraph(valid_nodes)

        # chọn seed node (degree cao nhất)
        seed = max(subG.nodes(), key=lambda n: subG.degree(n))
        seed_degree = subG.degree(seed)

        # chạy LT trên subgraph
        activated_lt, timeline_lt, edges_lt = run_lt_on_community(
            subG,
            valid_nodes,
            seed=seed,
            threshold=threshold
        )

        # vẽ network
        image_url = draw_network(
            list(subG.nodes())[:5000],
            edges_lt[:5000],
            seed,
            activated_lt,
            filename="lt_network.png"
        )

        return jsonify({
            "community_index": comm_idx,
            "community_size": len(subG.nodes()),
            "seed": seed,
            "seed_degree": seed_degree,
            "threshold": threshold,
            "activated_count": len(activated_lt),
            "timeline": timeline_lt,
            "image_url": image_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# API: NETWORK STATS
# ============================================================
@app.route("/analyze-network", methods=["GET"])
def analyze_network_api():
    try:
        with open(STATS_PATH, "r") as f:
            stats = json.load(f)
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)})

# ============================================================
# API: LEIDEN
# ============================================================
@app.route("/analyze-communities", methods=["GET"])
def analyze_communities_api():
    with open(COMM_PATH, "rb") as f:
        partition = pickle.load(f)

    sizes = [len(c) for c in partition]

    return jsonify({
        "communities_count": len(partition),
        "average": sum(sizes) / len(sizes),
        "largest": max(sizes),
        "smallest": min(sizes),
        "modularity": nx.algorithms.community.quality.modularity(G, partition),
        "sizes": sizes[:200]
    })

if __name__ == "__main__":
    app.run(debug=True)
