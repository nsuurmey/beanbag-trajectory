"""
Unit tests for the physics module.
"""

import pytest
import numpy as np
from cornhole_coach.physics import TrajectoryCalculator, TrajectoryPoint


class TestTrajectoryPoint:
    """Tests for TrajectoryPoint dataclass."""

    def test_trajectory_point_creation(self):
        """Test creating a trajectory point."""
        point = TrajectoryPoint(
            x=10.0, y=5.0, z=0.0, t=1.0,
            vx=20.0, vy=10.0, vz=0.0
        )

        assert point.x == 10.0
        assert point.y == 5.0
        assert point.z == 0.0
        assert point.t == 1.0

    def test_position_property(self):
        """Test position property returns numpy array."""
        point = TrajectoryPoint(
            x=10.0, y=5.0, z=2.0, t=1.0,
            vx=20.0, vy=10.0, vz=0.0
        )

        position = point.position
        np.testing.assert_array_equal(position, np.array([10.0, 5.0, 2.0]))

    def test_velocity_property(self):
        """Test velocity property returns numpy array."""
        point = TrajectoryPoint(
            x=10.0, y=5.0, z=0.0, t=1.0,
            vx=20.0, vy=10.0, vz=5.0
        )

        velocity = point.velocity
        np.testing.assert_array_equal(velocity, np.array([20.0, 10.0, 5.0]))

    def test_speed_property(self):
        """Test speed calculation."""
        point = TrajectoryPoint(
            x=10.0, y=5.0, z=0.0, t=1.0,
            vx=3.0, vy=4.0, vz=0.0
        )

        assert point.speed == pytest.approx(5.0)


