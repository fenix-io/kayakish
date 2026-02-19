/**
 * WebGL-based hull renderer using Three.js
 * Provides 3D visualization with lighting, shadows, and interactive controls
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

export class HullRenderer {
    constructor(container) {
        this.container = container;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.hullMesh = null;
        this.waterlinePlane = null;
        this.wireframeOverlay = null;
        this.curvesGroup = null;
        this.profilesGroup = null;
        this.measurementsGroup = null;
        this.groundPlane = null;
        this.animationId = null;
        this.hullData = null;
        this.keyLight = null;  // Store reference to key light for shadow toggling
        
        // Render settings
        this.settings = {
            showWireframe: false,
            showCurves: false,
            showProfiles: false,
            showWaterline: true,
            showShadows: true,
            showMeasurements: false,
            showFPS: false,
            renderMode: 'surface' // 'surface', 'wireframe', 'both', 'technical'
        };
        
        // FPS tracking
        this.fpsCounter = {
            frames: 0,
            lastTime: performance.now(),
            fps: 0
        };
    }

    /**
     * Initialize the Three.js scene, camera, renderer, and controls
     */
    init() {
        // Check WebGL support
        if (!this.hasWebGLSupport()) {
            console.error('WebGL not supported');
            return false;
        }

        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0xf0f0f0);

        // Create camera
        const aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 1000);
        this.camera.position.set(5, 4, 3);
        this.camera.lookAt(0, 0, 0);

        // Create WebGL renderer
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            alpha: false 
        });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

        // Replace existing canvas
        const existingCanvas = this.container.querySelector('canvas');
        if (existingCanvas) {
            existingCanvas.remove();
        }
        this.container.appendChild(this.renderer.domElement);

        // Add OrbitControls
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.screenSpacePanning = false;
        this.controls.minDistance = 1;
        this.controls.maxDistance = 50;
        this.controls.maxPolarAngle = Math.PI * 0.95;

        // Set up lighting
        this.setupLighting();

        // Add grid and axes helpers
        this.addHelpers();

        // Start animation loop
        this.animate();

        return true;
    }

    /**
     * Check if WebGL is supported
     */
    hasWebGLSupport() {
        try {
            const canvas = document.createElement('canvas');
            return !!(
                window.WebGLRenderingContext &&
                (canvas.getContext('webgl') || canvas.getContext('experimental-webgl'))
            );
        } catch (e) {
            return false;
        }
    }

    /**
     * Set up three-point lighting system
     */
    setupLighting() {
        // 1. Key light (main directional light)
        this.keyLight = new THREE.DirectionalLight(0xffffff, 0.8);
        this.keyLight.position.set(5, 10, 7.5);
        this.keyLight.castShadow = this.settings.showShadows;
        this.keyLight.shadow.mapSize.width = 2048;
        this.keyLight.shadow.mapSize.height = 2048;
        this.keyLight.shadow.camera.near = 0.5;
        this.keyLight.shadow.camera.far = 50;
        this.keyLight.shadow.camera.left = -10;
        this.keyLight.shadow.camera.right = 10;
        this.keyLight.shadow.camera.top = 10;
        this.keyLight.shadow.camera.bottom = -10;
        this.scene.add(this.keyLight);

        // 2. Fill light (soften shadows)
        const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
        fillLight.position.set(-5, 5, -5);
        this.scene.add(fillLight);

        // 3. Ambient light (base illumination)
        const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
        this.scene.add(ambientLight);

        // Optional: Hemisphere light for outdoor feel
        const hemiLight = new THREE.HemisphereLight(
            0x87CEEB,  // Sky color
            0x8B7355,  // Ground color
            0.4
        );
        this.scene.add(hemiLight);
    }

    /**
     * Add visual helpers (grid, axes, ground plane)
     */
    addHelpers() {
        // Grid helper
        const gridHelper = new THREE.GridHelper(20, 20, 0x888888, 0xcccccc);
        this.scene.add(gridHelper);

        // Axes helper (X=red, Y=green, Z=blue)
        const axesHelper = new THREE.AxesHelper(2);
        this.scene.add(axesHelper);

        // Add shadow-receiving ground/water plane
        this.addGroundPlane();
    }

    /**
     * Add a shadow-receiving ground plane (water surface)
     */
    addGroundPlane() {
        const groundGeometry = new THREE.PlaneGeometry(50, 50);
        const groundMaterial = new THREE.MeshPhongMaterial({
            color: 0x4a90a4,  // Water-like blue-grey
            transparent: true,
            opacity: 0.4,
            side: THREE.DoubleSide,
            shininess: 100,
            specular: new THREE.Color(0xffffff)
        });

        this.groundPlane = new THREE.Mesh(groundGeometry, groundMaterial);
        this.groundPlane.rotation.x = -Math.PI / 2;  // Rotate to horizontal (XZ plane)
        this.groundPlane.position.y = -0.5;  // Slightly below origin
        this.groundPlane.receiveShadow = true;
        
        this.scene.add(this.groundPlane);
    }

    /**
     * Animation loop
     */
    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());

        // Update FPS counter
        if (this.settings.showFPS) {
            this.updateFPS();
        }

        // Update controls
        if (this.controls) {
            this.controls.update();
        }

        // Render scene
        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
    }

    /**
     * Update FPS counter
     */
    updateFPS() {
        this.fpsCounter.frames++;
        const currentTime = performance.now();
        const elapsed = currentTime - this.fpsCounter.lastTime;

        // Update FPS display every 500ms
        if (elapsed >= 500) {
            this.fpsCounter.fps = Math.round((this.fpsCounter.frames * 1000) / elapsed);
            this.fpsCounter.frames = 0;
            this.fpsCounter.lastTime = currentTime;

            // Update FPS display element if it exists
            const fpsElement = document.getElementById('fpsDisplay');
            if (fpsElement) {
                fpsElement.textContent = `FPS: ${this.fpsCounter.fps}`;
            }
        }
    }

    /**
     * Render hull data
     * @param {Object} hullData - Hull data from API
     */
    renderHull(hullData) {
        if (!hullData) {
            console.error('No hull data provided');
            return;
        }

        this.hullData = hullData;

        // Show loading indicator
        this.showLoading();

        // Use setTimeout to allow UI to update before heavy computation
        setTimeout(() => {
            try {
                // Clear existing hull meshes
                this.clearHull();

                // Create hull mesh from profiles
                if (hullData.main_profiles && hullData.main_profiles.length > 0) {
                    this.createHullMesh(hullData);
                }

                // Create waterline plane
                if (hullData.waterline && this.settings.showWaterline) {
                    this.createWaterlinePlane(hullData);
                }

                // Create curve lines
                if (hullData.curves && this.settings.showCurves) {
                    this.createCurveLines(hullData);
                }

                // Create profile lines
                if (hullData.main_profiles && this.settings.showProfiles) {
                    this.createProfileLines(hullData);
                }

                // Create measurement overlays
                if (this.settings.showMeasurements) {
                    this.createMeasurements(hullData);
                }

                // Adjust camera to fit hull
                this.fitCameraToHull(hullData);
            } finally {
                // Hide loading indicator
                this.hideLoading();
            }
        }, 10);
    }

    /**
     * Show loading indicator
     */
    showLoading() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'flex';
        }
    }

    /**
     * Hide loading indicator
     */
    hideLoading() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    }

    /**
     * Create hull mesh from profile data
     * @param {Object} hullData - Hull data
     */
    createHullMesh(hullData) {
        const profiles = hullData.main_profiles;
        
        if (profiles.length < 2) {
            console.warn('Need at least 2 profiles to create mesh');
            return;
        }

        // Build geometry from profiles
        const geometry = this.buildGeometryFromProfiles(profiles, hullData.waterline);

        // Create realistic hull material
        const material = new THREE.MeshPhongMaterial({
            vertexColors: true,
            side: THREE.DoubleSide,
            flatShading: false,
            shininess: 60,              // Higher shininess for glossy appearance
            specular: new THREE.Color(0xffffff),  // White specular highlights
            emissive: new THREE.Color(0x000000),  // No emissionreflectivity: 0.3,           // Some reflectivity for wet appearance
            transparent: false,
            opacity: 1.0
        });

        // Create mesh
        this.hullMesh = new THREE.Mesh(geometry, material);
        this.hullMesh.castShadow = true;
        this.hullMesh.receiveShadow = true;
        this.scene.add(this.hullMesh);

        // Add wireframe overlay if enabled
        if (this.settings.showWireframe) {
            this.addWireframeOverlay(geometry);
        }
    }

    /**
     * Build BufferGeometry from profile data with arc-length resampling
     * @param {Array} profiles - Array of profile objects
     * @param {Number} waterline - Waterline Z-coordinate
     * @returns {THREE.BufferGeometry}
     */
    buildGeometryFromProfiles(profiles, waterline) {
        const vertices = [];
        const indices = [];
        const colors = [];

        // Target point count for resampling (ensures uniform mesh)
        const targetPointCount = 60;

        // Process each pair of adjacent profiles
        for (let p = 0; p < profiles.length - 1; p++) {
            const profile1 = profiles[p];
            const profile2 = profiles[p + 1];

            // Resample both profiles to common point count
            const resampled1 = this.resampleProfileByArcLength(profile1.points, targetPointCount);
            const resampled2 = this.resampleProfileByArcLength(profile2.points, targetPointCount);

            // Create quad faces between resampled profiles
            for (let i = 0; i < targetPointCount; i++) {
                const i_next = (i + 1) % targetPointCount;

                const p1 = resampled1[i];
                const p2 = resampled1[i_next];
                const p3 = resampled2[i];
                const p4 = resampled2[i_next];

                const vertexBase = vertices.length / 3;

                // Add vertices with coordinate transformation
                // Kayak: X=length, Y=beam, Z=height → Three.js: X=length, Y=height, Z=beam
                vertices.push(p1[0], p1[2], p1[1]);
                vertices.push(p2[0], p2[2], p2[1]);
                vertices.push(p3[0], p3[2], p3[1]);
                vertices.push(p4[0], p4[2], p4[1]);

                // Add vertex colors (based on waterline - using Z from kayak coords)
                this.addVertexColor(colors, p1[2], waterline);
                this.addVertexColor(colors, p2[2], waterline);
                this.addVertexColor(colors, p3[2], waterline);
                this.addVertexColor(colors, p4[2], waterline);

                // Create two triangles (counter-clockwise winding)
                // Triangle 1: p1, p3, p4
                indices.push(vertexBase + 0, vertexBase + 2, vertexBase + 3);
                // Triangle 2: p1, p4, p2
                indices.push(vertexBase + 0, vertexBase + 3, vertexBase + 1);
            }
        }

        // Add bow end cap (stern - first profile)
        this.addEndCap(vertices, indices, colors, profiles[0], waterline, targetPointCount, false);

        // Add stern end cap (bow - last profile)
        this.addEndCap(vertices, indices, colors, profiles[profiles.length - 1], waterline, targetPointCount, true);

        // Create BufferGeometry
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
        geometry.setIndex(indices);
        geometry.computeVertexNormals();

        return geometry;
    }

    /**
     * Resample profile points to uniform count using arc-length parameterization
     * @param {Array} points - Array of [x, y, z] points
     * @param {Number} targetCount - Desired number of points
     * @returns {Array} Resampled points
     */
    resampleProfileByArcLength(points, targetCount) {
        if (points.length === 0) return [];

        // Calculate cumulative arc lengths
        const arcLengths = [0];
        let totalLength = 0;

        for (let i = 1; i < points.length; i++) {
            const dx = points[i][0] - points[i - 1][0];
            const dy = points[i][1] - points[i - 1][1];
            const dz = points[i][2] - points[i - 1][2];
            const segmentLength = Math.sqrt(dx * dx + dy * dy + dz * dz);
            totalLength += segmentLength;
            arcLengths.push(totalLength);
        }

        if (totalLength === 0) {
            // All points are identical, just return copies
            return Array(targetCount).fill(points[0]);
        }

        // Resample at uniform arc length intervals
        const resampled = [];
        for (let i = 0; i < targetCount; i++) {
            const targetLength = (i / targetCount) * totalLength;

            // Find segment containing this arc length
            let segIdx = 0;
            for (let j = 0; j < arcLengths.length - 1; j++) {
                if (targetLength >= arcLengths[j] && targetLength <= arcLengths[j + 1]) {
                    segIdx = j;
                    break;
                }
            }

            // Interpolate within segment
            const p1 = points[segIdx];
            const p2 = points[(segIdx + 1) % points.length];
            const segLength = arcLengths[segIdx + 1] - arcLengths[segIdx];
            const localT = segLength > 0 ? (targetLength - arcLengths[segIdx]) / segLength : 0;

            const x = p1[0] + (p2[0] - p1[0]) * localT;
            const y = p1[1] + (p2[1] - p1[1]) * localT;
            const z = p1[2] + (p2[2] - p1[2]) * localT;

            resampled.push([x, y, z]);
        }

        return resampled;
    }

    /**
     * Add end cap (bow or stern) using triangular fan
     * @param {Array} vertices - Vertex array to append to
     * @param {Array} indices - Index array to append to
     * @param {Array} colors - Color array to append to
     * @param {Object} profile - Profile object with points
     * @param {Number} waterline - Waterline Z coordinate
     * @param {Number} targetPointCount - Number of points in resampled profile
     * @param {Boolean} reverse - Whether to reverse winding order (for correct normals)
     */
    addEndCap(vertices, indices, colors, profile, waterline, targetPointCount, reverse) {
        // Resample profile to ensure uniform point distribution
        const resampled = this.resampleProfileByArcLength(profile.points, targetPointCount);

        // Calculate center point of the profile
        let centerX = 0, centerY = 0, centerZ = 0;
        for (const point of resampled) {
            centerX += point[0];
            centerY += point[1];
            centerZ += point[2];
        }
        centerX /= resampled.length;
        centerY /= resampled.length;
        centerZ /= resampled.length;

        // Add center vertex (transformed to Three.js coords)
        const centerIndex = vertices.length / 3;
        vertices.push(centerX, centerZ, centerY);
        this.addVertexColor(colors, centerZ, waterline); // Use Z from kayak coords

        // Add perimeter vertices
        const perimeterStartIndex = vertices.length / 3;
        for (const point of resampled) {
            vertices.push(point[0], point[2], point[1]); // Transform coords
            this.addVertexColor(colors, point[2], waterline);
        }

        // Create triangular fan from center to perimeter
        for (let i = 0; i < targetPointCount; i++) {
            const i_next = (i + 1) % targetPointCount;
            const idx1 = perimeterStartIndex + i;
            const idx2 = perimeterStartIndex + i_next;

            // Add triangle with correct winding order
            if (reverse) {
                indices.push(centerIndex, idx2, idx1); // Reversed for bow
            } else {
                indices.push(centerIndex, idx1, idx2); // Normal for stern
            }
        }
    }

    /**
     * Add wireframe overlay to the hull mesh
     * @param {THREE.BufferGeometry} geometry - Hull geometry
     */
    addWireframeOverlay(geometry) {
        // Remove existing wireframe if present
        if (this.wireframeOverlay) {
            this.scene.remove(this.wireframeOverlay);
            this.wireframeOverlay.geometry.dispose();
            this.wireframeOverlay.material.dispose();
            this.wireframeOverlay = null;
        }

        if (!this.settings.showWireframe) {
            return;
        }

        // Create edges geometry (only draws actual edges, not all triangle boundaries)
        const edgesGeometry = new THREE.EdgesGeometry(geometry, 15); // Threshold angle in degrees
        
        // Create wireframe material
        const wireframeMaterial = new THREE.LineBasicMaterial({
            color: 0x000000,
            linewidth: 1,
            transparent: true,
            opacity: 0.3,
            depthTest: true
        });

        // Create line segments
        this.wireframeOverlay = new THREE.LineSegments(edgesGeometry, wireframeMaterial);
        this.scene.add(this.wireframeOverlay);
    }

    /**
     * Add vertex color based on waterline (improved color scheme)
     * @param {Array} colors - Color array to append to
     * @param {Number} zCoord - Z coordinate of vertex (kayak coords)
     * @param {Number} waterline - Waterline Z coordinate
     */
    addVertexColor(colors, zCoord, waterline) {
        const isAboveWater = zCoord >= waterline;
        if (isAboveWater) {
            // Dark navy blue for above waterline (deck area)
            colors.push(0.1, 0.2, 0.5);
        } else {
            // Lighter cyan-blue for below waterline (wet hull)
            colors.push(0.4, 0.7, 0.9);
        }
    }

    /**
     * Create waterline plane
     * @param {Object} hullData - Hull data
     */
    createWaterlinePlane(hullData) {
        const size = Math.max(
            hullData.max_x - hullData.min_x,
            hullData.max_y - hullData.min_y
        ) * 1.5;

        const geometry = new THREE.PlaneGeometry(size, size);
        const material = new THREE.MeshPhongMaterial({
            color: 0x00FFFF,
            transparent: true,
            opacity: 0.3,
            side: THREE.DoubleSide
        });

        this.waterlinePlane = new THREE.Mesh(geometry, material);
        this.waterlinePlane.rotation.x = Math.PI / 2;  // Rotate to horizontal
        this.waterlinePlane.position.y = hullData.waterline;  // Y is up in Three.js
        this.waterlinePlane.position.x = (hullData.max_x + hullData.min_x) / 2;
        this.waterlinePlane.position.z = 0;  // Centered on beam

        this.scene.add(this.waterlinePlane);
    }

    /**
     * Create curve lines with waterline-based color coding
     * @param {Object} hullData - Hull data
     */
    createCurveLines(hullData) {
        this.curvesGroup = new THREE.Group();
        const waterline = hullData.waterline;

        hullData.curves.forEach(curve => {
            if (curve.points.length < 2) return;

            // Create line segments with colors based on waterline position
            for (let i = 0; i < curve.points.length - 1; i++) {
                const p1 = curve.points[i];
                const p2 = curve.points[i + 1];

                // Transform coordinates: X=length, Z(kayak)→Y(three.js)=height, Y(kayak)→Z(three.js)=beam
                const points = [
                    new THREE.Vector3(p1[0], p1[2], p1[1]),
                    new THREE.Vector3(p2[0], p2[2], p2[1])
                ];

                // Determine color based on average z-position (height in kayak coords)
                const avgZ = (p1[2] + p2[2]) / 2;
                const isAboveWater = avgZ >= waterline;
                
                const geometry = new THREE.BufferGeometry().setFromPoints(points);
                const material = new THREE.LineBasicMaterial({
                    color: isAboveWater ? 0x0000CC : 0x99CCFF,  // Dark blue above, light blue below
                    linewidth: 2,
                    transparent: isAboveWater ? false : true,
                    opacity: isAboveWater ? 1.0 : 0.8
                });

                const line = new THREE.Line(geometry, material);
                this.curvesGroup.add(line);
            }
        });

        this.scene.add(this.curvesGroup);
    }

    /**
     * Create profile lines
     * @param {Object} hullData - Hull data
     */
    createProfileLines(hullData) {
        this.profilesGroup = new THREE.Group();

        hullData.main_profiles.forEach(profile => {
            if (profile.points.length < 2) return;

            // Transform coordinates: X=length, Z(kayak)→Y(three.js)=height, Y(kayak)→Z(three.js)=beam
            const points = profile.points.map(p => new THREE.Vector3(p[0], p[2], p[1]));
            // Close the loop
            points.push(points[0]);

            const geometry = new THREE.BufferGeometry().setFromPoints(points);
            const material = new THREE.LineBasicMaterial({ 
                color: 0x008000,
                transparent: true,
                opacity: 0.5,
                linewidth: 1
            });

            const line = new THREE.Line(geometry, material);
            this.profilesGroup.add(line);
        });

        this.scene.add(this.profilesGroup);
    }

    /**
     * Create measurement overlays (dimension lines and text labels)
     * @param {Object} hullData - Hull data
     */
    createMeasurements(hullData) {
        this.measurementsGroup = new THREE.Group();

        const minX = hullData.min_x;
        const maxX = hullData.max_x;
        const minY = hullData.min_y;
        const maxY = hullData.max_y;
        const minZ = hullData.min_z;
        const maxZ = hullData.max_z;
        const waterline = hullData.waterline;

        // Length measurement (stern to bow)
        this.addDimensionLine(
            new THREE.Vector3(minX, minZ, 0),
            new THREE.Vector3(maxX, minZ, 0),
            `Length: ${(maxX - minX).toFixed(2)}m`,
            0xff0000,
            new THREE.Vector3(0, -0.3, 0)
        );

        // Beam measurement (port to starboard at midship)
        const midX = (minX + maxX) / 2;
        this.addDimensionLine(
            new THREE.Vector3(midX, minZ, minY),
            new THREE.Vector3(midX, minZ, maxY),
            `Beam: ${(maxY - minY).toFixed(2)}m`,
            0x00ff00,
            new THREE.Vector3(0, -0.3, 0)
        );

        // Depth measurement (keel to highest point at midship)
        this.addDimensionLine(
            new THREE.Vector3(minX, minZ, 0),
            new THREE.Vector3(minX, maxZ, 0),
            `Depth: ${(maxZ - minZ).toFixed(2)}m`,
            0x0000ff,
            new THREE.Vector3(-0.3, 0, 0)
        );

        // Waterline level indicator (horizontal line at waterline)
        this.addWaterlineIndicator(hullData);

        this.scene.add(this.measurementsGroup);
    }

    /**
     * Add a dimension line with label
     * @param {THREE.Vector3} start - Start point in Three.js coords
     * @param {THREE.Vector3} end - End point in Three.js coords
     * @param {String} label - Text label
     * @param {Number} color - Line color (hex)
     * @param {THREE.Vector3} labelOffset - Offset for label position
     */
    addDimensionLine(start, end, label, color, labelOffset) {
        // Draw dimension line
        const points = [start, end];
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({
            color: color,
            linewidth: 2
        });
        const line = new THREE.Line(geometry, material);
        this.measurementsGroup.add(line);

        // Add end markers (small spheres)
        const markerGeometry = new THREE.SphereGeometry(0.02, 8, 8);
        const markerMaterial = new THREE.MeshBasicMaterial({ color: color });
        
        const startMarker = new THREE.Mesh(markerGeometry, markerMaterial);
        startMarker.position.copy(start);
        this.measurementsGroup.add(startMarker);

        const endMarker = new THREE.Mesh(markerGeometry, markerMaterial);
        endMarker.position.copy(end);
        this.measurementsGroup.add(endMarker);

        // Add text sprite at midpoint
        const midpoint = new THREE.Vector3().addVectors(start, end).multiplyScalar(0.5);
        midpoint.add(labelOffset);
        const textSprite = this.createTextSprite(label, color);
        textSprite.position.copy(midpoint);
        this.measurementsGroup.add(textSprite);
    }

    /**
     * Add waterline level indicator
     * @param {Object} hullData - Hull data
     */
    addWaterlineIndicator(hullData) {
        const waterline = hullData.waterline;
        const minX = hullData.min_x;
        const maxX = hullData.max_x;

        // Create waterline indicator line at bow
        const points = [
            new THREE.Vector3(maxX, waterline, 0),
            new THREE.Vector3(maxX + 0.2, waterline, 0)
        ];
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({
            color: 0x00ffff,
            linewidth: 3
        });
        const line = new THREE.Line(geometry, material);
        this.measurementsGroup.add(line);

        // Add label
        const labelPos = new THREE.Vector3(maxX + 0.3, waterline, 0);
        const textSprite = this.createTextSprite(`WL: ${waterline.toFixed(3)}m`, 0x00ffff);
        textSprite.position.copy(labelPos);
        this.measurementsGroup.add(textSprite);
    }

    /**
     * Create a text sprite (canvas-based texture)
     * @param {String} text - Text to display
     * @param {Number} color - Text color (hex)
     * @returns {THREE.Sprite}
     */
    createTextSprite(text, color) {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 256;
        canvas.height = 64;

        // Draw background
        context.fillStyle = 'rgba(0, 0, 0, 0.7)';
        context.fillRect(0, 0, canvas.width, canvas.height);

        // Draw text
        context.font = 'Bold 24px Arial';
        context.fillStyle = `#${color.toString(16).padStart(6, '0')}`;
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillText(text, canvas.width / 2, canvas.height / 2);

        // Create sprite
        const texture = new THREE.CanvasTexture(canvas);
        const material = new THREE.SpriteMaterial({ map: texture });
        const sprite = new THREE.Sprite(material);
        sprite.scale.set(0.5, 0.125, 1);  // Scale to reasonable size

        return sprite;
    }

    /**
     * Adjust camera to fit hull in view
     * @param {Object} hullData - Hull data
     */
    fitCameraToHull(hullData) {
        const centerX = (hullData.max_x + hullData.min_x) / 2;
        const centerY = (hullData.max_y + hullData.min_y) / 2;  // Kayak Y (beam)
        const centerZ = (hullData.max_z + hullData.min_z) / 2;  // Kayak Z (height)

        const sizeX = hullData.max_x - hullData.min_x;  // Length
        const sizeY = hullData.max_y - hullData.min_y;  // Beam
        const sizeZ = hullData.max_z - hullData.min_z;  // Height
        const maxSize = Math.max(sizeX, sizeY, sizeZ);

        // Position camera for isometric-ish view
        // Three.js coords: X=length, Y=height, Z=beam
        this.camera.position.set(
            centerX + sizeX * 1.5,
            centerZ + sizeZ * 2,      // Y in Three.js = height
            centerY + sizeY * 2       // Z in Three.js = beam
        );

        this.controls.target.set(centerX, centerZ, centerY);  // Transform center coords
        this.controls.update();
    }

    /**
     * Clear existing hull meshes
     */
    clearHull() {
        if (this.hullMesh) {
            this.scene.remove(this.hullMesh);
            this.hullMesh.geometry.dispose();
            this.hullMesh.material.dispose();
            this.hullMesh = null;
        }

        if (this.wireframeOverlay) {
            this.scene.remove(this.wireframeOverlay);
            this.wireframeOverlay.geometry.dispose();
            this.wireframeOverlay.material.dispose();
            this.wireframeOverlay = null;
        }

        if (this.waterlinePlane) {
            this.scene.remove(this.waterlinePlane);
            this.waterlinePlane.geometry.dispose();
            this.waterlinePlane.material.dispose();
            this.waterlinePlane = null;
        }

        if (this.curvesGroup) {
            this.curvesGroup.traverse(child => {
                if (child.geometry) child.geometry.dispose();
                if (child.material) child.material.dispose();
            });
            this.scene.remove(this.curvesGroup);
            this.curvesGroup = null;
        }

        if (this.profilesGroup) {
            this.profilesGroup.traverse(child => {
                if (child.geometry) child.geometry.dispose();
                if (child.material) child.material.dispose();
            });
            this.scene.remove(this.profilesGroup);
            this.profilesGroup = null;
        }

        if (this.measurementsGroup) {
            this.measurementsGroup.traverse(child => {
                if (child.geometry) child.geometry.dispose();
                if (child.material) {
                    if (child.material.map) child.material.map.dispose();
                    child.material.dispose();
                }
            });
            this.scene.remove(this.measurementsGroup);
            this.measurementsGroup = null;
        }
    }

    /**
     * Handle window resize
     */
    resize() {
        if (!this.camera || !this.renderer) return;

        const width = this.container.clientWidth;
        const height = this.container.clientHeight;

        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();

        this.renderer.setSize(width, height);
    }

    /**
     * Set camera to preset view
     * @param {String} preset - View preset name
     */
    setCameraPreset(preset) {
        if (!this.hullData || !this.camera || !this.controls) return;

        const centerX = (this.hullData.max_x + this.hullData.min_x) / 2;  // Length
        const centerY = (this.hullData.max_y + this.hullData.min_y) / 2;  // Beam (kayak Y)
        const centerZ = (this.hullData.max_z + this.hullData.min_z) / 2;  // Height (kayak Z)

        const sizeX = this.hullData.max_x - this.hullData.min_x;  // Length
        const sizeY = this.hullData.max_y - this.hullData.min_y;  // Beam
        const sizeZ = this.hullData.max_z - this.hullData.min_z;  // Height
        const maxSize = Math.max(sizeX, sizeY, sizeZ);

        // Three.js coords: X=length, Y=height, Z=beam
        const target = new THREE.Vector3(centerX, centerZ, centerY);
        let newPosition;
        
        switch (preset) {
            case 'iso':
                newPosition = new THREE.Vector3(
                    centerX + sizeX * 1.5,
                    centerZ + sizeZ * 2,
                    centerY + sizeY * 2
                );
                break;
            case 'side':
                // View from port side (looking at starboard)
                newPosition = new THREE.Vector3(
                    centerX,
                    centerZ,
                    centerY + maxSize * 3
                );
                break;
            case 'top':
                // View from above
                newPosition = new THREE.Vector3(
                    centerX,
                    centerZ + maxSize * 3,
                    centerY
                );
                break;
            case 'front':
                // View from bow
                newPosition = new THREE.Vector3(
                    centerX + maxSize * 3,
                    centerZ,
                    centerY
                );
                break;
            default:
                return;
        }

        // Animate camera transition
        this.animateCameraTo(newPosition, target);
    }

    /**
     * Animate camera to new position
     * @param {THREE.Vector3} targetPosition - Target camera position
     * @param {THREE.Vector3} targetLookAt - Target look-at point
     */
    animateCameraTo(targetPosition, targetLookAt) {
        const duration = 1000; // ms
        const startPosition = this.camera.position.clone();
        const startLookAt = this.controls.target.clone();
        const startTime = Date.now();

        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Ease in-out
            const eased = progress < 0.5
                ? 2 * progress * progress
                : 1 - Math.pow(-2 * progress + 2, 2) / 2;

            this.camera.position.lerpVectors(startPosition, targetPosition, eased);
            this.controls.target.lerpVectors(startLookAt, targetLookAt, eased);
            this.controls.update();

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        animate();
    }

    /**
     * Update render settings
     * @param {Object} settings - Settings to update
     */
    updateSettings(settings) {
        const oldSettings = {...this.settings};
        Object.assign(this.settings, settings);
        
        // Handle shadow toggling
        if ('showShadows' in settings && settings.showShadows !== oldSettings.showShadows) {
            this.toggleShadows(settings.showShadows);
        }
        
        // Re-render if hull data exists
        if (this.hullData) {
            this.renderHull(this.hullData);
        }
    }

    /**
     * Set render quality
     * @param {String} quality - Quality level: 'low', 'medium', or 'high'
     */
    setQuality(quality) {
        if (!this.renderer || !this.keyLight) return;

        const qualitySettings = {
            low: {
                pixelRatio: 1,
                shadowMapSize: 512,
                antialias: false
            },
            medium: {
                pixelRatio: Math.min(window.devicePixelRatio, 1.5),
                shadowMapSize: 1024,
                antialias: true
            },
            high: {
                pixelRatio: window.devicePixelRatio,
                shadowMapSize: 2048,
                antialias: true
            }
        };

        const settings = qualitySettings[quality] || qualitySettings.medium;

        // Update pixel ratio
        this.renderer.setPixelRatio(settings.pixelRatio);

        // Update shadow map size
        this.keyLight.shadow.mapSize.width = settings.shadowMapSize;
        this.keyLight.shadow.mapSize.height = settings.shadowMapSize;
        this.keyLight.shadow.map?.dispose();
        this.keyLight.shadow.map = null;

        // Note: Antialias cannot be changed after renderer creation
        // It would require recreating the renderer
        
        console.log(`Render quality set to: ${quality}`);
    }

    /**
     * Toggle shadow rendering
     * @param {Boolean} enabled - Enable or disable shadows
     */
    toggleShadows(enabled) {
        if (this.keyLight) {
            this.keyLight.castShadow = enabled;
        }
        if (this.renderer) {
            this.renderer.shadowMap.enabled = enabled;
        }
        if (this.hullMesh) {
            this.hullMesh.castShadow = enabled;
        }
    }

    /**
     * Dispose of resources
     */
    dispose() {
        // Stop animation loop
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }

        // Dispose of controls
        if (this.controls) {
            this.controls.dispose();
        }

        // Clear hull
        this.clearHull();

        // Dispose of ground plane
        if (this.groundPlane) {
            this.scene.remove(this.groundPlane);
            this.groundPlane.geometry.dispose();
            this.groundPlane.material.dispose();
            this.groundPlane = null;
        }

        // Dispose of renderer
        if (this.renderer) {
            this.renderer.dispose();
        }

        // Clear references
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.keyLight = null;
    }
}
