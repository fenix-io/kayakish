const API_BASE = window.location.origin;
let selectedKayak = null;
let hullDetails = null;
let currentView = 'iso';
let currentTab = 'visualization';
let stabilityData = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadKayakList();
    setupCanvas();
    setupStabilityCanvas();
    document.getElementById('viewSelect').addEventListener('change', (e) => {
        currentView = e.target.value;
        if (hullDetails) {
            drawHull(hullDetails);
        }
    });
    
    // Setup form submission handlers
    document.getElementById('createHullForm').addEventListener('submit', handleCreateHull);
    document.getElementById('stabilityForm').addEventListener('submit', handleStabilityAnalysis);
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
    
    // Update UI
    document.querySelectorAll('.kayak-item').forEach(item => {
        item.classList.remove('selected');
    });
    element.classList.add('selected');
    
    // Show summary view in left panel
    document.getElementById('summaryTitle').textContent = 'Summary';
    document.getElementById('toggleDetailsBtn').style.display = 'block';
    document.getElementById('toggleDetailsBtn').textContent = '+ Details';
    document.getElementById('toggleDetailsBtn').onclick = () => toggleDetailsView();
    
    // Display summary
    displaySummary(kayak);
    
    // Load hull details for visualization immediately
    loadHullDetailsForVisualization();
}

