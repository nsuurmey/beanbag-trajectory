"""
Physical constants and standard dimensions for cornhole boards and gameplay.
All measurements are in feet unless otherwise specified.
"""

# Standard cornhole board dimensions (in feet)
STANDARD_BOARD_LENGTH = 4.0  # 4 feet
STANDARD_BOARD_WIDTH = 2.0   # 2 feet
STANDARD_BOARD_HEIGHT_FRONT = 0.0  # Front edge at ground level
STANDARD_BOARD_HEIGHT_BACK = 1.0   # Back edge 12 inches = 1 foot high

# Hole specifications (in feet)
STANDARD_HOLE_DIAMETER = 6.0 / 12.0  # 6 inches = 0.5 feet
STANDARD_HOLE_CENTER_FROM_TOP = 9.0 / 12.0  # 9 inches from top edge
STANDARD_HOLE_CENTER_FROM_SIDE = STANDARD_BOARD_WIDTH / 2  # Centered horizontally

# Standard game setup (in feet)
STANDARD_THROW_DISTANCE = 27.0  # 27 feet between front edges
STANDARD_PLAYER_HEIGHT = 5.5  # Average release height (~5.5 feet)

# Physics constants
GRAVITY = 32.174  # ft/s² (standard gravity)

# Beanbag properties
BEANBAG_WEIGHT = 1.0  # pounds (standard cornhole bag weight)
BEANBAG_DIAMETER = 6.0 / 12.0  # 6 inches = 0.5 feet

# Air resistance coefficient (simplified model)
# For now, we'll assume negligible air resistance for simplicity
# Can be enhanced later with drag coefficient modeling
AIR_RESISTANCE_COEFFICIENT = 0.0

# Tolerance for "in the hole" (in feet)
# A bag landing within this radius of hole center is considered "in"
HOLE_SUCCESS_RADIUS = STANDARD_HOLE_DIAMETER / 2.0
