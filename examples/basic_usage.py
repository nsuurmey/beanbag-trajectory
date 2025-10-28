"""
Basic usage example for Cornhole Coach physics engine.

This example demonstrates how to:
1. Calculate a simple trajectory
2. Find optimal throw parameters for a cornhole board
3. Visualize the results
"""

from cornhole_coach import (
    TrajectoryCalculator,
    TrajectoryOptimizer,
    STANDARD_THROW_DISTANCE,
    STANDARD_PLAYER_HEIGHT,
)
from cornhole_coach.visualizer import TrajectoryVisualizer


def main():
    """Run basic usage examples."""
    print("=" * 60)
    print("Cornhole Coach - Basic Usage Example")
    print("=" * 60)
    print()

    # Example 1: Calculate a simple trajectory
    print("Example 1: Calculate a simple trajectory")
    print("-" * 60)

    calculator = TrajectoryCalculator()

    # Throw from 5.5 feet high at 30 ft/s with 35° pitch and 0° yaw
    trajectory = calculator.calculate_from_angles_and_speed(
        initial_position=(0.0, STANDARD_PLAYER_HEIGHT, 0.0),
        speed=30.0,
        pitch_angle=35.0,
        yaw_angle=0.0
    )

    print(f"Trajectory calculated with {len(trajectory)} points")
    print(f"Landing position: x={trajectory[-1].x:.2f} ft, "
          f"y={trajectory[-1].y:.2f} ft, z={trajectory[-1].z:.2f} ft")
    print(f"Flight time: {trajectory[-1].t:.2f} seconds")
    print()

    # Example 2: Optimize for cornhole board
    print("Example 2: Find optimal throw for cornhole board")
    print("-" * 60)

    optimizer = TrajectoryOptimizer()

    # Find best throw for standard 27-foot setup
    recommendation = optimizer.optimize_for_cornhole_board(
        throw_distance=STANDARD_THROW_DISTANCE,
        throw_height=STANDARD_PLAYER_HEIGHT
    )

    print(recommendation)
    print()

    # Example 3: Compare multiple solutions
    print("Example 3: Generate multiple throw options")
    print("-" * 60)

    solutions = optimizer.generate_multiple_solutions(
        throw_position=(0.0, STANDARD_PLAYER_HEIGHT, 0.0),
        target_position=(STANDARD_THROW_DISTANCE + 3.25, 0.75, 0.0),
        num_solutions=3
    )

    for i, solution in enumerate(solutions, 1):
        print(f"\nOption {i} ({solution.force_rating}):")
        print(f"  Velocity: {solution.velocity_mph:.1f} mph")
        print(f"  Pitch: {solution.pitch_angle:.1f}°")
        print(f"  Success: {solution.success_probability * 100:.1f}%")

    print()

    # Example 4: Visualization
    print("Example 4: Visualize trajectory")
    print("-" * 60)
    print("Creating visualization...")

    visualizer = TrajectoryVisualizer()

    # Plot the optimal recommendation
    fig = visualizer.plot_recommendation(
        recommendation=recommendation,
        board_distance=STANDARD_THROW_DISTANCE,
        show_3d=False
    )

    # Save plot
    visualizer.save_plot(fig, "examples/optimal_throw.png")
    print("Plot saved to: examples/optimal_throw.png")

    # Optionally show the plot (requires display)
    # visualizer.show()

    print()
    print("=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
