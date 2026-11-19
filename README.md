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
