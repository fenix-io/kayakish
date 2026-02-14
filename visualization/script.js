const API_BASE = window.location.origin;
let selectedKayak = null;
let hullDetails = null;
let currentView = 'iso';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadKayakList();
    setupCanvas();
    document.getElementById('viewSelect').addEventListener('change', (e) => {
        currentView = e.target.value;
        if (hullDetails) {
            drawHull(hullDetails);
        }
    });
    
    // Setup form submission handler
    document.getElementById('createHullForm').addEventListener('submit', handleCreateHull);
});

// Load list of kayaks
async function loadKayakList() {
    try {
        const response = await fetch(`${API_BASE}/hulls/`);
        if (!response.ok) throw new Error('Failed to load kayaks');
        
        const kayaks = await response.json();
        const container = document.getElementById('kayakListContainer');
        
        if (kayaks.length === 0) {
            container.innerHTML = '<p>No kayaks found</p>';
            return;
        }
        
        container.innerHTML = '';
        kayaks.forEach(kayak => {
            const item = document.createElement('div');
            item.className = 'kayak-item';
            item.innerHTML = `
                <div class="kayak-item-content">
                    <div>
                        <div class="kayak-item-name">${kayak.name}</div>
                        <div class="kayak-item-desc">${kayak.description || 'No description'}</div>
                    </div>
                    <button class="delete-btn" onclick="event.stopPropagation(); openDeleteModal('${kayak.name}')" title="Delete kayak">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                            <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                        </svg>
                    </button>
                </div>
            `;
            item.addEventListener('click', () => selectKayak(kayak, item));
            container.appendChild(item);
        });
    } catch (error) {
        document.getElementById('kayakListContainer').innerHTML = 
            `<p class="error">Error loading kayaks: ${error.message}</p>`;
    }
}

// Select a kayak and display summary
function selectKayak(kayak, element) {
    selectedKayak = kayak;
    hullDetails = null;
    
    // Update UI
    document.querySelectorAll('.kayak-item').forEach(item => {
        item.classList.remove('selected');
    });
    element.classList.add('selected');
    
    // Show summary view
    document.getElementById('summaryTitle').textContent = 'Summary';
    document.getElementById('toggleDetailsBtn').style.display = 'block';
    document.getElementById('toggleDetailsBtn').textContent = '+ Details';
    document.getElementById('toggleDetailsBtn').onclick = () => loadHullDetails();
    
    // Display summary
    const summaryContainer = document.getElementById('kayakSummaryContainer');
    summaryContainer.innerHTML = `
        <div class="summary-content">
            <div class="summary-row">
                <span class="summary-label">Name:</span>
                <span class="summary-value">${kayak.name}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Length:</span>
                <span class="summary-value">${kayak.length ? kayak.length.toFixed(2) + ' m' : 'N/A'}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Beam:</span>
                <span class="summary-value">${kayak.beam ? kayak.beam.toFixed(2) + ' m' : 'N/A'}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Depth:</span>
                <span class="summary-value">${kayak.depth ? kayak.depth.toFixed(2) + ' m' : 'N/A'}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Volume:</span>
                <span class="summary-value">${kayak.volume ? kayak.volume.toFixed(3) + ' m³' : 'N/A'}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Waterline:</span>
                <span class="summary-value">${kayak.waterline ? kayak.waterline.toFixed(3) + ' m' : 'N/A'}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Displacement:</span>
                <span class="summary-value">${kayak.displacement ? kayak.displacement.toFixed(2) + ' kg' : 'N/A'}</span>
            </div>
        </div>
    `;
}

// Load detailed hull information
async function loadHullDetails() {
    if (!selectedKayak) return;
    
    try {
        const button = document.getElementById('toggleDetailsBtn');
        const originalText = button.textContent;
        button.disabled = true;
        button.textContent = 'Loading...';
        
        const response = await fetch(`${API_BASE}/hulls/${selectedKayak.name}`);
        if (!response.ok) throw new Error('Failed to load hull details');
        
        hullDetails = await response.json();
        console.log('Hull details loaded:', hullDetails);
        
        // Draw hull
        drawHull(hullDetails);
        
        // Show details view
        showDetailsView();
        
        button.disabled = false;
    } catch (error) {
        const summaryContainer = document.getElementById('kayakSummaryContainer');
        summaryContainer.innerHTML += `<p class="error">Error loading details: ${error.message}</p>`;
        
        const button = document.getElementById('toggleDetailsBtn');
        button.disabled = false;
        button.textContent = '+ Details';
    }
}

