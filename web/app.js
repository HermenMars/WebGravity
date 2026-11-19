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
