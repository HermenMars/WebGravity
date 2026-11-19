#version 300 es

precision highp float;

in vec2 a_position;
in float a_mass;

out float v_mass;

void main() {

    gl_Position = vec4(a_position, 0.0, 1.0);

    v_mass = a_mass;

    gl_PointSize = 3.0 + min(a_mass * 20.0, 18.0);
}
