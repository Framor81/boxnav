"""
Following this tutorial:
https://gymnasium.farama.org/tutorials/gymnasium_basics/environment_creation/
"""


# TODO: add dependencies to readme
# - gymnasium
# - pillow
# - numpy
# - ue5osc
# - specific python version?

from pathlib import Path
from time import sleep

import gymnasium as gym
from gymnasium import spaces

from PIL import Image

import numpy as np

from ue5osc import Communicator

class BoxWorldEnv(gym.Env):


    # TODO: do we need a 'human' mode? we might be able to run UE in headless mode on a server
    # TODO: what is a good FPS? FPS is really controlled by UE
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    # TODO: initialize with shape of saved images (set resolution)
    def __init__(self):
        # TODO: don't hardcode the ports (have ue start game binary)
        self.ue = Communicator("127.0.0.1", 7447, 7001)

        try:
            self.ue.get_project_name()
        except TimeoutError:
            print("Start the UE game binary first.")
            raise SystemExit

        self.episode = 0
        self.reset()

        self.observation_space = spaces.Box(
            low=0, high=255, shape=(500, 700, 3), dtype=np.uint8
        )

        # The 'agent' can take 4 actions: move forward, move backward, turn left, turn right
        self.action_space = spaces.Discrete(4)

        # TODO: hardcode for now (until we figure out UE headless mode)
        self.render_mode = "rgb_array"


    def _get_obs(self):
        # TODO: don't hardcode the directory

        output_dir = Path("images").absolute()
        image_filename = output_dir / f"{self.episode:02}-{self.step:04}.png"
        image_filename_str = str(image_filename)

        if not output_dir.exists():
            output_dir.mkdir()

        self.ue.save_image(image_filename_str)

        # TODO: find a better way to determine the exact time to wait
        # For example, loop until the file exists (file will exist on creation not being filled)
        sleep(0.5)

        # TODO: maybe convert to numpy array before returning
        image = Image.open(image_filename)
        return image
        # TODO: also return location?
        # return {"agent": self._agent_location, "target": self._target_location}

    def _get_info(self):
        # NOTE: we may want to return more information (e.g., position)
        return None

    def reset(self, seed=None, options=None):
        # Super class (gym.Env) resets for us self.np_random
        super().reset(seed=seed)

        # TODO: find better values
        self.translation_magnitude = 1
        self.rotation_magnitude = 8

        # TODO: check filename to find next episode number
        self.episode += 1
        self.step = 1

        self.ue.reset()

        # TODO:
        # .set_resolution(...)
        # .set_raycast_length(...)
        # .set_quality(...)
        # set to 1st person camera view

        observation = self._get_obs()
        info = self._get_info()

        # TODO: handle the render mode

        return observation, info

    def step(self, action):

        match action:
            case 0:
                self.ue.move_forward(self.translation_magnitude)
            case 1:
                self.ue.move_backward(self.translation_magnitude)
            case 2:
                self.ue.rotate_left(self.rotation_magnitude)
            case 3:
                self.ue.rotate_right(self.rotation_magnitude)
            case _:
                raise RuntimeError("Invalid code path.")

        observation = self._get_obs()
        info = self._get_info()

        # TODO:
        # - use ue.get_location() and compare with known end location
        # - or add ue.get_distance_to_target() (requires path planning in UE)
        # - ***or use boxenv to get distance to target
        terminated = False

        reward = 1 if terminated else 0

        # TODO: detect if getting stuck
        truncated = False

        return observation, reward, terminated, truncated, info

    def render(self, mode="human"):
        raise NotImplementedError

    def close(self):
        # TODO: Close UE game binary? (handle in ue5osc?)
        self.ue.close_osc()
