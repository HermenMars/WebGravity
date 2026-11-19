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
