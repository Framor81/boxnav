from __future__ import annotations

from math import atan2, degrees, sqrt


def approx_equal(a: float, b: float, threshold: float = 0.0001) -> bool:
    """Compare to floats and return true if they are approximately equal.

    Args:
        a (float): first float
        b (float): second float
        threshold (float, optional): threshold for being equal. Defaults to 0.0001.

    Returns:
        bool: true if approximately equal
    """
    return abs(a - b) < threshold


class Pt:
    """Defines the x and y values of a point in R^2."""

    def __init__(self, x: float, y: float) -> None:
        """Set this Pt's X and Y values.

        Args:
            x (float): x-coordinate
            y (float): y-coordinate
        """
        self.x = x
        self.y = y

    def xy(self) -> tuple[float, float]:
        """Return point as a tuple."""
        return (self.x, self.y)

    def normalized(self) -> Pt:
        """Normalize this 2d vector."""
        magnitude = self.magnitude()
        return Pt(self.x / magnitude, self.y / magnitude)

    def magnitude(self) -> float:
        """Find the magnitude of this 2D vector."""
        return sqrt(self.x * self.x + self.y * self.y)

    def angle_between(self, other: Pt) -> float:
        """Calculate radian value of the angle between two points."""
        return atan2(Pt.determinant(self, other), Pt.scalar_product(self, other))

    def __mul__(self, scale: float) -> Pt:
        """Scale this vector."""
        return Pt(self.x * scale, self.y * scale)

    def __sub__(self, other: Pt) -> Pt:
        """Subtract this point from another."""
        return Pt(self.x - other.x, self.y - other.y)

    def __add__(self, other: Pt) -> Pt:
        """Add this point to another."""
        return Pt(self.x + other.x, self.y + other.y)

    def __eq__(self, other: Pt) -> bool:
        """Does this Pt's x and y coordinates match close to another Pt."""
        return approx_equal(self.x, other.x) and approx_equal(self.y, other.y)

    @classmethod
    def scalar_product(cls, A: Pt, B: Pt) -> float:
        """Scalar product of two points."""
        return A.x * B.x + A.y * B.y

    @classmethod
    def determinant(cls, A: Pt, B: Pt) -> float:
        """Determinant of two points."""
        return A.x * B.y - A.y * B.x

    @classmethod
    def distance(cls, A: Pt, B: Pt) -> float:
        """Distance between two points."""
        return sqrt((A.x - B.x) ** 2 + (A.y - B.y) ** 2)


class Box:
    def __init__(self, A: Pt, B: Pt, C: Pt, target: Pt) -> None:
        """Create a arbitrarily rotated box.

        Args:
            A (Pt): origin point
            B (Pt): next point clockwise
            C (Pt): next point clockwise
            target (Pt): target location inside box
        """
        self.A = A
        self.B = B
        self.C = C
        self.target = target

        self.AB = self.B - self.A
        self.dotAB = Pt.scalar_product(self.AB, self.AB)

        self.BC = self.C - self.B
        self.dotBC = Pt.scalar_product(self.BC, self.BC)

        self.origin = self.A.x, self.A.y
        self.width = Pt.distance(self.B, self.C)
        self.height = Pt.distance(self.A, self.B)

        # TODO: why 180?
        self.angle_degrees = 180 - degrees(
            atan2(self.A.x - self.B.x, self.A.y - self.B.y)
        )

    def point_is_inside(self, M: Pt) -> bool:
        """Determine whether the point is inside of this box.

        Args:
            M (Pt): A 2D point

        Returns:
            bool: Whether the Pt is inside this box
        """
        AM = M - self.A
        BM = M - self.B
        return (0 <= Pt.scalar_product(self.AB, AM) <= self.dotAB) and (
            0 <= Pt.scalar_product(self.BC, BM) <= self.dotBC
        )


if __name__ == "__main__":
    # Test from here: https://stackoverflow.com/questions/2752725/finding-whether-a-point-lies-inside-a-rectangle-or-not

    # Describe box with three points
    A = Pt(5, 0)
    B = Pt(0, 2)
    C = Pt(1, 5)
    ignored_target = Pt(0, 0)
    box = Box(A, B, C, ignored_target)

    AB = B - A
    assert AB == Pt(-5, 2)

    BC = C - B
    assert BC == Pt(1, 3)

    dotAB = Pt.scalar_product(AB, AB)
    assert dotAB == 29

    dotBC = Pt.scalar_product(BC, BC)
    assert dotBC == 10

    # First point to test (this point is inside the box)
    M = Pt(4, 2)

    AM = M - A
    assert AM == Pt(-1, 2)

    BM = M - B
    assert BM == Pt(4, 0)

    dotABAM = Pt.scalar_product(AB, AM)
    assert dotABAM == 9

    dotBCBM = Pt.scalar_product(BC, BM)
    assert dotBCBM == 4

    assert box.point_is_inside(M)

    # Second point to test (this point is outside the box)
    M = Pt(6, 1)

    AM = M - A
    assert AM == Pt(1, 1)

    BM = M - B
    assert BM == Pt(6, -1)

    dotABAM = Pt.scalar_product(AB, AM)
    assert dotABAM == -3

    dotBCBM = Pt.scalar_product(BC, BM)
    assert dotBCBM == 3

    assert not box.point_is_inside(M)

    print("All good.")
