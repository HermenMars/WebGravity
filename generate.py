from pathlib import Path

ROOT = Path(__file__).resolve().parent

FILES = {
    "CMakeLists.txt": r'''
cmake_minimum_required(VERSION 3.20)

project(WebGLSimulator LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(simulator
    engine/src/main.cpp
    engine/src/Physics.cpp
    engine/src/Simulation.cpp
)

target_include_directories(simulator PRIVATE engine/include)

set_target_properties(simulator PROPERTIES
    SUFFIX ".js"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/web"
)

if(EMSCRIPTEN)
    target_compile_options(simulator PRIVATE
        -O3
        -Wall
        -Wextra
    )

    target_link_options(simulator PRIVATE
        -O3
        -sWASM=1
        -sALLOW_MEMORY_GROWTH=1
        -sNO_EXIT_RUNTIME=1
        -sASSERTIONS=0
        -sEXPORTED_FUNCTIONS=['_main']
    )
endif()
''',

    "engine/include/Particle.hpp": r'''
#pragma once

struct Particle {
    double x = 0.0;
    double y = 0.0;

    double vx = 0.0;
    double vy = 0.0;

    double mass = 0.001;
};
''',

    "engine/include/Physics.hpp": r'''
#pragma once

#include "Particle.hpp"
#include <vector>

namespace Physics {

    void calculateGravity(
        std::vector<Particle>& particles,
        double dt,
        double gravity
    );

}
''',

    "engine/include/Simulation.hpp": r'''
#pragma once

#include "Particle.hpp"
#include <vector>

class Simulation {
public:
    void initialize(int count);
    void update(double dt);

    int getCount() const;

    float getX(int index) const;
    float getY(int index) const;
    float getMass(int index) const;

private:
    std::vector<Particle> particles;

    double gravity = 0.45;
};
''',

    "engine/src/Physics.cpp": r'''
#include "Physics.hpp"

#include <cmath>

namespace Physics {

void calculateGravity(
    std::vector<Particle>& particles,
    double dt,
    double gravity
) {
    const double softening = 0.015;
    const double softening2 = softening * softening;

    std::vector<double> ax(particles.size(), 0.0);
    std::vector<double> ay(particles.size(), 0.0);

    // Calculate gravitational acceleration.

    for (size_t i = 0; i < particles.size(); ++i) {
        for (size_t j = i + 1; j < particles.size(); ++j) {

            double dx = particles[j].x - particles[i].x;
            double dy = particles[j].y - particles[i].y;

            double distance2 = dx * dx + dy * dy + softening2;

            double inverseDistance = 1.0 / std::sqrt(distance2);
            double inverseDistance3 =
                inverseDistance * inverseDistance * inverseDistance;

            double force = gravity * inverseDistance3;

            ax[i] += force * particles[j].mass * dx;
            ay[i] += force * particles[j].mass * dy;

            ax[j] -= force * particles[i].mass * dx;
            ay[j] -= force * particles[i].mass * dy;
        }
    }

    // Semi-implicit Euler integration.

    for (size_t i = 0; i < particles.size(); ++i) {
        particles[i].vx += ax[i] * dt;
        particles[i].vy += ay[i] * dt;

        particles[i].x += particles[i].vx * dt;
        particles[i].y += particles[i].vy * dt;
    }
}

}
''',

    "engine/src/Simulation.cpp": r'''
#include "Simulation.hpp"
#include "Physics.hpp"

#include <cmath>
#include <random>
#include <algorithm>

void Simulation::initialize(int count) {

    particles.clear();

    count = std::clamp(count, 1, 500);

    // Central star.

    Particle star;

    star.x = 0.0;
    star.y = 0.0;
    star.mass = 1.0;

    particles.push_back(star);

    std::mt19937 rng(42);

    std::uniform_real_distribution<double> radiusDist(0.15, 0.85);
    std::uniform_real_distribution<double> angleDist(0.0, 6.28318530718);
    std::uniform_real_distribution<double> massDist(0.001, 0.006);

    for (int i = 0; i < count - 1; ++i) {

        double radius = radiusDist(rng);
        double angle = angleDist(rng);

        double mass = massDist(rng);

        Particle p;

        p.x = radius * std::cos(angle);
        p.y = radius * std::sin(angle);

        p.mass = mass;

        // Approximate circular orbital velocity.

        double velocity = std::sqrt(gravity / radius);

        p.vx = -std::sin(angle) * velocity;
        p.vy = std::cos(angle) * velocity;

        particles.push_back(p);
    }
}

void Simulation::update(double dt) {

    // Substeps improve numerical stability.

    const int substeps = 4;
    double step = dt / substeps;

    for (int i = 0; i < substeps; ++i) {
        Physics::calculateGravity(particles, step, gravity);
    }
}

int Simulation::getCount() const {
    return static_cast<int>(particles.size());
}

float Simulation::getX(int index) const {
    return static_cast<float>(particles.at(index).x);
}

float Simulation::getY(int index) const {
    return static_cast<float>(particles.at(index).y);
}

float Simulation::getMass(int index) const {
    return static_cast<float>(particles.at(index).mass);
}
''',

    "engine/src/main.cpp": r'''
#include "Simulation.hpp"

#include <emscripten.h>

Simulation simulation;

extern "C" {

EMSCRIPTEN_KEEPALIVE
void init_simulation(int count) {
    simulation.initialize(count);
}

EMSCRIPTEN_KEEPALIVE
void step_simulation(double dt) {
    simulation.update(dt);
}

EMSCRIPTEN_KEEPALIVE
int get_body_count() {
    return simulation.getCount();
}

EMSCRIPTEN_KEEPALIVE
float get_body_x(int index) {
    return simulation.getX(index);
}

EMSCRIPTEN_KEEPALIVE
float get_body_y(int index) {
    return simulation.getY(index);
}

EMSCRIPTEN_KEEPALIVE
float get_body_mass(int index) {
    return simulation.getMass(index);
}

}

int main() {
    simulation.initialize(100);
    return 0;
}
''',

    "web/index.html": r'''
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Gravity Simulator</title>

    <link rel="stylesheet" href="style.css">
</head>

<body>

<header>
    <div>
        <h1>Gravity Simulator</h1>
        <p>WebAssembly + WebGL 2.0</p>
    </div>

    <span id="status">Initializing...</span>
</header>

<main>

    <section class="simulation">
        <canvas id="simulationCanvas"></canvas>

        <div class="overlay">
            <span>2D N-BODY SIMULATION</span>
            <span id="bodyCount">Bodies: 0</span>
        </div>
    </section>

    <aside>

        <h2>Simulation controls</h2>

        <button id="pauseButton">Pause</button>
        <button id="resetButton">Reset</button>

        <div class="control">
            <label for="speed">
                Simulation speed
                <span id="speedValue">1.0x</span>
            </label>

            <input
                type="range"
                id="speed"
                min="0.1"
                max="3"
                value="1"
                step="0.1"
            >
        </div>

        <div class="control">
            <label for="particles">
                Number of bodies
                <span id="particleValue">100</span>
            </label>

            <input
                type="range"
                id="particles"
                min="10"
                max="300"
                value="100"
                step="10"
            >
        </div>

        <div class="information">
            <h3>Physics engine</h3>
            <p>Newtonian gravity</p>
            <p>Semi-implicit Euler integration</p>
            <p>4 physics substeps per frame</p>
            <p>Softened gravitational force</p>
        </div>

        <div class="information">
            <h3>Rendering</h3>
            <p>WebGL 2.0</p>
            <p>GPU point rendering</p>
            <p id="fps">FPS: 0</p>
        </div>

    </aside>

</main>

<footer>
    C++20 | WebAssembly | WebGL 2.0
</footer>

<script>
    var Module = {
        onRuntimeInitialized: function() {
            window.simulationReady = true;
            window.dispatchEvent(new Event("wasm-ready"));
        },

        printErr: function(text) {
            console.error(text);
        }
    };
</script>

<script src="simulator.js"></script>
<script src="app.js"></script>

</body>
</html>
''',

    "web/style.css": r'''
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    background: #090d18;
    color: #e5e7eb;
    font-family: Arial, sans-serif;
    min-height: 100vh;
}

header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 22px 30px;
    background: #111827;
    border-bottom: 1px solid #263247;
}

header h1 {
    font-size: 24px;
}

header p {
    color: #94a3b8;
    margin-top: 5px;
}

#status {
    color: #22c55e;
    font-size: 13px;
}

main {
    display: grid;
    grid-template-columns: 1fr 280px;
    gap: 20px;
    padding: 20px;
}

.simulation {
    position: relative;
    min-height: 500px;
    height: calc(100vh - 150px);
    background: #020617;
    border: 1px solid #263247;
    border-radius: 10px;
    overflow: hidden;
}

canvas {
    width: 100%;
    height: 100%;
    display: block;
}

.overlay {
    position: absolute;
    top: 15px;
    left: 15px;
    right: 15px;
    display: flex;
    justify-content: space-between;
    color: #94a3b8;
    font-size: 12px;
    pointer-events: none;
}

aside {
    background: #111827;
    border: 1px solid #263247;
    border-radius: 10px;
    padding: 20px;
}

aside h2 {
    margin-bottom: 20px;
    font-size: 19px;
}

button {
    width: 100%;
    padding: 11px;
    margin-bottom: 10px;
    border: 0;
    border-radius: 5px;
    background: #2563eb;
    color: white;
    cursor: pointer;
    font-size: 14px;
}

button:hover {
    background: #1d4ed8;
}

.control {
    margin-top: 25px;
}

.control label {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    margin-bottom: 12px;
}

input[type="range"] {
    width: 100%;
    accent-color: #3b82f6;
}

.information {
    margin-top: 30px;
    padding-top: 18px;
    border-top: 1px solid #263247;
}

.information h3 {
    margin-bottom: 12px;
}

.information p {
    color: #94a3b8;
    font-size: 12px;
    margin-bottom: 9px;
}

footer {
    padding: 15px;
    text-align: center;
    color: #64748b;
    font-size: 12px;
}

@media(max-width: 850px) {
    main {
        grid-template-columns: 1fr;
    }

    .simulation {
        height: 65vh;
        min-height: 350px;
    }
}
''',

    "web/shaders/vertex.glsl": r'''
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
''',

    "web/shaders/fragment.glsl": r'''
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
''',

    "web/app.js": r'''
const canvas = document.getElementById("simulationCanvas");
const gl = canvas.getContext("webgl2");

if (!gl) {
    document.getElementById("status").textContent =
        "WebGL 2.0 unavailable";
    throw new Error("WebGL 2.0 is required");
}

let program;
let positionBuffer;
let massBuffer;

let paused = false;
let speed = 1.0;
let particleCount = 100;

let positions = new Float32Array(600);
let masses = new Float32Array(300);

let lastFrame = 0;
let frameCounter = 0;
let fpsTimer = 0;

const vertexShaderSource = `#version 300 es
precision highp float;

in vec2 a_position;
in float a_mass;

out float v_mass;

void main() {
    gl_Position = vec4(a_position, 0.0, 1.0);
    v_mass = a_mass;
    gl_PointSize = 3.0 + min(a_mass * 20.0, 18.0);
}`;

const fragmentShaderSource = `#version 300 es
precision highp float;

in float v_mass;
out vec4 FragColor;

void main() {
    vec2 coord = gl_PointCoord - vec2(0.5);
    float d = length(coord);

    if(d > 0.5) discard;

    if(v_mass > 0.5) {
        FragColor = vec4(1.0, 0.72, 0.18, 1.0);
    } else {
        FragColor = vec4(0.35, 0.72, 1.0, 1.0);
    }
}`;

function createShader(type, source) {

    const shader = gl.createShader(type);

    gl.shaderSource(shader, source);
    gl.compileShader(shader);

    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        throw new Error(gl.getShaderInfoLog(shader));
    }

    return shader;
}

function initializeRenderer() {

    const vertexShader = createShader(
        gl.VERTEX_SHADER,
        vertexShaderSource
    );

    const fragmentShader = createShader(
        gl.FRAGMENT_SHADER,
        fragmentShaderSource
    );

    program = gl.createProgram();

    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);

    gl.linkProgram(program);

    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
        throw new Error(gl.getProgramInfoLog(program));
    }

    gl.useProgram(program);

    positionBuffer = gl.createBuffer();
    massBuffer = gl.createBuffer();

    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

    gl.clearColor(0.008, 0.016, 0.04, 1.0);
}

function resizeCanvas() {

    const dpr = Math.min(window.devicePixelRatio || 1, 2);

    const width = Math.floor(canvas.clientWidth * dpr);
    const height = Math.floor(canvas.clientHeight * dpr);

    if (canvas.width !== width || canvas.height !== height) {
        canvas.width = width;
        canvas.height = height;
    }

    gl.viewport(0, 0, canvas.width, canvas.height);
}

function resetSimulation() {

    Module._init_simulation(particleCount);

    const count = Module._get_body_count();

    positions = new Float32Array(count * 2);
    masses = new Float32Array(count);

    document.getElementById("bodyCount").textContent =
        "Bodies: " + count;
}

function updateSimulation(dt) {

    if (paused) return;

    Module._step_simulation(dt * speed);
}

function renderSimulation() {

    const count = Module._get_body_count();

    for (let i = 0; i < count; i++) {

        const x = Module._get_body_x(i);
        const y = Module._get_body_y(i);
        const mass = Module._get_body_mass(i);

        // Convert world coordinates to clip space.

        positions[i * 2] = x;
        positions[i * 2 + 1] = y;

        masses[i] = mass;
    }

    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.useProgram(program);

    // Position attribute.

    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);

    gl.bufferData(
        gl.ARRAY_BUFFER,
        positions,
        gl.DYNAMIC_DRAW
    );

    const positionLocation = gl.getAttribLocation(
        program,
        "a_position"
    );

    gl.enableVertexAttribArray(positionLocation);

    gl.vertexAttribPointer(
        positionLocation,
        2,
        gl.FLOAT,
        false,
        0,
        0
    );

    // Mass attribute.

    gl.bindBuffer(gl.ARRAY_BUFFER, massBuffer);

    gl.bufferData(
        gl.ARRAY_BUFFER,
        masses,
        gl.DYNAMIC_DRAW
    );

    const massLocation = gl.getAttribLocation(
        program,
        "a_mass"
    );

    gl.enableVertexAttribArray(massLocation);

    gl.vertexAttribPointer(
        massLocation,
        1,
        gl.FLOAT,
        false,
        0,
        0
    );

    gl.drawArrays(gl.POINTS, 0, count);
}

function animate(timestamp) {

    if (!lastFrame) lastFrame = timestamp;

    const dt = Math.min((timestamp - lastFrame) / 1000, 0.05);

    lastFrame = timestamp;

    updateSimulation(dt);
    resizeCanvas();
    renderSimulation();

    frameCounter++;

    if (timestamp - fpsTimer >= 1000) {

        document.getElementById("fps").textContent =
            "FPS: " + frameCounter;

        frameCounter = 0;
        fpsTimer = timestamp;
    }

    requestAnimationFrame(animate);
}

// UI controls.

document.getElementById("pauseButton").onclick = function() {

    paused = !paused;

    this.textContent = paused ? "Resume" : "Pause";
};

document.getElementById("resetButton").onclick = function() {
    resetSimulation();
};

document.getElementById("speed").oninput = function() {

    speed = Number(this.value);

    document.getElementById("speedValue").textContent =
        speed.toFixed(1) + "x";
};

document.getElementById("particles").oninput = function() {

    particleCount = Number(this.value);

    document.getElementById("particleValue").textContent =
        particleCount;
};

document.getElementById("particles").onchange = function() {
    resetSimulation();
};

// Start only after WebAssembly is ready.

window.addEventListener("wasm-ready", function() {

    try {

        initializeRenderer();
        resetSimulation();

        document.getElementById("status").textContent =
            "Running";

        requestAnimationFrame(animate);

    } catch(error) {

        console.error(error);

        document.getElementById("status").textContent =
            "Initialization failed";
    }
});

// Handle WebGL context loss.

canvas.addEventListener("webglcontextlost", function(event) {
    event.preventDefault();

    paused = true;

    document.getElementById("status").textContent =
        "WebGL context lost";
});
''',

    "README.md": r'''
# WebGL Gravity Simulator

A 2D N-body gravity simulator using:

- C++20
- WebAssembly
- Emscripten
- WebGL 2.0
- JavaScript
- HTML5 and CSS3
- CMake

## Requirements

- CMake
- Ninja
- Emscripten
- Python 3

## Build

```bash
emcmake cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release

cmake --build build
```

## Run

```bash
cd web
python -m http.server 8000
```

Open:

http://localhost:8000

The generated simulator.js and simulator.wasm files
are placed in the web directory.

## Physics

Newtonian gravitational attraction:

F = G * m1 * m2 / r^2

The simulation uses softened gravity and semi-implicit
Euler integration with four substeps per frame.

## License

MIT
'''
}


def create_project():

    print("\nGenerating WebGL Gravity Simulator...\n")

    for filename, content in FILES.items():

        filepath = ROOT / filename

        filepath.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        filepath.write_text(
            content.strip() + "\n",
            encoding="utf-8"
        )

        print(f"[CREATED] {filename}")

    print("\nProject generated successfully!")
    print(f"Location: {ROOT}")

    print("\nNext steps:")
    print("1. Install Emscripten, CMake and Ninja.")
    print("2. Build the project using emcmake.")
    print("3. Run the local HTTP server.")
    print("\nDone!")


if __name__ == "__main__":
    create_project()