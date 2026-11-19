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
