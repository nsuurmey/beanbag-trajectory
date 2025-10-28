"""
Unit tests for constants module.
"""

from cornhole_coach.constants import (
    STANDARD_BOARD_LENGTH,
    STANDARD_BOARD_WIDTH,
    STANDARD_BOARD_HEIGHT_BACK,
    STANDARD_HOLE_DIAMETER,
    STANDARD_THROW_DISTANCE,
    GRAVITY,
    HOLE_SUCCESS_RADIUS,
)


def test_board_dimensions():
    """Test standard board dimensions."""
    assert STANDARD_BOARD_LENGTH == 4.0  # 4 feet
    assert STANDARD_BOARD_WIDTH == 2.0  # 2 feet
    assert STANDARD_BOARD_HEIGHT_BACK == 1.0  # 1 foot (12 inches)


def test_hole_dimensions():
    """Test hole dimensions."""
    assert STANDARD_HOLE_DIAMETER == 0.5  # 6 inches = 0.5 feet
    assert HOLE_SUCCESS_RADIUS == 0.25  # Half of diameter


def test_game_setup():
    """Test standard game setup."""
    assert STANDARD_THROW_DISTANCE == 27.0  # 27 feet


def test_physics_constants():
    """Test physics constants."""
    assert GRAVITY > 32.0  # Standard gravity
    assert GRAVITY < 33.0
