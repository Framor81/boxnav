# BoxNav

![Demo of an agent operating in a box environment.](demo.gif)

A simple playground for making an agent navigate around some directed corridors represented as overlapping boxes.

## Getting Started in Unreal Engine

### Dependencies

Unreal Engine is needed for data collection, and you will want to either download our packaged game or the version on Gitea. You will also need to install [ue5osc](https://github.com/arcslaboratory/ue5osc) using the instructions found in its README.

### Beginning the Simulation in UE5

Then kick off the simulation with:

~~~bash
# Runs the navigator in Python
python boxsim.py <navigator>

# Runs the navigator in Python and generates an animated gif
python boxsim.py <navigator> --anim_ext gif

# Runs the navigator in Python and Unreal Engine
python boxsim.py <navigator> --ue

# Runs the navigator in Python and Unreal Engine and generates a dataset
python boxsim.py <navigator> --ue --save_images 'path/to/dataset'
~~~

See the command line arguments listed in `boxsim.py` for more options.

### Other Notes

Right-handed coordinate system.

- Up-Down is y relative to Oldenborg
- Left-right is x relative to Oldenborg