// Toggle between summary and details view
function toggleDetailsView() {
    const title = document.getElementById('summaryTitle');
    if (title.textContent === 'Summary') {
        loadHullDetails();
    } else {
        showSummaryView();
    }
}

// Show summary view
function showSummaryView() {
    if (!selectedKayak) return;
    
    document.getElementById('summaryTitle').textContent = 'Summary';
    document.getElementById('toggleDetailsBtn').textContent = '+ Details';
    document.getElementById('toggleDetailsBtn').onclick = () => loadHullDetails();
    
    const summaryContainer = document.getElementById('kayakSummaryContainer');
    summaryContainer.innerHTML = `
        <div class="summary-content">
            <div class="summary-row">
                <span class="summary-label">Name:</span>
                <span class="summary-value">${selectedKayak.name}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Length:</span>
                <span class="summary-value">${selectedKayak.length ? selectedKayak.length.toFixed(2) + ' m' : 'N/A'}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Beam:</span>
                <span class="summary-value">${selectedKayak.beam ? selectedKayak.beam.toFixed(2) + ' m' : 'N/A'}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Depth:</span>
                <span class="summary-value">${selectedKayak.depth ? selectedKayak.depth.toFixed(2) + ' m' : 'N/A'}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Volume:</span>
                <span class="summary-value">${selectedKayak.volume ? selectedKayak.volume.toFixed(3) + ' m³' : 'N/A'}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Waterline:</span>
                <span class="summary-value">${selectedKayak.waterline ? selectedKayak.waterline.toFixed(3) + ' m' : 'N/A'}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Displacement:</span>
                <span class="summary-value">${selectedKayak.displacement ? selectedKayak.displacement.toFixed(2) + ' kg' : 'N/A'}</span>
            </div>
        </div>
    `;
}

// Show details view
function showDetailsView() {
    if (!hullDetails) return;
    
    document.getElementById('summaryTitle').textContent = 'Details';
    document.getElementById('toggleDetailsBtn').textContent = '- Details';
    document.getElementById('toggleDetailsBtn').onclick = () => showSummaryView();
    
    displayDetailedSummary(hullDetails);
}

// Toggle curve/profile item
function toggleItem(id) {
    const content = document.getElementById(id);
    const icon = document.getElementById(id + '-icon');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        icon.textContent = '▼';
    } else {
        content.style.display = 'none';
        icon.textContent = '▶';
    }
}

