fetch("http://localhost:5000/network")
    .then(response => response.json())
    .then(data => {
        const edge_x = [], edge_y = [];
        data.edges.forEach(edge => {
            const sourceNode = data.nodes.find(n => n.id === edge.source);
            const targetNode = data.nodes.find(n => n.id === edge.target);
            edge_x.push(sourceNode.x, targetNode.x, null);
            edge_y.push(sourceNode.y, targetNode.y, null);
        });

        const edge_trace = {
            x: edge_x,
            y: edge_y,
            mode: "lines",
            line: { width: 0.5, color: "#888" },
            hoverinfo: "none"
        };

        const node_trace = {
            x: data.nodes.map(n => n.x),
            y: data.nodes.map(n => n.y),
            mode: "markers+text",
            text: data.nodes.map(n => n.label),
            textposition: "top center",
            textfont: { size: 8 },
            marker: {
                size: 10,
                color: data.nodes.map(n => n.color)
            },
            hoverinfo: "text",
            hovertext: data.nodes.map(n => n.id) 
        };

        const layout = {
            title: `Community Structure (${data.num_communities} communities)`,
            showlegend: false,
            xaxis: { showgrid: false, zeroline: false, showticklabels: false },
            yaxis: { showgrid: false, zeroline: false, showticklabels: false },
            hovermode: "closest",
            dragmode: "pan", 
            margin: { t: 40, b: 20, l: 20, r: 20 }
        };

        Plotly.newPlot("graph", [edge_trace, node_trace], layout, {
            scrollZoom: true 
        });


        // graph of degree distribution
        const degree_trace = {
            x: data.degree_distribution.map(d => d.degree),
            y: data.degree_distribution.map(d => d.count),
            type: "bar",
            marker: { color: "#1f77b4" },
            hoverinfo: "x+y",
            text: data.degree_distribution.map(d => d.count),
            textposition: "auto"
        };

        const degree_layout = {
            title: "Degree Distribution",
            xaxis: { title: "Degree" },
            yaxis: { title: "Count" },
            margin: { t: 40, b: 50, l: 50, r: 20 },
            height: 800
        };

        Plotly.newPlot("graph-degree", [degree_trace], degree_layout, {
            scrollZoom: false
        });
        
    })
    .catch(error => console.error("Error fetching graph data:", error));

fetch("http://localhost:5000/network-parameter")
    .then(response => response.json())
    .then(data => {
        document.getElementById("avarage_path_length").textContent = data.avarage_path_length.toFixed(3);
        document.getElementById("density").textContent = data.density.toFixed(3);
        document.getElementById("clustering_coef").textContent = data.clustering_coef.toFixed(3);
    })
    .catch(error => {
        console.error("Error: ", error)
    });