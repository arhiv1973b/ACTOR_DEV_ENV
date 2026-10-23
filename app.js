const tileGrid = document.getElementById('tileGrid');
const searchBox = document.getElementById('searchBox');
const modal = document.getElementById('modal');
const modalIframe = document.getElementById('modalIframe');

async function loadGraphData() {
    try {
        const response = await fetch('registry_chunks/index.json');
        const masterIndex = await response.json();
        
        const chunkPromises = masterIndex.chunks.map(filename => 
            fetch(`registry_chunks/${filename}`).then(r => r.json())
        );
        const chunks = await Promise.all(chunkPromises);
        const allNodes = chunks.flatMap(chunk => chunk.evidence_nodes);

        let semanticEdges = [];
        try {
            const edgesResponse = await fetch('registry_chunks/edges.json');
            const edgesData = await edgesResponse.json();
            semanticEdges = edgesData.edges || [];
        } catch (e) {
            console.warn("edges.json пока не найден или пуст.");
        }

        renderTiles(allNodes);
        
        const cyElements = [
             ...allNodes.map(node => ({
                 data: { 
                     id: node.node_id, 
                     label: node.node_id,
                     ...node 
                 }
             })),
             ...semanticEdges.map(edge => ({
                 data: {
                     source: edge.source,
                     target: edge.target,
                     relation: edge.relation
                 },
                 classes: edge.relation
             }))
         ];
        initGraph(cyElements);
        return { nodes: allNodes, edges: semanticEdges };
    } catch (e) { 
        console.error("A©t0r: Ошибка загрузки реестра и связей:", e); 
    }
}

function initGraph(elements) {
    const cy = cytoscape({
        container: document.getElementById('cy'),
        elements: elements,
        style: [
            {
                selector: 'node',
                style: {
                    'background-color': '#1E90FF',
                    'label': 'data(label)',
                    'color': '#E0E0E0',
                    'font-size': '10px',
                    'text-valign': 'bottom',
                    'text-margin-y': 5
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 1.5,
                    'line-color': '#444', 
                    'curve-style': 'bezier',
                    'opacity': 0.6
                }
            },
            {
                selector: 'edge.shared_idnp',
                style: {
                    'line-color': '#FF4136',
                    'target-arrow-color': '#FF4136',
                    'target-arrow-shape': 'triangle',
                    'label': 'IDNP',
                    'font-size': '8px',
                    'color': '#FF4136',
                    'opacity': 1,
                    'z-index': 10
                }
            },
            {
                selector: 'edge.shared_case_ref',
                style: {
                    'line-color': '#FFDC00',
                    'target-arrow-color': '#FFDC00',
                    'target-arrow-shape': 'triangle',
                    'label': 'Case',
                    'font-size': '8px',
                    'color': '#FFDC00',
                    'opacity': 1,
                    'z-index': 10
                }
            },
            {
                selector: 'edge.shared_ip_address',
                style: {
                    'line-color': '#2ECC40',
                    'target-arrow-color': '#2ECC40',
                    'target-arrow-shape': 'triangle',
                    'label': 'IP',
                    'font-size': '8px',
                    'color': '#2ECC40',
                    'opacity': 1,
                    'z-index': 10
                }
            }
        ],
        layout: {
            name: 'cose', 
            idealEdgeLength: 100,
            nodeOverlap: 20,
            refresh: 20,
            fit: true,
            padding: 30
        }
    });
}

function renderTiles(nodes) {
    tileGrid.innerHTML = '';
    const nodeMap = new Map(nodes.map(n => [n.node_id, n]));
    
    nodes.forEach(node => {
        const tile = document.createElement('div');
        tile.className = 'tile';
        tile.dataset.id = node.node_id;
        
        const linkCount = node.links ? node.links.length : 0;
        tile.innerHTML = `<h3>${node.node_id || 'N/A'}</h3>
                          <p>${node.forensic_content_summary || node.document_ref || 'Без описания'}</p>
                          <small>Hash: ${node.hash_sha256?.substring(0,16) || '...'}</small>
                          ${linkCount > 0 ? `<div class="links-indicator">Связи: ${linkCount}</div>` : ''}`;
        
        tile.onclick = () => {
            openModal(node.drive_iframe_src);
            highlightLinks(node.links, nodeMap);
        };
        tileGrid.appendChild(tile);
    });
}

function highlightLinks(links, nodeMap) {
    document.querySelectorAll('.tile').forEach(t => t.classList.remove('highlighted'));
    if (!links) return;
    links.forEach(id => {
        const related = document.querySelector(`[data-id="${id}"]`);
        if (related) related.classList.add('highlighted');
    });
}

function openModal(src) {
    if (!src) return;
    const previewUrl = src.replace(/\/view.*$/, '/preview').replace(/\/edit.*$/, '/preview');
    modalIframe.src = previewUrl;
    modal.style.display = 'block';
}

document.querySelector('.close').onclick = () => { modal.style.display = 'none'; modalIframe.src = ''; };

// View Toggle Logic
function toggleView(view) {
    document.getElementById('tileGrid').style.display = view === 'grid' ? 'grid' : 'none';
    document.getElementById('cy').style.display = view === 'graph' ? 'block' : 'none';
}

// Live Search
searchBox.oninput = (e) => {
    const val = e.target.value.toLowerCase();
    document.querySelectorAll('.tile').forEach(tile => {
        const text = tile.innerText.toLowerCase();
        tile.style.display = text.includes(val) ? '' : 'none';
    });
};

loadGraphData();
