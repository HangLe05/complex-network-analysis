import random
import pickle
import networkx as nx
import matplotlib.pyplot as plt

# ============================================================
# 1. TẢI GRAPH ĐÃ XỬ LÝ
# ============================================================

def load_processed_graph(path="data/processed_data/graph_partial.pkl"):
    print("Đang load graph đã xử lý từ:", path)
    with open(path, "rb") as f:
        G = pickle.load(f)
    print("Load xong. Số node:", G.number_of_nodes(), " | Số cạnh:", G.number_of_edges())
    return G


# ============================================================
# 2. TẢI CỘNG ĐỒNG ĐÃ LỌC
# ============================================================

def load_processed_communities(path="data/processed_data/communities_filtered.pkl"):
    print("Đang load cộng đồng đã xử lý từ:", path)
    with open(path, "rb") as f:
        communities = pickle.load(f)
    print("Load xong. Số cộng đồng:", len(communities))
    return communities


# 3. MÔ HÌNH INDEPENDENT CASCADE (IC)
# ============================================================

def independent_cascade(G, seeds, p=0.1, max_steps=50):
    activated = set(seeds)
    newly_activated = set(seeds)
    timeline = [len(activated)]
    edges_activated = []

    for step in range(max_steps):
        next_new = set()
        for u in newly_activated:
            if u not in G:
                continue
            for v in G.neighbors(u):
                if v not in activated:
                    if random.random() < p:
                        next_new.add(v)
                        edges_activated.append((u, v))
        if not next_new:
            break
        activated |= next_new
        newly_activated = next_new
        timeline.append(len(activated))

    return activated, timeline, edges_activated


# ============================================================
# 4. CHẠY IC TRÊN MỘT CỘNG ĐỒNG
# ============================================================

def run_ic_on_community(G, community, p=0.1):
    """
    Chạy IC trên một cộng đồng cụ thể.
    """

    # lọc node hợp lệ
    valid_nodes = [n for n in community if n in G]

    if not valid_nodes:
        print("Không có node nào trong cộng đồng tồn tại trong graph.")
        return set(), [0]

    seed = max(community, key=lambda n: G.degree(n))
    print("Chạy IC trên cộng đồng có", len(valid_nodes), "node.")

    return independent_cascade(G, [seed], p=p)
# ============================================================
# 5. MAIN TEST
# ============================================================

def main():
    G = load_processed_graph()
    communities = load_processed_communities()

    smallest_comm = min(communities, key=len)
    print("Cộng đồng nhỏ nhất có:", len(smallest_comm), "node.")

    activated, timeline = run_ic_on_community(G, smallest_comm, p=0.1)
    print("\nKẾT QUẢ IC:")
    print("Tổng số node bị ảnh hưởng:", len(activated))
    print("Timeline lan truyền:", timeline)


# ============================================================
# CHẠY CHƯƠNG TRÌNH
# ============================================================

if __name__ == "__main__":
    main()