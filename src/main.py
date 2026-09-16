import pickle
import networkx as nx
from community_detection import run_leiden
from ic_model import run_ic_on_community
from lt_model import run_lt_on_community
from network_analysis import analyze_network
import os

# ============================================================
# 1. LOAD DỮ LIỆU ĐÃ XỬ LÝ
# ============================================================

def load_processed_graph(path="data/processed_data/graph_full.pkl"):
    print("Đang load graph đã xử lý từ:", path)
    with open(path, "rb") as f:
        G = pickle.load(f)
    print("Load xong. Số node:", G.number_of_nodes(), " | Số cạnh:", G.number_of_edges())
    return G


# ============================================================
# 2. MAIN PIPELINE
# ============================================================

def main():
    print("\n================= MAIN PIPELINE =================")

    # ---- 1. Load graph ----
    G = load_processed_graph()

    # ---- 2. Phân tích mạng phức hợp ----
    print("\n=== Phân tích mạng phức hợp ===")
    analyze_network(G)

    # ---- 3. Chạy Hit-Leiden để tạo cộng đồng mới ----
    print("\n=== Chạy Hit-Leiden ===")
    detected_communities = run_leiden(G)
    print("Hit-Leiden tìm được", len(detected_communities), "cộng đồng.")

    # ---- 4. Chọn cộng đồng nhỏ nhất để chạy IC ----
    print("\n=== Chọn cộng đồng nhỏ nhất để chạy IC ===")
    smallest_comm = min(detected_communities, key=len)
    print("Cộng đồng nhỏ nhất có:", len(smallest_comm), "node.")

    #----5. Chọn SEED ---
    print("\n=== 5. Chọn Seed ===")

    # Chọn node có degree cao nhất
    seed = max(
        smallest_comm,
        key=lambda node: G.degree(node)
    )

    print("Seed:", seed)

    print(
        "Degree của seed:",
        G.degree(seed)
    )


    # ---- 6. Chạy mô hình IC ----
    print("\n=== Chạy mô hình IC ===")
    activated, timeline = run_ic_on_community(G, smallest_comm, seed, p=0.1)

    # ---- 7. In kết quả ----
    print("\n================= KẾT QUẢ CUỐI =================")
    print("Tổng số node bị ảnh hưởng bởi IC:", len(activated),"node")
    print("Timeline lan truyền:", timeline)
    print("================================================")

    # ---- 8. Chạy mô hình LT ----
    print("\n=== Chạy mô hình LT ===")
    activated_lt, timeline_lt, edges_lt = run_lt_on_community(G, smallest_comm, threshold=0.5)

    # ---- 9. In kết quả ----
    print("Tổng số node bị ảnh hưởng bởi LT:", len(activated_lt),"node")
    print("Timeline lan truyền:", timeline_lt)
    print("================================================")
    


# ============================================================
# CHẠY CHƯƠNG TRÌNH
# ============================================================

if __name__ == "__main__":
    main()
