// static/js/bloch-sphere.js - 3D Bloch Sphere Implementation
class BlochSphere {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, 400/300, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        
        this.setupRenderer();
        this.createSphere();
        this.createAxes();
        this.createLabels();
        this.createStateVector();
        this.setupControls();
        this.animate();
    }
    
    setupRenderer() {
        this.renderer.setSize(400, 300);
        this.renderer.setClearColor(0x121417, 1);
        this.container.appendChild(this.renderer.domElement);
        
        this.camera.position.set(3, 2, 3);
        this.camera.lookAt(0, 0, 0);
    }
    
    createSphere() {
        // Translucent sphere
        const geometry = new THREE.SphereGeometry(1, 32, 32);
        const material = new THREE.MeshBasicMaterial({
            color: 0x50E3C2,
            transparent: true,
            opacity: 0.1,
            wireframe: true
        });
        this.sphere = new THREE.Mesh(geometry, material);
        this.scene.add(this.sphere);
    }
    
    createAxes() {
        // X, Y, Z axes
        const axisLength = 1.3;
        
        // X axis (red)
        const xGeometry = new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(-axisLength, 0, 0),
            new THREE.Vector3(axisLength, 0, 0)
        ]);
        const xMaterial = new THREE.LineBasicMaterial({ color: 0xff0000 });
        const xLine = new THREE.Line(xGeometry, xMaterial);
        this.scene.add(xLine);
        
        // Y axis (green)
        const yGeometry = new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(0, -axisLength, 0),
            new THREE.Vector3(0, axisLength, 0)
        ]);
        const yMaterial = new THREE.LineBasicMaterial({ color: 0x00ff00 });
        const yLine = new THREE.Line(yGeometry, yMaterial);
        this.scene.add(yLine);
        
        // Z axis (blue)
        const zGeometry = new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(0, 0, -axisLength),
            new THREE.Vector3(0, 0, axisLength)
        ]);
        const zMaterial = new THREE.LineBasicMaterial({ color: 0x0000ff });
        const zLine = new THREE.Line(zGeometry, zMaterial);
        this.scene.add(zLine);
    }
    
    createLabels() {
        // Create text sprites for quantum state labels
        this.createTextSprite('|0⟩', 0, 0, 1.4, 0x39D98A);
        this.createTextSprite('|1⟩', 0, 0, -1.4, 0xFF9D42);
        this.createTextSprite('|+⟩', 1.4, 0, 0, 0x73B7FF);
        this.createTextSprite('|-⟩', -1.4, 0, 0, 0x9F7AEA);
    }
    
    createTextSprite(text, x, y, z, color) {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 64;
        canvas.height = 32;
        
        context.fillStyle = `#${color.toString(16).padStart(6, '0')}`;
        context.font = '20px Arial';
        context.textAlign = 'center';
        context.fillText(text, 32, 20);
        
        const texture = new THREE.CanvasTexture(canvas);
        const material = new THREE.SpriteMaterial({ map: texture });
        const sprite = new THREE.Sprite(material);
        
        sprite.position.set(x, y, z);
        sprite.scale.set(0.5, 0.25, 1);
        this.scene.add(sprite);
    }
    
    createStateVector() {
        // State vector arrow
        this.stateVector = new THREE.ArrowHelper(
            new THREE.Vector3(0, 0, 1),  // direction
            new THREE.Vector3(0, 0, 0),  // origin
            1,                           // length
            0xFF5A5F,                    // color (red)
            0.2,                         // head length
            0.1                          // head width
        );
        this.scene.add(this.stateVector);
        
        // State point
        const pointGeometry = new THREE.SphereGeometry(0.05, 16, 16);
        const pointMaterial = new THREE.MeshBasicMaterial({ color: 0xFF5A5F });
        this.statePoint = new THREE.Mesh(pointGeometry, pointMaterial);
        this.statePoint.position.set(0, 0, 1);
        this.scene.add(this.statePoint);
    }
    
    setupControls() {
        // Mouse controls for rotation
        this.mouse = { x: 0, y: 0 };
        this.isMouseDown = false;
        
        this.container.addEventListener('mousedown', (e) => {
            this.isMouseDown = true;
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
        });
        
        this.container.addEventListener('mousemove', (e) => {
            if (this.isMouseDown) {
                const deltaX = e.clientX - this.mouse.x;
                const deltaY = e.clientY - this.mouse.y;
                
                this.sphere.rotation.y += deltaX * 0.01;
                this.sphere.rotation.x += deltaY * 0.01;
                
                this.mouse.x = e.clientX;
                this.mouse.y = e.clientY;
            }
        });
        
        this.container.addEventListener('mouseup', () => {
            this.isMouseDown = false;
        });
    }
    
    updateStateVector(x, y, z) {
        // Update arrow direction
        const direction = new THREE.Vector3(x, y, z).normalize();
        this.stateVector.setDirection(direction);
        
        // Update point position
        this.statePoint.position.set(x, y, z);
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        // Auto-rotate sphere
        this.sphere.rotation.y += 0.005;
        
        this.renderer.render(this.scene, this.camera);
    }
}

// Initialize Bloch sphere when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.blochSphere = new BlochSphere('bloch-container');
});
