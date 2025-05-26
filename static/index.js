fetch("/simulation/centrality_top10")
    .then(response => response.json())
    .then(data => {
        const tableData = data.name.map((name, index) => ({
            name,
            degree: data.degree_centrality[index],
            betweenness: data.betweenness_centrality[index],
            closeness: data.closeness_centrality[index],
            score: data.score[index]
        }));
        const tbody = document.querySelector('#centrality-table');
        tableData.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                    <td>${row.name}</td>
                    <td>${row.degree.toFixed(3)}</td>
                    <td>${row.betweenness.toFixed(3)}</td>
                    <td>${row.closeness.toFixed(3)}</td>
                    <td>${row.score.toFixed(3)}</td>
                `;
            tbody.appendChild(tr);
        });
    })
    .catch(error => {
        console.error("Error: ", error);
    });


document.getElementById("runSimulation").onclick = () => {
    const source = document.getElementById("node-select").value;

    fetch("/simulation/multiple_simulation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            source: source
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            printTop10Nodes(data);
        });
};
function printTop10Nodes(data) {
    const resultList = document.getElementById("resultList");
    resultList.innerHTML = "";
    top10Nodes = data.top10_nodes;
    top10Nodes.forEach((station, index) => {
        const li = document.createElement("li");
        li.textContent = `${index + 1}.${station}`;
        resultList.appendChild(li);
    });
}

// document.getElementById("optimalImmunity").addEventListener("click", () => {
//     console.log("clicked");

//     fetch("http://localhost:5000/simulation/best_node")
//         .then(response => response.json())
//         .then(data => {
//             const best_nodes = data.best_nodes;
//             console.log("Best nodes:", best_nodes);

//             return fetch("http://localhost:5000/simulation/optimal_immunity", {
//                 method: "POST",
//                 headers: { "Content-Type": "application/json" },
//                 body: JSON.stringify({ bests: best_nodes })
//             });
//         })
//         .then(response => response.json())
//         .then(data => {
//             console.log("simulation data:", data);
//             updateChart(data.infected_count, "simulation with best nodes", c = "rgba(10, 200, 180, 1)", bgc = "rgba(10, 200, 180, 0.2)");
//             document.getElementById("optimalImmunity").disabled = true;
//         })
// });

fetch('/nodes')
    .then(response => response.json())
    .then(nodes => {
        const select = document.getElementById('node-select');
        nodes.forEach(node => {
            const option = document.createElement('option');
            option.value = node.id;
            option.textContent = node.label;
            select.appendChild(option);
        });
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('node-select').innerHTML = '<option>Error</option>';
    });