class TestTrajectoryCalculator:
    """Tests for TrajectoryCalculator class."""

    def test_initialization(self):
        """Test calculator initialization."""
        calc = TrajectoryCalculator()
        assert calc.gravity == pytest.approx(32.174)

        calc_custom = TrajectoryCalculator(gravity=10.0)
        assert calc_custom.gravity == pytest.approx(10.0)

    def test_horizontal_throw(self):
        """Test horizontal throw (0 degree angle)."""
        calc = TrajectoryCalculator()

        # Throw horizontally from 10 feet high at 30 ft/s
        trajectory = calc.calculate_trajectory(
            initial_position=(0.0, 10.0, 0.0),
            initial_velocity=(30.0, 0.0, 0.0),
            time_step=0.1
        )

        assert len(trajectory) > 0

        # First point should be at start
        assert trajectory[0].x == pytest.approx(0.0)
        assert trajectory[0].y == pytest.approx(10.0)

        # Last point should be on ground
        assert trajectory[-1].y == pytest.approx(0.0, abs=0.01)

        # Should land around 23.6 feet away
        # Using t = sqrt(2h/g) = sqrt(20/32.174) ≈ 0.789s
        # distance = vx * t ≈ 30 * 0.789 ≈ 23.67 feet
        assert trajectory[-1].x == pytest.approx(23.67, abs=0.5)

    def test_45_degree_throw(self):
        """Test 45-degree throw."""
        calc = TrajectoryCalculator()

        # Throw at 45 degrees from ground level at 30 ft/s
        trajectory = calc.calculate_from_angles_and_speed(
            initial_position=(0.0, 0.0, 0.0),
            speed=30.0,
            pitch_angle=45.0,
            yaw_angle=0.0
        )

        assert len(trajectory) > 0

        # Should start at origin
        assert trajectory[0].x == pytest.approx(0.0)
        assert trajectory[0].y == pytest.approx(0.0)

        # Should end on ground
        assert trajectory[-1].y == pytest.approx(0.0, abs=0.01)

        # For 45° throw, range R = v²/g
        # R = 30² / 32.174 ≈ 27.95 feet
        expected_range = 30.0 ** 2 / calc.gravity
        assert trajectory[-1].x == pytest.approx(expected_range, abs=1.0)

    def test_vertical_velocity_decreases(self):
        """Test that vertical velocity decreases due to gravity."""
        calc = TrajectoryCalculator()

        trajectory = calc.calculate_trajectory(
            initial_position=(0.0, 0.0, 0.0),
            initial_velocity=(20.0, 20.0, 0.0),
            time_step=0.1,
            max_time=2.0
        )

        # Check that vertical velocity decreases over time
        for i in range(len(trajectory) - 1):
            assert trajectory[i + 1].vy < trajectory[i].vy

    def test_horizontal_velocity_constant(self):
        """Test that horizontal velocity remains constant."""
        calc = TrajectoryCalculator()

        trajectory = calc.calculate_trajectory(
            initial_position=(0.0, 5.0, 0.0),
            initial_velocity=(25.0, 10.0, 0.0),
            time_step=0.1
        )

        # All points should have same horizontal velocity
        for point in trajectory:
            assert point.vx == pytest.approx(25.0)

    def test_find_landing_point(self):
        """Test finding landing point."""
        calc = TrajectoryCalculator()

        landing = calc.find_landing_point(
            initial_position=(0.0, 5.0, 0.0),
            initial_velocity=(20.0, 10.0, 0.0)
        )

        assert landing is not None
        assert landing.y == pytest.approx(0.0, abs=0.001)
        assert landing.x > 0
        assert landing.t > 0

    def test_calculate_required_velocity_2d(self):
        """Test required velocity calculation."""
        calc = TrajectoryCalculator()

        # Calculate velocity needed to hit target 27 feet away at ground level
        velocity = calc.calculate_required_velocity_2d(
            start_height=5.0,
            horizontal_distance=27.0,
            target_height=0.0,  # Ground level target
            launch_angle=30.0
        )

        assert velocity is not None
        assert velocity > 0

        # Verify by calculating trajectory
        trajectory = calc.calculate_from_angles_and_speed(
            initial_position=(0.0, 5.0, 0.0),
            speed=velocity,
            pitch_angle=30.0
        )

        # Should land near target (within 1 foot)
        assert trajectory[-1].x == pytest.approx(27.0, abs=1.0)
        # Should land on or very near ground
        assert trajectory[-1].y == pytest.approx(0.0, abs=0.1)

    def test_impossible_trajectory(self):
        """Test that impossible trajectories return None."""
        calc = TrajectoryCalculator()

        # Try to hit target above maximum parabola height
        velocity = calc.calculate_required_velocity_2d(
            start_height=0.0,
            horizontal_distance=100.0,
            target_height=100.0,  # Impossibly high
            launch_angle=45.0
        )

        assert velocity is None

    def test_ground_intersection(self):
        """Test ground intersection calculation."""
        calc = TrajectoryCalculator()

        # Throw from 10 feet with upward velocity
        t = calc._find_ground_intersection_time(y0=10.0, vy0=10.0, g=32.174)

        assert t is not None
        assert t > 0

        # Verify: y = 10 + 10t - 0.5*32.174*t² = 0
        y_at_t = 10.0 + 10.0 * t - 0.5 * 32.174 * t * t
        assert y_at_t == pytest.approx(0.0, abs=0.001)

    def test_lateral_movement(self):
        """Test lateral (z-axis) movement."""
        calc = TrajectoryCalculator()

        # Throw with lateral velocity
        trajectory = calc.calculate_trajectory(
            initial_position=(0.0, 5.0, 0.0),
            initial_velocity=(20.0, 10.0, 5.0),  # vz = 5 ft/s
            time_step=0.1
        )

        # Landing point should have moved laterally
        assert trajectory[-1].z > 0

        # All points should have same lateral velocity
        for point in trajectory:
            assert point.vz == pytest.approx(5.0)

    def test_yaw_angle(self):
        """Test throwing with yaw angle."""
        calc = TrajectoryCalculator()

        # Throw straight (0° yaw)
        traj_straight = calc.calculate_from_angles_and_speed(
            initial_position=(0.0, 5.0, 0.0),
            speed=30.0,
            pitch_angle=35.0,
            yaw_angle=0.0
        )

        # Throw right (10° yaw)
        traj_right = calc.calculate_from_angles_and_speed(
            initial_position=(0.0, 5.0, 0.0),
            speed=30.0,
            pitch_angle=35.0,
            yaw_angle=10.0
        )

        # Right throw should land further right (positive z)
        assert traj_right[-1].z > traj_straight[-1].z

        # Throw left (-10° yaw)
        traj_left = calc.calculate_from_angles_and_speed(
            initial_position=(0.0, 5.0, 0.0),
            speed=30.0,
            pitch_angle=35.0,
            yaw_angle=-10.0
        )

        # Left throw should land further left (negative z)
        assert traj_left[-1].z < traj_straight[-1].z
