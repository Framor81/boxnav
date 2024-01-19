"""
Following this tutorial:
https://gymnasium.farama.org/tutorials/gymnasium_basics/environment_creation/
"""

# TODO: add dependencies to readme (gymnasium, pillow, numpy)


import gymnasium as gym
from gymnasium import spaces

import numpy as np


class BoxWorldEnv(gym.Env):
    # TODO: do we need a 'human' mode? we might be able to run UE in headless mode on a server
    # TODO: what is a good FPS? FPS is really controlled by UE5
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    # TODO:
    # - get_obs
    # - get_info
    # - reset
    # - step
    # - render
    # - close

    # TODO: initialize with shape of saved images
    def __init__(self):

        # TODO: call reset and change settings in game
        # .reset()
        # .set_resolution(...)

        # The 'agent' observes an image rendered by UE5
        # TODO: where do we set the image resolution
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(500, 700, 3), dtype=np.uint8
        )

        # The 'agent' can take 4 actions: move forward, move backward, turn left, turn right
        self.action_space = spaces.Discrete(4)

        # TODO: hardcode for now (until we figure out UE5 headless mode)
        self.render_mode = "rgb_array"
