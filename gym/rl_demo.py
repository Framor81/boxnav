# NOTE: this is the "proper" way to create an environment
# import gymnasium as gym
# env = gym.make("LunarLander-v2", render_mode="human")

# TODO: change this when the gym is properly installed
import sys
sys.path.append(r'C:\Users\ajcd2020\OneDrive - Pomona College\Documents\ARCSLaboratory\boxnav\gym\envs')
from box_world import BoxWorldEnv

env = BoxWorldEnv()

# Reset the environment
observation, info = env.reset(seed=42)

NUM_STEPS = 4

for _ in range(NUM_STEPS):

    # Select a random action
    action = env.action_space.sample()

    # Execute the randomly selected action
    # - observation: a screenshot from Unreal Engine
    # - reward: some value denoting progress toward the goal
    # - terminated: returns true if the agent made it to the final goal
    # - TODO: what is truncated? (probably a way to denote being stuck)
    # - info: additional information about the environment
    observation, reward, terminated, truncated, info = env.step(action)

    if terminated or truncated:
        observation, info = env.reset()

env.close()

print("Done!")
