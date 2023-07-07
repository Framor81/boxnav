import math
from argparse import ArgumentParser, Namespace

# from boxunreal import UENavigatorWrapper
from box.boxunreal import UENavigatorWrapper
from box.box import Box, Pt
from box.boxenv import BoxEnv
from box.boxnavigator import PerfectNavigator, WanderingNavigator

import matplotlib.pyplot as plt
from celluloid import Camera

# TODO: this should probably be a command line argument (pass in a list of coordinates)
# route 2, uses path w/ water fountain & stairs
boxes = [
    Box(Pt(-185, 1060), Pt(420, 1060), Pt(420, -350), Pt(10, 420)),
    Box(Pt(-1110, 590), Pt(420, 590), Pt(420, 245), Pt(-770, 420)),
    Box(Pt(-855, -100), Pt(-855, 590), Pt(-700, 590), Pt(-780, 0)),
    Box(Pt(-700, 65), Pt(-700, -100), Pt(-4690, -100), Pt(-4500, -32)),
    Box(Pt(-4690, 65), Pt(-4415, 65), Pt(-4415, -2400), Pt(-4570, -433)),
    Box(Pt(-4415, -295), Pt(-4415, -640), Pt(-5755, -640), Pt(-5590, -450)),
    Box(Pt(-5530, -2400), Pt(-5755, -2400), Pt(-5755, 2845), Pt(-5655, 1983)),
    # Box(Pt(-5755, 1680), Pt(-5755, -2350), Pt(-4600, 2350), Pt(-5000, 1983)),
]


def simulate(args: Namespace, dataset_path: str):
    """Create and update the box environment and run the navigator."""

    env = BoxEnv(boxes)

    agent_position = Pt(0, 0)
    agent_rotation = math.radians(90)

    if args.navigator == "wandering":
        NavigatorConstructor = WanderingNavigator
    elif args.navigator == "perfect":
        NavigatorConstructor = PerfectNavigator
    else:
        raise ValueError("Invalid value for navigator.")

    agent = NavigatorConstructor(
        agent_position, agent_rotation, env, out_of_bounds=args.ue
    )

    # Wrap the agent in a UE wrapper if we're using UE
    if args.ue:
        agent = UENavigatorWrapper(
            agent,
            dataset_path,
            py_server_port=args.py_port,
            ue_server_port=args.ue_port,
            save_images=args.collect,
        )

    fig, ax = plt.subplots()
    camera = Camera(fig)
    while not agent.at_final_target() and agent.num_actions_taken() < args.max_actions:
        action_taken, correct_action = agent.take_action()

        if args.anim_type:
            env.display(ax)
            agent.display(ax, env.scale)
            ax.invert_xaxis()
            camera.snap()
    if args.ue:
        agent.ue5.close_osc()

    if agent.at_final_target():
        print(
            f"Simulation complete, it took {agent.num_actions_taken()} actions to reach the end."
        )
    else:
        print(
            f"Agent was not able to reach target within {agent.num_actions_taken()} actions."
        )

    if args.anim_type:
        print("Saving animation...")
        anim = camera.animate()
        anim.save("output." + args.anim_type)  # type: ignore


def main():
    """Parse arguments and run simulation."""

    argparser = ArgumentParser("Navigate around a box environment.")
    argparser.add_argument("navigator", type=str, help="Navigator to run.")
    argparser.add_argument("dataset_path", type=str, help="Path to dataset.")

    argparser.add_argument("--anim_type", type=str, help="Extension for output format.")
    argparser.add_argument("--ue", action="store_true", help="Connect to UnrealEngine.")
    argparser.add_argument(
        "--py_port", type=int, default=7001, help="Python OSC server port."
    )
    argparser.add_argument(
        "--ue_port", type=int, default=7447, help="UE OSC server port."
    )
    argparser.add_argument("--collect", action="store_true", help="Collect images.")
    argparser.add_argument("--resolution", type=str, help="Set resolution of images.")
    argparser.add_argument(
        "--max_actions", type=int, default=50, help="Maxiumum actions to take."
    )
    args = argparser.parse_args()

    if args.collect and not args.ue:
        raise ValueError("Cannot collect data without connecting to UE.")

    if args.collect and not args.dataset_path:
        raise ValueError("Must provide a dataset path to collect data.")

    # Check port/set default
    # if args.port == None:
    #     args.port = 9000

    simulate(args, args.dataset_path)


if __name__ == "__main__":
    # try:
    main()
    print("Done")
    # except Exception as e:
    #     print(e)
    #     raise SystemExit
