from enum import Enum
from math import cos, degrees, radians, sin
from random import choice, random

import matplotlib.pyplot as plt
from matplotlib.patches import Arrow, Wedge

from .box import Pt
from .boxenv import BoxEnv


def close_enough(A: Pt, B: Pt, threshold: float = 1) -> bool:
    """Determine whether Pt A is close enough to Pt B depending on the threshold value.

    Args:
        A (Pt): First Pt to compare
        B (Pt): Second Pt to compare
        threshold (float, optional): max distance for being "close". Defaults to 1.

    Returns:
        bool: Is Pt A close enough to Pt B given a threshold
    """
    # TODO: find good threshold value
    distance = (A - B).magnitude()
    return distance < threshold


class Action(Enum):
    FORWARD = 0
    BACKWARD = 1
    ROTATE_LEFT = 2
    ROTATE_RIGHT = 3

    def __str__(self) -> str:
        return self.name


class BoxNavigatorBase:
    """Base class for box navigators.

    A navigator can roam from box to box until it gets to the target
    location of the final box.
    """

    def __init__(
        self,
        position: Pt,
        rotation: float,
        env: BoxEnv,
        allow_out_of_bounds: bool = False,
    ) -> None:
        """Initialize member variables for any navigator.

        Args:
            position (Pt): initial position
            rotation (float): initial rotation in radians
            env (BoxEnv): box environment
            allow_out_of_bounds (bool, optional): whether to allow the navigator to go out of bounds. Defaults to False.
        """
        self.env = env
        self.position = position
        self.rotation = rotation

        self.allow_out_of_bounds = allow_out_of_bounds

        self.target = self.env.boxes[0].target
        # experimental:
        self.is_out_of_bound = False

        # TODO: change from wedge to field-of-view?
        self.half_target_wedge = radians(5)

        # How much a navigator should translate or rotate in a given step
        # of the simulation. These are fairly arbitrary.
        # measured in centimeters
        self.distance_threshold = 50
        self.translation_increment = 50
        self.rotation_increment = radians(5)

        self.actions_taken = 0

    def at_final_target(self) -> bool:
        """Is the navigator at the final target."""
        return close_enough(
            self.position, self.env.boxes[-1].target, self.distance_threshold
        )

    def correct_action(self) -> Action:
        # TODO: docstring
        # TODO: cache this result?

        # Find the correct action by calculating the angle between the
        # target and the heading of the agent.
        heading_vector = Pt(cos(self.rotation), sin(self.rotation)).normalized()
        target_vector = (self.target - self.position).normalized()
        signed_angle_to_target = heading_vector.angle_between(target_vector)

        # Already facing correct direction
        if abs(signed_angle_to_target) < self.half_target_wedge:
            action = Action.FORWARD

        # Need to rotate left (think of unit circle)
        elif signed_angle_to_target > 0:
            action = Action.ROTATE_LEFT

        # Need to rotate right (think of unit circle)
        else:
            action = Action.ROTATE_RIGHT

        return action

    def num_actions_taken(self) -> int:
        return self.actions_taken

    def take_action(self) -> tuple[Action, Action]:
        """Execute a single action in the environment.

        Returns:
            tuple[Action, Action]: return action taken and correct action.
        """
        self.update_target_if_needed()

        action_taken = self.navigator_specific_action()
        self.actions_taken += 1
        correct_action = self.correct_action()

        if action_taken == Action.FORWARD:
            self.move_forward()
        elif action_taken == Action.ROTATE_LEFT:
            self.rotate_left()
        elif action_taken == Action.ROTATE_RIGHT:
            self.rotate_right()
        else:
            self.move_backward()

        return action_taken, correct_action

    def navigator_specific_action(self) -> Action:
        """
        Raises:
            NotImplemented: implement in child classes
        """
        raise NotImplementedError(
            "This method should only be implemented in the inheriting classes."
        )

    def update_target_if_needed(self) -> None:
        """Switch to next target when close enough to current target."""
        surrounding_boxes = self.env.get_boxes(self.position)
        if (
            close_enough(self.position, self.target, self.distance_threshold)
            and len(surrounding_boxes) > 1
        ):
            self.target = surrounding_boxes[-1].target

    def move_forward(self) -> None:
        """Move forward by a fixed amount."""
        new_x = self.position.x + self.translation_increment * cos(self.rotation)
        new_y = self.position.y + self.translation_increment * sin(self.rotation)
        self.move(Pt(new_x, new_y))

    def move_backward(self) -> None:
        """Move backward by a fixed amount."""
        new_x = self.position.x - self.translation_increment * cos(self.rotation)
        new_y = self.position.y - self.translation_increment * sin(self.rotation)
        self.move(Pt(new_x, new_y))

    def move(self, new_pt: Pt) -> None:
        """Jump to the given position if it is within a box.

        Args:
            new_pt (Pt): new position

        Raises:
            NotImplemented: position is not valid
        """

        if self.allow_out_of_bounds or self.env.get_boxes(new_pt):
            self.position = new_pt
            self.is_out_of_bound = False
        else:
            self.is_out_of_bound = True
            # TODO: project to boundary?

    def rotate_right(self) -> None:
        """Rotate to the right by a set amount."""
        self.rotation -= self.rotation_increment

    def rotate_left(self) -> None:
        """Rotate to the left by a set amount."""
        self.rotation += self.rotation_increment

    def display(self, ax: plt.Axes, scale: float) -> None:
        """Plot the agent to the given axis.

        Args:
            ax (plt.Axes): axis for plotting
            scale (float): scale of arrows
        """

        # Plot agent and agent's heading
        ax.plot(self.position.x, self.position.y, "ro")
        wedge_lo = degrees(self.rotation - self.half_target_wedge)
        wedge_hi = degrees(self.rotation + self.half_target_wedge)
        ax.add_patch(Wedge(self.position.xy(), scale, wedge_lo, wedge_hi, color="red"))

        # Plot target and line to target
        ax.plot(self.target.x, self.target.y, "bo")
        dxy = (self.target - self.position).normalized() * scale
        ax.add_patch(Arrow(self.position.x, self.position.y, dxy.x, dxy.y, color="b"))


class PerfectNavigator(BoxNavigatorBase):
    """A "perfect" navigator that does not make mistakes."""

    def __init__(
        self,
        position: Pt,
        rotation: float,
        env: BoxEnv,
        allow_out_of_bounds: bool,
    ) -> None:
        super().__init__(position, rotation, env, allow_out_of_bounds)

    def navigator_specific_action(self) -> Action:
        """The perfect navigator always chooses the correct action."""
        return self.correct_action()


class WanderingNavigator(BoxNavigatorBase):
    """A navigator that wanders in a directed fashion toward the end goal."""

    # TODO: rename this

    def __init__(
        self,
        position: Pt,
        rotation: float,
        env: BoxEnv,
        allow_out_of_bounds: bool,
        chance_of_random_action: float = 0.25,
    ) -> None:
        super().__init__(position, rotation, env, allow_out_of_bounds)
        self.possible_actions = [
            Action.FORWARD,
            Action.ROTATE_LEFT,
            Action.ROTATE_RIGHT,
        ]

        self.chance_of_random_action = chance_of_random_action

    def navigator_specific_action(self) -> Action:
        # Take a random action some percent of the time
        return (
            choice(self.possible_actions)
            if random() < self.chance_of_random_action
            else self.correct_action()
        )
