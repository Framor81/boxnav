# BoxNav

![Demo of an agent operating in a box environment.](demo.gif)

A simple playground for making an agent navigate around some directed corridors represented as overlapping boxes.

## Getting Started in Unreal Engine

### Dependencies

Unreal Engine is needed for data collection, and you will want to either download our packaged game or the version on Gitea. You will also need to install [ue5osc](https://github.com/arcslaboratory/ue5osc) using the instructions found in its README.

### Beginning the Simulation in UE5
Clone this repository. Move into the cloned boxnav directory. Press play on your Unreal Engine project.

Then to kick off the simulation you must first ensure the following steps are followed:

1. First, create and activate an anaconda environment.

~~~
conda create --name <env_name>
conda activate <env_name>
~~~

2. Next, install the needed libraries.

~~~
conda install python matplotlib celluloid
python -m pip install python-osc
~~~

3. After cloning the ue5osc library, navigate into this repository and install this library with:

```
cd ue5osc
python -m pip install --editable .
```

4. Now every time you want to run the Boxnav script you must ensure you open the environment with:

```
conda activate <env_name>
```

5. After activating the environment, the script is now ready to run with the commands:

~~~bash
# Runs the navigator in Python
python boxsim.py <navigator>

# Runs the navigator in Python and generates an animated gif
python boxsim.py <navigator> --anim_ext gif

# Runs the navigator in Python and Unreal Engine
python boxsim.py <navigator> --ue

# Runs the navigator in Python and Unreal Engine and generates a dataset
python boxsim.py <navigator> --save_images 'path/to/dataset'
~~~

### Note about Command Line Arguments

The commands above showcase some examples as to how the script can be ran. Please look into the boxsim.py file for details over the arguments that can be passed.

### Notes about Unreal Engine

- In our packaged 'game' you can add the following lines into the Game.ini file found in either:
    - MacOS: (Hidden folder) \<Packaged_Game_Name>\Epic\ARCSAssets\Saved\Config\Mac
    - Windows: \<Packaged_Game_Name>\ARCSAssets\Saved\Config\Windows
```
[/ARCSRobots/SimpleRobotCamera/BP_Pawn_SimpleRobotCamera.BP_Pawn_SimpleRobotCamera_C]
UEPort=<port>
PyPort=<port>
RobotVisible=<Bool>
```

### Other Notes

Right-handed coordinate system.

- Up-Down is y relative to Oldenborg
- Left-right is x relative to Oldenborg
