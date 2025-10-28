"""
Trajectory optimization module for finding optimal throw parameters.

This module uses numerical optimization to find the best launch angle and
velocity to land a beanbag in the cornhole hole.
"""

from dataclasses import dataclass
from typing import Optional, Tuple, List
import numpy as np
from scipy.optimize import minimize, differential_evolution

from .physics import TrajectoryCalculator, TrajectoryPoint
from .constants import (
    STANDARD_HOLE_DIAMETER,
    STANDARD_BOARD_LENGTH,
    STANDARD_BOARD_HEIGHT_BACK,
    HOLE_SUCCESS_RADIUS,
)


@dataclass
class ThrowRecommendation:
    """Recommended throw parameters for a successful cornhole shot."""

    velocity: float  # Initial speed (ft/s)
    velocity_mph: float  # Initial speed (mph)
    pitch_angle: float  # Elevation angle (degrees)
    yaw_angle: float  # Horizontal direction (degrees, 0 = straight)
    force_rating: str  # Descriptive force level
    trajectory: List[TrajectoryPoint]  # Full trajectory path
    landing_point: TrajectoryPoint  # Where bag lands
    distance_from_hole: float  # Distance from hole center (feet)
    success_probability: float  # Estimated probability of success (0-1)

    def __str__(self) -> str:
        """Return human-readable recommendation."""
        return (
            f"Throw Recommendation:\n"
            f"  Force: {self.force_rating} ({self.velocity_mph:.1f} mph)\n"
            f"  Pitch Angle: {self.pitch_angle:.1f}°\n"
            f"  Yaw Angle: {self.yaw_angle:.1f}° {'Left' if self.yaw_angle < 0 else 'Right' if self.yaw_angle > 0 else 'Straight'}\n"
            f"  Distance from Hole: {self.distance_from_hole * 12:.2f} inches\n"
            f"  Success Probability: {self.success_probability * 100:.1f}%"
        )


