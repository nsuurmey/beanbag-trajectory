"""
Core physics module for projectile motion calculations.

This module implements the fundamental physics equations for calculating
beanbag trajectories in 3D space, accounting for gravity and initial conditions.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np

from .constants import GRAVITY


@dataclass
class TrajectoryPoint:
    """Represents a single point along a trajectory path."""

    x: float  # Horizontal distance (feet)
    y: float  # Height (feet)
    z: float  # Lateral position (feet)
    t: float  # Time (seconds)
    vx: float  # Velocity in x direction (ft/s)
    vy: float  # Velocity in y direction (ft/s)
    vz: float  # Velocity in z direction (ft/s)

    @property
    def position(self) -> np.ndarray:
        """Return position as numpy array [x, y, z]."""
        return np.array([self.x, self.y, self.z])

    @property
    def velocity(self) -> np.ndarray:
        """Return velocity as numpy array [vx, vy, vz]."""
        return np.array([self.vx, self.vy, self.vz])

    @property
    def speed(self) -> float:
        """Return total speed magnitude."""
        return np.linalg.norm(self.velocity)


class TrajectoryCalculator:
    """
    Calculates projectile trajectories for beanbag throws.

    Uses classical projectile motion equations:
    - x(t) = x0 + vx0 * t
    - y(t) = y0 + vy0 * t - 0.5 * g * t²
    - z(t) = z0 + vz0 * t

    Where:
    - (x, y, z) are position coordinates
    - (vx0, vy0, vz0) are initial velocity components
    - g is gravitational acceleration
    - t is time
    """

    def __init__(self, gravity: float = GRAVITY):
        """
        Initialize the trajectory calculator.

        Args:
            gravity: Gravitational acceleration (ft/s²). Default is standard gravity.
        """
        self.gravity = gravity

    def calculate_trajectory(
        self,
        initial_position: Tuple[float, float, float],
        initial_velocity: Tuple[float, float, float],
        time_step: float = 0.01,
        max_time: float = 5.0,
        stop_at_ground: bool = True
    ) -> List[TrajectoryPoint]:
        """
        Calculate the complete trajectory from initial conditions.

        Args:
            initial_position: Starting position (x0, y0, z0) in feet
            initial_velocity: Initial velocity (vx0, vy0, vz0) in ft/s
            time_step: Time increment for calculations (seconds)
            max_time: Maximum simulation time (seconds)
            stop_at_ground: If True, stop when trajectory hits ground (y <= 0)

        Returns:
            List of TrajectoryPoint objects representing the path
        """
        x0, y0, z0 = initial_position
        vx0, vy0, vz0 = initial_velocity

        trajectory = []
        t = 0.0

        while t <= max_time:
            # Calculate position at time t
            x = x0 + vx0 * t
            y = y0 + vy0 * t - 0.5 * self.gravity * t * t
            z = z0 + vz0 * t

            # Calculate velocity at time t
            vx = vx0
            vy = vy0 - self.gravity * t
            vz = vz0

            # Stop if we've hit the ground
            if stop_at_ground and y < 0 and t > 0:
                # Interpolate to find exact ground intersection
                t_ground = self._find_ground_intersection_time(
                    y0, vy0, self.gravity
                )
                if t_ground is not None:
                    x = x0 + vx0 * t_ground
                    y = 0.0
                    z = z0 + vz0 * t_ground
                    vx = vx0
                    vy = vy0 - self.gravity * t_ground
                    vz = vz0

                    trajectory.append(TrajectoryPoint(
                        x=x, y=y, z=z, t=t_ground,
                        vx=vx, vy=vy, vz=vz
                    ))
                break

            trajectory.append(TrajectoryPoint(
                x=x, y=y, z=z, t=t,
                vx=vx, vy=vy, vz=vz
            ))

            t += time_step

        return trajectory

    def _find_ground_intersection_time(
        self, y0: float, vy0: float, g: float
    ) -> Optional[float]:
        """
        Find the exact time when trajectory intersects the ground (y = 0).

        Solves: 0 = y0 + vy0*t - 0.5*g*t²

        Args:
            y0: Initial height
            vy0: Initial vertical velocity
            g: Gravity

        Returns:
            Time of intersection, or None if no valid solution
        """
        # Quadratic formula: at² + bt + c = 0
        # -0.5*g*t² + vy0*t + y0 = 0
        a = -0.5 * g
        b = vy0
        c = y0

        discriminant = b * b - 4 * a * c

        if discriminant < 0:
            return None

        t1 = (-b + np.sqrt(discriminant)) / (2 * a)
        t2 = (-b - np.sqrt(discriminant)) / (2 * a)

        # Return the positive time (future)
        if t1 > 0 and t2 > 0:
            return min(t1, t2)
        elif t1 > 0:
            return t1
        elif t2 > 0:
            return t2
        else:
            return None

    def calculate_from_angles_and_speed(
        self,
        initial_position: Tuple[float, float, float],
        speed: float,
        pitch_angle: float,
        yaw_angle: float = 0.0,
        **kwargs
    ) -> List[TrajectoryPoint]:
        """
        Calculate trajectory from launch angles and initial speed.

        Args:
            initial_position: Starting position (x0, y0, z0) in feet
            speed: Initial speed magnitude (ft/s)
            pitch_angle: Elevation angle in degrees (0° = horizontal, 90° = straight up)
            yaw_angle: Horizontal direction in degrees (0° = straight ahead, positive = right)
            **kwargs: Additional arguments passed to calculate_trajectory

        Returns:
            List of TrajectoryPoint objects representing the path
        """
        # Convert angles to radians
        pitch_rad = np.radians(pitch_angle)
        yaw_rad = np.radians(yaw_angle)

        # Calculate velocity components
        # vx: forward velocity
        # vy: vertical velocity
        # vz: lateral velocity
        vx = speed * np.cos(pitch_rad) * np.cos(yaw_rad)
        vy = speed * np.sin(pitch_rad)
        vz = speed * np.cos(pitch_rad) * np.sin(yaw_rad)

        return self.calculate_trajectory(
            initial_position=initial_position,
            initial_velocity=(vx, vy, vz),
            **kwargs
        )

    def find_landing_point(
        self,
        initial_position: Tuple[float, float, float],
        initial_velocity: Tuple[float, float, float]
    ) -> Optional[TrajectoryPoint]:
        """
        Find where the trajectory lands (y = 0).

        Args:
            initial_position: Starting position (x0, y0, z0) in feet
            initial_velocity: Initial velocity (vx0, vy0, vz0) in ft/s

        Returns:
            TrajectoryPoint at landing, or None if doesn't land
        """
        x0, y0, z0 = initial_position
        vx0, vy0, vz0 = initial_velocity

        t_land = self._find_ground_intersection_time(y0, vy0, self.gravity)

        if t_land is None or t_land < 0:
            return None

        x = x0 + vx0 * t_land
        y = 0.0
        z = z0 + vz0 * t_land
        vx = vx0
        vy = vy0 - self.gravity * t_land
        vz = vz0

        return TrajectoryPoint(
            x=x, y=y, z=z, t=t_land,
            vx=vx, vy=vy, vz=vz
        )

    def calculate_required_velocity_2d(
        self,
        start_height: float,
        horizontal_distance: float,
        target_height: float,
        launch_angle: float
    ) -> Optional[float]:
        """
        Calculate the required initial velocity for a 2D trajectory.

        Given a launch angle and target position, calculates the required
        initial velocity to reach that target.

        Args:
            start_height: Initial height (feet)
            horizontal_distance: Horizontal distance to target (feet)
            target_height: Target height (feet)
            launch_angle: Launch angle in degrees

        Returns:
            Required initial velocity (ft/s), or None if impossible
        """
        angle_rad = np.radians(launch_angle)

        # Using the trajectory equation solved for v0:
        # v0 = sqrt(g * x² / (2 * cos²(θ) * (x*tan(θ) - Δy)))
        # where Δy = target_height - start_height

        delta_y = target_height - start_height
        cos_angle = np.cos(angle_rad)
        tan_angle = np.tan(angle_rad)

        denominator = 2 * cos_angle * cos_angle * (
            horizontal_distance * tan_angle - delta_y
        )

        if denominator <= 0:
            return None  # Impossible trajectory

        numerator = self.gravity * horizontal_distance * horizontal_distance

        v0_squared = numerator / denominator

        if v0_squared < 0:
            return None

        return np.sqrt(v0_squared)
