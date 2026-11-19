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
