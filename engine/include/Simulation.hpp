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
