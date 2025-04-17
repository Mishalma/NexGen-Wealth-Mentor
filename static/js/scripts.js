// Sidebar Toggle
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebar-toggle');
sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('-translate-x-full');
});

// Three.js 3D Background and Cubes
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('three-canvas'), alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);

const ambientLight = new THREE.AmbientLight(0x404040);
scene.add(ambientLight);
const pointLight = new THREE.PointLight(0x10B981, 1, 100);
pointLight.position.set(10, 10, 10);
scene.add(pointLight);

camera.position.z = 5;

// Hologram Orb
const orbGeometry = new THREE.SphereGeometry(0.3, 32, 32);
const orbMaterial = new THREE.MeshBasicMaterial({ color: 0x10B981, transparent: true, opacity: 0.5 });
const orb = new THREE.Mesh(orbGeometry, orbMaterial);
scene.add(orb);

function animate() {
    requestAnimationFrame(animate);
    orb.rotation.y += 0.01;
    renderer.render(scene, camera);
}
animate();

// Real-Time Insights
function updateInsight() {
    const insights = [
        "Reduce dining expenses by 10% to save ₹2,000 monthly.",
        "Housing costs are high. Consider refinancing.",
        "Invest ₹5,000 monthly for long-term growth.",
        "Extra debt payments can save ₹10,000 in interest."
    ];
    const insightText = document.getElementById('insight-text');
    insightText.textContent = insights[Math.floor(Math.random() * insights.length)];
    gsap.from(insightText, { opacity: 0, y: 20, duration: 0.8, ease: 'power3.out' });
}

// GSAP Parallax Scroll
window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    gsap.to('.cube-container', {
        y: scrollY * 0.2,
        ease: 'power3.out',
        duration: 0.5
    });
});

// Initial Animations
gsap.from('nav a', { y: -30, opacity: 0, duration: 0.8, stagger: 0.1, ease: 'power3.out', delay: 0.2 });