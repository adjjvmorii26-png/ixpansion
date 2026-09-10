/**
 * Astral Forge — Crucible Core
 * Applies intentional distortions to lattice state.
 */

const fs = require('fs');
const path = require('path');

const DISTORTIONS = {
  fold:    path.join(__dirname, 'distortions', 'fold.mtx'),
  shear:   path.join(__dirname, 'distortions', 'shear.mtx'),
  liquefy: path.join(__dirname, 'distortions', 'liquefy.mtx'),
  bloom:   path.join(__dirname, 'distortions', 'bloom.mtx')
};

function loadMatrix(name) {
  const file = DISTORTIONS[name] || DISTORTIONS.fold;
  const lines = fs.readFileSync(file, 'utf8')
    .split('\n')
    .filter(l => l && !l.startsWith('#') && l.trim());
  return lines.map(l => l.trim().split(/\s+/).map(Number));
}

function apply(vector, matrix) {
  const [x, y, z] = vector;
  const m = matrix;
  return [
    m[0][0]*x + m[0][1]*y + m[0][2]*z,
    m[1][0]*x + m[1][1]*y + m[1][2]*z,
    m[2][0]*x + m[2][1]*y + m[2][2]*z
  ];
}

function forge(state, distortionName = 'fold') {
  const matrix = loadMatrix(distortionName);
  const input = [
    state.alpha || 0.7,
    state.beta  || 0.7,
    state.gamma || 0.7
  ];
  const output = apply(input, matrix);
  return {
    distortion: distortionName,
    input,
    output: output.map(v => +v.toFixed(4)),
    temperature: +(0.5 + Math.abs(output[0] - input[0]) * 2).toFixed(3)
  };
}

module.exports = { forge, loadMatrix, apply };

if (require.main === module) {
  console.log(JSON.stringify(forge({ alpha: 0.88, beta: 0.81, gamma: 0.74 }, 'bloom'), null, 2));
}
