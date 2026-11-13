/**
 * Holodeck 3D Renderer v0.1
 * Thin Three.js adapter: maps body state → mesh transforms.
 * Does not own physics. Deterministic layout helpers only.
 */

import { mapBodyTo3D } from "./mapping.mjs";

/**
 * @typedef {{ id: number, x: number, y: number, z?: number, radius: number, mass?: number }} BodyState
 */

export function createRenderer(canvas, THREE) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);
  renderer.shadowMap.enabled = true;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0a0a12);
  scene.fog = new THREE.Fog(0x0a0a12, 40, 120);

  const camera = new THREE.PerspectiveCamera(50, canvas.clientWidth / canvas.clientHeight, 0.1, 200);
  camera.position.set(12, 14, 22);
  camera.lookAt(0, 2, 0);

  const ambient = new THREE.AmbientLight(0x6688aa, 0.45);
  scene.add(ambient);
  const sun = new THREE.DirectionalLight(0xffffff, 1.05);
  sun.position.set(12, 24, 10);
  sun.castShadow = true;
  sun.shadow.mapSize.set(1024, 1024);
  scene.add(sun);
  const fill = new THREE.DirectionalLight(0x4466ff, 0.25);
  fill.position.set(-10, 8, -8);
  scene.add(fill);

  const groundGeo = new THREE.PlaneGeometry(80, 80);
  const groundMat = new THREE.MeshStandardMaterial({
    color: 0x1a1a28,
    roughness: 0.9,
    metalness: 0.05
  });
  const ground = new THREE.Mesh(groundGeo, groundMat);
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);

  const grid = new THREE.GridHelper(80, 40, 0x334455, 0x222233);
  grid.position.y = 0.01;
  scene.add(grid);

  /** @type {Map<number, import("three").Mesh>} */
  const meshes = new Map();
  const sphereGeo = new THREE.SphereGeometry(1, 24, 16);

  function colorForId(id) {
    const hue = (id * 47) % 360;
    return new THREE.Color(`hsl(${hue}, 70%, 55%)`);
  }

  function ensureMesh(body) {
    let mesh = meshes.get(body.id);
    if (!mesh) {
      const mat = new THREE.MeshStandardMaterial({
        color: colorForId(body.id),
        roughness: 0.35,
        metalness: 0.15
      });
      mesh = new THREE.Mesh(sphereGeo, mat);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      scene.add(mesh);
      meshes.set(body.id, mesh);
    }
    return mesh;
  }

  function syncBodies(bodies) {
    const seen = new Set();
    for (const b of bodies) {
      seen.add(b.id);
      const mesh = ensureMesh(b);
      const m = mapBodyTo3D(b);
      mesh.scale.setScalar(m.r);
      mesh.position.set(m.x, m.y, m.z);
    }
    for (const [id, mesh] of meshes) {
      if (!seen.has(id)) {
        scene.remove(mesh);
        // sphereGeo is shared by every body mesh; dispose it only once in dispose().
        mesh.material?.dispose?.();
        meshes.delete(id);
      }
    }
  }

  function resize() {
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    if (w < 1 || h < 1) return;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h, false);
  }

  let dragging = false;
  let prevX = 0, prevY = 0;
  let theta = 0.6, phi = 0.9, radius = 28;

  function updateCamera() {
    camera.position.x = radius * Math.sin(phi) * Math.cos(theta);
    camera.position.y = radius * Math.cos(phi);
    camera.position.z = radius * Math.sin(phi) * Math.sin(theta);
    camera.lookAt(0, 2, 0);
  }
  updateCamera();

  canvas.addEventListener("pointerdown", (e) => {
    dragging = true;
    prevX = e.clientX;
    prevY = e.clientY;
    canvas.setPointerCapture(e.pointerId);
  });
  canvas.addEventListener("pointerup", () => { dragging = false; });
  canvas.addEventListener("pointermove", (e) => {
    if (!dragging) return;
    const dx = e.clientX - prevX;
    const dy = e.clientY - prevY;
    prevX = e.clientX;
    prevY = e.clientY;
    theta += dx * 0.005;
    phi = Math.max(0.15, Math.min(Math.PI / 2 - 0.05, phi - dy * 0.005));
    updateCamera();
  });
  canvas.addEventListener("wheel", (e) => {
    e.preventDefault();
    radius = Math.max(8, Math.min(60, radius + e.deltaY * 0.02));
    updateCamera();
  }, { passive: false });

  function render() {
    renderer.render(scene, camera);
  }

  return {
    scene,
    camera,
    renderer,
    syncBodies,
    resize,
    render,
    dispose() {
      for (const mesh of meshes.values()) {
        scene.remove(mesh);
        mesh.material?.dispose?.();
      }
      meshes.clear();
      sphereGeo.dispose();
      groundGeo.dispose();
      groundMat.dispose();
      renderer.dispose();
    }
  };
}
