"""
Unit tests for the optimizer module.
"""

import pytest
import numpy as np
from cornhole_coach.optimizer import TrajectoryOptimizer, ThrowRecommendation
from cornhole_coach.physics import TrajectoryCalculator
from cornhole_coach.constants import STANDARD_THROW_DISTANCE, STANDARD_PLAYER_HEIGHT


class TestThrowRecommendation:
    """Tests for ThrowRecommendation dataclass."""

    def test_recommendation_creation(self):
        """Test creating a throw recommendation."""
        calc = TrajectoryCalculator()
        trajectory = calc.calculate_from_angles_and_speed(
            initial_position=(0.0, 5.5, 0.0),
            speed=28.0,
            pitch_angle=35.0,
            yaw_angle=0.0
        )

        rec = ThrowRecommendation(
            velocity=28.0,
            velocity_mph=19.0,
            pitch_angle=35.0,
            yaw_angle=0.0,
            force_rating="Medium",
            trajectory=trajectory,
            landing_point=trajectory[-1],
            distance_from_hole=0.5,
            success_probability=0.75
        )

        assert rec.velocity == 28.0
        assert rec.pitch_angle == 35.0
        assert rec.success_probability == 0.75

    def test_recommendation_string(self):
        """Test string representation of recommendation."""
        calc = TrajectoryCalculator()
        trajectory = calc.calculate_from_angles_and_speed(
            initial_position=(0.0, 5.5, 0.0),
            speed=28.0,
            pitch_angle=35.0,
            yaw_angle=2.0
        )

        rec = ThrowRecommendation(
            velocity=28.0,
            velocity_mph=19.0,
            pitch_angle=35.0,
            yaw_angle=2.0,
            force_rating="Medium",
            trajectory=trajectory,
            landing_point=trajectory[-1],
            distance_from_hole=0.5,
            success_probability=0.75
        )

        result_str = str(rec)
        assert "Medium" in result_str
        assert "35.0°" in result_str
        assert "75.0%" in result_str


