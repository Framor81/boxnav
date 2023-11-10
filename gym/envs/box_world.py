"""
Following this tutorial:
https://gymnasium.farama.org/tutorials/gymnasium_basics/environment_creation/
"""


import gymnasium as gym
from gymnasium import spaces


class BoxWorldEnv(gym.Env):
    # TODO: do we need a 'human' mode?
    # TODO: what is a good FPS?
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    # TODO:
    # - init
    # - get_obs
    # - get_info
    # - reset
    # - step
    # - render
    # - close