// Display detailed hull information
function displayDetailedSummary(hull) {
    const summaryContainer = document.getElementById('kayakSummaryContainer');
    
    let curvesHtml = '<h3>Curves:</h3>';
    if (hull.curves && hull.curves.length > 0) {
        curvesHtml += '<div style="max-height: 200px; overflow-y: auto;">';
        hull.curves.forEach((curve, idx) => {
            const curveId = `curve-${idx}`;
            curvesHtml += `
                <div class="collapsible-item">
                    <div class="collapsible-header" onclick="toggleItem('${curveId}')">
                        <span class="collapse-icon" id="${curveId}-icon">▼</span>
                        <strong>${curve.name}</strong>
                        <span style="color: #666; font-size: 10px; margin-left: 5px;">(${curve.points.length} points)</span>
                    </div>
                    <div class="collapsible-content" id="${curveId}">
                        ${curve.points.map(p => `<div class="point-item">[${p[0].toFixed(3)}, ${p[1].toFixed(3)}, ${p[2].toFixed(3)}]</div>`).join('')}
                    </div>
                </div>
            `;
        });
        curvesHtml += '</div>';
    } else {
        curvesHtml += '<p style="font-size: 11px; color: #666;">No curves</p>';
    }
    
    let profilesHtml = '<h3 style="margin-top: 10px;">Profiles:</h3>';
    if (hull.profiles && hull.profiles.length > 0) {
        profilesHtml += '<div style="max-height: 200px; overflow-y: auto;">';
        hull.profiles.forEach((profile, idx) => {
            const profileId = `profile-${idx}`;
            profilesHtml += `
                <div class="collapsible-item">
                    <div class="collapsible-header" onclick="toggleItem('${profileId}')">
                        <span class="collapse-icon" id="${profileId}-icon">▼</span>
                        <strong>Station ${profile.station.toFixed(3)} m</strong>
                        <span style="color: #666; font-size: 10px; margin-left: 5px;">(${profile.points.length} points)</span>
                    </div>
                    <div class="collapsible-content" id="${profileId}">
                        ${profile.points.map(p => `<div class="point-item">[${p[0].toFixed(3)}, ${p[1].toFixed(3)}, ${p[2].toFixed(3)}]</div>`).join('')}
                    </div>
                </div>
            `;
        });
        profilesHtml += '</div>';
    } else {
        profilesHtml += '<p style="font-size: 11px; color: #666;">No profiles</p>';
    }
    
    summaryContainer.innerHTML = `
        <div class="summary-content">
            <div class="summary-row">
                <span class="summary-label">Name:</span>
                <span class="summary-value">${hull.name}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Length:</span>
                <span class="summary-value">${hull.length ? hull.length.toFixed(3) + ' m' : 'N/A'}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Beam:</span>
                <span class="summary-value">${hull.beam ? hull.beam.toFixed(3) + ' m' : 'N/A'}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Depth:</span>
                <span class="summary-value">${hull.depth ? hull.depth.toFixed(3) + ' m' : 'N/A'}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Volume:</span>
                <span class="summary-value">${hull.volume ? hull.volume.toFixed(6) + ' m³' : 'N/A'}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Waterline:</span>
                <span class="summary-value">${hull.waterline ? hull.waterline.toFixed(3) + ' m' : 'N/A'}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Displacement:</span>
                <span class="summary-value">${hull.displacement ? hull.displacement.toFixed(2) + ' kg' : 'N/A'}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">CG:</span>
                <span class="summary-value">${hull.cg ? `(${hull.cg[0].toFixed(3)}, ${hull.cg[1].toFixed(3)}, ${hull.cg[2].toFixed(3)})` : 'N/A'}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">CB:</span>
                <span class="summary-value">${hull.cb ? `(${hull.cb[0].toFixed(3)}, ${hull.cb[1].toFixed(3)}, ${hull.cb[2].toFixed(3)})` : 'N/A'}</span>
            </div>
            ${curvesHtml}
            ${profilesHtml}
        </div>
    `;
}

// Setup canvas
function setupCanvas() {
    const canvas = document.getElementById('hullCanvas');
    const container = canvas.parentElement;
    
    // Resize canvas to fit container
    function resizeCanvas() {
        const rect = container.getBoundingClientRect();
        canvas.width = rect.width - 30;
        canvas.height = rect.height - 120; // Account for header and controls
        
        if (hullDetails) {
            drawHull(hullDetails);
        }
    }
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
}

