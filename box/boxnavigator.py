from enum import Enum
from math import atan2, cos, degrees, radians, sin
from random import choice, random, uniform

import matplotlib.pyplot as plt
from matplotlib.patches import Arrow, Wedge, Rectangle

from .box import Pt, close_enough, Box
from .boxenv import BoxEnv


class Action(Enum):
    FORWARD = 0
    BACKWARD = 1
    ROTATE_LEFT = 2
    ROTATE_RIGHT = 3
    TELEPORT = 4

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
        self.stuck = False  # Can only be True in unreal wrapper
        self.previous_target = self.position
        self.current_box = self.env.boxes[0]  # Start in the first box
        self.dominant_direction = self.determine_direction_to_target(self.target)
        self.anchor_1 = self.rotation_anchor(self.target, self.current_box)[0]
        self.anchor_2 = self.rotation_anchor(self.target, self.current_box)[1]

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
            case Action.TELEPORT:
                self.teleport()
            case _:
                raise NotImplementedError("Unknown action.")

        self.actions_taken += 1
        return action_taken, correct_action, self.valid_movement

    def navigator_specific_action(self) -> Action:
        raise NotImplementedError("Implemented in inheriting classes.")

    def determine_direction_to_target(self, current_target: Pt) -> str:
        """Determine the 'direction' to the target based on changes in coordinates."""

        # Get the location from the previous box's target
        previous_target = self.previous_target

        # Calculate the change in coordinates
        delta_x = current_target.x - previous_target.x
        delta_y = current_target.y - previous_target.y

        # Determine the dominant change
        if abs(delta_x) > abs(delta_y):
            if delta_x > 0:
                dominant_direction = "left"
            else:
                dominant_direction = "right"
        else:
            if delta_y > 0:
                dominant_direction = "up"
            else:
                dominant_direction = "down"

        return dominant_direction

    def rotation_anchor(self, current_target: Pt, current_box: Box) -> [Pt]:
        width_half = current_box.width / 2
        height_half = current_box.height / 2

        if self.dominant_direction in ["left", "right"]:
            # Calculate the distance from the center to the left and right sides of the box
            anchor_1 = Pt(current_target.x, current_target.y - height_half)
            anchor_2 = Pt(current_target.x, current_target.y + height_half)

        elif self.dominant_direction in ["up", "down"]:
            # Calculate the distance from the center to the top and bottom sides of the box
            anchor_1 = Pt(current_target.x - width_half, current_target.y)
            anchor_2 = Pt(current_target.x + width_half, current_target.y)

        else:
            # Default to using the current target
            self.anchor_1 = Pt(current_target.x, current_target.y)
            self.anchor_2 = Pt(current_target.x, current_target.y)

        return [Pt(anchor_1.x, anchor_1.y), Pt(anchor_2.x, anchor_2.y)]

    def update_target(self) -> None:
        """Switch to next target when close enough to current target."""
        surrounding_boxes = self.env.get_boxes_enclosing_point(self.position)
        if (
            close_enough(self.position, self.target, self.distance_threshold)
            and len(surrounding_boxes) > 1
        ):
            self.previous_target = self.target
            self.target = surrounding_boxes[-1].target
            self.current_box = surrounding_boxes[-1]  # Update current box
            self.dominant_direction = self.determine_direction_to_target(self.target)
            self.anchor_1 = self.rotation_anchor(self.target, self.current_box)[0]
            self.anchor_2 = self.rotation_anchor(self.target, self.current_box)[1]

    def teleport(self) -> None:
        # Teleport to a random point with a random rotation
        random_point = self.random_point_withing_teleport_region()
        self.checked_move(random_point)
        random_angle = self.random_rotation_within_target_cone(
            self.anchor_1, self.anchor_2
        )
        self.rotation = random_angle

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
        self.position = new_pt

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

        # Check if the environment is of type TeleportingNavigator
        if isinstance(self, TeleportingNavigator):
            self.draw_current_past_rectangle(ax, scale)  # Draw the rectangle
            ax.plot(self.anchor_1.x, self.anchor_1.y, "mx")
            ax.plot(self.anchor_2.x, self.anchor_2.y, "mx")


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


