import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import os
import pickle
import json

# Cố định seed để kết quả ổn định
np.random.seed(42)

# ================================
# ĐƯỜNG DẪN CƠ SỞ
# ================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data", "processed_data")

# ============================================================
# 1. PHÂN BỐ BẬC 
# ============================================================
def degree_distribution(G):
    degrees = np.array([d for _, d in G.degree()])
    sample_size = min(20000, len(degrees))
    degrees_sample = np.random.choice(degrees, sample_size, replace=False)
    return degrees


# ============================================================
# 2. HỆ SỐ PHÂN CỤM 
# ============================================================
def clustering_analysis(G, sample_size=3000):
    nodes = np.array(G.nodes())
    sample = np.random.choice(nodes, min(sample_size, len(nodes)), replace=False)

    avg_clustering = nx.average_clustering(G, nodes=sample)
    print("Hệ số phân cụm trung bình (sample):", avg_clustering)
    return avg_clustering


# ============================================================
# 3. ĐƯỜNG ĐI TRUNG BÌNH 
# ============================================================
def path_length_analysis(G, sample_size=600):
    nodes = np.array(G.nodes())
    sample = np.random.choice(nodes, min(sample_size, len(nodes)), replace=False)

    lengths = []
    for u in sample:
        sp = nx.single_source_shortest_path_length(G, u, cutoff=8)
        lengths.extend(sp.values())

    avg_length = float(np.mean(lengths))
    print("Đường đi trung bình (ước lượng, sample):", avg_length)
    return avg_length


# ============================================================
# 4. HÀM CHÍNH 
# ============================================================
def analyze_network(G):
    print("Phân tích mạng phức hợp...")

    degrees = degree_distribution(G)
    clustering = clustering_analysis(G)
    avg_path = path_length_analysis(G)

    try:
        largest_cc = max(nx.connected_components(G), key=len)
        H = G.subgraph(largest_cc)
        sample_nodes = np.random.choice(list(H.nodes()), min(200, len(H)), replace=False)
        max_dist = 0
        for u in sample_nodes:
            sp = nx.single_source_shortest_path_length(H, u, cutoff=10)
            max_dist = max(max_dist, max(sp.values()))
        diameter_est = max_dist
    except Exception:
        diameter_est = None

    assortativity = nx.degree_assortativity_coefficient(G)

    sample_nodes = np.random.choice(list(G.nodes()), min(300, G.number_of_nodes()), replace=False)
    betweenness = nx.betweenness_centrality_subset(G, sources=sample_nodes, targets=sample_nodes)
    avg_betweenness = float(np.mean(list(betweenness.values())))

    closeness_vals = [nx.closeness_centrality(G, u=n) for n in sample_nodes]
    avg_closeness = float(np.mean(closeness_vals))

    components = [len(c) for c in nx.connected_components(G)]
    num_components = len(components)
    largest_component = max(components)
    smallest_component = min(components)

    small_world_test(G)

    print("Hoàn tất phân tích mạng phức hợp.")

    stats = {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "degree_avg": float(np.mean(degrees)),
        "degree_max": int(np.max(degrees)),
        "degree_min": int(np.min(degrees)),
        "clustering": clustering,
        "avg_path": avg_path,
        "diameter_est": diameter_est,
        "assortativity": assortativity,
        "avg_betweenness": avg_betweenness,
        "avg_closeness": avg_closeness,
        "num_components": num_components,
        "largest_component": largest_component,
        "smallest_component": smallest_component
    }
    return stats



# ================================
# ĐƯỜNG DẪN TUYỆT ĐỐI
# ================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRAPH_PATH = os.path.join(BASE_DIR, "..", "data", "processed_data", "graph_full.pkl")
OUT_PATH = os.path.join(BASE_DIR, "network_stats.json")
IMG_PATH = os.path.join(BASE_DIR, "..", "web", "static", "img", "network_sample.png")


def run_worker():
    print("Worker: Đang load graph...")
    with open(GRAPH_PATH, "rb") as f:
        G = pickle.load(f)

    print("Worker: Bắt đầu phân tích mạng...")

    # Gọi hàm phân tích chính đã mở rộng
    stats = analyze_network(G)

    # Vẽ sample mạng và lưu ảnh

    print("Worker: Lưu kết quả vào network_stats.json")
    with open(OUT_PATH, "w") as f:
        json.dump(stats, f, indent=4)

    print("Worker: Hoàn tất. File kết quả:", OUT_PATH)

if __name__ == "__main__":
    run_worker()
