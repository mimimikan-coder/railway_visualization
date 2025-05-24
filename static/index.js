let top10Nodes = [];
let chart = null;

fetch("http://localhost:5000/simulation")
    .then(response => response.json())
    .then(data => {
        console.log(data);

        const ctx = document.getElementById("myChart").getContext("2d");
        chart = new Chart(ctx, {
            type: "line",
            data: {
                labels: data.steps,
                datasets: [{
                    label: "no immunity",
                    data: data.infected,
                    borderColor: "rgba(255, 99, 132, 1)",
                    backgroundColor: "rgba(255, 99, 132, 0.2)",
                    borderWidth: 2,
                    fill: false
                },
                {
                    label: "with immunity",
                    data: data.infected_immunity,
                    borderColor: "rgba(54, 162, 235, 1)",
                    backgroundColor: "rgba(54, 162, 235, 0.2)",
                    borderWidth: 2,
                    fill: false
                },
                {
                    label: "sis infected",
                    data: data.infected_sis,
                    borderColor: "rgba(25, 250, 100, 1)",
                    backgroundColor: "rgba(25, 250, 100, 0.2)",
                    borderWidth: 2,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: "no/with immunity simulation"
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        })
    })
    .catch(error => console.error("Error fetching data", error));



document.getElementById("runSimulation").addEventListener("click", () => {
    fetch("http://localhost:5000/simulation/multiple_simulation")
        .then(response => response.json())
        .then(data => {
            const resultList = document.getElementById("resultList");
            resultList.innerHTML = "";

            top10Nodes = data.top10_nodes;
            top10Nodes.forEach((station, index) => {
                const li = document.createElement("li");
                li.textContent = `${index + 1}.${station}`;
                resultList.appendChild(li);
            });
            document.getElementById("SIRwithImmunity").disabled = false;
        });
    //.catch(error => console.error("Error running simulation: ", error));

});

// シミュで得た遅延駅を免疫にしてシミュ実行
document.getElementById("SIRwithImmunity").addEventListener("click", () => {
    fetch("http://localhost:5000/simulation/SIRwith_immunity", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ immune_nodes: top10Nodes })
    })
        .then(response => response.json())
        .then(data => {
            updateChart(data.infected_counts, "simulation with TOP10 station");
        });
});

// 最尤ノードでシミュ
document.getElementById("optimalImmunity").addEventListener("click", () => {
    console.log("clicked");

    fetch("http://localhost:5000/simulation/best_node")
        .then(response => response.json())
        .then(data => {
            const best_nodes = data.best_nodes;
            console.log("Best nodes:", best_nodes);

            return fetch("http://localhost:5000/simulation/optimal_immunity", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ bests: best_nodes })
            });
        })
        .then(response => response.json())
        .then(data => {
            console.log("simulation data:", data);
            updateChart(data.infected_count, "simulation with best nodes", c = "rgba(10, 200, 180, 1)", bgc = "rgba(10, 200, 180, 0.2)");
            document.getElementById("optimalImmunity").disabled = true;
        })
});

// グラフ更新関数
function updateChart(infectedCounts, title, c = "rgba(100, 25, 24, 1)", bgc = "rgba(100, 25, 24, 0.2)") {
    if (!chart) {
        console.error("not exist");
        return;
    }
    chart.data.datasets.push({
        label: title,
        data: infectedCounts,
        borderColor: c,
        borderWidth: 2,
        backgroundColor: bgc,
        fill: false
    });
    chart.update();
}