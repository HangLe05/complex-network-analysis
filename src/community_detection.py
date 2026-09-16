import igraph as ig
import leidenalg
import networkx as nx
import pickle
import os

# ============================================================
# 1. CHẠY LEIDEN TRÊN GRAPH
# ============================================================
def leiden_community_detection(G):
    try:
        edges = list(G.edges())
        nodes = list(G.nodes())
        mapping = {node: idx for idx, node in enumerate(nodes)}

        ig_edges = [(mapping[u], mapping[v]) for u, v in edges]
        ig_graph = ig.Graph(len(nodes), ig_edges)

        weights = [G[u][v].get("weight", 1.0) for u, v in edges]

        partition = leidenalg.find_partition(
            ig_graph,
            leidenalg.ModularityVertexPartition,
            weights=weights
        )

        communities = []
        for comm in partition:
            communities.append([nodes[idx] for idx in comm])

        return communities

    except Exception as e:
        print("Lỗi Leiden:", e)
        print("Dùng connected components (demo).")
        return [list(c) for c in nx.connected_components(G)]

# ============================================================
# 2. PHÂN TÍCH CỘNG ĐỒNG
# ============================================================
def analyze_communities(G, communities):
    sizes = [len(c) for c in communities]
    print("Kích thước trung bình:", sum(sizes)/len(sizes))
    print("Cộng đồng lớn nhất:", max(sizes))
    print("Cộng đồng nhỏ nhất:", min(sizes))

    try:
        from networkx.algorithms.community.quality import modularity
        mod = modularity(G, communities)
        print("Modularity:", mod)
    except Exception as e:
        print("Không tính được modularity:", e)

    return sizes

# ============================================================
# 3. HÀM CHÍNH: LEIDEN + LỌC NODE + LƯU FILE
# ============================================================
def run_leiden(G):
    print("Chạy Leiden...")
    communities = leiden_community_detection(G)

    print("Hoàn thành Leiden.")
    print("Số cộng đồng tìm được:", len(communities))

    print("Phân tích cộng đồng...")
    analyze_communities(G, communities)

    # Lọc node hợp lệ
    valid_nodes = set(G.nodes())
    filtered = []
    for comm in communities:
        fixed = [n for n in comm if n in valid_nodes]
        if len(fixed) > 0:
            filtered.append(fixed)

    print("Sau khi lọc:", len(filtered), "cộng đồng hợp lệ.")

    # Lưu communities_filtered.pkl
    CURRENT_DIR = os.path.dirname(__file__) if '__file__' in locals() else os.getcwd()
    PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
    OUT_PATH = os.path.join(PROJECT_ROOT, "data", "processed_data", "communities_filtered.pkl")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "wb") as f:
        pickle.dump(filtered, f)

    print("Đã lưu communities_filtered.pkl tại:", OUT_PATH)
    return filtered
