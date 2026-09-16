import networkx as nx
import pickle
import os

# ============================================================
# 1. ĐỌC TOÀN BỘ GRAPH YOUTUBE
# ============================================================

def load_full_graph(path):
    G = nx.Graph()

    print("Đang đọc toàn bộ graph từ:", path)
    with open(path, 'r') as f:   # dùng open thay vì gzip.open
        for i, line in enumerate(f):

            if line.startswith('#') or line.strip() == "":
                continue

            try:
                u, v = line.strip().split()
            except ValueError:
                continue

            if u != v:
                G.add_edge(u, v)

            # In tiến độ mỗi 500k dòng
            if i % 500000 == 0:
                print(f"  Đã đọc {i:,} dòng...")

    print("Đọc xong toàn bộ graph.")
    print("Số node:", G.number_of_nodes())
    print("Số cạnh:", G.number_of_edges())
    return G


# ============================================================
# 2. ĐỌC CỘNG ĐỒNG GROUND-TRUTH
# ============================================================

def load_youtube_communities(path):
    communities = []

    print("Đang đọc cộng đồng từ:", path)
    with open(path, 'r') as f:   # cũng dùng open
        for line in f:
            nodes = line.strip().split()
            if len(nodes) >= 3:
                communities.append(nodes)

    print("Đọc xong cộng đồng.")
    print("Số cộng đồng:", len(communities))
    return communities


# ============================================================
# 3. LỌC CỘNG ĐỒNG THEO GRAPH
# ============================================================

def filter_communities(G, communities):
    filtered = []
    for comm in communities:
        comm2 = [n for n in comm if n in G]
        if len(comm2) >= 3:
            filtered.append(comm2)

    print("Số cộng đồng sau lọc:", len(filtered))
    return filtered


# ============================================================
# 4. LƯU DỮ LIỆU ĐÃ XỬ LÝ
# ============================================================

def save_processed_data(G, communities, out_dir="data/processed_data"):
    os.makedirs(out_dir, exist_ok=True)

    graph_path = os.path.join(out_dir, "graph_full.pkl")
    comm_path = os.path.join(out_dir, "communities_filtered.pkl")

    with open(graph_path, "wb") as f:
        pickle.dump(G, f)

    with open(comm_path, "wb") as f:
        pickle.dump(communities, f)

    print("Đã lưu graph vào:", graph_path)
    print("Đã lưu cộng đồng vào:", comm_path)


# ============================================================
# 5. MAIN PIPELINE
# ============================================================

def main():
    raw_graph = r"data/raw_data/com-youtube.ungraph.txt"
    raw_comm  = r"data/raw_data/com-youtube.all.cmty.txt"

    # ---- 1. Đọc toàn bộ graph ----
    G = load_full_graph(raw_graph)

    # ---- 2. Đọc cộng đồng ----
    communities = load_youtube_communities(raw_comm)

    # ---- 3. Lọc cộng đồng ----
    communities = filter_communities(G, communities)

    # ---- 4. Lưu dữ liệu đã xử lý ----
    save_processed_data(G, communities)

    print("\nTIỀN XỬ LÝ HOÀN TẤT.")


# ============================================================
# CHẠY CHƯƠNG TRÌNH
# ============================================================

if __name__ == "__main__":
    main()