# Cornhole Coach - Physics Engine

A robust Python library for calculating optimal beanbag throw trajectories in cornhole/bags games using physics-based modeling. This is the core physics engine that powers the Cornhole Coach mobile application.

## Features

- **Precise Trajectory Calculation**: Uses classical projectile motion physics to calculate beanbag paths
- **3D Trajectory Modeling**: Supports full 3D trajectories with pitch and yaw angles
- **Smart Optimization**: Automatically finds optimal throw parameters (velocity, angle) to hit targets
- **Multiple Solutions**: Generate different throwing styles (low arc, medium arc, high arc)
- **Visualization Tools**: Built-in plotting capabilities for trajectory analysis
- **Comprehensive Testing**: Extensive unit test coverage ensuring accuracy

## Installation

### From Source

```bash
git clone https://github.com/yourusername/beanbag-trajectory.git
cd beanbag-trajectory
pip install -e .
```

### For Development

```bash
pip install -e ".[dev]"
```

## Quick Start

### Basic Trajectory Calculation

```python
from cornhole_coach import TrajectoryCalculator, STANDARD_PLAYER_HEIGHT

calculator = TrajectoryCalculator()

# Calculate trajectory with specific angles and speed
trajectory = calculator.calculate_from_angles_and_speed(
    initial_position=(0.0, STANDARD_PLAYER_HEIGHT, 0.0),
    speed=30.0,        # ft/s
    pitch_angle=35.0,  # degrees
    yaw_angle=0.0      # degrees
)

# Get landing position
landing = trajectory[-1]
print(f"Lands at: {landing.x:.2f} ft forward, {landing.z:.2f} ft lateral")
```

### Find Optimal Throw Parameters

```python
from cornhole_coach import TrajectoryOptimizer, STANDARD_THROW_DISTANCE

optimizer = TrajectoryOptimizer()

# Optimize for standard cornhole setup (27 feet)
recommendation = optimizer.optimize_for_cornhole_board(
    throw_distance=STANDARD_THROW_DISTANCE,
    throw_height=5.5  # feet
)

print(recommendation)
# Output:
# Throw Recommendation:
#   Force: Medium (20.4 mph)
#   Pitch Angle: 36.2°
#   Yaw Angle: 0.0° Straight
#   Distance from Hole: 3.45 inches
#   Success Probability: 87.3%
```

### Visualize Trajectories

```python
from cornhole_coach.visualizer import TrajectoryVisualizer

visualizer = TrajectoryVisualizer()

# Plot the recommended trajectory
fig = visualizer.plot_recommendation(
    recommendation=recommendation,
    board_distance=27.0
)

visualizer.save_plot(fig, "optimal_throw.png")
```

## Physics Model

The physics engine uses classical projectile motion equations:

### Position Equations
- **x(t) = x₀ + vₓ₀ · t** (horizontal distance)
- **y(t) = y₀ + vᵧ₀ · t - ½g · t²** (height)
- **z(t) = z₀ + vᵤ₀ · t** (lateral position)

Where:
- (x, y, z) are position coordinates
- (vₓ₀, vᵧ₀, vᵤ₀) are initial velocity components
- g is gravitational acceleration (32.174 ft/s²)
- t is time

### Velocity Components

From launch angles:
- **vₓ = v₀ · cos(pitch) · cos(yaw)** (forward)
- **vᵧ = v₀ · sin(pitch)** (vertical)
- **vᵤ = v₀ · cos(pitch) · sin(yaw)** (lateral)

## API Reference

### Core Classes

#### `TrajectoryCalculator`
Calculates projectile trajectories for beanbag throws.

```python
calculator = TrajectoryCalculator(gravity=32.174)

# Calculate from velocity components
trajectory = calculator.calculate_trajectory(
    initial_position=(x0, y0, z0),
    initial_velocity=(vx0, vy0, vz0),
    time_step=0.01,
    max_time=5.0
)

# Calculate from angles and speed
trajectory = calculator.calculate_from_angles_and_speed(
    initial_position=(x0, y0, z0),
    speed=30.0,
    pitch_angle=35.0,
    yaw_angle=0.0
)

# Find landing point
landing = calculator.find_landing_point(
    initial_position=(x0, y0, z0),
    initial_velocity=(vx0, vy0, vz0)
)
```

