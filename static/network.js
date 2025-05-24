fetch('/network-data')
.then(response => response.json())
.then(data => {
    const width = 2000, height = 2000;
    const svg = d3.select("#network");
    const colorMap = {"S": "#aaa", "I": "red", "R": "green"};

    const simulation = d3.forceSimulation(data.nodes)
        .force("link", d3.forceLink(data.links).id(d =>d.id).distance(40))
        .force("charge", d3.forceManyBody().strength(-100))
        .force("center", d3.forceCenter(width/2, height/2))
        .force("collide", d3.forceCollide(10))
        .alpha(1)
        .alphaDecay(0.03);
    const link = svg.append("g")
        .selectAll("line")
        .data(data.links)
        .enter().append("circle")
        .attr("r", 50)
        .attr("fill", "#aaa");
    const node = svg.append("g")
        .selectAll("circle")
        .data(data.nodes)
        .enter().append("circle")
        .attr("r", 50)
        .attr("fill", "#aaa");
    node.append("title").text(d => d.id);
    simulation.on("tick", ()=>{
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);
    });

    data.nodes.forEach(d => {
        d.x = width / 2 + (Math.random() -0.5*100);
        d.y = height / 2 + (Math.random() -0.5*100);
    });

    svg.call(d3.zoom().on("zoom", function (event) {
        svg.selectAll("g").attr("transform", event.transform);
    }));

    let step = 0;
    const history = data.history;
    let interval;
    const stepLabel = document.getElementById("stepLabel");
    const stepSlider = document.getElementById("stepSlider");
    stepSlider.max = history.length - 1;

    function update(stepIndex){
        const state = history[stepIndex];
        node.attr("fill", d => colorMap[state[d.id]]);
        stepLabel.textContent = stepIndex;
        stepSlider.value = stepIndex;
    }

    document.getElementById("start").onclick = () => {
        clearInterval(interval);
        interval = setInterval(() => {
            step++;
            if (step >= history.length){
                clearInterval(interval);
                return;
            }
            update(step);
        }, 800);
    };

    document.getElementById("pause").onclick = () => {
        clearInterval(interval);
    };

    stepSlider.oninput = (e) => {
        step = +e.target.value;
        update(state);
    };
    update(0);
});

d3.json("/data/centrality_nodes.json").then(data => {
  const svg = d3.select("svg");

  const scaleRadius = d3.scaleLinear()
    .domain(d3.extent(data.nodes, d => d.centrality))
    .range([4, 20]); 

  const scaleColor = d3.scaleSequential(d3.interpolateOrRd)
    .domain(d3.extent(data.nodes, d => d.centrality));

  const nodes = svg.selectAll("circle")
    .data(data.nodes)
    .enter().append("circle")
    .attr("cx", d => d.x)
    .attr("cy", d => d.y)
    .attr("r", d => scaleRadius(d.centrality))
    .attr("fill", d => scaleColor(d.centrality));

  nodes.append("title")
    .text(d => `${d.name} (${d.centrality.toFixed(4)})`);
});


const top10 = data.nodes
  .sort((a, b) => b.centrality - a.centrality)
  .slice(0, 10);

const labels = top10.map(d => d.name);
const scores = top10.map(d => d.centrality);

new Chart(ctx, {
  type: "bar",
  data: {
    labels: labels,
    datasets: [{
      label: "centrality score",
      data: scores
    }]
  }
});