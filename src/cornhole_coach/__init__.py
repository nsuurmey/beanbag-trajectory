"""
Cornhole Coach - Physics Engine for Optimal Trajectory Calculation

This package provides tools for calculating optimal beanbag throw trajectories
for cornhole/bags games using physics-based modeling.
"""

__version__ = "0.1.0"

from .physics import TrajectoryCalculator, TrajectoryPoint
from .optimizer import TrajectoryOptimizer, ThrowRecommendation
from .constants import (
    STANDARD_BOARD_LENGTH,
    STANDARD_BOARD_WIDTH,
    STANDARD_HOLE_DIAMETER,
    STANDARD_THROW_DISTANCE,
    STANDARD_PLAYER_HEIGHT,
    GRAVITY,
)

__all__ = [
    "TrajectoryCalculator",
    "TrajectoryPoint",
    "TrajectoryOptimizer",
    "ThrowRecommendation",
    "STANDARD_BOARD_LENGTH",
    "STANDARD_BOARD_WIDTH",
    "STANDARD_HOLE_DIAMETER",
    "STANDARD_THROW_DISTANCE",
    "STANDARD_PLAYER_HEIGHT",
    "GRAVITY",
]