// Draw hull on canvas
function drawHull(hull) {
    const canvas = document.getElementById('hullCanvas');
    const ctx = canvas.getContext('2d');
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    if (!hull.curves || hull.curves.length === 0) {
        ctx.fillText('No hull data to display', canvas.width / 2 - 50, canvas.height / 2);
        return;
    }
    
    // Calculate bounds and scale
    const bounds = {
        minX: hull.min_x || 0,
        maxX: hull.max_x || 5,
        minY: hull.min_y || -0.3,
        maxY: hull.max_y || 0.3,
        minZ: hull.min_z || 0,
        maxZ: hull.max_z || 0.3
    };
    
    // Add padding
    const padding = 40;
    const drawWidth = canvas.width - 2 * padding;
    const drawHeight = canvas.height - 2 * padding;
    
    // Calculate scale and offset based on view
    let scaleX, scaleY, offsetX, offsetY;
    let getScreenCoords;
    
    switch (currentView) {
        case 'iso': // Isometric side view
            const scaleIso = Math.min(
                drawWidth / ((bounds.maxX - bounds.minX) + (bounds.maxY - bounds.minY) * 0.5),
                drawHeight / ((bounds.maxZ - bounds.minZ) + (bounds.maxX - bounds.minX) * 0.3)
            );
            offsetX = padding + drawWidth / 2;
            offsetY = padding + drawHeight * 0.85;
            
            // Isometric projection from side-ish angle
            getScreenCoords = (x, y, z) => ({
                x: offsetX + (x - (bounds.maxX + bounds.minX) / 2) * scaleIso * 0.866 
                    - y * scaleIso * 0.5,
                y: offsetY - (z - bounds.minZ) * scaleIso 
                    - (x - (bounds.maxX + bounds.minX) / 2) * scaleIso * 0.25 
                    - y * scaleIso * 0.433
            });
            break;
            
        case 'side': // 2D Side view (X-Z)
            scaleX = drawWidth / (bounds.maxX - bounds.minX);
            scaleY = drawHeight / (bounds.maxZ - bounds.minZ);
            const scaleSide = Math.min(scaleX, scaleY);
            offsetX = padding + (drawWidth - (bounds.maxX - bounds.minX) * scaleSide) / 2;
            offsetY = padding + drawHeight;
            
            getScreenCoords = (x, y, z) => ({
                x: offsetX + (x - bounds.minX) * scaleSide,
                y: offsetY - (z - bounds.minZ) * scaleSide
            });
            break;
            
        case 'top': // X-Y view
            scaleX = drawWidth / (bounds.maxX - bounds.minX);
            scaleY = drawHeight / (bounds.maxY - bounds.minY);
            const scaleTop = Math.min(scaleX, scaleY);
            offsetX = padding + (drawWidth - (bounds.maxX - bounds.minX) * scaleTop) / 2;
            offsetY = padding + (drawHeight + (bounds.maxY - bounds.minY) * scaleTop) / 2;
            
            getScreenCoords = (x, y, z) => ({
                x: offsetX + (x - bounds.minX) * scaleTop,
                y: offsetY - (y - bounds.minY) * scaleTop
            });
            break;
            
        case 'front': // Y-Z view
            scaleX = drawWidth / (bounds.maxY - bounds.minY);
            scaleY = drawHeight / (bounds.maxZ - bounds.minZ);
            const scaleFront = Math.min(scaleX, scaleY);
            offsetX = padding + drawWidth / 2;
            offsetY = padding + drawHeight;
            
            getScreenCoords = (x, y, z) => ({
                x: offsetX + y * scaleFront,
                y: offsetY - (z - bounds.minZ) * scaleFront
            });
            break;
            
        case '3d': // 3D isometric
            // Calculate projected dimensions
            const projectedWidth = (bounds.maxX - bounds.minX) * 0.866 + (bounds.maxY - bounds.minY) * 0.866;
            const projectedHeight = (bounds.maxZ - bounds.minZ) + 
                                   (bounds.maxX - bounds.minX) * 0.5 + 
                                   (bounds.maxY - bounds.minY) * 0.5;
            
            const scale3d = Math.min(
                drawWidth / projectedWidth,
                drawHeight / projectedHeight
            );
            offsetX = padding + drawWidth / 2;
            offsetY = padding + drawHeight * 0.8;
            
            getScreenCoords = (x, y, z) => ({
                x: offsetX + (x - (bounds.maxX + bounds.minX) / 2) * scale3d * 0.866 
                    - y * scale3d * 0.866,
                y: offsetY - (z - bounds.minZ) * scale3d 
                    - (x - (bounds.maxX + bounds.minX) / 2) * scale3d * 0.5 
                    - y * scale3d * 0.5
            });
            break;
    }
    
    // Draw curves
    ctx.strokeStyle = 'blue';
    ctx.lineWidth = 2;
    hull.curves.forEach(curve => {
        if (curve.points.length < 2) return;
        
        ctx.beginPath();
        const firstPoint = getScreenCoords(...curve.points[0]);
        ctx.moveTo(firstPoint.x, firstPoint.y);
        
        for (let i = 1; i < curve.points.length; i++) {
            const point = getScreenCoords(...curve.points[i]);
            ctx.lineTo(point.x, point.y);
        }
        ctx.stroke();
    });
    
    // Draw curve points
    ctx.fillStyle = 'red';
    hull.curves.forEach(curve => {
        curve.points.forEach(point => {
            const coords = getScreenCoords(...point);
            ctx.beginPath();
            ctx.arc(coords.x, coords.y, 3, 0, 2 * Math.PI);
            ctx.fill();
        });
    });
    
    // Draw profile points
    if (hull.profiles && hull.profiles.length > 0) {
        ctx.fillStyle = 'green';
        hull.profiles.forEach(profile => {
            profile.points.forEach(point => {
                const coords = getScreenCoords(...point);
                ctx.beginPath();
                ctx.arc(coords.x, coords.y, 3, 0, 2 * Math.PI);
                ctx.fill();
            });
        });
    }
    
    // Draw waterline
    if (hull.waterline) {
        ctx.strokeStyle = 'cyan';
        ctx.lineWidth = 3;
        ctx.setLineDash([5, 5]);
        
        if (currentView === 'iso') {
            // Draw waterline plane in isometric view
            const wlFrontPort = getScreenCoords(bounds.minX, bounds.maxY, hull.waterline);
            const wlFrontStbd = getScreenCoords(bounds.minX, bounds.minY, hull.waterline);
            const wlRearPort = getScreenCoords(bounds.maxX, bounds.maxY, hull.waterline);
            const wlRearStbd = getScreenCoords(bounds.maxX, bounds.minY, hull.waterline);
            ctx.beginPath();
            ctx.moveTo(wlFrontPort.x, wlFrontPort.y);
            ctx.lineTo(wlRearPort.x, wlRearPort.y);
            ctx.lineTo(wlRearStbd.x, wlRearStbd.y);
            ctx.lineTo(wlFrontStbd.x, wlFrontStbd.y);
            ctx.closePath();
            ctx.stroke();
        } else if (currentView === 'side') {
            // Horizontal line at waterline height
            const wl = getScreenCoords(bounds.minX, 0, hull.waterline);
            const wr = getScreenCoords(bounds.maxX, 0, hull.waterline);
            ctx.beginPath();
            ctx.moveTo(wl.x, wl.y);
            ctx.lineTo(wr.x, wr.y);
            ctx.stroke();
        } else if (currentView === 'front') {
            // Horizontal line at waterline height
            const wl = getScreenCoords(0, bounds.minY, hull.waterline);
            const wr = getScreenCoords(0, bounds.maxY, hull.waterline);
            ctx.beginPath();
            ctx.moveTo(wl.x, wl.y);
            ctx.lineTo(wr.x, wr.y);
            ctx.stroke();
        }
        
        ctx.setLineDash([]);
    }
    
    // Draw axes labels
    ctx.fillStyle = 'black';
    ctx.font = '12px Arial';
    const viewLabels = {
        'iso': 'Isometric Side View (X-Y-Z)',
        'side': '← Stern | X-axis (Length) | Bow →    ↑ Z (Height)',
        'top': '← Stern | X-axis (Length) | Bow →    ← Port | Y-axis (Beam) | Starboard →',
        'front': '← Port | Y-axis (Beam) | Starboard →    ↑ Z (Height)',
        '3d': '3D Isometric View'
    };
    ctx.fillText(viewLabels[currentView], padding, canvas.height - 10);
}

