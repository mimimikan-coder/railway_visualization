document.getElementById("startSimulation").onclick = () => {
  const model = document.getElementById("modelSelect").value;
  const source = document.getElementById("node-select").value;

  fetch("/network/simulation", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: model,
      source: source
    })
  })
    .then(response => response.json())
    .then(data => {
      console.log(data);
      drawNetworkAnimation(data);
    });
};

function drawNetworkAnimation(data) {
  const svg = d3.select("#network");
  svg.selectAll("*").remove();
  const g = svg.append("g");

  const colorMap = { S: "#aaa", I: "red", R: "green" };
  const history = data.nodes[0].history.map((_, i) => {
    const state = {};
    data.nodes.forEach(d => {
      state[d.id] = d.history[i];
    });
    return state;
  });

  const stepLabel = document.getElementById("stepLabel");
  const stepSlider = document.getElementById("stepSlider");
  const maxStep = history.length;
  stepSlider.max = maxStep - 1;

  // const simulation = d3.forceSimulation(data.nodes)
  //   .force("link", d3.forceLink(links).id(d => d.id).distance(40))
  //   .force("charge", d3.forceManyBody().strength(-100))
  //   .force("center", [400, 300])
  //   .force("collide", d3.forceCollide(10))
  //   .alpha(1)
  //   .alphaDecay(0.03);

  const link = g.selectAll("line")
    .data(data.links)
    .enter().append("line")
    .attr("x1", d => data.nodes.find(n => n.id === d.source).x)
    .attr("y1", d => data.nodes.find(n => n.id === d.source).y)
    .attr("x2", d => data.nodes.find(n => n.id === d.target).x)
    .attr("y2", d => data.nodes.find(n => n.id === d.target).y)
    .attr("stroke", "#ccc");

  const node = g.selectAll("circle")
    .data(data.nodes)
    .enter().append("circle")
    .attr("cx", d => d.x)
    .attr("cy", d => d.y)
    .attr("r", 2)
    .attr("fill", d => colorMap[d.history[0]])
    .call(d3.drag()
      .on("start", (event, d) => {
        d.fx = d.x;
        d.fy = d.y;
      })
      .on("drag", (event, d) => {
        d3.select(event.sourceEvent.target)
          .attr("cx", d.x = event.x)
          .attr("cy", d.y = event.y);
      })
      .on("end", (event, d) => {
        d.fx = null;
        d.fy = null;
      })
    );

  svg.call(
    d3.zoom()
      .scaleExtent([0.5, 5])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      })
  );

  node.append("title").text(d => d.id);

  // simulation.on("tick", () => {
  //   link
  //     .attr("x1", d => d.source.x)
  //     .attr("y1", d => d.source.y)
  //     .attr("x2", d => d.target.x)
  //     .attr("y2", d => d.target.y);
  //   node
  //     .attr("cx", d => d.x)
  //     .attr("cy", d => d.y);
  // });

  // svg.call(d3.zoom().on("zoom", function (event) {
  //   svg.selectAll("g").attr("transform", event.transform);
  // }));

  let step = 0;
  let interval;

  function update(stepIndex) {
    const state = history[stepIndex];
    node.attr("fill", d => colorMap[state[d.id]]);
    stepLabel.textContent = stepIndex;
    stepSlider.value = stepIndex;
  }

  document.getElementById("start").onclick = () => {
    clearInterval(interval);
    interval = setInterval(() => {
      step++;
      if (step >= history.length) {
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
    update(step);
  };

  update(0);

  // function dragstarted(event, d) {
  //   if (!event.active) simulation.alphaTarget(0.3).restart();
  //   d.fx = d.x;
  //   d.fy = d.y;
  // }

  // function dragged(event, d) {
  //   d.fx = event.x;
  //   d.fy = event.y;
  // }

  // function dragended(event, d) {
  //   if (!event.active) simulation.alphaTarget(0);
  //   d.fx = null;
  //   d.fy = null;
  // }
}

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

document.getElementById('node-select').addEventListener('change', (event) => {
  const selectedNode = event.target.value;
  document.getElementById('selected-node').textContent = selectedNode || 'None';
  console.log('Selected:', selectedNode);
});