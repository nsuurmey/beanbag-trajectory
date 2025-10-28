"""
Visualization module for trajectory plotting.

Provides tools for visualizing trajectories, board setup, and throw recommendations.
"""

from typing import List, Optional, Tuple
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from .physics import TrajectoryPoint
from .optimizer import ThrowRecommendation
from .constants import (
    STANDARD_BOARD_LENGTH,
    STANDARD_BOARD_WIDTH,
    STANDARD_BOARD_HEIGHT_BACK,
    STANDARD_HOLE_DIAMETER,
)


class TrajectoryVisualizer:
    """Visualizes trajectories and cornhole board setups."""

    def __init__(self, figsize: Tuple[int, int] = (12, 8)):
        """
        Initialize visualizer.

        Args:
            figsize: Figure size for plots (width, height)
        """
        self.figsize = figsize

    def plot_trajectory_2d(
        self,
        trajectory: List[TrajectoryPoint],
        title: str = "Beanbag Trajectory",
        show_board: bool = True,
        board_distance: float = 27.0,
        ax: Optional[plt.Axes] = None
    ) -> plt.Figure:
        """
        Plot trajectory in 2D (side view: distance vs height).

        Args:
            trajectory: List of trajectory points
            title: Plot title
            show_board: Whether to draw the cornhole board
            board_distance: Distance to board front edge (feet)
            ax: Existing axes to plot on (if None, creates new figure)

        Returns:
            Matplotlib figure
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=self.figsize)
        else:
            fig = ax.get_figure()

        # Extract coordinates
        x_coords = [p.x for p in trajectory]
        y_coords = [p.y for p in trajectory]

        # Plot trajectory
        ax.plot(x_coords, y_coords, 'b-', linewidth=2, label='Trajectory')
        ax.plot(x_coords[0], y_coords[0], 'go', markersize=10, label='Start')
        ax.plot(x_coords[-1], y_coords[-1], 'ro', markersize=10, label='Landing')

        # Draw board if requested
        if show_board:
            self._draw_board_2d(ax, board_distance)

        ax.set_xlabel('Distance (feet)', fontsize=12)
        ax.set_ylabel('Height (feet)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_aspect('equal', adjustable='box')

        return fig

    def plot_trajectory_3d(
        self,
        trajectory: List[TrajectoryPoint],
        title: str = "Beanbag Trajectory (3D)",
        show_board: bool = True,
        board_distance: float = 27.0,
        ax: Optional[Axes3D] = None
    ) -> plt.Figure:
        """
        Plot trajectory in 3D.

        Args:
            trajectory: List of trajectory points
            title: Plot title
            show_board: Whether to draw the cornhole board
            board_distance: Distance to board front edge (feet)
            ax: Existing 3D axes to plot on (if None, creates new figure)

        Returns:
            Matplotlib figure
        """
        if ax is None:
            fig = plt.figure(figsize=self.figsize)
            ax = fig.add_subplot(111, projection='3d')
        else:
            fig = ax.get_figure()

        # Extract coordinates
        x_coords = [p.x for p in trajectory]
        y_coords = [p.y for p in trajectory]
        z_coords = [p.z for p in trajectory]

        # Plot trajectory
        ax.plot(x_coords, z_coords, y_coords, 'b-', linewidth=2, label='Trajectory')
        ax.scatter(x_coords[0], z_coords[0], y_coords[0],
                   color='g', s=100, label='Start')
        ax.scatter(x_coords[-1], z_coords[-1], y_coords[-1],
                   color='r', s=100, label='Landing')

        # Draw board if requested
        if show_board:
            self._draw_board_3d(ax, board_distance)

        ax.set_xlabel('Distance (feet)', fontsize=10)
        ax.set_ylabel('Lateral (feet)', fontsize=10)
        ax.set_zlabel('Height (feet)', fontsize=10)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend()

        return fig

    def plot_recommendation(
        self,
        recommendation: ThrowRecommendation,
        board_distance: float = 27.0,
        show_3d: bool = False
    ) -> plt.Figure:
        """
        Plot a throw recommendation with annotations.

        Args:
            recommendation: ThrowRecommendation object
            board_distance: Distance to board front edge (feet)
            show_3d: If True, creates 3D plot; otherwise 2D

        Returns:
            Matplotlib figure
        """
        trajectory = recommendation.trajectory

        if show_3d:
            fig = plt.figure(figsize=self.figsize)
            ax = fig.add_subplot(111, projection='3d')
            self.plot_trajectory_3d(trajectory, ax=ax, board_distance=board_distance)
        else:
            fig, ax = plt.subplots(figsize=self.figsize)
            self.plot_trajectory_2d(trajectory, ax=ax, board_distance=board_distance)

        # Add recommendation text
        info_text = (
            f"Force: {recommendation.force_rating} ({recommendation.velocity_mph:.1f} mph)\n"
            f"Pitch: {recommendation.pitch_angle:.1f}°\n"
            f"Yaw: {recommendation.yaw_angle:.1f}°\n"
            f"Distance from Hole: {recommendation.distance_from_hole * 12:.1f} in\n"
            f"Success: {recommendation.success_probability * 100:.1f}%"
        )

        ax.text(
            0.02, 0.98, info_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        )

        plt.tight_layout()
        return fig

    def plot_multiple_trajectories(
        self,
        trajectories: List[List[TrajectoryPoint]],
        labels: Optional[List[str]] = None,
        title: str = "Multiple Trajectories",
        board_distance: float = 27.0
    ) -> plt.Figure:
        """
        Plot multiple trajectories on the same graph for comparison.

        Args:
            trajectories: List of trajectory lists
            labels: Labels for each trajectory
            title: Plot title
            board_distance: Distance to board front edge (feet)

        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        colors = ['b', 'r', 'g', 'orange', 'purple', 'brown']

        for i, trajectory in enumerate(trajectories):
            x_coords = [p.x for p in trajectory]
            y_coords = [p.y for p in trajectory]

            label = labels[i] if labels and i < len(labels) else f"Trajectory {i+1}"
            color = colors[i % len(colors)]

            ax.plot(x_coords, y_coords, color=color, linewidth=2,
                    label=label, alpha=0.7)
            ax.plot(x_coords[-1], y_coords[-1], 'o', color=color, markersize=8)

        # Draw board
        self._draw_board_2d(ax, board_distance)

        ax.set_xlabel('Distance (feet)', fontsize=12)
        ax.set_ylabel('Height (feet)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_aspect('equal', adjustable='box')

        plt.tight_layout()
        return fig

    def _draw_board_2d(self, ax: plt.Axes, board_distance: float):
        """
        Draw cornhole board in 2D side view.

        Args:
            ax: Matplotlib axes
            board_distance: Distance to board front edge (feet)
        """
        # Board outline
        board_x = [
            board_distance,
            board_distance + STANDARD_BOARD_LENGTH,
            board_distance + STANDARD_BOARD_LENGTH,
            board_distance,
            board_distance
        ]
        board_y = [
            0,
            STANDARD_BOARD_HEIGHT_BACK,
            STANDARD_BOARD_HEIGHT_BACK + 0.1,  # Board thickness
            0.1,
            0
        ]

        ax.fill(board_x, board_y, color='tan', alpha=0.5, label='Board')
        ax.plot(board_x, board_y, 'k-', linewidth=2)

        # Hole position (9 inches from top)
        hole_x = board_distance + STANDARD_BOARD_LENGTH - (9.0 / 12.0)
        hole_y = ((STANDARD_BOARD_LENGTH - 9.0/12.0) / STANDARD_BOARD_LENGTH) * STANDARD_BOARD_HEIGHT_BACK

        ax.plot(hole_x, hole_y, 'ko', markersize=12, label='Hole')
        ax.plot(hole_x, hole_y, 'wo', markersize=8)

    def _draw_board_3d(self, ax: Axes3D, board_distance: float):
        """
        Draw cornhole board in 3D view.

        Args:
            ax: Matplotlib 3D axes
            board_distance: Distance to board front edge (feet)
        """
        # Board corners
        x = [board_distance, board_distance + STANDARD_BOARD_LENGTH]
        y = [-STANDARD_BOARD_WIDTH / 2, STANDARD_BOARD_WIDTH / 2]
        z = [0, STANDARD_BOARD_HEIGHT_BACK]

        # Create mesh grid for board surface
        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X)
        Z[:, 1] = STANDARD_BOARD_HEIGHT_BACK

        # Interpolate Z values
        for i in range(Z.shape[0]):
            Z[i, :] = np.linspace(0, STANDARD_BOARD_HEIGHT_BACK, Z.shape[1])

        ax.plot_surface(X, Y, Z, alpha=0.3, color='tan')

        # Hole position
        hole_x = board_distance + STANDARD_BOARD_LENGTH - (9.0 / 12.0)
        hole_y = 0  # Centered
        hole_z = ((STANDARD_BOARD_LENGTH - 9.0/12.0) / STANDARD_BOARD_LENGTH) * STANDARD_BOARD_HEIGHT_BACK

        ax.scatter(hole_x, hole_y, hole_z, color='black', s=200, marker='o')

    def save_plot(self, fig: plt.Figure, filename: str, dpi: int = 300):
        """
        Save plot to file.

        Args:
            fig: Matplotlib figure
            filename: Output filename
            dpi: Resolution (dots per inch)
        """
        fig.savefig(filename, dpi=dpi, bbox_inches='tight')
        print(f"Plot saved to {filename}")

    @staticmethod
    def show():
        """Display all open plots."""
        plt.show()