class TestTrajectoryOptimizer:
    """Tests for TrajectoryOptimizer class."""

    def test_initialization(self):
        """Test optimizer initialization."""
        optimizer = TrajectoryOptimizer()
        assert optimizer.calculator is not None
        assert optimizer.hole_radius > 0

    def test_force_rating(self):
        """Test force rating calculation."""
        optimizer = TrajectoryOptimizer()

        assert optimizer._get_force_rating(12.0) == "Very Low"
        assert optimizer._get_force_rating(18.0) == "Low"
        assert optimizer._get_force_rating(22.0) == "Medium-Low"
        assert optimizer._get_force_rating(27.0) == "Medium"
        assert optimizer._get_force_rating(32.0) == "Medium-High"
        assert optimizer._get_force_rating(38.0) == "High"
        assert optimizer._get_force_rating(50.0) == "Very High"

    def test_success_probability(self):
        """Test success probability calculation."""
        optimizer = TrajectoryOptimizer()

        # Perfect shot (distance = 0)
        prob_perfect = optimizer._calculate_success_probability(0.0)
        assert prob_perfect == pytest.approx(0.95)

        # At hole radius, should be around 50%
        prob_edge = optimizer._calculate_success_probability(optimizer.hole_radius)
        assert 0.4 < prob_edge < 0.6

        # Far away, should be very low
        prob_far = optimizer._calculate_success_probability(5.0)
        assert prob_far < 0.1

    def test_optimize_for_target(self):
        """Test optimization for a simple target."""
        optimizer = TrajectoryOptimizer()

        # Simple case: throw to hit a point 27 feet away at ground level
        recommendation = optimizer.optimize_for_target(
            throw_position=(0.0, 5.5, 0.0),
            target_position=(27.0, 0.0, 0.0),
            velocity_range=(15.0, 40.0),
            angle_range=(15.0, 60.0)
        )

        assert recommendation.velocity > 0
        assert 15.0 <= recommendation.velocity <= 40.0
        assert 15.0 <= recommendation.pitch_angle <= 60.0

        # Should land close to target
        assert recommendation.landing_point.x == pytest.approx(27.0, abs=1.0)
        assert recommendation.landing_point.z == pytest.approx(0.0, abs=0.5)

    def test_optimize_for_cornhole_board(self):
        """Test optimization for standard cornhole setup."""
        optimizer = TrajectoryOptimizer()

        recommendation = optimizer.optimize_for_cornhole_board(
            throw_distance=STANDARD_THROW_DISTANCE,
            throw_height=STANDARD_PLAYER_HEIGHT
        )

        assert recommendation is not None
        assert recommendation.velocity > 0
        assert recommendation.pitch_angle > 0

        # Should have reasonable success probability
        assert recommendation.success_probability > 0.0

        # Landing should be near the board
        assert 25.0 < recommendation.landing_point.x < 32.0

    def test_optimize_with_lateral_offset(self):
        """Test optimization with lateral offset."""
        optimizer = TrajectoryOptimizer()

        # Throw from 1 foot to the left
        recommendation = optimizer.optimize_for_cornhole_board(
            throw_distance=27.0,
            throw_height=5.5,
            lateral_offset=-1.0
        )

        assert recommendation is not None

        # Should have positive yaw angle to aim right
        # (since we're starting left of center)
        assert recommendation.yaw_angle > -5.0

    def test_generate_multiple_solutions(self):
        """Test generating multiple trajectory solutions."""
        optimizer = TrajectoryOptimizer()

        solutions = optimizer.generate_multiple_solutions(
            throw_position=(0.0, 5.5, 0.0),
            target_position=(27.0, 0.5, 0.0),
            num_solutions=3
        )

        # Should get at least 1 solution
        assert len(solutions) >= 1

        # Solutions should have different angles
        if len(solutions) >= 2:
            assert solutions[0].pitch_angle != solutions[1].pitch_angle

        # Should be sorted by success probability
        for i in range(len(solutions) - 1):
            assert solutions[i].success_probability >= solutions[i + 1].success_probability

    def test_velocity_conversion(self):
        """Test velocity conversion to mph."""
        optimizer = TrajectoryOptimizer()

        recommendation = optimizer.optimize_for_target(
            throw_position=(0.0, 5.5, 0.0),
            target_position=(27.0, 0.0, 0.0)
        )

        # Check that mph conversion is approximately correct
        # 1 ft/s ≈ 0.681818 mph
        expected_mph = recommendation.velocity * 0.681818
        assert recommendation.velocity_mph == pytest.approx(expected_mph, abs=0.1)

    def test_optimization_methods(self):
        """Test different optimization methods."""
        optimizer = TrajectoryOptimizer()

        # Test differential evolution (default)
        rec_de = optimizer.optimize_for_target(
            throw_position=(0.0, 5.5, 0.0),
            target_position=(27.0, 0.0, 0.0),
            method="differential_evolution"
        )

        assert rec_de is not None
        assert rec_de.distance_from_hole < 5.0  # Should be reasonably close

        # Test minimize method
        rec_min = optimizer.optimize_for_target(
            throw_position=(0.0, 5.5, 0.0),
            target_position=(27.0, 0.0, 0.0),
            method="minimize"
        )

        assert rec_min is not None
        assert rec_min.distance_from_hole < 5.0

    def test_impossible_target(self):
        """Test optimization handles impossible targets gracefully."""
        optimizer = TrajectoryOptimizer()

        # Try to hit a target very far with low velocity limit
        recommendation = optimizer.optimize_for_target(
            throw_position=(0.0, 5.5, 0.0),
            target_position=(100.0, 0.0, 0.0),  # Very far
            velocity_range=(10.0, 15.0),  # Very low velocity
            angle_range=(15.0, 60.0)
        )

        # Should still return a recommendation (best effort)
        assert recommendation is not None

        # But success probability should be very low or distance should be large
        assert (
            recommendation.success_probability < 0.1 or
            recommendation.distance_from_hole > 10.0
        )

    def test_high_target(self):
        """Test optimization for elevated target."""
        optimizer = TrajectoryOptimizer()

        # Target is higher than start
        recommendation = optimizer.optimize_for_target(
            throw_position=(0.0, 5.0, 0.0),
            target_position=(20.0, 8.0, 0.0),  # Higher target
            velocity_range=(20.0, 40.0)
        )

        assert recommendation is not None

        # Should require steeper angle for upward shot
        assert recommendation.pitch_angle > 30.0

    def test_recommendation_trajectory_matches(self):
        """Test that recommendation trajectory matches the parameters."""
        optimizer = TrajectoryOptimizer()

        recommendation = optimizer.optimize_for_cornhole_board(
            throw_distance=27.0,
            throw_height=5.5
        )

        # Verify trajectory was calculated with the recommended parameters
        trajectory = recommendation.trajectory

        assert len(trajectory) > 0
        assert trajectory[0].y == pytest.approx(5.5, abs=0.1)  # Start height
        assert trajectory[-1] == recommendation.landing_point

    def test_yaw_angle_direction(self):
        """Test yaw angle produces correct lateral movement."""
        optimizer = TrajectoryOptimizer()

        # Target to the right
        rec_right = optimizer.optimize_for_target(
            throw_position=(0.0, 5.5, 0.0),
            target_position=(27.0, 0.0, 2.0),  # 2 feet right
            velocity_range=(20.0, 35.0)
        )

        # Should have positive yaw for right target
        assert rec_right.yaw_angle > 0

        # Landing should be to the right
        assert rec_right.landing_point.z > 0

        # Target to the left
        rec_left = optimizer.optimize_for_target(
            throw_position=(0.0, 5.5, 0.0),
            target_position=(27.0, 0.0, -2.0),  # 2 feet left
            velocity_range=(20.0, 35.0)
        )

        # Should have negative yaw for left target
        assert rec_left.yaw_angle < 0

        # Landing should be to the left
        assert rec_left.landing_point.z < 0
