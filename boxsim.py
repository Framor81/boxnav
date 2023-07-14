from argparse import ArgumentParser, Namespace
from math import radians
from pathlib import Path

import matplotlib.pyplot as plt
from celluloid import Camera

from box.box import Box, Pt
from box.boxenv import BoxEnv
from box.boxnavigator import PerfectNavigator, WanderingNavigator
from box.boxunreal import UENavigatorWrapper

# TODO: this should probably be a command line argument (pass in a list of coordinates)
# route 2, uses path w/ water fountain & stairs

boxes = [
    Box(Pt(-185, 1250), Pt(420, 1250), Pt(420, -350), Pt(10, 650)),
    Box(Pt(-1110, 775), Pt(420, 775), Pt(420, 450), Pt(-835, 650)),
    Box(Pt(-910, 100), Pt(-910, 775), Pt(-750, 775), Pt(-820, 200)),
    # Box(Pt(-750, 340), Pt(-750, 100), Pt(-4800, 100), Pt(-4650, 150)),
    # Box(Pt(-4750, 340), Pt(-4480, 340), Pt(-4480, -2200), Pt(-4600, -2000)),
    # Box(Pt(-4480, -1935), Pt(-4480, -2200), Pt(-6450, -640), Pt(-5700, -2000)),
    # Box(Pt(-5525, -2200), Pt(-5830, -2200), Pt(-5830, 3025), Pt(-5780, 2550)),
    # Box(Pt(-5525, 2800), Pt(-5525, 2300), Pt(-4600, 2300), Pt(-6100, 2600)),
]


def simulate(args: Namespace, dataset_path: str) -> None:
    """Create and update the box environment and run the navigator."""

    box_world = BoxEnv(boxes)

    initial_position = Pt(0, 0)
    initial_rotation = radians(90)

    if args.navigator == "wandering":
        NavigatorConstructor = WanderingNavigator
    elif args.navigator == "perfect":
        NavigatorConstructor = PerfectNavigator
    else:
        raise ValueError("Invalid value for navigator.")

    agent = NavigatorConstructor(
        initial_position, initial_rotation, box_world, allow_out_of_bounds=args.ue
    )

    # Wrap the agent if we want to connect to Unreal Engine
    if args.ue:
        agent = UENavigatorWrapper(
            agent,
            args.save_images,
            args.py_port,
            args.ue_port,
        )

    fig, ax = plt.subplots()
    camera = Camera(fig)
    while not agent.at_final_target() and agent.num_actions_taken() < args.max_actions:
        try:
            _, _ = agent.take_action()
        except TimeoutError as e:
            print(e)
            if isinstance(agent, UENavigatorWrapper):
                agent.ue5.close_osc()
            raise SystemExit

        if args.anim_ext:
            box_world.display(ax)
            agent.display(ax, box_world.scale)
            ax.invert_xaxis()
            camera.snap()

    if isinstance(agent, UENavigatorWrapper):
        agent.ue5.close_osc()

    print("Simulation complete.", end=" ")

    num_actions = agent.num_actions_taken()
    if agent.at_final_target():
        print(f"Agent reached final target in {num_actions} actions.")
    else:
        print(f"Agent was unable to reach final target within {num_actions} actions.")

    if args.anim_ext:
        output_filename = None
        num = 1
        while not output_filename or Path(output_filename).exists():
            output_filename = f"output_{num}.{args.anim_ext}"
            num += 1
        anim = camera.animate()
        anim.save(output_filename)
        print(f"Animation saved to {output_filename}.")


def main():
    """Parse arguments and run simulation."""

    argparser = ArgumentParser("Navigate around a box environment.")

    #
    # Required arguments
    #

    argparser.add_argument("navigator", type=str, help="Navigator to run.")

    #
    # Optional arguments
    #

    argparser.add_argument("--anim_ext", type=str, help="Output format for animation.")

    argparser.add_argument(
        "--max_actions", type=int, default=50, help="Maximum allowed actions."
    )

    argparser.add_argument(
        "--save_images",
        type=str,
        help="Directory in which images should be saved (no images saved otherwise).",
    )

    argparser.add_argument(
        "--ue", action="store_true", help="Connect and send command to Unreal Engine."
    )

    argparser.add_argument(
        "--py_port", type=int, default=7001, help="Python OSC server port."
    )

    argparser.add_argument(
        "--ue_port", type=int, default=7447, help="Unreal Engine OSC server port."
    )

    argparser.add_argument(
        "--resolution", type=str, help="Set resolution of images as ResX."
    )

    args = argparser.parse_args()

    possible_navigators = ["wandering", "perfect"]
    if args.navigator not in possible_navigators:
        raise ValueError(
            f"Invalid navigator type: {args.navigator}. Possible options: {'|'.join(possible_navigators)}"
        )

    if args.save_images and not args.ue:
        raise ValueError("Cannot collect data without connecting to Unreal Engine.")

    if args.resolution and not args.ue:
        raise ValueError("Resolution is unnecessary without Unreal Engine.")

    simulate(args, args.save_images)


if __name__ == "__main__":
    main()
