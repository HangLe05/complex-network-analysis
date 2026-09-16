import networkx as nx


# ============================================================
# 1. MÔ HÌNH LINEAR THRESHOLD (LT)
# ============================================================

def linear_threshold(
    G,
    community,
    seed,
    threshold=0.5,
    max_steps=50
):
    
    # --------------------------------------------------------
    # 1. Kiểm tra threshold
    # --------------------------------------------------------
    if threshold < 0 or threshold > 1:
        raise ValueError(
            "Threshold phải nằm trong khoảng 0 đến 1."
        )

    # --------------------------------------------------------
    # 2. Chỉ lấy node thuộc cộng đồng
    # --------------------------------------------------------
    community_nodes = {
        n for n in community
        if n in G
    }
    if not community_nodes:
        return set(), [0], []

    # --------------------------------------------------------
    # 3. Kiểm tra seed
    # --------------------------------------------------------
    if seed not in community_nodes:
        raise ValueError(
            "Seed không thuộc cộng đồng."
        )

    # --------------------------------------------------------
    # 4. Tạo đồ thị con của cộng đồng
    # --------------------------------------------------------

    subG = G.subgraph(community_nodes)

    # --------------------------------------------------------
    # 5. Seed được kích hoạt ban đầu
    # --------------------------------------------------------

    activated = {seed}

    timeline = [1]

    edges_activated = []

    # --------------------------------------------------------
    # 6. Lan truyền
    # --------------------------------------------------------

    for step in range(max_steps):

        next_new = set()

        # Xét các node chưa kích hoạt
        for v in community_nodes:

            if v in activated:
                continue
            neighbors = list(subG.neighbors(v))
            if not neighbors:
                continue
            active_neighbors = [
                u
                for u in neighbors
                if u in activated
            ]
            if not active_neighbors:
                continue

            influence = (
                len(active_neighbors)
                / len(neighbors)
            )

            if influence >= threshold:

                next_new.add(v)

                # Lưu cạnh lan truyền
                for u in active_neighbors:
                    edges_activated.append((u, v))

        if not next_new:
            break

        activated.update(next_new)

        timeline.append(len(activated))

    return activated, timeline, edges_activated

# ============================================================
# 2. CHẠY LT TRÊN MỘT CỘNG ĐỒNG
# ============================================================

def run_lt_on_community(
    G,
    community,
    seed=None,
    threshold=0.5
):
    
    # --------------------------------------------------------
    # 1. Node hợp lệ
    # --------------------------------------------------------

    valid_nodes = [
        n for n in community
        if n in G
    ]

    if not valid_nodes:
        return set(), [0], []

    # --------------------------------------------------------
    # 2. Tạo đồ thị con
    # --------------------------------------------------------

    subG = G.subgraph(valid_nodes)

    # --------------------------------------------------------
    # 3. Chọn seed
    # --------------------------------------------------------

    if seed is None:

        seed = max(
            valid_nodes,
            key=lambda n: subG.degree(n)
        )

    # --------------------------------------------------------
    # 4. Chạy LT
    # --------------------------------------------------------

    return linear_threshold(
        G,
        valid_nodes,
        seed,
        threshold=threshold,
        max_steps=50
    )