import { HullRenderer } from './webgl-renderer.js';

const API_BASE = window.location.origin;
let selectedKayak = null;
let hullDetails = null;
let currentView = 'iso';
let currentTab = 'visualization';
let stabilityData = null;
let resistanceData = null;
let notificationTimeout = null;
let hullRenderer = null;

// Notification functions
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    const messageEl = document.getElementById('notificationMessage');
    
    // Clear any existing timeout
    if (notificationTimeout) {
        clearTimeout(notificationTimeout);
    }
    
    // Set message and type
    messageEl.textContent = message;
    notification.className = 'notification show ' + type;
    
    // Auto-hide after 10 seconds
    notificationTimeout = setTimeout(() => {
        closeNotification();
    }, 10000);
}

function closeNotification() {
    const notification = document.getElementById('notification');
    notification.classList.remove('show');
    
    if (notificationTimeout) {
        clearTimeout(notificationTimeout);
        notificationTimeout = null;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadKayakList();
    setupCanvas();
    setupStabilityCanvas();
    document.getElementById('viewSelect').addEventListener('change', (e) => {
        currentView = e.target.value;
        if (hullRenderer) {
            hullRenderer.setCameraPreset(currentView);
        }
    });
    
    document.getElementById('qualitySelect').addEventListener('change', (e) => {
        if (hullRenderer) {
            hullRenderer.setQuality(e.target.value);
        }
    });
    
    // Rendering mode selector
    document.getElementById('renderModeSelect').addEventListener('change', (e) => {
        if (hullRenderer) {
            const mode = e.target.value;
            
            // Map rendering modes to settings
            const modeSettings = {
                surface: {
                    showSurface: true,
                    showWireframe: false,
                    showCurves: false,
                    showProfiles: false,
                    showMeasurements: false
                },
                wireframe: {
                    showSurface: false,
                    showWireframe: true,
                    showCurves: false,
                    showProfiles: false,
                    showMeasurements: false
                },
                both: {
                    showSurface: true,
                    showWireframe: true,
                    showCurves: false,
                    showProfiles: false,
                    showMeasurements: false
                },
                technical: {
                    showSurface: true,
                    showWireframe: true,
                    showCurves: true,
                    showProfiles: true,
                    showMeasurements: true
                }
            };
            
            const settings = modeSettings[mode];
            if (settings) {
                hullRenderer.updateSettings(settings);
                
                // Update checkbox UI to reflect mode
                document.getElementById('showWireframe').checked = settings.showWireframe;
                document.getElementById('showCurves').checked = settings.showCurves;
                document.getElementById('showProfiles').checked = settings.showProfiles;
                document.getElementById('showMeasurements').checked = settings.showMeasurements;
            }
        }
    });
    
    // Setup visualization toggles
    document.getElementById('showWireframe').addEventListener('change', (e) => {
        if (hullRenderer) {
            hullRenderer.updateSettings({ showWireframe: e.target.checked });
        }
    });
    
    document.getElementById('showWaterline').addEventListener('change', (e) => {
        if (hullRenderer) {
            hullRenderer.updateSettings({ showWaterline: e.target.checked });
        }
    });
    
    document.getElementById('showCurves').addEventListener('change', (e) => {
        if (hullRenderer) {
            hullRenderer.updateSettings({ showCurves: e.target.checked });
        }
    });
    
    document.getElementById('showProfiles').addEventListener('change', (e) => {
        if (hullRenderer) {
            hullRenderer.updateSettings({ showProfiles: e.target.checked });
        }
    });
    
    document.getElementById('showMeasurements').addEventListener('change', (e) => {
        if (hullRenderer) {
            hullRenderer.updateSettings({ showMeasurements: e.target.checked });
        }
    });
    
    document.getElementById('showShadows').addEventListener('change', (e) => {
        if (hullRenderer) {
            hullRenderer.updateSettings({ showShadows: e.target.checked });
        }
    });
    
    document.getElementById('showFPS').addEventListener('change', (e) => {
        if (hullRenderer) {
            hullRenderer.updateSettings({ showFPS: e.target.checked });
        }
        // Show/hide FPS display element
        const fpsDisplay = document.getElementById('fpsDisplay');
        if (fpsDisplay) {
            fpsDisplay.style.display = e.target.checked ? 'block' : 'none';
        }
    });
    
    // Setup modal event handlers
    const controlsModal = document.getElementById('controlsModal');
    const controlsInfoBtn = document.getElementById('controlsInfoBtn');
    const closeControlsModal = document.getElementById('closeControlsModal');
    
    controlsInfoBtn.addEventListener('click', () => {
        controlsModal.style.display = 'flex';
    });
    
    closeControlsModal.addEventListener('click', () => {
        controlsModal.style.display = 'none';
    });
    
    // Close modal when clicking outside the content
    controlsModal.addEventListener('click', (e) => {
        if (e.target === controlsModal) {
            controlsModal.style.display = 'none';
        }
    });
    
    // Setup form submission handlers
    document.getElementById('createHullForm').addEventListener('submit', handleCreateHull);
    document.getElementById('editHullForm').addEventListener('submit', handleEditHull);
    document.getElementById('stabilityForm').addEventListener('submit', handleStabilityAnalysis);
    document.getElementById('resistanceForm').addEventListener('submit', handleResistanceAnalysis);
    
    // Setup keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Don't trigger shortcuts if user is typing in an input field
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
            return;
        }
        
        if (!hullRenderer) return;
        
        switch(e.key.toLowerCase()) {
            case '1':
                document.getElementById('viewSelect').value = 'iso';
                hullRenderer.setCameraPreset('iso');
                break;
            case '2':
                document.getElementById('viewSelect').value = 'side';
                hullRenderer.setCameraPreset('side');
                break;
            case '3':
                document.getElementById('viewSelect').value = 'top';
                hullRenderer.setCameraPreset('top');
                break;
            case '4':
                document.getElementById('viewSelect').value = 'front';
                hullRenderer.setCameraPreset('front');
                break;
            case 'w':
                const wireframeCheckbox = document.getElementById('showWireframe');
                wireframeCheckbox.checked = !wireframeCheckbox.checked;
                hullRenderer.updateSettings({ showWireframe: wireframeCheckbox.checked });
                break;
            case 'c':
                const curvesCheckbox = document.getElementById('showCurves');
                curvesCheckbox.checked = !curvesCheckbox.checked;
                hullRenderer.updateSettings({ showCurves: curvesCheckbox.checked });
                break;
            case 'p':
                const profilesCheckbox = document.getElementById('showProfiles');
                profilesCheckbox.checked = !profilesCheckbox.checked;
                hullRenderer.updateSettings({ showProfiles: profilesCheckbox.checked });
                break;
            case 'm':
                const measurementsCheckbox = document.getElementById('showMeasurements');
                measurementsCheckbox.checked = !measurementsCheckbox.checked;
                hullRenderer.updateSettings({ showMeasurements: measurementsCheckbox.checked });
                break;
        }
    });
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
                    <div class="kayak-item-actions">
                        <button class="edit-btn" onclick="event.stopPropagation(); openEditModal('${kayak.name}')" title="Edit kayak">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                                <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"/>
                            </svg>
                        </button>
                        <button class="delete-btn" onclick="event.stopPropagation(); openDeleteModal('${kayak.name}')" title="Delete kayak">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                                <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                                <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                            </svg>
                        </button>
                    </div>
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
        
        // Draw hull
        drawHull(hullDetails);
        
        // Initialize profiles
        initializeProfiles(hullDetails);
        
        // Populate stability form with hull values
        populateStabilityForm(hullDetails);
        
        // Populate resistance form
        populateResistanceForm(hullDetails);
        
    } catch (error) {
        console.error('Error loading hull details:', error);
        showNotification(`Error loading hull: ${error.message}`, 'error');
        // Clear the visualization
        if (hullRenderer) {
            hullRenderer.clearHull();
        }
    }
}