// Modal functions
function openCreateModal() {
    document.getElementById('createModal').classList.add('show');
}

let kayakToDelete = null;

function openDeleteModal(kayakName) {
    kayakToDelete = kayakName;
    document.getElementById('deleteKayakName').textContent = kayakName;
    document.getElementById('deleteModal').classList.add('show');
}

function closeDeleteModal() {
    document.getElementById('deleteModal').classList.remove('show');
    kayakToDelete = null;
}

function closeCreateModal() {
    document.getElementById('createModal').classList.remove('show');
    document.getElementById('createHullForm').reset();
    // Refresh the kayak list when modal closes
    loadKayakList();
}

// Close modal when clicking outside
window.addEventListener('click', (event) => {
    const createModal = document.getElementById('createModal');
    const deleteModal = document.getElementById('deleteModal');
    
    if (event.target === createModal) {
        closeCreateModal();
    }
    if (event.target === deleteModal) {
        closeDeleteModal();
    }
});

// Delete kayak function
async function confirmDeleteKayak() {
    if (!kayakToDelete) return;
    
    try {
        const deleteBtn = document.querySelector('#deleteModal .btn-danger');
        deleteBtn.disabled = true;
        deleteBtn.textContent = 'Deleting...';
        
        const response = await fetch(`${API_BASE}/hulls/${kayakToDelete}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete kayak');
        }
        
        closeDeleteModal();
        loadKayakList();
        
        // Clear visualization if deleted kayak was selected
        if (selectedKayak && selectedKayak.name === kayakToDelete) {
            selectedKayak = null;
            hullDetails = null;
            document.getElementById('kayakSummaryContainer').innerHTML = '<p>Select a kayak to view summary</p>';
            const canvas = document.getElementById('hullCanvas');
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
        
    } catch (error) {
        console.error('Error deleting kayak:', error);
        alert(`Error deleting kayak: ${error.message}`);
        
        const deleteBtn = document.querySelector('#deleteModal .btn-danger');
        deleteBtn.disabled = false;
        deleteBtn.textContent = 'Delete';
    }
}

// Parse curves data from textarea
function parseCurvesData(text) {
    const curves = [];
    const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0);
    
    let currentCurve = null;
    
    for (const line of lines) {
        if (line.toLowerCase().startsWith('curve:')) {
            // Save previous curve if exists
            if (currentCurve && currentCurve.points.length > 0) {
                curves.push(currentCurve);
            }
            // Start new curve
            const curveName = line.substring(6).trim();
            currentCurve = {
                name: curveName,
                points: []
            };
        } else if (currentCurve) {
            // Parse point coordinates
            const coords = line.split(',').map(s => parseFloat(s.trim()));
            if (coords.length === 3 && coords.every(n => !isNaN(n))) {
                currentCurve.points.push(coords);
            }
        }
    }
    
    // Add last curve
    if (currentCurve && currentCurve.points.length > 0) {
        curves.push(currentCurve);
    }
    
    return curves;
}

// Handle form submission
async function handleCreateHull(e) {
    e.preventDefault();
    
    try {
        // Get form values
        const name = document.getElementById('hullName').value.trim();
        const description = document.getElementById('hullDescription').value.trim() || null;
        const units = document.getElementById('hullUnits').value;
        const targetWaterline = document.getElementById('targetWaterline').value;
        const targetPayload = document.getElementById('targetPayload').value;
        const targetWeight = document.getElementById('targetWeight').value;
        const curvesText = document.getElementById('curvesData').value;
        
        // Parse curves
        const curves = parseCurvesData(curvesText);
        
        if (curves.length === 0) {
            alert('Please enter at least one curve with points');
            return;
        }
        
        // Build request body
        const requestBody = {
            name: name,
            description: description,
            units: units,
            target_waterline: targetWaterline ? parseFloat(targetWaterline) : null,
            target_payload: targetPayload ? parseFloat(targetPayload) : null,
            target_weight: targetWeight ? parseFloat(targetWeight) : null,
            curves: curves
        };
        
        // Show loading state
        const submitBtn = e.target.querySelector('.btn-primary');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Creating...';
        
        // Make POST request
        const response = await fetch(`${API_BASE}/hulls/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to create kayak');
        }
        
        const result = await response.json();
        console.log('Kayak created:', result);
        
        // Close modal (this will refresh the list automatically)
        closeCreateModal();
        
        // Show success message
        alert(`Kayak "${name}" created successfully!`);
        
    } catch (error) {
        console.error('Error creating kayak:', error);
        alert(`Error creating kayak: ${error.message}`);
        
        // Restore button
        const submitBtn = e.target.querySelector('.btn-primary');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create Kayak';
    }
}
