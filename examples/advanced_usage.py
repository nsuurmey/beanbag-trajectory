"""
Advanced usage example for Cornhole Coach physics engine.

This example demonstrates:
1. Custom board setups (non-standard distances, angles)
2. Accounting for wind or environmental factors
3. Analyzing trajectory characteristics
4. Comparing different throwing styles
"""

from cornhole_coach import (
    TrajectoryCalculator,
    TrajectoryOptimizer,
    STANDARD_PLAYER_HEIGHT,
)
from cornhole_coach.visualizer import TrajectoryVisualizer
import numpy as np


def analyze_trajectory_characteristics(trajectory):
    """
    Analyze and print characteristics of a trajectory.

    Args:
        trajectory: List of TrajectoryPoint objects
    """
    # Find maximum height
    max_height = max(point.y for point in trajectory)
    max_height_point = max(trajectory, key=lambda p: p.y)

    # Calculate total distance
    total_distance = trajectory[-1].x

    # Find peak time
    peak_time = max_height_point.t

    # Calculate average speed
    speeds = [point.speed for point in trajectory]
    avg_speed = np.mean(speeds)

    print(f"  Total distance: {total_distance:.2f} ft")
    print(f"  Maximum height: {max_height:.2f} ft (at t={peak_time:.2f}s)")
    print(f"  Flight time: {trajectory[-1].t:.2f} seconds")
    print(f"  Average speed: {avg_speed:.2f} ft/s ({avg_speed * 0.681818:.2f} mph)")
    print(f"  Landing velocity: {trajectory[-1].speed:.2f} ft/s")


def compare_throwing_styles():
    """Compare different throwing styles (low, medium, high arc)."""
    print("=" * 60)
    print("Comparing Throwing Styles")
    print("=" * 60)
    print()

    optimizer = TrajectoryOptimizer()

    # Target: standard cornhole setup
    throw_pos = (0.0, STANDARD_PLAYER_HEIGHT, 0.0)
    target_pos = (27.0 + 3.25, 0.75, 0.0)  # Hole position

    styles = [
        ("Low Arc", (15.0, 30.0)),
        ("Medium Arc", (30.0, 45.0)),
        ("High Arc", (45.0, 60.0)),
    ]

    results = []

    for style_name, angle_range in styles:
        print(f"{style_name}:")
        print("-" * 40)

        recommendation = optimizer.optimize_for_target(
            throw_position=throw_pos,
            target_position=target_pos,
            angle_range=angle_range
        )

        print(f"  Force: {recommendation.force_rating}")
        print(f"  Velocity: {recommendation.velocity_mph:.1f} mph")
        print(f"  Pitch: {recommendation.pitch_angle:.1f}°")
        print(f"  Success: {recommendation.success_probability * 100:.1f}%")

        analyze_trajectory_characteristics(recommendation.trajectory)
        print()

        results.append((style_name, recommendation))

    # Visualize all styles
    print("Creating comparison visualization...")
    visualizer = TrajectoryVisualizer()

    trajectories = [rec.trajectory for _, rec in results]
    labels = [name for name, _ in results]

    fig = visualizer.plot_multiple_trajectories(
        trajectories=trajectories,
        labels=labels,
        title="Throwing Style Comparison",
        board_distance=27.0
    )

    visualizer.save_plot(fig, "examples/throwing_styles_comparison.png")
    print("Plot saved to: examples/throwing_styles_comparison.png")
    print()


def custom_board_setup():
    """Optimize for a custom board setup."""
    print("=" * 60)
    print("Custom Board Setup")
    print("=" * 60)
    print()

    # Scenario: Playing at 30 feet instead of 27 feet
    custom_distance = 30.0
    player_height = 6.0  # Taller player

    print(f"Setup: {custom_distance} feet, throw height {player_height} feet")
    print("-" * 40)

    optimizer = TrajectoryOptimizer()

    recommendation = optimizer.optimize_for_cornhole_board(
        throw_distance=custom_distance,
        throw_height=player_height
    )

    print(recommendation)
    print()

    analyze_trajectory_characteristics(recommendation.trajectory)
    print()


def lateral_accuracy_test():
    """Test throwing accuracy with lateral offsets."""
    print("=" * 60)
    print("Lateral Accuracy Test")
    print("=" * 60)
    print()

    optimizer = TrajectoryOptimizer()

    # Test throwing from different lateral positions
    lateral_offsets = [-2.0, -1.0, 0.0, 1.0, 2.0]

    print("Testing throws from different lateral positions:")
    print("-" * 40)

    for offset in lateral_offsets:
        recommendation = optimizer.optimize_for_cornhole_board(
            throw_distance=27.0,
            throw_height=STANDARD_PLAYER_HEIGHT,
            lateral_offset=offset
        )

        direction = "Left" if offset < 0 else "Right" if offset > 0 else "Center"
        print(f"{direction:>6} ({offset:+.1f} ft): "
              f"Yaw {recommendation.yaw_angle:+.1f}°, "
              f"Success {recommendation.success_probability * 100:.0f}%")

    print()


def velocity_sensitivity_analysis():
    """Analyze how trajectory changes with different velocities."""
    print("=" * 60)
    print("Velocity Sensitivity Analysis")
    print("=" * 60)
    print()

    calculator = TrajectoryCalculator()
    throw_pos = (0.0, STANDARD_PLAYER_HEIGHT, 0.0)
    pitch_angle = 35.0

    velocities = [20, 25, 30, 35, 40]

    print(f"Fixed pitch angle: {pitch_angle}°")
    print("-" * 40)

    trajectories = []
    labels = []

    for velocity in velocities:
        trajectory = calculator.calculate_from_angles_and_speed(
            initial_position=throw_pos,
            speed=velocity,
            pitch_angle=pitch_angle
        )

        distance = trajectory[-1].x
        max_height = max(point.y for point in trajectory)

        print(f"Velocity {velocity} ft/s ({velocity * 0.681818:.1f} mph): "
              f"Distance {distance:.1f} ft, Max height {max_height:.1f} ft")

        trajectories.append(trajectory)
        labels.append(f"{velocity} ft/s")

    # Visualize
    print()
    print("Creating visualization...")
    visualizer = TrajectoryVisualizer()

    fig = visualizer.plot_multiple_trajectories(
        trajectories=trajectories,
        labels=labels,
        title="Velocity Sensitivity Analysis",
        board_distance=27.0
    )

    visualizer.save_plot(fig, "examples/velocity_sensitivity.png")
    print("Plot saved to: examples/velocity_sensitivity.png")
    print()


def main():
    """Run all advanced examples."""
    compare_throwing_styles()
    custom_board_setup()
    lateral_accuracy_test()
    velocity_sensitivity_analysis()

    print("=" * 60)
    print("Advanced examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