// Populate stability form with hull values
function populateStabilityForm(hull) {
    // Populate paddler weight from target_payload
    if (hull.target_payload !== null && hull.target_payload !== undefined) {
        document.getElementById('paddlerWeight').value = hull.target_payload;
    }
    
    // Populate hull weight from target_weight
    if (hull.target_weight !== null && hull.target_weight !== undefined) {
        document.getElementById('hullWeight').value = hull.target_weight;
    }
    
    // Set default values (these are already in HTML but let's ensure they're set)
    if (!document.getElementById('paddlerCgZ').value) {
        document.getElementById('paddlerCgZ').value = '0.25';
    }
    
    if (!document.getElementById('angleStep').value) {
        document.getElementById('angleStep').value = '3';
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
    
    let mainProfilesHtml = '<h3 style="margin-top: 10px;">Main Profiles:</h3>';
    if (hull.main_profiles && hull.main_profiles.length > 0) {
        mainProfilesHtml += '<div style="max-height: 200px; overflow-y: auto;">';
        hull.main_profiles.forEach((profile, idx) => {
            const profileId = `main-profile-${idx}`;
            mainProfilesHtml += `
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
        mainProfilesHtml += '</div>';
        mainProfilesHtml += '<p style="font-size: 10px; color: #666; margin-top: 5px; font-style: italic;">Shown in green on visualization</p>';
    } else {
        mainProfilesHtml += '<p style="font-size: 11px; color: #666;">No main profiles</p>';
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
            ${mainProfilesHtml}
        </div>
    `;
}

// Setup canvas
function setupCanvas() {
    // Use the visualization tab container, not the entire canvas-container
    const container = document.getElementById('visualization-tab');
    
    // Try to initialize WebGL renderer
    if (!hullRenderer) {
        hullRenderer = new HullRenderer(container);
        const initialized = hullRenderer.init();
        
        if (!initialized) {
            console.error('Failed to initialize WebGL renderer');
            showNotification('WebGL not supported. Please use a modern browser.', 'error');
            
            // Show WebGL warning in legend
            const webglWarning = document.getElementById('webglWarning');
            if (webglWarning) {
                webglWarning.style.display = 'block';
            }
            
            // Disable visualization controls
            const controls = [
                'viewSelect', 'qualitySelect', 'renderModeSelect',
                'showWireframe', 'showWaterline', 'showCurves', 
                'showProfiles', 'showMeasurements', 'showShadows', 'showFPS'
            ];
            controls.forEach(id => {
                const element = document.getElementById(id);
                if (element) element.disabled = true;
            });
            
            return;
        }
        
        // Hide WebGL warning (only shown if WebGL fails)
        const webglWarning = document.getElementById('webglWarning');
        if (webglWarning) {
            webglWarning.style.display = 'none';
        }
        
        // Handle window resize
        window.addEventListener('resize', () => {
            if (hullRenderer) {
                hullRenderer.resize();
            }
        });
    }
}

// Draw hull using WebGL renderer
function drawHull(hull) {
    if (!hullRenderer) {
        console.error('Hull renderer not initialized');
        return;
    }
    
    if (!hull || !hull.main_profiles || hull.main_profiles.length === 0) {
        console.warn('No hull data to display');
        return;
    }
    
    // Render hull using WebGL
    hullRenderer.renderHull(hull);
}

// Modal functions
function openCreateModal() {
    document.getElementById('createModal').classList.add('show');
}

let editingKayakName = null;

async function openEditModal(kayakName) {
    editingKayakName = kayakName;
    
    try {
        // Fetch full hull details
        const response = await fetch(`${API_BASE}/hulls/${kayakName}`);
        if (!response.ok) throw new Error('Failed to load kayak details');
        
        const hull = await response.json();
        
        // Populate form fields
        document.getElementById('editHullName').value = hull.name || '';
        document.getElementById('editHullDescription').value = hull.description || '';
        document.getElementById('editTargetWaterline').value = hull.target_waterline || '';
        document.getElementById('editTargetPayload').value = hull.target_payload || '';
        document.getElementById('editTargetWeight').value = hull.target_weight || '';
        
        // Format curves to textarea
        const curvesText = formatCurvesToText(hull.curves);
        document.getElementById('editCurvesData').value = curvesText;
        
        // Show modal
        document.getElementById('editModal').classList.add('show');
        
    } catch (error) {
        console.error('Error loading kayak for edit:', error);
        alert(`Error loading kayak: ${error.message}`);
    }
}

function formatCurvesToText(curves) {
    if (!curves || curves.length === 0) return '';
    
    let text = '';
    // Filter out mirrored curves - keep only originals
    const originalCurves = curves.filter(curve => curve.mirrored !== true);
    
    // Deduplicate by curve name and points - keep only first occurrence
    const seen = new Map();
    const uniqueCurves = [];
    
    originalCurves.forEach(curve => {
        // Create a key based on curve name and points
        const pointsKey = curve.points.map(p => `${p[0].toFixed(2)},${p[1].toFixed(2)},${p[2].toFixed(2)}`).join('|');
        const key = `${curve.name}:${pointsKey}`;
        
        if (!seen.has(key)) {
            seen.set(key, true);
            uniqueCurves.push(curve);
        }
    });
    
    uniqueCurves.forEach((curve, idx) => {
        text += `curve: ${curve.name}\n`;
        curve.points.forEach(point => {
            // Format to 2 decimals with space after commas
            text += `${point[0].toFixed(2)}, ${point[1].toFixed(2)}, ${point[2].toFixed(2)}\n`;
        });
        // Add blank line between curves except after last one
        if (idx < uniqueCurves.length - 1) {
            text += '\n';
        }
    });
    
    return text;
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
    const modal = document.getElementById('createModal');
    const form = document.getElementById('createHullForm');
    
    // Reset button state
    const submitBtn = form.querySelector('.btn-primary');
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create Kayak';
    }
    
    modal.classList.remove('show');
    form.reset();
    
    // Refresh the kayak list when modal closes
    loadKayakList();
}

function closeEditModal() {
    const modal = document.getElementById('editModal');
    const form = document.getElementById('editHullForm');
    
    // Reset button state
    const submitBtn = form.querySelector('.btn-primary');
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Update Kayak';
    }
    
    modal.classList.remove('show');
    form.reset();
    editingKayakName = null;
    
    // Refresh the kayak list when modal closes
    loadKayakList();
}

// Close modal when clicking outside
window.addEventListener('click', (event) => {
    const createModal = document.getElementById('createModal');
    const editModal = document.getElementById('editModal');
    const deleteModal = document.getElementById('deleteModal');
    
    if (event.target === createModal) {
        closeCreateModal();
    }
    if (event.target === editModal) {
        closeEditModal();
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
            // Clear WebGL visualization
            if (hullRenderer) {
                hullRenderer.clearHull();
            }
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
    
    const submitBtn = e.target.querySelector('.btn-primary');
    let success = false;
    
    try {
        // Get form values
        const name = document.getElementById('hullName').value.trim();
        const description = document.getElementById('hullDescription').value.trim() || null;
        const targetWaterline = document.getElementById('targetWaterline').value;
        const targetPayload = document.getElementById('targetPayload').value;
        const targetWeight = document.getElementById('targetWeight').value;
        const curvesText = document.getElementById('curvesData').value;
        
        // Parse curves
        const curves = parseCurvesData(curvesText);
        
        if (curves.length === 0) {
            showNotification('Please enter at least one curve with points', 'error');
            return;
        }
        
        // Build request body
        const requestBody = {
            name: name,
            description: description,
            target_waterline: targetWaterline ? parseFloat(targetWaterline) : null,
            target_payload: targetPayload ? parseFloat(targetPayload) : null,
            target_weight: targetWeight ? parseFloat(targetWeight) : null,
            curves: curves
        };
        
        // Show loading state
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
            let errorMessage = 'Failed to create kayak';
            try {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } else {
                    const errorText = await response.text();
                    errorMessage = `Server error (${response.status}): ${errorText.substring(0, 100)}`;
                }
            } catch (e) {
                errorMessage = `Server error (${response.status})`;
            }
            throw new Error(errorMessage);
        }
        
        const result = await response.json();
        
        success = true;
        
        // Show success notification
        showNotification(`Kayak "${name}" created successfully!`, 'success');
        
        // Close modal (this will refresh the list automatically)
        closeCreateModal();
        
    } catch (error) {
        console.error('Error creating kayak:', error);
        showNotification(`Error creating kayak: ${error.message}`, 'error');
    } finally {
        // Always restore button if creation wasn't successful
        if (!success && submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Create Kayak';
        }
    }
}

// Handle edit form submission
async function handleEditHull(e) {
    e.preventDefault();
    
    if (!editingKayakName) {
        showNotification('No kayak selected for editing', 'error');
        return;
    }
    
    const submitBtn = e.target.querySelector('.btn-primary');
    let success = false;
    
    try {
        // Get form values
        const name = document.getElementById('editHullName').value.trim();
        const description = document.getElementById('editHullDescription').value.trim() || null;
        const targetWaterline = document.getElementById('editTargetWaterline').value;
        const targetPayload = document.getElementById('editTargetPayload').value;
        const targetWeight = document.getElementById('editTargetWeight').value;
        const curvesText = document.getElementById('editCurvesData').value;
        
        // Parse curves
        const curves = parseCurvesData(curvesText);
        
        if (curves.length === 0) {
            showNotification('Please enter at least one curve with points', 'error');
            return;
        }
        
        // Build request body
        const requestBody = {
            name: name,
            description: description,
            target_waterline: targetWaterline ? parseFloat(targetWaterline) : null,
            target_payload: targetPayload ? parseFloat(targetPayload) : null,
            target_weight: targetWeight ? parseFloat(targetWeight) : null,
            curves: curves
        };
        
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.textContent = 'Updating...';
        
        // Make PUT request
        const response = await fetch(`${API_BASE}/hulls/${editingKayakName}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            let errorMessage = 'Failed to update kayak';
            try {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } else {
                    const errorText = await response.text();
                    console.error('Error response text:', errorText);
                    errorMessage = `Server error (${response.status}): ${errorText.substring(0, 100)}`;
                }
            } catch (e) {
                console.error('Error parsing error response:', e);
                errorMessage = `Server error (${response.status})`;
            }
            throw new Error(errorMessage);
        }
        
        const result = await response.json();
        
        success = true;
        
        // Show success notification
        showNotification(`Kayak "${name}" updated successfully!`, 'success');
        
        // If the updated kayak was selected, reload its details
        if (selectedKayak && selectedKayak.name === editingKayakName) {
            selectedKayak = result;
            hullDetails = null;
            loadHullDetailsForVisualization();
        }
        
        // Close modal (this will refresh the list automatically)
        closeEditModal();
        
    } catch (error) {
        console.error('Error updating kayak:', error);
        showNotification(`Error updating kayak: ${error.message}`, 'error');
    } finally {
        // Always restore button if update wasn't successful
        if (!success && submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Update Kayak';
        }
    }
}

// Tab switching function
function switchTab(tabName) {
    currentTab = tabName;
    
    // Update tab buttons by checking the onclick text
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
        // Check if this button's onclick contains the current tabName
        const onclickAttr = btn.getAttribute('onclick');
        if (onclickAttr && onclickAttr.includes(`'${tabName}'`)) {
            btn.classList.add('active');
        }
    });
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Redraw content when switching to relevant tabs
    if (tabName === 'visualization' && hullDetails) {
        // WebGL renderer is already initialized, just redraw
        drawHull(hullDetails);
    } else if (tabName === 'stability' && stabilityData) {
        setupStabilityCanvas();
        drawStabilityResults(stabilityData);
    } else if (tabName === 'resistance' && resistanceData) {
        setupResistanceCanvas();
        drawResistanceResults(resistanceData);
    } else if (tabName === 'profiles' && currentProfile) {
        // Defer drawing until browser completes layout (canvas needs dimensions)
        requestAnimationFrame(() => {
            drawProfile();
            drawHullSideView();
        });
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
        const breakOnVanishing = document.getElementById('breakOnVanishing').checked;
        
        // Build request body
        const requestBody = {
            hull_name: selectedKayak.name,
            paddler_weight: paddlerWeight ? parseFloat(paddlerWeight) : null,
            paddler_cg_z: parseFloat(paddlerCgZ),
            hull_weight: hullWeight ? parseFloat(hullWeight) : null,
            max_angle: parseFloat(maxAngle),
            step: parseFloat(angleStep),
            break_on_vanishing: breakOnVanishing
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

// ========== RESISTANCE TAB ==========

// Populate resistance form (no hull-specific values needed, but could add presets)
function populateResistanceForm(hull) {
    // Form already has default values, but we could add logic here
    // For example, adjust max speed based on hull length
    // For now, keeping defaults
}

// Setup resistance canvas
function setupResistanceCanvas() {
    const resistanceCanvas = document.getElementById('resistanceCanvas');
    const powerCanvas = document.getElementById('powerCanvas');
    if (!resistanceCanvas || !powerCanvas) return;
    
    const container = resistanceCanvas.closest('.resistance-graphs');
    
    // Resize canvases to fit container
    function resizeCanvas() {
        if (!container) return;
        const rect = container.getBoundingClientRect();
        
        // Each canvas gets half the width minus gap
        const canvasWidth = (rect.width - 15) / 2 - 20; // 15px gap, some padding
        const canvasHeight = Math.max(400, rect.height - 80); // Account for title
        
        resistanceCanvas.width = canvasWidth;
        resistanceCanvas.height = canvasHeight;
        powerCanvas.width = canvasWidth;
        powerCanvas.height = canvasHeight;
        
        if (resistanceData) {
            drawResistanceResults(resistanceData);
        }
    }
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
}

// Handle resistance analysis form submission
async function handleResistanceAnalysis(e) {
    e.preventDefault();
    
    if (!selectedKayak) {
        alert('Please select a kayak first');
        return;
    }
    
    try {
        // Get form values
        const minSpeed = parseFloat(document.getElementById('minSpeed').value);
        const maxSpeed = parseFloat(document.getElementById('maxSpeed').value);
        const speedStep = parseFloat(document.getElementById('speedStep').value);
        const waterType = document.getElementById('waterType').value;
        const roughnessAllowance = parseFloat(document.getElementById('roughnessAllowance').value);
        const propulsionEfficiency = parseFloat(document.getElementById('propulsionEfficiency').value);
        
        // Validate inputs
        if (minSpeed < 0) {
            alert('Minimum speed must be non-negative');
            return;
        }
        if (maxSpeed <= minSpeed) {
            alert('Maximum speed must be greater than minimum speed');
            return;
        }
        if (speedStep <= 0) {
            alert('Speed step must be positive');
            return;
        }
        
        // Build request body
        const requestBody = {
            hull_name: selectedKayak.name,
            min_speed: minSpeed,
            max_speed: maxSpeed,
            speed_step: speedStep,
            water_type: waterType,
            roughness_allowance: roughnessAllowance,
            propulsion_efficiency: propulsionEfficiency
        };
        
        // Hide form and results, show loader
        document.querySelector('.resistance-form-container').style.display = 'none';
        document.getElementById('resistanceResults').classList.remove('show');
        document.getElementById('resistanceLoader').classList.add('show');
        
        // Make POST request
        const response = await fetch(`${API_BASE}/hulls/${selectedKayak.name}/resistance`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to analyze resistance');
        }
        
        resistanceData = await response.json();
        
        // Hide loader, show results
        document.getElementById('resistanceLoader').classList.remove('show');
        document.getElementById('resistanceResults').classList.add('show');
        
        // Populate summary parameters
        populateResistanceParameters(resistanceData);
        
        // Draw results
        setupResistanceCanvas();
        drawResistanceResults(resistanceData);
        
    } catch (error) {
        console.error('Error analyzing resistance:', error);
        alert(`Error analyzing resistance: ${error.message}`);
        
        // Hide loader, show form
        document.getElementById('resistanceLoader').classList.remove('show');
        document.querySelector('.resistance-form-container').style.display = 'block';
    }
}

// Populate resistance parameters summary
function populateResistanceParameters(data) {
    document.getElementById('paramWaterlineLength').textContent = 
        data.waterline_length ? `${data.waterline_length.toFixed(3)} m` : 'N/A';
    document.getElementById('paramWaterlineBeam').textContent = 
        data.waterline_beam ? `${data.waterline_beam.toFixed(3)} m` : 'N/A';
    document.getElementById('paramWettedSurface').textContent = 
        data.wetted_surface ? `${data.wetted_surface.toFixed(3)} m²` : 'N/A';
    document.getElementById('paramHullSpeed').textContent = 
        data.hull_speed_kmh ? `${data.hull_speed_kmh.toFixed(2)} km/h (${data.hull_speed_knots.toFixed(2)} kn)` : 'N/A';
    document.getElementById('paramBlockCoeff').textContent = 
        data.block_coefficient ? data.block_coefficient.toFixed(3) : 'N/A';
    document.getElementById('paramPrismaticCoeff').textContent = 
        data.prismatic_coefficient ? data.prismatic_coefficient.toFixed(3) : 'N/A';
}

// Draw resistance results on canvas
function drawResistanceResults(data) {
    const resistanceCanvas = document.getElementById('resistanceCanvas');
    const powerCanvas = document.getElementById('powerCanvas');
    if (!resistanceCanvas || !powerCanvas) return;
    
    if (!data.resistance_points || data.resistance_points.length === 0) {
        const ctx = resistanceCanvas.getContext('2d');
        ctx.fillStyle = '#666';
        ctx.font = '14px Arial';
        ctx.fillText('No resistance data to display', resistanceCanvas.width / 2 - 100, resistanceCanvas.height / 2);
        return;
    }
    
    const points = data.resistance_points;
    
    // Draw resistance graph
    drawResistanceGraph(resistanceCanvas, points, data);
    
    // Draw power graph
    drawPowerGraph(powerCanvas, points, data);
    
    // Add button to go back to form
    addResistanceBackButton();
}

// Draw resistance vs speed graph
function drawResistanceGraph(canvas, points, data) {
    const ctx = canvas.getContext('2d');
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Calculate bounds (convert to km/h for display)
    const maxSpeed = Math.max(...points.map(p => p.speed_kmh));
    const maxResistance = Math.max(...points.map(p => p.total_resistance));
    
    // Drawing parameters
    const padding = 60;
    const graphWidth = canvas.width - 2 * padding;
    const graphHeight = canvas.height - 2 * padding - 40; // Space for legend
    
    // Scale factors
    const scaleX = graphWidth / maxSpeed;
    const scaleY = graphHeight / maxResistance;
    const zeroY = padding + graphHeight;
    
    // Draw axes
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding, zeroY);
    ctx.lineTo(padding + graphWidth, zeroY);
    ctx.stroke();
    
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, zeroY);
    ctx.stroke();
    
    // Draw grid
    ctx.strokeStyle = '#ddd';
    ctx.lineWidth = 1;
    
    // Vertical grid lines (speed in km/h)
    const speedStep = maxSpeed > 20 ? 5 : 2;
    for (let speed = 0; speed <= maxSpeed; speed += speedStep) {
        const x = padding + speed * scaleX;
        ctx.beginPath();
        ctx.moveTo(x, padding);
        ctx.lineTo(x, zeroY);
        ctx.stroke();
        
        // Label
        ctx.fillStyle = '#333';
        ctx.font = '11px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(speed.toFixed(0), x, zeroY + 15);
    }
    
    // Horizontal grid lines (resistance in N)
    const resistanceStep = maxResistance / 8;
    for (let i = 0; i <= 8; i++) {
        const resistance = i * resistanceStep;
        const y = zeroY - resistance * scaleY;
        ctx.strokeStyle = '#ddd';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(padding + graphWidth, y);
        ctx.stroke();
        
        // Label
        ctx.fillStyle = '#333';
        ctx.font = '11px Arial';
        ctx.textAlign = 'right';
        ctx.fillText(resistance.toFixed(1), padding - 5, y + 4);
    }
    
    // Axis labels
    ctx.fillStyle = '#000';
    ctx.font = 'bold 12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Speed (km/h)', canvas.width / 2, canvas.height - 5);
    
    ctx.save();
    ctx.translate(15, canvas.height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Resistance (N)', 0, 0);
    ctx.restore();
    
    // Draw total resistance curve
    ctx.strokeStyle = '#007bff';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    points.forEach((point, idx) => {
        const x = padding + point.speed_kmh * scaleX;
        const y = zeroY - point.total_resistance * scaleY;
        if (idx === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    ctx.stroke();
    
    // Draw frictional resistance curve
    ctx.strokeStyle = '#28a745';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([5, 3]);
    ctx.beginPath();
    points.forEach((point, idx) => {
        const x = padding + point.speed_kmh * scaleX;
        const y = zeroY - point.frictional_resistance * scaleY;
        if (idx === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    ctx.stroke();
    
    // Draw residuary resistance curve
    ctx.strokeStyle = '#ffc107';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([2, 2]);
    ctx.beginPath();
    points.forEach((point, idx) => {
        const x = padding + point.speed_kmh * scaleX;
        const y = zeroY - point.residuary_resistance * scaleY;
        if (idx === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    ctx.stroke();
    ctx.setLineDash([]);
    
    // Draw hull speed line (if available)
    if (data.hull_speed_kmh) {
        const hullSpeedX = padding + data.hull_speed_kmh * scaleX;
        ctx.strokeStyle = '#dc3545';
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.moveTo(hullSpeedX, padding);
        ctx.lineTo(hullSpeedX, zeroY);
        ctx.stroke();
        ctx.setLineDash([]);
        
        // Label
        ctx.fillStyle = '#dc3545';
        ctx.font = '10px Arial';
        ctx.textAlign = 'left';
        ctx.fillText('Hull Speed', hullSpeedX + 3, padding + 15);
    }
    
    // Legend
    const legendY = canvas.height - 25;
    const legendItems = [
        { color: '#007bff', label: 'Total', dash: [] },
        { color: '#28a745', label: 'Frictional', dash: [5, 3] },
        { color: '#ffc107', label: 'Residuary', dash: [2, 2] }
    ];
    
    let legendX = padding;
    legendItems.forEach(item => {
        ctx.strokeStyle = item.color;
        ctx.lineWidth = 2;
        ctx.setLineDash(item.dash);
        ctx.beginPath();
        ctx.moveTo(legendX, legendY);
        ctx.lineTo(legendX + 30, legendY);
        ctx.stroke();
        ctx.setLineDash([]);
        
        ctx.fillStyle = '#333';
        ctx.font = '11px Arial';
        ctx.textAlign = 'left';
        ctx.fillText(item.label, legendX + 35, legendY + 4);
        
        legendX += 100;
    });
}

// Draw power vs speed graph
function drawPowerGraph(canvas, points, data) {
    const ctx = canvas.getContext('2d');
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Calculate bounds (convert to km/h for display)
    const maxSpeed = Math.max(...points.map(p => p.speed_kmh));
    const maxPower = Math.max(...points.map(p => p.paddler_power));
    
    // Drawing parameters
    const padding = 60;
    const graphWidth = canvas.width - 2 * padding;
    const graphHeight = canvas.height - 2 * padding - 40; // Space for legend
    
    // Scale factors
    const scaleX = graphWidth / maxSpeed;
    const scaleY = graphHeight / maxPower;
    const zeroY = padding + graphHeight;
    
    // Draw axes
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding, zeroY);
    ctx.lineTo(padding + graphWidth, zeroY);
    ctx.stroke();
    
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, zeroY);
    ctx.stroke();
    
    // Draw grid
    ctx.strokeStyle = '#ddd';
    ctx.lineWidth = 1;
    
    // Vertical grid lines (speed in km/h)
    const speedStep = maxSpeed > 20 ? 5 : 2;
    for (let speed = 0; speed <= maxSpeed; speed += speedStep) {
        const x = padding + speed * scaleX;
        ctx.beginPath();
        ctx.moveTo(x, padding);
        ctx.lineTo(x, zeroY);
        ctx.stroke();
        
        // Label
        ctx.fillStyle = '#333';
        ctx.font = '11px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(speed.toFixed(0), x, zeroY + 15);
    }
    
    // Horizontal grid lines (power in W)
    const powerStep = maxPower / 8;
    for (let i = 0; i <= 8; i++) {
        const power = i * powerStep;
        const y = zeroY - power * scaleY;
        ctx.strokeStyle = '#ddd';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(padding + graphWidth, y);
        ctx.stroke();
        
        // Label
        ctx.fillStyle = '#333';
        ctx.font = '11px Arial';
        ctx.textAlign = 'right';
        ctx.fillText(power.toFixed(0), padding - 5, y + 4);
    }
    
    // Axis labels
    ctx.fillStyle = '#000';
    ctx.font = 'bold 12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Speed (km/h)', canvas.width / 2, canvas.height - 5);
    
    ctx.save();
    ctx.translate(15, canvas.height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Power (W)', 0, 0);
    ctx.restore();
    
    // Draw paddler power curve
    ctx.strokeStyle = '#6f42c1';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    points.forEach((point, idx) => {
        const x = padding + point.speed_kmh * scaleX;
        const y = zeroY - point.paddler_power * scaleY;
        if (idx === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    ctx.stroke();
    
    // Draw effective power curve
    ctx.strokeStyle = '#17a2b8';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([5, 3]);
    ctx.beginPath();
    points.forEach((point, idx) => {
        const x = padding + point.speed_kmh * scaleX;
        const y = zeroY - point.effective_power * scaleY;
        if (idx === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    ctx.stroke();
    ctx.setLineDash([]);
    
    // Draw hull speed line (if available)
    if (data.hull_speed_kmh) {
        const hullSpeedX = padding + data.hull_speed_kmh * scaleX;
        ctx.strokeStyle = '#dc3545';
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.moveTo(hullSpeedX, padding);
        ctx.lineTo(hullSpeedX, zeroY);
        ctx.stroke();
        ctx.setLineDash([]);
        
        // Label
        ctx.fillStyle = '#dc3545';
        ctx.font = '10px Arial';
        ctx.textAlign = 'left';
        ctx.fillText('Hull Speed', hullSpeedX + 3, padding + 15);
    }
    
    // Legend
    const legendY = canvas.height - 25;
    const legendItems = [
        { color: '#6f42c1', label: 'Paddler Power', dash: [] },
        { color: '#17a2b8', label: 'Effective Power', dash: [5, 3] }
    ];
    
    let legendX = padding;
    legendItems.forEach(item => {
        ctx.strokeStyle = item.color;
        ctx.lineWidth = 2;
        ctx.setLineDash(item.dash);
        ctx.beginPath();
        ctx.moveTo(legendX, legendY);
        ctx.lineTo(legendX + 30, legendY);
        ctx.stroke();
        ctx.setLineDash([]);
        
        ctx.fillStyle = '#333';
        ctx.font = '11px Arial';
        ctx.textAlign = 'left';
        ctx.fillText(item.label, legendX + 35, legendY + 4);
        
        legendX += 140;
    });
}

// Add back button for resistance analysis
function addResistanceBackButton() {
    // Check if button already exists
    if (document.getElementById('resistanceBackBtn')) return;
    
    const resultsDiv = document.getElementById('resistanceResults');
    const button = document.createElement('button');
    button.id = 'resistanceBackBtn';
    button.textContent = '← Back to Form';
    button.className = 'btn-secondary';
    button.style.marginTop = '10px';
    button.onclick = () => {
        document.getElementById('resistanceResults').classList.remove('show');
        document.querySelector('.resistance-form-container').style.display = 'block';
    };
    resultsDiv.insertBefore(button, resultsDiv.firstChild);
}

// ========== PROFILES TAB ==========

let currentProfile = null;
let beam = null;
let depth = null;
let length = null;

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
        option.textContent = `Station ${profile.station.toFixed(2)} m`;
        stationSelect.appendChild(option);
    });
    
    beam = hull.beam || null;
    depth = hull.depth || null;
    length = hull.length || null;
    // Setup canvases
    setupProfileCanvases();
    
    // Select first profile
    if (hull.profiles.length > 0) {
        stationSelect.value = '0';
        selectStation();
    }
}

// Setup profile canvases - only handles window resize listener
// Canvas sizing is handled dynamically by ensureCanvasSize() before each draw
function setupProfileCanvases() {
    function onResize() {
        if (currentProfile !== null) {
            drawProfile();
            drawHullSideView();
        }
    }
    
    window.addEventListener('resize', onResize);
}

// Change profile by offset (e.g., -1, +1, -10, +10)
function changeProfile(offset) {
    const stationSelect = document.getElementById('stationSelect');
    const currentIdx = parseInt(stationSelect.value);
    
    if (isNaN(currentIdx) || !hullDetails || !hullDetails.profiles) return;
    
    const newIdx = currentIdx + offset;
    const maxIdx = hullDetails.profiles.length - 1;
    
    // Check bounds
    if (newIdx < 0 || newIdx > maxIdx) return;
    
    // Update selector and draw
    stationSelect.value = newIdx.toString();
    selectStation();
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
    
    // Update navigation button states
    updateNavButtons();
    
    // Only draw if profiles tab is active
    if (currentTab === 'profiles') {
        drawProfile();
        drawHullSideView();
    }
}

// Update navigation button states based on current position
function updateNavButtons() {
    if (!hullDetails || !hullDetails.profiles) return;
    
    const stationSelect = document.getElementById('stationSelect');
    const currentIdx = parseInt(stationSelect.value);
    
    if (isNaN(currentIdx)) return;
    
    const maxIdx = hullDetails.profiles.length - 1;
    
    // Get all nav buttons
    const navButtons = document.querySelectorAll('.nav-btn');
    if (navButtons.length !== 4) return;
    
    const [btn10Left, btn1Left, btn1Right, btn10Right] = navButtons;
    
    // Update button states
    btn10Left.disabled = (currentIdx - 10) < 0;
    btn1Left.disabled = (currentIdx - 1) < 0;
    btn1Right.disabled = (currentIdx + 1) > maxIdx;
    btn10Right.disabled = (currentIdx + 10) > maxIdx;
}

// Ensure canvas is properly sized
function ensureCanvasSize(canvas) {
    if (!canvas) return false;
    const rect = canvas.getBoundingClientRect();
    if (rect.width > 0 && rect.height > 0) {
        // Only update if different to avoid unnecessary redraws
        if (canvas.width !== Math.floor(rect.width) || canvas.height !== Math.floor(rect.height)) {
            canvas.width = Math.floor(rect.width);
            canvas.height = Math.floor(rect.height);
        }
        return true;
    }
    return false;
}

// Draw the current profile cross-section
function drawProfile() {
    const canvas = document.getElementById('profileCanvas');
    if (!canvas || !currentProfile) return;
    
    // Ensure canvas is properly sized before drawing
    if (!ensureCanvasSize(canvas)) {
        console.warn('Canvas not ready for drawing');
        return;
    }
    
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
    const minY = -beam / 2 
    const maxY = beam / 2 
    const minZ = 0 
    const maxZ = depth 
    // Add padding
    const padding = 40;
    const drawWidth = canvas.width - 2 * padding;
    const drawHeight = canvas.height - 2 * padding;
    
    // Calculate scale using fixed beam and depth for all profiles
    // This ensures all profiles are drawn at the same scale for comparison
    const rangeY = beam;  // Full beam width (already maxY - minY)
    const rangeZ = depth; // Full depth (already maxZ - minZ)
    
    // Calculate scale for each dimension and use the most restrictive
    const scaleY = drawWidth / rangeY;
    const scaleZ = drawHeight / rangeZ;
    const scale = Math.min(scaleY, scaleZ) * 0.50;
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
    
    // Ensure canvas is properly sized before drawing
    if (!ensureCanvasSize(canvas)) {
        console.warn('Hull side canvas not ready for drawing');
        return;
    }
    
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
    const minX = 0;
    const maxX = length;
    const minZ = 0;
    const maxZ = depth;
    
    // Add padding
    const padding = 35;
    const drawWidth = canvas.width - 2 * padding;
    const drawHeight = canvas.height - 2 * padding;
    
    // Calculate scale
    const rangeX = maxX - minX;
    const rangeZ = maxZ - minZ;
    const scaleX = drawWidth / rangeX;
    const scaleZ = drawHeight / rangeZ;
    const scale = Math.min(scaleX, scaleZ) * 0.9;
    
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    // Helper function to convert coords to canvas coords
    function toCanvas(x, z) {
        return {
            x: centerX + ((x - rangeX / 2) * scale),
            y: centerY - ((z - rangeZ / 2) * scale)
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

// Expose functions to global scope for inline onclick handlers
// (Required because script.js is now an ES6 module)
window.switchTab = switchTab;
window.openCreateModal = openCreateModal;
window.closeCreateModal = closeCreateModal;
window.openEditModal = openEditModal;
window.closeEditModal = closeEditModal;
window.openDeleteModal = openDeleteModal;
window.closeDeleteModal = closeDeleteModal;
window.confirmDeleteKayak = confirmDeleteKayak;
window.changeProfile = changeProfile;
window.selectStation = selectStation;
window.toggleDetailsView = toggleDetailsView;
window.closeNotification = closeNotification;
