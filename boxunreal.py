from ue5env import UE5EnvWrapper
from boxnavigator import Action, BoxNavigatorBase

from math import degrees
from pathlib import Path
from time import sleep


class UENavigatorWrapper:
    """A wrapper for navigators that facilitates coordination with UnrealEngine 5."""

    def __init__(
        self,
        navigator: BoxNavigatorBase,
        dataset_path: str,
        ue_image_path: str,
        port: int = 9000,
        save_images: bool = False,
    ) -> None:

        self.ue5 = UE5EnvWrapper(port)

        self.navigator = navigator
        self.dataset_path = Path(dataset_path)
        self.ue_image_path = Path(ue_image_path)
        self.save_images = save_images

        # Sync UE and boxsim
        self.sync_positions()
        self.sync_rotation()
        self.reset()

        # Create the dataset directory if it doesn't exist
        self.dataset_path.mkdir(parents=True, exist_ok=True)

        self.images_saved = 0

    def at_final_target(self):
        return self.navigator.at_final_target()

    def display(self, ax, scale):
        return self.navigator.display(ax, scale)

    def reset(self):
        return self.ue5.reset()

    def sync_positions(self) -> None:
        """Move UE agent to match boxsim agent."""

        # Get z position from UE
        _, _, unreal_z = self.ue5.get_camera_location(0)

        # Get x, y position from boxsim
        x, y = self.navigator.position.xy()

        self.ue5.set_camera_location(x, y, unreal_z)

    # def sync_box_position_to_unreal(self) -> None:
    #     """Move Boxsim agent to match Unreal Agent Position"""
    #     unrealX, unrealY, _ = self.ue5.get_camera_location(0)
    #     self.navigator.move(Pt(unrealX, unrealY))

    def sync_rotation(self) -> None:
        """Sync UE agent location to box agent."""
        # Conversion from Box to unreal location is (180 - boxYaw) = unrealYaw
        unreal_yaw: float = degrees(self.navigator.rotation)
        self.ue5.set_camera_yaw(unreal_yaw, 0)

    def take_action(self) -> tuple[Action, Action]:
        """Execute action in the navigator and in the UE agent.

        Returns:
            tuple[Action, Action]: return action taken and correct action.

        Raises:
            RuntimeError: If the action is not defined.
        """

        action_taken, correct_action = self.navigator.take_action()
        if self.save_images:
            self.save_image(correct_action)

        if action_taken == Action.FORWARD:
            self.ue5.forward(
                #self.navigator.translation_increment
            )  # TODO: once forward and back functions fixed, update accordingly
        elif action_taken == Action.BACKWARD:
            self.ue5.back(self.navigator.translation_increment)
        elif action_taken == Action.ROTATE_LEFT:
            self.sync_rotation()
        elif action_taken == Action.ROTATE_RIGHT:
            self.sync_rotation()
        else:
            raise RuntimeError(f"Undefined action: {action_taken}")

        return action_taken, correct_action

    def save_image(self, action: Action) -> None:

        # Rotations are swapped in UE
        if action == Action.ROTATE_LEFT:
            action = Action.ROTATE_RIGHT
        elif action == Action.ROTATE_RIGHT:
            action = Action.ROTATE_LEFT

        # Generate the next filename
        image_filepath = (
            self.dataset_path / f"{self.images_saved:06}_{str(action).lower()}.png"
        )
        self.images_saved += 1

        # Tell UE to save an image
        self.ue5.save_image(0)

        # Sleep to give time for the image to save
        # TODO: maybe loop until the image exists?
        sleep(2)

        # Move the UE image to the dataset directory
        self.ue_image_path.rename(image_filepath)
