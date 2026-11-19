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
