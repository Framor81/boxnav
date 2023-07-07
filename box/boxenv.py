from .box import Box, Pt

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


class BoxEnv:
    """A simple 2D environment of interconnected boxes.

    The intended set of boxes works like this:
    1. Each box has a target.
    2. The target should be in an overlapping region between two consecutive boxes.
    3. The final box includes the final target of the entire environment.
    """

    def __init__(self, boxes: list[Box]) -> None:
        """Create boxes to be displayed in the display environment.

        Args:
            boxes (list[Box]): List of boxes to add
        """
        self.boxes = boxes

        # Get scale for plotting
        # TODO: this doesn't work with rotated boxes
        # allow diagonal boxes
        padding = 5
        min_x = min(min(b.A.x, b.B.x, b.C.x) for b in boxes)
        max_x = max(max(b.A.x, b.B.x, b.C.x) for b in boxes)
        min_y = min(min(b.A.y, b.B.y, b.C.y) for b in boxes)
        max_y = max(max(b.A.y, b.B.y, b.C.y) for b in boxes)

        self.xlim = [min_x - padding, max_x + padding]
        self.ylim = [min_y - padding, max_y + padding]
        self.scale = 0.4 * min(abs(max_x - min_x), abs(max_y - min_y))

    def get_boxes(self, pt: Pt) -> list[Box]:
        """Gives a list of the boxes a Pt is in.

        Args:
            pt (Pt): Location of wanderer

        Returns:
            list[Box]: list of boxes a Pt is in
        """
        return [box for box in self.boxes if box.point_is_inside(pt)]

    def display(self, ax: plt.Axes) -> None:
        """Add Boxes to the display environment.

        Args:
            ax (plt.Axes): Axis of the display
        """
        for box in self.boxes:
            ax.add_patch(
                Rectangle(
                    box.origin, box.width, box.height, box.angle_degrees, fill=None
                )
            )
        ax.set_xlim(self.xlim[::-1])
        ax.set_ylim(self.ylim)
        ax.set_aspect("equal")

    def test_display(self) -> None:
        """Test if the display updates."""
        _, ax = plt.subplots(1, 1)
        self.display(ax)
        plt.show()


if __name__ == "__main__":
    boxes = [
        Box(Pt(50, 0), Pt(0, 20), Pt(10, 50), Pt(25, 25)),
        Box(Pt(10, 30), Pt(0, 40), Pt(5, 60), Pt(0, 0)),
    ]
    env = BoxEnv(boxes)
    env.test_display()
