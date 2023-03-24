# BoxNav

![](demo.gif)

A simple playground for making an agent navigate around some directed corridors represented as overlapping boxes.

## Getting Started in Unreal Engine

### Dependencies
Create or open an unreal engine project. Ensure you have the [unrealcv]https://github.com/unrealcv/unrealcv plugin file copied into your current project. Ensure you also have the [ue5env]https://github.com/arcslaboratory/ue5env library downloaded. 

### Beginning the Simulation
Clone this repository. Move into the cloned boxenv directory. Press play on your Unreal Engine project.

Then kick off the simulation with:

~~~bash
python boxsim.py --navigator <navigator> --ue --dataset_path <dataset_path> --port <port> --ue_image_path <image_path>
~~~

### Note about Command Line Arguments

The above command specifies the required arguments needed to run the box simulation in Unreal Engine. But there are other optional specifications. Here are all the arguments you can specify:
- ---anim_type \<extension>: (optional) extension for output format.
- ---navigator \<navigator>: must choose between "wandering" and "perfect"
- ---ue: must note if you want to connect to Unreal Engine
- ---collect: (optional) use if you want to collect images
- ---dataset_path \<dataset_path>: must specify a path connected to your dataset folder
- ---ue_image_path \<image_path>: must specify a path to store collected images 

You can look at how these arguments are used in the boxsim.py file.

### Other Notes

Right-handed coordinate system.

- Up-Down is y relative to Oldenborg
- Left-right is x relative to Oldenborg


Things to do:

- Document code
- Add box to box navigation for boy scout (move to next target)
- Implement wanderer navigator
- Create environment using Oldenborg values from Liz (find spreadsheet on Slack)
