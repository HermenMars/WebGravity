#version 300 es

precision highp float;

in float v_mass;

out vec4 FragColor;

void main() {

    vec2 coord = gl_PointCoord - vec2(0.5);

    float distanceFromCenter = length(coord);

    if(distanceFromCenter > 0.5) {
        discard;
    }

    if(v_mass > 0.5) {
        FragColor = vec4(1.0, 0.72, 0.18, 1.0);
    } else {
        FragColor = vec4(0.35, 0.72, 1.0, 1.0);
    }
}