class TrajectoryOptimizer:
    """
    Optimizes throw parameters to maximize probability of landing in the hole.
    """

    # Force rating thresholds (ft/s)
    FORCE_THRESHOLDS = {
        "Very Low": (0, 15),
        "Low": (15, 20),
        "Medium-Low": (20, 25),
        "Medium": (25, 30),
        "Medium-High": (30, 35),
        "High": (35, 45),
        "Very High": (45, float('inf')),
    }

    def __init__(
        self,
        calculator: Optional[TrajectoryCalculator] = None,
        hole_radius: float = HOLE_SUCCESS_RADIUS
    ):
        """
        Initialize the optimizer.

        Args:
            calculator: TrajectoryCalculator instance. If None, creates default.
            hole_radius: Radius for "success" (feet). Default is hole radius.
        """
        self.calculator = calculator or TrajectoryCalculator()
        self.hole_radius = hole_radius

    def optimize_for_target(
        self,
        throw_position: Tuple[float, float, float],
        target_position: Tuple[float, float, float],
        velocity_range: Tuple[float, float] = (15.0, 40.0),
        angle_range: Tuple[float, float] = (15.0, 60.0),
        method: str = "differential_evolution"
    ) -> ThrowRecommendation:
        """
        Find optimal throw parameters to hit a target position.

        Args:
            throw_position: Starting position (x, y, z) in feet
            target_position: Target position (x, y, z) in feet
            velocity_range: Min and max velocity to consider (ft/s)
            angle_range: Min and max pitch angle to consider (degrees)
            method: Optimization method ('minimize' or 'differential_evolution')

        Returns:
            ThrowRecommendation with optimal parameters
        """
        target_x, target_y, target_z = target_position
        start_x, start_y, start_z = throw_position

        # Calculate required horizontal distance and lateral offset
        horizontal_distance = target_x - start_x
        lateral_distance = target_z - start_z

        def objective_function(params):
            """
            Objective function to minimize: distance from target.

            Args:
                params: [velocity, pitch_angle, yaw_angle]

            Returns:
                Distance from target (squared for smooth optimization)
            """
            velocity, pitch_angle, yaw_angle = params

            # Calculate trajectory
            trajectory = self.calculator.calculate_from_angles_and_speed(
                initial_position=throw_position,
                speed=velocity,
                pitch_angle=pitch_angle,
                yaw_angle=yaw_angle
            )

            if not trajectory:
                return 1e10  # Very high penalty for invalid trajectory

            # Find landing point
            landing = trajectory[-1]

            # Calculate 3D distance from target
            distance = np.sqrt(
                (landing.x - target_x) ** 2 +
                (landing.y - target_y) ** 2 +
                (landing.z - target_z) ** 2
            )

            return distance

        # Set up optimization bounds
        bounds = [
            velocity_range,  # velocity (ft/s)
            angle_range,  # pitch angle (degrees)
            (-15.0, 15.0),  # yaw angle (degrees) - limit lateral adjustment
        ]

        # Initial guess
        x0 = [
            (velocity_range[0] + velocity_range[1]) / 2,
            35.0,  # Start with ~35 degree angle (common throwing angle)
            np.degrees(np.arctan2(lateral_distance, horizontal_distance))
        ]

        # Optimize
        if method == "differential_evolution":
            result = differential_evolution(
                objective_function,
                bounds=bounds,
                seed=42,
                maxiter=300,
                atol=0.01,
                tol=0.01
            )
        else:
            result = minimize(
                objective_function,
                x0=x0,
                bounds=bounds,
                method='L-BFGS-B'
            )

        # Extract optimal parameters
        opt_velocity, opt_pitch, opt_yaw = result.x

        # Calculate final trajectory with optimal parameters
        trajectory = self.calculator.calculate_from_angles_and_speed(
            initial_position=throw_position,
            speed=opt_velocity,
            pitch_angle=opt_pitch,
            yaw_angle=opt_yaw
        )

        landing = trajectory[-1]
        distance_from_target = np.sqrt(
            (landing.x - target_x) ** 2 +
            (landing.y - target_y) ** 2 +
            (landing.z - target_z) ** 2
        )

        # Calculate success probability based on distance from hole
        success_prob = self._calculate_success_probability(distance_from_target)

        # Get force rating
        force_rating = self._get_force_rating(opt_velocity)

        # Convert to mph for user display
        velocity_mph = opt_velocity * 0.681818  # ft/s to mph

        return ThrowRecommendation(
            velocity=opt_velocity,
            velocity_mph=velocity_mph,
            pitch_angle=opt_pitch,
            yaw_angle=opt_yaw,
            force_rating=force_rating,
            trajectory=trajectory,
            landing_point=landing,
            distance_from_hole=distance_from_target,
            success_probability=success_prob
        )

    def optimize_for_cornhole_board(
        self,
        throw_distance: float,
        throw_height: float,
        board_angle: float = 0.0,
        lateral_offset: float = 0.0,
        **kwargs
    ) -> ThrowRecommendation:
        """
        Optimize for a standard cornhole board setup.

        Args:
            throw_distance: Distance from throw position to board front (feet)
            throw_height: Height of throw release point (feet)
            board_angle: Angle of board tilt (degrees). Default assumes standard
                         12" rise over 48" run.
            lateral_offset: Horizontal offset from center (feet, + = right)
            **kwargs: Additional arguments for optimize_for_target

        Returns:
            ThrowRecommendation for hitting the hole
        """
        # Calculate hole position
        # Hole is 9 inches from top edge, centered laterally
        hole_distance_from_front = STANDARD_BOARD_LENGTH - (9.0 / 12.0)

        # If board_angle is 0, calculate from standard dimensions
        if board_angle == 0.0:
            # Standard board: 12" rise over 48" length
            board_angle = np.degrees(
                np.arctan(STANDARD_BOARD_HEIGHT_BACK / STANDARD_BOARD_LENGTH)
            )

        # Calculate hole height above ground
        hole_height = (
            hole_distance_from_front / STANDARD_BOARD_LENGTH
        ) * STANDARD_BOARD_HEIGHT_BACK

        # Throw position
        throw_pos = (0.0, throw_height, lateral_offset)

        # Target position (hole center)
        target_pos = (
            throw_distance + hole_distance_from_front,
            hole_height,
            0.0  # Hole is centered on board
        )

        return self.optimize_for_target(
            throw_position=throw_pos,
            target_position=target_pos,
            **kwargs
        )

    def _calculate_success_probability(self, distance_from_hole: float) -> float:
        """
        Estimate probability of success based on distance from hole center.

        Uses a smooth falloff function based on hole radius.

        Args:
            distance_from_hole: Distance from hole center (feet)

        Returns:
            Probability between 0 and 1
        """
        # Perfect shot (distance = 0) has 95% chance (accounting for bag bounce)
        # At hole radius, probability is 50%
        # Beyond 2x hole radius, probability drops to near 0

        if distance_from_hole <= 0:
            return 0.95

        # Logistic decay function
        k = 5.0  # Decay rate
        x0 = self.hole_radius  # Midpoint

        prob = 0.95 / (1 + np.exp(k * (distance_from_hole - x0) / x0))

        return max(0.0, min(1.0, prob))

    def _get_force_rating(self, velocity: float) -> str:
        """
        Convert velocity to descriptive force rating.

        Args:
            velocity: Velocity in ft/s

        Returns:
            Force rating string
        """
        for rating, (min_vel, max_vel) in self.FORCE_THRESHOLDS.items():
            if min_vel <= velocity < max_vel:
                return rating

        return "Very High"

    def generate_multiple_solutions(
        self,
        throw_position: Tuple[float, float, float],
        target_position: Tuple[float, float, float],
        num_solutions: int = 3
    ) -> List[ThrowRecommendation]:
        """
        Generate multiple valid throw solutions with different arcs.

        This provides options like "low arc", "medium arc", "high arc".

        Args:
            throw_position: Starting position (x, y, z) in feet
            target_position: Target position (x, y, z) in feet
            num_solutions: Number of different solutions to generate

        Returns:
            List of ThrowRecommendation objects, sorted by success probability
        """
        solutions = []

        # Try different angle ranges to get different arc profiles
        angle_ranges = [
            (15.0, 30.0),  # Low arc
            (30.0, 45.0),  # Medium arc
            (45.0, 60.0),  # High arc
        ]

        for angle_range in angle_ranges[:num_solutions]:
            try:
                solution = self.optimize_for_target(
                    throw_position=throw_position,
                    target_position=target_position,
                    angle_range=angle_range
                )
                solutions.append(solution)
            except Exception:
                continue  # Skip if optimization fails for this range

        # Sort by success probability
        solutions.sort(key=lambda s: s.success_probability, reverse=True)

        return solutions
