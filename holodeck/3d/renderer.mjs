/**
 * Holodeck 3D Renderer v0.1
 * Thin Three.js adapter: maps body state to mesh transforms.
 * Physics remains owned by Holodeck Core.
 */

/** @typedef {{ id: number, x: number, y: number, z?: number, radius: number }} BodyState */

export function createRenderer(canvas, THREE) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);
  renderer.shadowMap.enabled = true;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0a0a12);
  scene.fog = new THREE.Fog(0x0a0a12, 40, 120);

  const camera = new THREE.PerspectiveCamera(
    50,
    canvas.clientHeight > 0 ? canvas.clientWidth / canvas.clientHeight : 1,
    0.1,
    200
  );
  camera.position.set(12, 14, 22);
  camera.lookAt(0, 2, 0);

  const ambient = new THREE.AmbientLight(0x6688aa, 0.45);
  const sun = new THREE.DirectionalLight(0xffffff, 1.05);
  sun.position.set(12, 24, 10);
  sun.castShadow = true;
  sun.shadow.mapSize.set(1024, 1024);
  const fill = new THREE.DirectionalLight(0x4466ff, 0.25);
  fill.position.set(-10, 8, -8);
  scene.add(ambient, sun, fill);

  const groundGeo = new THREE.PlaneGeometry(80, 80);
  const groundMat = new THREE.MeshStandardMaterial({
    color: 0x1a1a28, roughness: 0.9, metalness: 0.05
  });
  const ground = new THREE.Mesh(groundGeo, groundMat);
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);

  const grid = new THREE.GridHelper(80, 40, 0x334455, 0x222233);
  grid.position.y = 0.01;
  scene.add(grid);

  /** @type {Map<number, THREE.Mesh>} */
  const meshes = new Map();
  // Shared geometry is owned by the renderer, never by an individual body.
  const sphereGeo = new THREE.SphereGeometry(1, 24, 16);
  let disposed = false;

  function colorForId(id) {
    return new THREE.Color(`hsl(${(id * 47) % 360}, 70%, 55%)`);
  }

  function ensureMesh(body) {
    let mesh = meshes.get(body.id);
    if (!mesh) {
      mesh = new THREE.Mesh(sphereGeo, new THREE.MeshStandardMaterial({
        color: colorForId(body.id), roughness: 0.35, metalness: 0.15
      }));
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      scene.add(mesh);
      meshes.set(body.id, mesh);
    }
    return mesh;
  }

  function syncBodies(bodies) {
    if (disposed) return;
    if (!Array.isArray(bodies)) throw new TypeError("bodies must be an array");
    const seen = new Set();
    for (const body of bodies) {
      if (!body || !Number.isSafeInteger(body.id) || seen.has(body.id) ||
          !Number.isFinite(body.x) || !Number.isFinite(body.y) ||
          !Number.isFinite(body.radius) ||
          (body.z !== undefined && !Number.isFinite(body.z))) {
        throw new TypeError("invalid or duplicate body state");
      }
      seen.add(body.id);
      const mesh = ensureMesh(body);
      const r = Math.max(0.2, body.radius / 14);
      mesh.scale.setScalar(r);
      const hasDepth = typeof body.z === "number";
      const height = hasDepth ? body.y : Math.max(r, (400 - body.y) / 40);
      mesh.position.set((body.x - 400) / 40, height, hasDepth ? body.z : 0);
    }
    for (const [id, mesh] of meshes) {
      if (!seen.has(id)) {
        scene.remove(mesh);
        // Each mesh owns its material. Geometry is shared and disposed once.
        mesh.material?.dispose?.();
        meshes.delete(id);
      }
    }
  }

  function resize() {
    if (disposed) return;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    if (width < 1 || height < 1) return;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height, false);
  }

  let dragging = false;
  let prevX = 0;
  let prevY = 0;
  let theta = 0.6;
  let phi = 0.9;
  let radius = 28;

  function updateCamera() {
    camera.position.x = radius * Math.sin(phi) * Math.cos(theta);
    camera.position.y = radius * Math.cos(phi);
    camera.position.z = radius * Math.sin(phi) * Math.sin(theta);
    camera.lookAt(0, 2, 0);
  }
  updateCamera();

  function onPointerDown(event) {
    if (disposed || event.isPrimary === false) return;
    dragging = true;
    prevX = event.clientX;
    prevY = event.clientY;
    canvas.setPointerCapture?.(event.pointerId);
  }
  function onPointerUp() { dragging = false; }
  function onPointerMove(event) {
    if (disposed || !dragging) return;
    const dx = event.clientX - prevX;
    const dy = event.clientY - prevY;
    prevX = event.clientX;
    prevY = event.clientY;
    theta += dx * 0.005;
    phi = Math.max(0.15, Math.min(Math.PI / 2 - 0.05, phi - dy * 0.005));
    updateCamera();
  }
  function onWheel(event) {
    if (disposed) return;
    event.preventDefault();
    radius = Math.max(8, Math.min(60, radius + event.deltaY * 0.02));
    updateCamera();
  }

  canvas.addEventListener("pointerdown", onPointerDown);
  canvas.addEventListener("pointerup", onPointerUp);
  canvas.addEventListener("pointercancel", onPointerUp);
  canvas.addEventListener("lostpointercapture", onPointerUp);
  canvas.addEventListener("pointermove", onPointerMove);
  canvas.addEventListener("wheel", onWheel, { passive: false });

  function render() {
    if (!disposed) renderer.render(scene, camera);
  }

  function dispose() {
    if (disposed) return;
    disposed = true;
    dragging = false;
    canvas.removeEventListener("pointerdown", onPointerDown);
    canvas.removeEventListener("pointerup", onPointerUp);
    canvas.removeEventListener("pointercancel", onPointerUp);
    canvas.removeEventListener("lostpointercapture", onPointerUp);
    canvas.removeEventListener("pointermove", onPointerMove);
    canvas.removeEventListener("wheel", onWheel);

    for (const mesh of meshes.values()) {
      scene.remove(mesh);
      mesh.material?.dispose?.();
    }
    meshes.clear();
    sphereGeo.dispose();
    groundGeo.dispose();
    groundMat.dispose();
    // GridHelper owns its own geometry and material(s).
    grid.geometry?.dispose?.();
    if (Array.isArray(grid.material)) {
      for (const material of grid.material) material.dispose?.();
    } else {
      grid.material?.dispose?.();
    }
    renderer.dispose();
  }

  return { scene, camera, renderer, syncBodies, resize, render, dispose };
}