class TeleportingNavigator(BoxNavigatorBase):
    """A navigator that wanders in a teleporting fashion toward the end goal."""

    def __init__(
        self,
        position: Pt,
        rotation: float,
        env: BoxEnv,
        distance_threshold: int,
        forward_increment: float,
        rotation_increment: float,
        ahead_box=None,
    ) -> None:
        super().__init__(
            position,
            rotation,
            env,
            distance_threshold,
            forward_increment,
            rotation_increment,
        )
        # Give variables more descriptive names
        self.possible_actions = [Action.TELEPORT]

        self.ahead_box = ahead_box
        self.counter = 0
        self.box_size = 50
        self.pause_box = False

    def navigator_specific_action(self) -> Action:
        return Action.TELEPORT

    def draw_rectangle_ahead(self, ax: plt.Axes, scale: float) -> None:
        """Draw a rectangle ahead of the agent's current location."""
        # If not the first action set a temporary box
        if self.counter != 1:
            self.temp_box = self.ahead_box

            # Based on dominant direction. Get outer coord of box to set up the box ahead.
            if self.dominant_direction == "up":
                box_position = self.temp_box.upper
            elif self.dominant_direction == "down":
                box_position = self.temp_box.lower
            elif self.dominant_direction == "right":
                box_position = self.temp_box.left
            else:
                box_position = self.temp_box.right
        else:
            box_position = self.position.y

        # if not the first move and the target is within our orange box. Lock that and continue teleporting until we're on top of it.
        if self.counter != 1 and self.temp_box.point_is_inside(self.target):
            self.pause_box = True
        else:
            self.pause_box = False

        # Calculate half the width and height of the rectangle
        half_width = self.current_box.width / 2
        half_height = self.current_box.height / 2

        # Calculate the position where the rectangle will be centered
        if self.dominant_direction == "up":
            ahead_pt = Pt(
                ((self.current_box.right + self.current_box.left) / 2),
                box_position + 0.05 * scale,
            )
            half_height = self.box_size
        elif self.dominant_direction == "down":
            ahead_pt = Pt(
                ((self.current_box.right + self.current_box.left) / 2),
                box_position - 0.05 * scale,
            )
            half_height = self.box_size
        elif self.dominant_direction == "left":  # Coords are switched from left & right
            ahead_pt = Pt(
                (box_position + 0.05 * scale),
                (self.current_box.upper + self.current_box.lower) / 2,
            )
            half_width = self.box_size
        else:
            ahead_pt = Pt(
                (box_position - 0.05 * scale),
                (self.current_box.upper + self.current_box.lower) / 2,
            )
            half_width = self.box_size

        # Calculate the position of the rectangle's center
        rectangle_center_x = ahead_pt.x
        rectangle_center_y = ahead_pt.y

        # Define the points of the rectangle based on the center position
        bottom_left = Pt(
            rectangle_center_x - half_width, rectangle_center_y - half_height
        )
        upper_left = Pt(
            rectangle_center_x - half_width, rectangle_center_y + half_height
        )
        upper_right = Pt(
            rectangle_center_x + half_width, rectangle_center_y + half_height
        )
        target_inside_box = Pt(0, 0)  # This point is at the origin of the box

        # Create a Box instance for the rectangle
        self.ahead_box = Box(bottom_left, upper_left, upper_right, target_inside_box)

        # Check if the ahead_box contains the target
        if self.counter != 1 and self.pause_box:
            self.ahead_box = self.temp_box
        # print(self.ahead_box)

        # Add the rectangle patch to the plot
        ax.add_patch(
            Rectangle(
                self.ahead_box.origin,
                self.ahead_box.width,
                self.ahead_box.height,
                self.ahead_box.angle_degrees,
                facecolor="orange",  # Color of the rectangle
                alpha=0.6,  # Transparency level of the rectangle
            )
        )

    def draw_current_past_rectangle(self, ax: plt.Axes, scale: float) -> None:
        """Draw a rectangle ahead of the agent's current location and it's current box."""
        if self.counter == 1:
            self.draw_rectangle_ahead(ax, scale)
        else:
            self.draw_rectangle_ahead(ax, scale)
            ax.add_patch(
                Rectangle(
                    self.temp_box.origin,
                    self.temp_box.width,
                    self.temp_box.height,
                    self.temp_box.angle_degrees,
                    facecolor="yellow",  # Color of the rectangle
                    alpha=0.6,  # Transparency level of the rectangle
                )
            )

    def random_point_withing_teleport_region(
        self,
    ) -> Pt:  # Generate random x and y coords within the box's bounds
        self.counter += 1
        if self.counter == 1:
            return Pt(self.position.x, self.position.y)
        else:
            x = uniform(self.ahead_box.left, self.ahead_box.right)
            y = uniform(self.ahead_box.lower, self.ahead_box.upper)

            # Create a random point
            random_pt = Pt(x, y)
            return random_pt

    def random_rotation_within_target_cone(self, anchor_1: Pt, anchor_2: Pt) -> float:
        if self.current_box.point_is_inside(self.target):
            # If the target is inside the current box, calculate the angle to the target
            # this is in order to prevent confusing directions where we may face away from the target
            angle = atan2(
                self.target.y - self.position.y, self.target.x - self.position.x
            )
        else:
            # Calculate a random point between anchor_1 and anchor_2
            random_x = uniform(anchor_1.x, anchor_2.x)
            random_y = uniform(anchor_1.y, anchor_2.y)

            # calculate the angle from the agent to this random_point and use this as our angle
            angle = atan2(random_y - self.position.y, random_x - self.position.x)

        return angle