#### `TrajectoryOptimizer`
Optimizes throw parameters to maximize hole success probability.

```python
optimizer = TrajectoryOptimizer()

# Optimize for any target
recommendation = optimizer.optimize_for_target(
    throw_position=(0, 5.5, 0),
    target_position=(27, 0.75, 0),
    velocity_range=(15.0, 40.0),
    angle_range=(15.0, 60.0)
)

# Optimize for cornhole board
recommendation = optimizer.optimize_for_cornhole_board(
    throw_distance=27.0,
    throw_height=5.5,
    lateral_offset=0.0
)

# Generate multiple solutions
solutions = optimizer.generate_multiple_solutions(
    throw_position=(0, 5.5, 0),
    target_position=(27, 0.75, 0),
    num_solutions=3
)
```

#### `ThrowRecommendation`
Contains optimized throw parameters and analysis.

**Attributes:**
- `velocity`: Initial speed (ft/s)
- `velocity_mph`: Initial speed (mph)
- `pitch_angle`: Elevation angle (degrees)
- `yaw_angle`: Horizontal direction (degrees)
- `force_rating`: Descriptive force level (e.g., "Medium", "High")
- `trajectory`: Full trajectory path
- `landing_point`: Where the bag lands
- `distance_from_hole`: Distance from target (feet)
- `success_probability`: Estimated success rate (0-1)

#### `TrajectoryVisualizer`
Visualization tools for trajectories and recommendations.

```python
visualizer = TrajectoryVisualizer()

# 2D plot (side view)
fig = visualizer.plot_trajectory_2d(trajectory, show_board=True)

# 3D plot
fig = visualizer.plot_trajectory_3d(trajectory, show_board=True)

# Plot recommendation with annotations
fig = visualizer.plot_recommendation(recommendation)

# Compare multiple trajectories
fig = visualizer.plot_multiple_trajectories(
    trajectories=[traj1, traj2, traj3],
    labels=["Low Arc", "Medium Arc", "High Arc"]
)

# Save plots
visualizer.save_plot(fig, "output.png", dpi=300)
```

### Constants

Standard cornhole dimensions and physics constants:

```python
from cornhole_coach.constants import (
    STANDARD_BOARD_LENGTH,      # 4.0 feet
    STANDARD_BOARD_WIDTH,       # 2.0 feet
    STANDARD_BOARD_HEIGHT_BACK, # 1.0 foot
    STANDARD_HOLE_DIAMETER,     # 0.5 feet (6 inches)
    STANDARD_THROW_DISTANCE,    # 27.0 feet
    STANDARD_PLAYER_HEIGHT,     # 5.5 feet
    GRAVITY,                    # 32.174 ft/s²
)
```

## Examples

See the `examples/` directory for complete examples:

- **`basic_usage.py`**: Simple trajectory calculations and optimization
- **`advanced_usage.py`**: Advanced scenarios including:
  - Comparing throwing styles (low/medium/high arc)
  - Custom board setups
  - Lateral accuracy testing
  - Velocity sensitivity analysis

Run examples:

```bash
python examples/basic_usage.py
python examples/advanced_usage.py
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cornhole_coach --cov-report=html

# Run specific test file
pytest tests/test_physics.py
```

## Success Metrics (from PRD)

The physics engine is designed to meet these accuracy goals:

- **≥ 85%** of recommended throws (when executed precisely) land within board boundaries
- **≥ 50%** of recommended throws land in the hole
- **≤ 3 seconds** processing time from input to recommendation

## Roadmap

### v0.2.0 (Planned)
- [ ] Air resistance modeling
- [ ] Wind factor integration
- [ ] Spin/rotation effects
- [ ] Different bag weights and materials

### v0.3.0 (Planned)
- [ ] Machine learning-based trajectory prediction
- [ ] Player style profiling
- [ ] Environmental condition adjustments (temperature, altitude)

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Physics equations based on classical mechanics
- Optimization powered by SciPy
- Visualization using Matplotlib

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Built for the Cornhole Coach mobile application**