// Display summary in left panel
function displaySummary(kayak) {
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

// Load hull details for visualization (called automatically)
async function loadHullDetailsForVisualization() {
    if (!selectedKayak) return;
    
    try {
        const response = await fetch(`${API_BASE}/hulls/${selectedKayak.name}`);
        if (!response.ok) throw new Error('Failed to load hull details');
        
        hullDetails = await response.json();
        console.log('Hull details loaded:', hullDetails);
        
        // Draw hull
        drawHull(hullDetails);
        
        // Initialize profiles
        initializeProfiles(hullDetails);
        
    } catch (error) {
        console.error('Error loading hull details:', error);
        const canvas = document.getElementById('hullCanvas');
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#666';
        ctx.font = '14px Arial';
        ctx.fillText(`Error loading hull: ${error.message}`, canvas.width / 2 - 100, canvas.height / 2);
    }
}

// Toggle between summary and details view (only affects left panel)
function toggleDetailsView() {
    const title = document.getElementById('summaryTitle');
    if (title.textContent === 'Summary') {
        showDetailsView();
    } else {
        showSummaryView();
    }
}

// Show summary view (only affects left panel)
function showSummaryView() {
    if (!selectedKayak) return;
    
    document.getElementById('summaryTitle').textContent = 'Summary';
    document.getElementById('toggleDetailsBtn').textContent = '+ Details';
    
    displaySummary(selectedKayak);
}

// Show details view (only affects left panel)
function showDetailsView() {
    if (!hullDetails) return;
    
    document.getElementById('summaryTitle').textContent = 'Details';
    document.getElementById('toggleDetailsBtn').textContent = '- Details';
    
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
    ctx.lineWidth = 2;
    hull.curves.forEach(curve => {
        if (curve.points.length < 2) return;
        
        // Draw curve segments with color based on waterline
        for (let i = 0; i < curve.points.length - 1; i++) {
            const p1 = curve.points[i];
            const p2 = curve.points[i + 1];
            
            // Check if segment is below waterline
            const belowWaterline = hull.waterline && 
                                  (p1[2] < hull.waterline && p2[2] < hull.waterline);
            
            ctx.strokeStyle = belowWaterline ? '#99CCFF' : '#0000CC'; // Light blue below, dark blue above
            
            ctx.beginPath();
            const point1 = getScreenCoords(...p1);
            const point2 = getScreenCoords(...p2);
            ctx.moveTo(point1.x, point1.y);
            ctx.lineTo(point2.x, point2.y);
            ctx.stroke();
        }
    });
    
    // Draw curve points
    hull.curves.forEach(curve => {
        curve.points.forEach(point => {
            const coords = getScreenCoords(...point);
            
            // Check if point is below waterline
            const belowWaterline = hull.waterline && point[2] < hull.waterline;
            ctx.fillStyle = belowWaterline ? '#FFB3B3' : '#CC0000'; // Light pink below, dark red above
            
            ctx.beginPath();
            ctx.arc(coords.x, coords.y, 3, 0, 2 * Math.PI);
            ctx.fill();
        });
    });
    
    // Draw waterline
    if (hull.waterline) {
        ctx.strokeStyle = 'cyan';
        ctx.lineWidth = 2;
        
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

// Tab switching function
function switchTab(tabName) {
    currentTab = tabName;
    
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Setup canvas when switching to relevant tabs
    if (tabName === 'visualization' && hullDetails) {
        setupCanvas();
        drawHull(hullDetails);
    } else if (tabName === 'stability' && stabilityData) {
        setupStabilityCanvas();
        drawStabilityResults(stabilityData);
    }
}

// Setup stability canvas
function setupStabilityCanvas() {
    const gzCanvas = document.getElementById('gzCanvas');
    const momentCanvas = document.getElementById('momentCanvas');
    if (!gzCanvas || !momentCanvas) return;
    
    const container = gzCanvas.closest('.stability-graphs');
    
    // Resize canvases to fit container
    function resizeCanvas() {
        if (!container) return;
        const rect = container.getBoundingClientRect();
        
        // Each canvas gets half the width minus gap
        const canvasWidth = (rect.width - 15) / 2 - 20; // 15px gap, some padding
        const canvasHeight = Math.max(400, rect.height - 80); // Account for title
        
        gzCanvas.width = canvasWidth;
        gzCanvas.height = canvasHeight;
        momentCanvas.width = canvasWidth;
        momentCanvas.height = canvasHeight;
        
        if (stabilityData) {
            drawStabilityResults(stabilityData);
        }
    }
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
}

// Handle stability analysis form submission
async function handleStabilityAnalysis(e) {
    e.preventDefault();
    
    if (!selectedKayak) {
        alert('Please select a kayak first');
        return;
    }
    
    try {
        // Get form values
        const paddlerWeight = document.getElementById('paddlerWeight').value;
        const paddlerCgZ = document.getElementById('paddlerCgZ').value;
        const hullWeight = document.getElementById('hullWeight').value;
        const maxAngle = document.getElementById('maxAngle').value;
        const angleStep = document.getElementById('angleStep').value;
        
        // Build request body
        const requestBody = {
            hull_name: selectedKayak.name,
            paddler_weight: paddlerWeight ? parseFloat(paddlerWeight) : null,
            paddler_cg_z: parseFloat(paddlerCgZ),
            hull_weight: hullWeight ? parseFloat(hullWeight) : null,
            max_angle: parseFloat(maxAngle),
            step: parseFloat(angleStep)
        };
        
        // Hide form and results, show loader
        document.querySelector('.stability-form-container').style.display = 'none';
        document.getElementById('stabilityResults').classList.remove('show');
        document.getElementById('stabilityLoader').classList.add('show');
        
        // Make POST request
        const response = await fetch(`${API_BASE}/hulls/${selectedKayak.name}/stability`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to analyze stability');
        }
        
        stabilityData = await response.json();
        console.log('Stability analysis result:', stabilityData);
        
        // Hide loader, show results
        document.getElementById('stabilityLoader').classList.remove('show');
        document.getElementById('stabilityResults').classList.add('show');
        
        // Draw results
        setupStabilityCanvas();
        drawStabilityResults(stabilityData);
        
    } catch (error) {
        console.error('Error analyzing stability:', error);
        alert(`Error analyzing stability: ${error.message}`);
        
        // Hide loader, show form
        document.getElementById('stabilityLoader').classList.remove('show');
        document.querySelector('.stability-form-container').style.display = 'block';
    }
}

// Draw stability results on canvas
function drawStabilityResults(data) {
    const gzCanvas = document.getElementById('gzCanvas');
    const momentCanvas = document.getElementById('momentCanvas');
    if (!gzCanvas || !momentCanvas) return;
    
    if (!data.stability_points || data.stability_points.length === 0) {
        const ctx = gzCanvas.getContext('2d');
        ctx.fillStyle = '#666';
        ctx.font = '14px Arial';
        ctx.fillText('No stability data to display', gzCanvas.width / 2 - 100, gzCanvas.height / 2);
        return;
    }
    
    const points = data.stability_points;
    
    // Draw GZ graph
    drawGZGraph(gzCanvas, points, data);
    
    // Draw Moment graph
    drawMomentGraph(momentCanvas, points, data);
    
    // Add button to go back to form
    addBackButton();
}

// Draw GZ (Righting Arm) graph
function drawGZGraph(canvas, points, data) {
    const ctx = canvas.getContext('2d');
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Calculate bounds
    const maxAngle = Math.max(...points.map(p => p.angle));
    const minGz = Math.min(...points.map(p => p.gz), 0);
    const maxGz = Math.max(...points.map(p => p.gz));
    
    // Drawing parameters
    const padding = 50;
    const graphWidth = canvas.width - 2 * padding;
    const graphHeight = canvas.height - 2 * padding - 60; // Space for summary
    
    // Scale factors
    const scaleX = graphWidth / maxAngle;
    const scaleY = graphHeight / (maxGz - minGz);
    const zeroY = padding + (maxGz * scaleY);
    
    // Draw axes
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding, zeroY);
    ctx.lineTo(padding + graphWidth, zeroY);
    ctx.stroke();
    
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, padding + graphHeight);
    ctx.stroke();
    
    // Draw grid
    ctx.strokeStyle = '#ddd';
    ctx.lineWidth = 1;
    
    // Vertical grid lines (angle)
    const angleStep = maxAngle > 60 ? 15 : 10;
    for (let angle = 0; angle <= maxAngle; angle += angleStep) {
        const x = padding + angle * scaleX;
        ctx.beginPath();
        ctx.moveTo(x, padding);
        ctx.lineTo(x, padding + graphHeight);
        ctx.stroke();
    }
    
    // Horizontal grid lines (GZ)
    const gzRange = maxGz - minGz;
    const gzStep = gzRange / 8;
    for (let i = 0; i <= 8; i++) {
        const gz = minGz + i * gzStep;
        const y = zeroY - gz * scaleY;
        if (y >= padding && y <= padding + graphHeight) {
            ctx.beginPath();
            ctx.moveTo(padding, y);
            ctx.lineTo(padding + graphWidth, y);
            ctx.stroke();
        }
    }
    
    // Draw GZ curve
    ctx.strokeStyle = '#007bff';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    
    points.forEach((point, idx) => {
        const x = padding + point.angle * scaleX;
        const y = zeroY - point.gz * scaleY;
        
        if (idx === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    ctx.stroke();
    
    // Draw points
    ctx.fillStyle = '#007bff';
    points.forEach(point => {
        const x = padding + point.angle * scaleX;
        const y = zeroY - point.gz * scaleY;
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, 2 * Math.PI);
        ctx.fill();
    });
    
    // Mark max GZ point
    const maxGzPoint = points.reduce((max, p) => p.gz > max.gz ? p : max, points[0]);
    if (maxGzPoint) {
        const x = padding + maxGzPoint.angle * scaleX;
        const y = zeroY - maxGzPoint.gz * scaleY;
        ctx.strokeStyle = '#28a745';
        ctx.fillStyle = '#28a745';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, 2 * Math.PI);
        ctx.stroke();
        ctx.fill();
    }
    
    // Mark vanishing angle
    if (data.vanishing_angle !== null && data.vanishing_angle !== undefined) {
        const x = padding + data.vanishing_angle * scaleX;
        ctx.strokeStyle = '#dc3545';
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.moveTo(x, padding);
        ctx.lineTo(x, padding + graphHeight);
        ctx.stroke();
        ctx.setLineDash([]);
    }
    
    // Labels
    ctx.fillStyle = '#333';
    ctx.font = 'bold 12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Heel Angle (degrees)', padding + graphWidth / 2, canvas.height - 10);
    
    ctx.save();
    ctx.translate(12, padding + graphHeight / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('GZ - Righting Arm (m)', 0, 0);
    ctx.restore();
    
    // Axis labels
    ctx.font = '10px Arial';
    ctx.fillStyle = '#666';
    ctx.textAlign = 'center';
    
    // X-axis labels
    for (let angle = 0; angle <= maxAngle; angle += angleStep) {
        const x = padding + angle * scaleX;
        ctx.fillText(angle.toString(), x, zeroY + 18);
    }
    
    // Y-axis labels
    ctx.textAlign = 'right';
    for (let i = 0; i <= 8; i++) {
        const gz = minGz + i * gzStep;
        const y = zeroY - gz * scaleY;
        if (y >= padding && y <= padding + graphHeight) {
            ctx.fillText(gz.toFixed(3), padding - 5, y + 4);
        }
    }
    
    // Summary
    const summaryY = padding + graphHeight + 30;
    ctx.textAlign = 'left';
    ctx.font = '11px Arial';
    ctx.fillStyle = '#333';
    
    let summaryLine = summaryY;
    ctx.fillStyle = '#28a745';
    ctx.fillText(`Max GZ: ${maxGzPoint.gz.toFixed(4)}m at ${maxGzPoint.angle.toFixed(1)}°`, padding, summaryLine);
    summaryLine += 16;
    
    if (data.vanishing_angle !== null && data.vanishing_angle !== undefined) {
        ctx.fillStyle = '#dc3545';
        ctx.fillText(`Vanishing: ${data.vanishing_angle.toFixed(1)}°`, padding, summaryLine);
    } else {
        ctx.fillStyle = '#28a745';
        ctx.fillText(`Vanishing: > ${maxAngle}° (Very stable!)`, padding, summaryLine);
    }
}

// Draw Moment graph
function drawMomentGraph(canvas, points, data) {
    const ctx = canvas.getContext('2d');
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Calculate bounds
    const maxAngle = Math.max(...points.map(p => p.angle));
    const minMoment = Math.min(...points.map(p => p.moment), 0);
    const maxMoment = Math.max(...points.map(p => p.moment));
    
    // Drawing parameters
    const padding = 50;
    const graphWidth = canvas.width - 2 * padding;
    const graphHeight = canvas.height - 2 * padding - 60; // Space for summary
    
    // Scale factors
    const scaleX = graphWidth / maxAngle;
    const scaleY = graphHeight / (maxMoment - minMoment);
    const zeroY = padding + (maxMoment * scaleY);
    
    // Draw axes
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding, zeroY);
    ctx.lineTo(padding + graphWidth, zeroY);
    ctx.stroke();
    
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, padding + graphHeight);
    ctx.stroke();
    
    // Draw grid
    ctx.strokeStyle = '#ddd';
    ctx.lineWidth = 1;
    
    // Vertical grid lines (angle)
    const angleStep = maxAngle > 60 ? 15 : 10;
    for (let angle = 0; angle <= maxAngle; angle += angleStep) {
        const x = padding + angle * scaleX;
        ctx.beginPath();
        ctx.moveTo(x, padding);
        ctx.lineTo(x, padding + graphHeight);
        ctx.stroke();
    }
    
    // Horizontal grid lines (Moment)
    const momentRange = maxMoment - minMoment;
    const momentStep = momentRange / 8;
    for (let i = 0; i <= 8; i++) {
        const moment = minMoment + i * momentStep;
        const y = zeroY - moment * scaleY;
        if (y >= padding && y <= padding + graphHeight) {
            ctx.beginPath();
            ctx.moveTo(padding, y);
            ctx.lineTo(padding + graphWidth, y);
            ctx.stroke();
        }
    }
    
    // Draw Moment curve
    ctx.strokeStyle = '#28a745';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    
    points.forEach((point, idx) => {
        const x = padding + point.angle * scaleX;
        const y = zeroY - point.moment * scaleY;
        
        if (idx === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    ctx.stroke();
    
    // Draw points
    ctx.fillStyle = '#28a745';
    points.forEach(point => {
        const x = padding + point.angle * scaleX;
        const y = zeroY - point.moment * scaleY;
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, 2 * Math.PI);
        ctx.fill();
    });
    
    // Mark max moment point
    if (data.max_moment_angle !== null && data.max_moment_angle !== undefined) {
        const maxPoint = points.find(p => Math.abs(p.angle - data.max_moment_angle) < 0.1);
        if (maxPoint) {
            const x = padding + maxPoint.angle * scaleX;
            const y = zeroY - maxPoint.moment * scaleY;
            ctx.strokeStyle = '#ff6b00';
            ctx.fillStyle = '#ff6b00';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(x, y, 5, 0, 2 * Math.PI);
            ctx.stroke();
            ctx.fill();
        }
    }
    
    // Mark vanishing angle
    if (data.vanishing_angle !== null && data.vanishing_angle !== undefined) {
        const x = padding + data.vanishing_angle * scaleX;
        ctx.strokeStyle = '#dc3545';
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.moveTo(x, padding);
        ctx.lineTo(x, padding + graphHeight);
        ctx.stroke();
        ctx.setLineDash([]);
    }
    
    // Labels
    ctx.fillStyle = '#333';
    ctx.font = 'bold 12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Heel Angle (degrees)', padding + graphWidth / 2, canvas.height - 10);
    
    ctx.save();
    ctx.translate(12, padding + graphHeight / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Righting Moment (N·m)', 0, 0);
    ctx.restore();
    
    // Axis labels
    ctx.font = '10px Arial';
    ctx.fillStyle = '#666';
    ctx.textAlign = 'center';
    
    // X-axis labels
    for (let angle = 0; angle <= maxAngle; angle += angleStep) {
        const x = padding + angle * scaleX;
        ctx.fillText(angle.toString(), x, zeroY + 18);
    }
    
    // Y-axis labels
    ctx.textAlign = 'right';
    for (let i = 0; i <= 8; i++) {
        const moment = minMoment + i * momentStep;
        const y = zeroY - moment * scaleY;
        if (y >= padding && y <= padding + graphHeight) {
            ctx.fillText(moment.toFixed(1), padding - 5, y + 4);
        }
    }
    
    // Summary
    const summaryY = padding + graphHeight + 30;
    ctx.textAlign = 'left';
    ctx.font = '11px Arial';
    ctx.fillStyle = '#333';
    
    let summaryLine = summaryY;
    ctx.fillStyle = '#ff6b00';
    const maxMomentValue = data.max_moment || maxMoment;
    const maxMomentAngle = data.max_moment_angle || points.reduce((max, p) => p.moment > max.moment ? p : max, points[0]).angle;
    ctx.fillText(`Max Moment: ${maxMomentValue.toFixed(1)} N·m at ${maxMomentAngle.toFixed(1)}°`, padding, summaryLine);
}

// Add back button to return to stability form
function addBackButton() {
    // Check if button already exists
    if (document.getElementById('backToFormBtn')) return;
    
    const resultsDiv = document.getElementById('stabilityResults');
    const button = document.createElement('button');
    button.id = 'backToFormBtn';
    button.className = 'btn-secondary';
    button.textContent = 'New Analysis';
    button.style.position = 'absolute';
    button.style.top = '15px';
    button.style.right = '15px';
    button.onclick = () => {
        document.getElementById('stabilityResults').classList.remove('show');
        document.querySelector('.stability-form-container').style.display = 'block';
    };
    
    resultsDiv.style.position = 'relative';
    resultsDiv.appendChild(button);
}

// ========== PROFILES TAB ==========

let currentProfile = null;

// Initialize profiles when hull details are loaded
function initializeProfiles(hull) {
    if (!hull.profiles || hull.profiles.length === 0) {
        document.getElementById('profilesEmpty').style.display = 'flex';
        document.getElementById('profilesContent').classList.remove('show');
        return;
    }
    
    // Hide empty state, show content
    document.getElementById('profilesEmpty').style.display = 'none';
    document.getElementById('profilesContent').classList.add('show');
    
    // Populate station selector
    const stationSelect = document.getElementById('stationSelect');
    stationSelect.innerHTML = '<option value="">Select a station...</option>';
    
    hull.profiles.forEach((profile, idx) => {
        const option = document.createElement('option');
        option.value = idx;
        option.textContent = `Station ${profile.station.toFixed(4)} m`;
        stationSelect.appendChild(option);
    });
    
    // Setup canvases
    setupProfileCanvases();
    
    // Select first profile
    if (hull.profiles.length > 0) {
        stationSelect.value = '0';
        selectStation();
    }
}

// Setup profile canvases
function setupProfileCanvases() {
    const profileCanvas = document.getElementById('profileCanvas');
    const hullSideCanvas = document.getElementById('hullSideCanvas');
    if (!profileCanvas || !hullSideCanvas) return;
    
    function resizeCanvases() {
        // Wait a tick for flex layout to settle
        requestAnimationFrame(() => {
            // Get the actual rendered size of the canvas elements
            const profileRect = profileCanvas.getBoundingClientRect();
            const sideRect = hullSideCanvas.getBoundingClientRect();
            
            if (profileRect.width > 0 && profileRect.height > 0) {
                // Set canvas internal resolution to match display size
                profileCanvas.width = Math.floor(profileRect.width);
                profileCanvas.height = Math.floor(profileRect.height);
            }
            
            if (sideRect.width > 0 && sideRect.height > 0) {
                // Set canvas internal resolution to match display size
                hullSideCanvas.width = Math.floor(sideRect.width);
                hullSideCanvas.height = Math.floor(sideRect.height);
            }
            
            if (currentProfile !== null) {
                drawProfile();
                drawHullSideView();
            }
        });
    }
    
    resizeCanvases();
    // Also call after delays to ensure layout is complete
    setTimeout(resizeCanvases, 100);
    setTimeout(resizeCanvases, 300);
    window.addEventListener('resize', resizeCanvases);
}

// Select a station and draw its profile
function selectStation() {
    const stationSelect = document.getElementById('stationSelect');
    const profileIdx = parseInt(stationSelect.value);
    
    if (isNaN(profileIdx) || !hullDetails || !hullDetails.profiles) return;
    
    currentProfile = hullDetails.profiles[profileIdx];
    
    // Update station info
    const stationInfo = document.getElementById('stationInfo');
    stationInfo.textContent = `${currentProfile.points.length} points`;
    
    // Draw views
    drawProfile();
    drawHullSideView();
}

// Draw the current profile cross-section
function drawProfile() {
    const canvas = document.getElementById('profileCanvas');
    if (!canvas || !currentProfile) return;
    
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const points = currentProfile.points;
    if (points.length === 0) {
        ctx.fillStyle = '#666';
        ctx.font = '11px Arial';
        ctx.fillText('No points in this profile', canvas.width / 2 - 80, canvas.height / 2);
        return;
    }
    
    // Calculate bounds (Y-Z plane)
    const yValues = points.map(p => p[1]);
    const zValues = points.map(p => p[2]);
    const minY = Math.min(...yValues);
    const maxY = Math.max(...yValues);
    const minZ = Math.min(...zValues);
    const maxZ = Math.max(...zValues);
    
    // Add padding
    const padding = 40;
    const drawWidth = canvas.width - 2 * padding;
    const drawHeight = canvas.height - 2 * padding;
    
    // Calculate scale (maintain aspect ratio)
    const rangeY = maxY - minY || 1;
    const rangeZ = maxZ - minZ || 1;
    const scale = Math.min(drawWidth / rangeY, drawHeight / rangeZ) * 0.9;
    
    // Center the drawing
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    
    // Helper function to convert profile coords to canvas coords
    function toCanvas(y, z) {
        return {
            x: centerX + (y - (minY + maxY) / 2) * scale,
            y: centerY - (z - (minZ + maxZ) / 2) * scale
        };
    }
    
    // Draw axes
    ctx.strokeStyle = '#999';
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]);
    
    // Y axis (horizontal)
    ctx.beginPath();
    ctx.moveTo(padding, centerY);
    ctx.lineTo(canvas.width - padding, centerY);
    ctx.stroke();
    
    // Z axis (vertical)
    ctx.beginPath();
    ctx.moveTo(centerX, padding);
    ctx.lineTo(centerX, canvas.height - padding);
    ctx.stroke();
    
    ctx.setLineDash([]);
    
    // Draw profile outline
    ctx.strokeStyle = '#007bff';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    points.forEach((point, idx) => {
        const coords = toCanvas(point[1], point[2]);
        if (idx === 0) {
            ctx.moveTo(coords.x, coords.y);
        } else {
            ctx.lineTo(coords.x, coords.y);
        }
    });
    
    // Close the profile
    if (points.length > 0) {
        const firstCoords = toCanvas(points[0][1], points[0][2]);
        ctx.lineTo(firstCoords.x, firstCoords.y);
    }
    
    ctx.stroke();
    
    // Draw points
    ctx.fillStyle = '#007bff';
    points.forEach(point => {
        const coords = toCanvas(point[1], point[2]);
        ctx.beginPath();
        ctx.arc(coords.x, coords.y, 2.5, 0, 2 * Math.PI);
        ctx.fill();
    });
    
    // Draw labels
    ctx.fillStyle = '#333';
    ctx.font = '10px Arial';
    ctx.textAlign = 'center';
    
    // Y axis label (Port/Starboard)
    ctx.fillText('← Port', padding + 30, centerY - 8);
    ctx.fillText('Starboard →', canvas.width - padding - 30, centerY - 8);
    
    // Z axis label (Height)
    ctx.save();
    ctx.translate(centerX + 12, padding + 30);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Height (Z)', 0, 0);
    ctx.restore();
    
    // Draw scale info
    ctx.font = '9px Arial';
    ctx.fillStyle = '#666';
    ctx.textAlign = 'left';
    ctx.fillText(`Y: ${minY.toFixed(3)} to ${maxY.toFixed(3)} m`, padding, canvas.height - padding + 15);
    ctx.fillText(`Z: ${minZ.toFixed(3)} to ${maxZ.toFixed(3)} m`, padding, canvas.height - padding + 27);
}

