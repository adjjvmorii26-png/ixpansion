// Crest Waveforms Fragment
precision mediump float;
uniform float u_time;
uniform vec3 u_generators; // alpha beta delta
varying vec2 v_uv;

void main() {
  float pulse = 0.5 + 0.5 * sin(u_time * 2.0);
  vec3 col = vec3(
    u_generators.x * (0.55 + 0.45 * sin(v_uv.x * 9.5 + u_time)),
    u_generators.y * (0.55 + 0.45 * cos(v_uv.y * 7.0 - u_time)),
    u_generators.z * (0.45 + 0.55 * pulse)
  );
  gl_FragColor = vec4(col, 0.76);
}
