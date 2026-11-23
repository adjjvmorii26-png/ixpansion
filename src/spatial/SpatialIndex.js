/**
 * 3D spatial hash with exact-radius filtering.
 *
 * Entities must expose a finite `position: { x, y, z }` object by
 * default. Supply getPosition(entity) to adapt another data model. No Three.js
 * dependency is required.
 */
export class SpatialIndex {
  constructor({ cellSize = 50, getPosition = (entity) => entity.position } = {}) {
    if (!Number.isFinite(cellSize) || cellSize <= 0) {
      throw new RangeError("cellSize must be finite and > 0");
    }
    if (typeof getPosition !== "function") {
      throw new TypeError("getPosition must be a function");
    }
    this.cellSize = cellSize;
    this.getPosition = getPosition;
    this.grid = new Map();
    this.size = 0;
  }

  clear() {
    this.grid.clear();
    this.size = 0;
  }

  _position(value, name = "position") {
    if (!value || !Number.isFinite(value.x) || !Number.isFinite(value.y) || !Number.isFinite(value.z)) {
      throw new TypeError(name + " must contain finite x, y, z coordinates");
    }
    return value;
  }

  _cell(position) {
    return [
      Math.floor(position.x / this.cellSize),
      Math.floor(position.y / this.cellSize),
      Math.floor(position.z / this.cellSize),
    ];
  }

  _key(cx, cy, cz) {
    return cx + "," + cy + "," + cz;
  }

  insert(entity) {
    const position = this._position(this.getPosition(entity), "entity position");
    const [cx, cy, cz] = this._cell(position);
    const key = this._key(cx, cy, cz);
    if (!this.grid.has(key)) this.grid.set(key, []);
    this.grid.get(key).push(entity);
    this.size += 1;
    return this;
  }

  rebuild(entities) {
    this.clear();
    for (const entity of entities) this.insert(entity);
    return this;
  }

  getNearby(position, radius, { exclude = null } = {}) {
    this._position(position);
    if (!Number.isFinite(radius) || radius < 0) {
      throw new RangeError("radius must be finite and >= 0");
    }
    const [baseCx, baseCy, baseCz] = this._cell(position);
    const cellRadius = Math.ceil(radius / this.cellSize);
    const radiusSquared = radius * radius;
    const nearby = [];

    for (let x = -cellRadius; x <= cellRadius; x++) {
      for (let y = -cellRadius; y <= cellRadius; y++) {
        for (let z = -cellRadius; z <= cellRadius; z++) {
          const cell = this.grid.get(this._key(baseCx + x, baseCy + y, baseCz + z));
          if (!cell) continue;
          for (const entity of cell) {
            if (entity === exclude) continue;
            const p = this._position(this.getPosition(entity), "entity position");
            const dx = p.x - position.x;
            const dy = p.y - position.y;
            const dz = p.z - position.z;
            if (dx * dx + dy * dy + dz * dz <= radiusSquared) nearby.push(entity);
          }
        }
      }
    }
    return nearby;
  }
}