// Draw hull side view with current station marked
function drawHullSideView() {
    const canvas = document.getElementById('hullSideCanvas');
    if (!canvas || !hullDetails || !currentProfile) return;
    
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const curves = hullDetails.curves;
    if (!curves || curves.length === 0) {
        ctx.fillStyle = '#666';
        ctx.font = '11px Arial';
        ctx.fillText('No curves to display', canvas.width / 2 - 70, canvas.height / 2);
        return;
    }
    
    // Calculate bounds (X-Z plane for side view)
    let minX = Infinity, maxX = -Infinity;
    let minZ = Infinity, maxZ = -Infinity;
    
    curves.forEach(curve => {
        curve.points.forEach(p => {
            minX = Math.min(minX, p[0]);
            maxX = Math.max(maxX, p[0]);
            minZ = Math.min(minZ, p[2]);
            maxZ = Math.max(maxZ, p[2]);
        });
    });
    
    // Add padding
    const padding = 35;
    const drawWidth = canvas.width - 2 * padding;
    const drawHeight = canvas.height - 2 * padding;
    
    // Calculate scale
    const rangeX = maxX - minX || 1;
    const rangeZ = maxZ - minZ || 1;
    const scaleX = drawWidth / rangeX;
    const scaleZ = drawHeight / rangeZ;
    const scale = Math.min(scaleX, scaleZ) * 0.9;
    
    // Helper function to convert coords to canvas coords
    function toCanvas(x, z) {
        return {
            x: padding + (x - minX) * scale,
            y: canvas.height - padding - (z - minZ) * scale
        };
    }
    
    // Draw curves
    ctx.strokeStyle = '#007bff';
    ctx.lineWidth = 1.5;
    
    curves.forEach(curve => {
        if (!curve.points || curve.points.length === 0) return;
        
        ctx.beginPath();
        curve.points.forEach((point, idx) => {
            const coords = toCanvas(point[0], point[2]);
            if (idx === 0) {
                ctx.moveTo(coords.x, coords.y);
            } else {
                ctx.lineTo(coords.x, coords.y);
            }
        });
        ctx.stroke();
    });
    
    // Draw current station line
    const stationX = currentProfile.station;
    const stationCoords = toCanvas(stationX, minZ);
    const stationCoordsTop = toCanvas(stationX, maxZ);
    
    ctx.strokeStyle = '#dc3545';
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(stationCoords.x, stationCoords.y);
    ctx.lineTo(stationCoordsTop.x, stationCoordsTop.y);
    ctx.stroke();
    ctx.setLineDash([]);
    
    // Label for station
    ctx.fillStyle = '#dc3545';
    ctx.font = '9px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(`Station ${stationX.toFixed(3)}m`, stationCoords.x, stationCoords.y + 15);
    
    // Draw axes labels
    ctx.fillStyle = '#333';
    ctx.font = '10px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Stern ← X (Length) → Bow', canvas.width / 2, canvas.height - 8);
    
    ctx.save();
    ctx.translate(12, canvas.height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Height (Z)', 0, 0);
    ctx.restore();
}
