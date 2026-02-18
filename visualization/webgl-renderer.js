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
        this.curvesGroup = null;
        this.profilesGroup = null;
        this.animationId = null;
        this.hullData = null;
        
        // Render settings
        this.settings = {
            showWireframe: false,
            showCurves: false,
            showProfiles: false,
            showWaterline: true,
            showShadows: true,
            renderMode: 'surface' // 'surface', 'wireframe', 'both', 'technical'
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
        const keyLight = new THREE.DirectionalLight(0xffffff, 0.8);
        keyLight.position.set(5, 10, 7.5);
        keyLight.castShadow = this.settings.showShadows;
        keyLight.shadow.mapSize.width = 2048;
        keyLight.shadow.mapSize.height = 2048;
        keyLight.shadow.camera.near = 0.5;
        keyLight.shadow.camera.far = 50;
        this.scene.add(keyLight);

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
     * Add visual helpers (grid, axes)
     */
    addHelpers() {
        // Grid helper
        const gridHelper = new THREE.GridHelper(20, 20, 0x888888, 0xcccccc);
        this.scene.add(gridHelper);

        // Axes helper (X=red, Y=green, Z=blue)
        const axesHelper = new THREE.AxesHelper(2);
        this.scene.add(axesHelper);
    }

    /**
     * Animation loop
     */
    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());

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
     * Render hull data
     * @param {Object} hullData - Hull data from API
     */
    renderHull(hullData) {
        if (!hullData) {
            console.error('No hull data provided');
            return;
        }

        this.hullData = hullData;

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

        // Adjust camera to fit hull
        this.fitCameraToHull(hullData);
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

        // Create material
        const material = new THREE.MeshPhongMaterial({
            vertexColors: true,
            side: THREE.DoubleSide,
            flatShading: false,
            shininess: 30,
            specular: 0x555555
        });

        // Create mesh
        this.hullMesh = new THREE.Mesh(geometry, material);
        this.hullMesh.castShadow = true;
        this.hullMesh.receiveShadow = true;
        this.scene.add(this.hullMesh);
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
     * Add vertex color based on waterline
     * @param {Array} colors - Color array to append to
     * @param {Number} zCoord - Z coordinate of vertex
     * @param {Number} waterline - Waterline Z coordinate
     */
    addVertexColor(colors, zCoord, waterline) {
        const isAboveWater = zCoord >= waterline;
        if (isAboveWater) {
            colors.push(0.0, 0.0, 0.8);  // Dark blue above waterline
        } else {
            colors.push(0.6, 0.8, 1.0);  // Light blue below waterline
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
     * Create curve lines
     * @param {Object} hullData - Hull data
     */
    createCurveLines(hullData) {
        this.curvesGroup = new THREE.Group();

        hullData.curves.forEach(curve => {
            if (curve.points.length < 2) return;

            // Transform coordinates: X=length, Z(kayak)→Y(three.js)=height, Y(kayak)→Z(three.js)=beam
            const points = curve.points.map(p => new THREE.Vector3(p[0], p[2], p[1]));
            const geometry = new THREE.BufferGeometry().setFromPoints(points);
            const material = new THREE.LineBasicMaterial({ 
                color: 0x0000CC,
                linewidth: 2
            });

            const line = new THREE.Line(geometry, material);
            this.curvesGroup.add(line);
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
        Object.assign(this.settings, settings);
        
        // Re-render if hull data exists
        if (this.hullData) {
            this.renderHull(this.hullData);
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

        // Dispose of renderer
        if (this.renderer) {
            this.renderer.dispose();
        }

        // Clear references
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
    }
}
