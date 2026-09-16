document.addEventListener("DOMContentLoaded", () => {

    // Biến toàn cục quản lý các instance của Chart.js
    let icLineChart = null;
    let icBarChart = null;
    let commChart = null;
    let ltLineChart = null;
    let ltBarChart = null;

    // Helper an toàn để format số thập phân
    const formatNum = (val, digits = 3) => {
        return (typeof val === 'number' && !isNaN(val)) ? val.toFixed(digits) : (val ?? '-');
    };

    // Tùy chỉnh chung cho Chart.js
    Chart.defaults.font.family = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
    Chart.defaults.responsive = true;
    Chart.defaults.maintainAspectRatio = false;

    // ============================
    // 0) HÀM TẢI DANH SÁCH CỘNG ĐỒNG CHO SELECT (IC & LT)
    // ============================
    async function loadCommunities() {
        const icSelect = document.getElementById("ic-community-select");
        const ltSelect = document.getElementById("lt-community-select");

        try {
            const res = await fetch("/get-communities");
            if (!res.ok) return;
            const communities = await res.json();

            // Đổ dữ liệu vào IC Select
            if (icSelect) {
                icSelect.innerHTML = "";
                communities.forEach((comm, idx) => {
                    const opt = document.createElement("option");
                    opt.value = idx;
                    opt.textContent = `Cộng đồng ${idx} (${comm.length ?? comm} node)`;
                    icSelect.appendChild(opt);
                });
            }

            // Đổ dữ liệu vào LT Select
            if (ltSelect) {
                ltSelect.innerHTML = "";
                communities.forEach((comm, idx) => {
                    const opt = document.createElement("option");
                    opt.value = idx;
                    opt.textContent = `Cộng đồng ${idx} (${comm.length ?? comm} node)`;
                    ltSelect.appendChild(opt);
                });
            }
        } catch (err) {
            console.warn("Không thể tải danh sách cộng đồng tự động:", err);
        }
    }

    // Tải danh sách cộng đồng ngay khi mở trang
    loadCommunities();

    // ============================
    // 1) LAN TRUYỀN IC (INDEPENDENT CASCADE)
    // ============================
    const runBtn = document.getElementById("btn-run-ic");
    const commSelect = document.getElementById("ic-community-select");
    const pInput = document.getElementById("ic-p-input");
    const resultText = document.getElementById("ic-summary-info");

    if (runBtn) {
        runBtn.addEventListener("click", async () => {
            if (!commSelect || commSelect.value === "") {
                alert("Vui lòng chọn một cộng đồng!");
                return;
            }

            const communityIndex = parseInt(commSelect.value);
            const rawP = pInput ? pInput.value.replace(",", ".") : "0.1";
            const p = parseFloat(rawP);

            if (resultText) {
                resultText.className = "mb-0";
                resultText.textContent = "Đang chạy mô phỏng IC...";
            }

            try {
                const res = await fetch("/run-ic", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ community_index: communityIndex, p: p })
                });

                const data = await res.json();

                if (!res.ok) {
                    if (resultText) resultText.textContent = "Lỗi: " + (data.error || "Không rõ");
                    return;
                }

                // Tóm tắt kết quả chuẩn hóa
                if (resultText) {
                    resultText.className = "mb-0";
                    resultText.innerHTML = `<strong>Cộng đồng:</strong> ${data.community_index} (Kích thước = ${data.community_size} node) &nbsp;|&nbsp; <strong>Seed node:</strong> ${data.seed} &nbsp;|&nbsp; <strong>Tổng số node bị ảnh hưởng:</strong> <span class="text-danger fw-bold">${data.activated_count}</span>`;
                }

                // 1.1 LINE CHART
                const lineCanvas = document.getElementById("icCumulativeChart");
                if (lineCanvas) {
                    const lineCtx = lineCanvas.getContext("2d");
                    if (icLineChart !== null) icLineChart.destroy();
                    
                    icLineChart = new Chart(lineCtx, {
                        type: "line",
                        data: {
                            labels: data.timeline.map((_, i) => "Bước " + i),
                            datasets: [{
                                label: "Tổng node bị ảnh hưởng",
                                data: data.timeline,
                                borderColor: "#2563eb",
                                backgroundColor: "rgba(37, 99, 235, 0.1)",
                                fill: true,
                                tension: 0.3,
                                pointRadius: 4,
                                pointHoverRadius: 6
                            }]
                        }
                    });
                }

                // 1.2 BAR CHART
                const barCanvas = document.getElementById("icNewChart");
                if (barCanvas) {
                    const increments = data.timeline.map((v, i, arr) => i === 0 ? v : v - arr[i - 1]);
                    const barCtx = barCanvas.getContext("2d");
                    if (icBarChart !== null) icBarChart.destroy();

                    icBarChart = new Chart(barCtx, {
                        type: "bar",
                        data: {
                            labels: increments.map((_, i) => "Bước " + i),
                            datasets: [{
                                label: "Node mới kích hoạt",
                                data: increments,
                                backgroundColor: "#f97316",
                                borderRadius: 6
                            }]
                        }
                    });
                }

                // 1.3 NETWORK GRAPH IC
                const realContainer = document.getElementById("realNetwork");
                if (realContainer && data.image_url) {
                    realContainer.innerHTML = `
                        <div class="w-100 rounded border p-3 bg-light d-flex align-items-center justify-content-center" style="min-height: 400px; max-height: 520px; overflow: hidden;">
                            <img src="${data.image_url}?t=${new Date().getTime()}" 
                                 alt="Network graph IC" 
                                 style="max-width: 100%; max-height: 490px; width: auto; height: auto; object-fit: contain; display: block;">
                        </div>
                    `;
                }

            } catch (err) {
                if (resultText) resultText.textContent = "Lỗi khi gọi API IC: " + err;
            }
        });
    }

    // ============================
    // 2) PHÂN TÍCH MẠNG PHỨC HỢP
    // ============================
    const networkBtn = document.getElementById("analyze-network-btn");
    const networkResults = document.getElementById("network-results");
    const networkPlaceholder = document.getElementById("network-placeholder");

    if (networkBtn) {
        networkBtn.addEventListener("click", async () => {
            if (networkPlaceholder) {
                networkPlaceholder.innerHTML = '<div class="spinner-border text-primary" role="status"></div><p class="mt-2 mb-0">Đang phân tích mạng...</p>';
            }
            
            try {
                const res = await fetch("/analyze-network");
                const data = await res.json();

                if (networkPlaceholder) networkPlaceholder.style.display = "none";
                if (networkResults) networkResults.style.display = "block";

                const setElText = (id, val) => {
                    const el = document.getElementById(id);
                    if (el) el.innerText = val;
                };

                setElText("nodes", data.nodes ?? '-');
                setElText("edges", data.edges ?? '-');
                setElText("degree_avg", formatNum(data.degree_avg));
                setElText("degree_max", data.degree_max ?? '-');
                setElText("degree_min", data.degree_min ?? '-');
                setElText("clustering", formatNum(data.clustering));
                setElText("avg_path", formatNum(data.avg_path));
                setElText("diameter_est", data.diameter_est ?? '-');
                setElText("assortativity", formatNum(data.assortativity));
                setElText("avg_betweenness", formatNum(data.avg_betweenness));
                setElText("avg_closeness", formatNum(data.avg_closeness));
                setElText("num_components", data.num_components ?? '-');
                setElText("largest_component", data.largest_component ?? '-');
                setElText("smallest_component", data.smallest_component ?? '-');

            } catch (err) {
                if (networkPlaceholder) {
                    networkPlaceholder.innerHTML = "<p class='text-danger'>Lỗi khi gọi API phân tích mạng: " + err + "</p>";
                }
            }
        });
    }

    // ============================
    // 3) PHÂN TÍCH CỘNG ĐỒNG LEIDEN
    // ============================
    const commBtn = document.getElementById("analyze-communities-btn");
    const commResult = document.getElementById("communities-result");
    const commChartCanvas = document.getElementById("commChart");

    if (commBtn) {
        commBtn.addEventListener("click", async () => {
            if (commResult) commResult.textContent = "Đang phân tích cộng đồng...";
            
            try {
                const res = await fetch("/analyze-communities");
                const data = await res.json();

                if (commResult) {
                    commResult.innerHTML = `
                        <ul class="list-unstyled mb-0 row g-2">
                            <li class="col-6 col-md-4"><strong>Số cộng đồng:</strong> ${data.communities_count}</li>
                            <li class="col-6 col-md-4"><strong>Kích thước TB:</strong> ${formatNum(data.average, 2)} node</li>
                            <li class="col-6 col-md-4"><strong>Modularity:</strong> ${formatNum(data.modularity)}</li>
                            <li class="col-6 col-md-4"><strong>Cộng đồng lớn nhất:</strong> ${data.largest} node</li>
                            <li class="col-6 col-md-4"><strong>Cộng đồng nhỏ nhất:</strong> ${data.smallest} node</li>
                        </ul>
                    `;
                }

                if (commChartCanvas) {
                    if (commChartCanvas.parentElement) {
                        commChartCanvas.parentElement.style.height = "480px";
                    }

                    const ctx = commChartCanvas.getContext("2d");
                    if (commChart !== null) commChart.destroy();

                    commChart = new Chart(ctx, {
                        type: "bar",
                        data: {
                            labels: data.sizes.map((_, i) => `Cụm ${i}`),
                            datasets: [{
                                label: "Kích thước cộng đồng (node)",
                                data: data.sizes,
                                backgroundColor: "rgba(16, 185, 129, 0.7)",
                                borderRadius: 4
                            }]
                        },
                        options: {
                            maintainAspectRatio: false,
                            scales: {
                                x: { title: { display: true, text: "Cộng đồng" } },
                                y: { title: { display: true, text: "Số node" } }
                            }
                        }
                    });
                }
            } catch (err) {
                if (commResult) commResult.textContent = "Lỗi khi gọi API cộng đồng: " + err;
            }
        });
    }

    // ============================
    // 4) LAN TRUYỀN LT (LINEAR THRESHOLD)
    // ============================
    const ltrunBtn = document.getElementById("lt-run-btn");
    const ltcommSelect = document.getElementById("lt-community-select");
    const ltThresholdInput = document.getElementById("lt-threshold");
    const ltResult = document.getElementById("lt-result-text");

    if (ltrunBtn) {
        ltrunBtn.addEventListener("click", async () => {
            if (!ltcommSelect || ltcommSelect.value === "") {
                alert("Vui lòng chọn một cộng đồng!");
                return;
            }

            const communityIndex = parseInt(ltcommSelect.value);
            const rawThreshold = ltThresholdInput ? ltThresholdInput.value.replace(",", ".") : "0.1";
            const threshold = parseFloat(rawThreshold);

            if (isNaN(threshold) || threshold < 0 || threshold > 1) {
                if (ltResult) ltResult.textContent = "Threshold phải nằm trong khoảng từ 0 đến 1.";
                return;
            }

            if (ltResult) {
                ltResult.className = "mb-0";
                ltResult.textContent = "Đang chạy mô phỏng LT...";
            }

            try {
                const res = await fetch("/run-lt", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ community_index: communityIndex, threshold: threshold })
                });

                const data = await res.json();

                if (!res.ok) {
                    if (ltResult) ltResult.textContent = "Lỗi: " + (data.error || "Không rõ");
                    return;
                }

                // Tóm tắt kết quả chuẩn hóa đồng nhất với IC
                if (ltResult) {
                    ltResult.className = "mb-0";
                    ltResult.innerHTML = `<strong>Cộng đồng:</strong> ${data.community_index} (Kích thước = ${data.community_size} node) &nbsp;|&nbsp; <strong>Seed node:</strong> ${data.seed} &nbsp;|&nbsp; <strong>Threshold:</strong> ${data.threshold} &nbsp;|&nbsp; <strong>Tổng số node bị ảnh hưởng:</strong> <span class="text-danger fw-bold">${data.activated_count}</span>`;
                }

                // 4.1 LINE CHART
                const ltLineCanvas = document.getElementById("ltlineChart");
                if (ltLineCanvas) {
                    const lineCtx = ltLineCanvas.getContext("2d");
                    if (ltLineChart !== null) ltLineChart.destroy();

                    ltLineChart = new Chart(lineCtx, {
                        type: "line",
                        data: {
                            labels: data.timeline.map((_, i) => "Bước " + i),
                            datasets: [{
                                label: "Tổng node bị ảnh hưởng",
                                data: data.timeline,
                                borderColor: "#2563eb",
                                backgroundColor: "rgba(37, 99, 235, 0.1)",
                                fill: true,
                                tension: 0.3,
                                pointRadius: 4,
                                pointHoverRadius: 6
                            }]
                        }
                    });
                }

                // 4.2 BAR CHART
                const ltBarCanvas = document.getElementById("ltbarChart");
                if (ltBarCanvas) {
                    const increments = data.timeline.map((v, i, arr) => i === 0 ? v : v - arr[i - 1]);
                    const ltBarCtx = ltBarCanvas.getContext("2d");
                    if (ltBarChart !== null) ltBarChart.destroy();

                    ltBarChart = new Chart(ltBarCtx, {
                        type: "bar",
                        data: {
                            labels: increments.map((_, i) => "Bước " + i),
                            datasets: [{
                                label: "Node mới kích hoạt",
                                data: increments,
                                backgroundColor: "#f97316",
                                borderRadius: 6
                            }]
                        }
                    });
                }

                // 4.3 NETWORK GRAPH LT
                const ltNetworkContainer = document.getElementById("lt-network");
                if (ltNetworkContainer && data.image_url) {
                    ltNetworkContainer.innerHTML = `
                        <div class="w-100 rounded border p-3 bg-light d-flex align-items-center justify-content-center" style="min-height: 400px; max-height: 520px; overflow: hidden;">
                            <img src="${data.image_url}?t=${new Date().getTime()}" 
                                 alt="Network graph LT" 
                                 style="max-width: 100%; max-height: 490px; width: auto; height: auto; object-fit: contain; display: block;">
                        </div>
                    `;
                }

            } catch (err) {
                if (ltResult) ltResult.textContent = "Lỗi khi gọi API LT: " + err;
            }
        });
    }

    // ============================
    // 5) RESIZE CHART KHI CHUYỂN TAB
    // ============================
    const tabElements = document.querySelectorAll('button[data-bs-toggle="tab"]');
    tabElements.forEach(tabEl => {
        tabEl.addEventListener('shown.bs.tab', (event) => {
            const targetTab = event.target.getAttribute('data-bs-target');
            requestAnimationFrame(() => {
                if (targetTab === '#ic') {
                    icLineChart?.resize();
                    icBarChart?.resize();
                } else if (targetTab === '#lt') {
                    ltLineChart?.resize();
                    ltBarChart?.resize();
                } else if (targetTab === '#communities') {
                    commChart?.resize();
                }
            });
        });
    });

});