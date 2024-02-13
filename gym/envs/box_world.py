"""
Following this tutorial:
https://gymnasium.farama.org/tutorials/gymnasium_basics/environment_creation/
"""

# NOTE: for next time
# - continue ue5osc interface

# TODO: add dependencies to readme
# - gymnasium
# - pillow
# - numpy
# - ue5osc
# - specific python version?


import gymnasium as gym
from gymnasium import spaces

import numpy as np

from ue5osc import Communicator, start_ue

class BoxWorldEnv(gym.Env):


    # TODO: do we need a 'human' mode? we might be able to run UE in headless mode on a server
    # TODO: what is a good FPS? FPS is really controlled by UE
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    # TODO: initialize with shape of saved images
    def __init__(self):
        # TODO: don't hardcode the ports
        self.ue = Communicator("127.0.0.1", 7447, 7001)

        # TODO: start UE game binary

        # TODO: call reset and change settings in game
        # .reset()
        # .set_resolution(...)

        # The 'agent' observes an image rendered by UE
        # TODO: where do we set the image resolution
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(500, 700, 3), dtype=np.uint8
        )

        # The 'agent' can take 4 actions: move forward, move backward, turn left, turn right
        self.action_space = spaces.Discrete(4)

        # TODO: hardcode for now (until we figure out UE headless mode)
        self.render_mode = "rgb_array"

    def _get_obs(self):
        pass

    def _get_info(self):
        pass

    def reset(self, seed=None, options=None):
        # Super class (gym.Env) resets for us self.np_random
        super().reset(seed=seed)

        self.ue.reset()

        observation = self._get_obs()
        info = self._get_info()

        # TODO: handle the render mode

        return observation, info

    def step(self, action):

        observation = self._get_obs()
        info = self._get_info()

        # TODO: use ue.get_location() and compare with known end location
        terminated = False

        reward = 1 if terminated else 0

        # TODO: detect if getting stuck
        truncated = False

        return observation, reward, terminated, truncated, info

    def render(self, mode="human"):
        raise NotImplementedError

    def close(self):
        # Close OSC
        # Close UE game binary?
        raise NotImplementedError
