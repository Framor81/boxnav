from enum import Enum
from math import cos, degrees, radians, sin
from random import choice, random

import matplotlib.pyplot as plt
from matplotlib.patches import Arrow, Wedge

from .box import Pt, close_enough
from .boxenv import BoxEnv


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
        distance_threshold: int,
        movement_increment: float,
        rotation_increment: float,
    ) -> None:
        """Initialize member variables for any navigator.

        Args:
            position (Pt): initial position
            rotation (float): initial rotation in radians
            env (BoxEnv): box environment
        """
        self.env = env
        self.position = position
        self.rotation = rotation

        self.target = self.env.boxes[0].target
        self.final_target = self.env.boxes[-1].target

        # TODO: find appropriate values for these
        self.distance_threshold = distance_threshold
        self.movement_increment = movement_increment
        self.rotation_increment = rotation_increment
        self.half_target_wedge = radians(6)

        self.actions_taken = 0
        self.current_box = self.env.boxes[0]  # Start in the first box

    def at_final_target(self) -> bool:
        """Is the navigator at the final target."""
        return close_enough(self.position, self.final_target, self.distance_threshold)

    def correct_action(self) -> Action:
        """Compute the 'correct' action given the current position and target."""

        # Compute angle between heading and target
        heading_vector = Pt(cos(self.rotation), sin(self.rotation)).normalized()
        target_vector = (self.target - self.position).normalized()
        self.signed_angle_to_target = heading_vector.angle_between(target_vector)

        # Already facing correct direction
        if abs(self.signed_angle_to_target) < self.half_target_wedge:
            action = Action.FORWARD

        # Need to rotate left (think of unit circle); rotation indicated by positive degrees
        elif self.signed_angle_to_target > 0:
            action = Action.ROTATE_LEFT

        # Need to rotate right (think of unit circle); rotation indicated by negative degrees
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
        self.update_target()

        # Each navigator type will produce its own action
        action_taken = self.navigator_specific_action()

        # Also compute the 'correct' action
        correct_action = self.correct_action()
        self.valid_movement = False

        match action_taken:
            case Action.FORWARD:
                if self.move_forward():
                    self.valid_movement = True
            case Action.ROTATE_LEFT:
                self.rotate_left()
            case Action.ROTATE_RIGHT:
                self.rotate_right()
            case Action.BACKWARD:
                if self.move_backward():
                    self.valid_movement = True
            case _:
                raise NotImplementedError("Unknown action.")

        self.actions_taken += 1
        return action_taken, correct_action, self.valid_movement

    def navigator_specific_action(self) -> Action:
        raise NotImplementedError("Implemented in inheriting classes.")

    def update_target(self) -> None:
        """Switch to next target when close enough to current target."""
        surrounding_boxes = self.env.get_boxes_enclosing_point(self.position)
        if (
            close_enough(self.position, self.target, self.distance_threshold)
            and len(surrounding_boxes) > 1
        ):
            self.target = surrounding_boxes[-1].target
            self.current_box = surrounding_boxes[-1]  # Update current box

    def move_forward(self) -> None:
        """Move forward by a fixed amount."""
        new_x = self.position.x + self.movement_increment * cos(self.rotation)
        new_y = self.position.y + self.movement_increment * sin(self.rotation)
        if self.can_move_to_point(Pt(new_x, new_y)):
            self.checked_move(Pt(new_x, new_y))
            return True

    def move_backward(self) -> None:
        """Move backward by a fixed amount."""
        new_x = self.position.x - self.movement_increment * cos(self.rotation)
        new_y = self.position.y - self.movement_increment * sin(self.rotation)
        if self.can_move_to_point(Pt(new_x, new_y)):
            self.checked_move(Pt(new_x, new_y))
            return True
        return False

    def can_move_to_point(self, pt: Pt) -> bool:
        """Check if the navigator can move to the given point; if the point is inside
        the current box, False otherwise."""
        return self.current_box.point_is_inside(pt)

    def checked_move(self, new_pt: Pt) -> None:
        """Move to the given position if it is within the current target box.

        Args:
            new_pt (Pt): The new position to move to.
        """
        if self.current_box.point_is_inside(new_pt):
            self.position = new_pt
            return True
        else:
            return False

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
            scale (float): scale of arrows and wedge
        """

        # Plot agent and agent's heading
        ax.plot(self.position.x, self.position.y, "ro")
        wedge_lo = degrees(self.rotation - self.half_target_wedge)
        wedge_hi = degrees(self.rotation + self.half_target_wedge)
        ax.add_patch(Wedge(self.position.xy(), scale, wedge_lo, wedge_hi, color="red"))

        # Plot target and line to target
        ax.plot(self.target.x, self.target.y, "go")
        dxy = (self.target - self.position).normalized() * scale
        ax.add_patch(Arrow(self.position.x, self.position.y, dxy.x, dxy.y, color="g"))


class PerfectNavigator(BoxNavigatorBase):
    """A "perfect" navigator that does not make mistakes."""

    def __init__(
        self,
        position: Pt,
        rotation: float,
        env: BoxEnv,
        distance_threshold: int,
        forward_increment: float,
        rotation_increment: float,
    ) -> None:
        super().__init__(
            position,
            rotation,
            env,
            distance_threshold,
            forward_increment,
            rotation_increment,
        )

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
        distance_threshold: int,
        forward_increment: float,
        rotation_increment: float,
        chance_of_random_action: float = 0.25,
    ) -> None:
        super().__init__(
            position,
            rotation,
            env,
            distance_threshold,
            forward_increment,
            rotation_increment,
        )
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
