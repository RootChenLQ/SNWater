document.addEventListener('DOMContentLoaded', () => {
    console.log("Hydropower KG Frontend Loaded");

    const searchButton = document.getElementById('search-button');
    const searchInput = document.getElementById('search-input');
    const nodeInfoDiv = document.getElementById('node-info');

    // --- Graph Visualization (Part 2) ---
    const graphContainer = document.getElementById('graph-container');
    const width = graphContainer.clientWidth;
    const height = graphContainer.clientHeight;

    const svg = d3.select("#graph-container").append("svg")
        .attr("width", "100%")
        .attr("height", "100%")
        .call(d3.zoom().on("zoom", (event) => g.attr("transform", event.transform)));

    const g = svg.append("g");

    let simulation = d3.forceSimulation()
        .force("link", d3.forceLink().id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width / 2, height / 2));

    function drawGraph(graph) {
        g.selectAll("*").remove();

        const links = g.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(graph.links)
            .join("line")
            .attr("stroke-width", 1.5)
            .attr("stroke", "#999");

        const nodes = g.append("g")
            .attr("class", "nodes")
            .selectAll("circle")
            .data(graph.nodes)
            .join("circle")
            .attr("r", 10)
            .attr("fill", d => color(d.label))
            .call(drag(simulation));

        nodes.append("title").text(d => d.properties.name || d.id);

        nodes.on("click", (event, d) => {
            displayNodeProperties(d);
        });

        simulation.nodes(graph.nodes).on("tick", () => {
            links
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            nodes
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
        });

        simulation.force("link").links(graph.links);
        simulation.alpha(1).restart();
    }

    function displayNodeProperties(nodeData) {
        nodeInfoDiv.innerHTML = '<h3>Node Properties</h3>';
        const form = document.createElement('form');
        form.id = 'node-property-form';

        for (const [key, value] of Object.entries(nodeData.properties)) {
            const label = document.createElement('label');
            label.textContent = key;
            const input = document.createElement('input');
            input.type = 'text';
            input.name = key;
            input.value = value;
            if (key === 'id') {
                input.readOnly = true; // Don't allow editing the ID
            }
            form.appendChild(label);
            form.appendChild(input);
        }

        const saveButton = document.createElement('button');
        saveButton.type = 'submit';
        saveButton.textContent = 'Save Changes';
        form.appendChild(saveButton);

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const updatedProperties = Object.fromEntries(formData.entries());

            await saveNodeProperties(nodeData.properties.id, updatedProperties);
        });

        nodeInfoDiv.appendChild(form);
    }

    async function saveNodeProperties(nodeId, properties) {
        try {
            const response = await fetch('/api/node/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: nodeId, properties: properties })
            });
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            const result = await response.json();
            if (result.status === 'success') {
                alert('Node updated successfully!');
                // Refresh graph to show new data
                search();
            } else {
                throw new Error(result.message || 'Failed to update node.');
            }
        } catch (error) {
            console.error('Error saving node properties:', error);
            alert(`Error: ${error.message}`);
        }
    }

    const color = d3.scaleOrdinal(d3.schemeCategory10);
    const drag = simulation => {
        // Drag functions (same as before)
        return d3.drag()
            .on("start", (e,d) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
            .on("drag", (e,d) => { d.fx = e.x; d.fy = e.y; })
            .on("end", (e,d) => { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; });
    };

    async function search() {
        const query = searchInput.value;
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const graphData = await response.json();
            if (graphData.error) {
                alert(`API Error: ${graphData.error}`);
                drawGraph({ nodes: [], links: [] }); // Draw an empty graph
                return;
            }
            drawGraph(graphData);
        } catch (error) {
            console.error("Fetch error:", error);
            alert("Failed to fetch graph data. Is the backend server running and connected to the database?");
            drawGraph({ nodes: [], links: [] }); // Draw an empty graph on error
        }
    }

    searchButton.addEventListener('click', search);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') search();
    });

    // Initial search to load the full graph
    search();

    // --- Q&A System (Part 3) ---
    const qaButton = document.getElementById('qa-button');
    const recommendationText = document.getElementById('recommendation-text');

    qaButton.addEventListener('click', async () => {
        const station = document.getElementById('qa-station').value;
        const flow = parseFloat(document.getElementById('qa-flow').value);
        const level = parseFloat(document.getElementById('qa-level').value);

        if (!station || isNaN(flow) || isNaN(level)) {
            alert("Please fill in all fields for the Q&A system.");
            return;
        }

        recommendationText.textContent = "Getting recommendation from AI expert...";

        try {
            const response = await fetch('/api/qna', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ station, flow, level })
            });

            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

            const result = await response.json();

            if (result.error) {
                recommendationText.textContent = `Error: ${result.error}`;
            } else {
                recommendationText.textContent = result.recommendation;
            }
        } catch (error) {
            console.error('Error getting recommendation:', error);
            recommendationText.textContent = "Failed to get recommendation due to a network or server error.";
        }
    });
});
