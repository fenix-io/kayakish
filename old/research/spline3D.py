import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq

class Point3D:
    """
    Simple 3D point class with x, y, z coordinates.
    Immutable and lightweight.
    """
    __slots__ = ("x", "y", "z")

    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def to_array(self):
        """Return point as a NumPy array [x, y, z]."""
        return np.array([self.x, self.y, self.z])

    def __repr__(self):
        return f"Point3D({self.x}, {self.y}, {self.z})"


class Spline3D:
    def __init__(self, points, bc_type='natural'):
        """
        points: list of Point3D objects
        bc_type: boundary condition for CubicSpline ('natural', 'clamped', etc.)
                 - 'natural': second derivative = 0 at endpoints (zero curvature)
                 - 'clamped': first derivative fixed at endpoints (fixed tangent)
        """
        self.points = points

        # Extract coordinate arrays
        self.x = np.array([p.x for p in points])
        self.y = np.array([p.y for p in points])
        self.z = np.array([p.z for p in points])

        # Parameterization by cumulative chord length
        dist = np.sqrt(np.diff(self.x)**2 + np.diff(self.y)**2 + np.diff(self.z)**2)
        self.t = np.concatenate(([0], np.cumsum(dist)))

        # Cubic splines for each coordinate
        self.sx = CubicSpline(self.t, self.x, bc_type=bc_type)
        self.sy = CubicSpline(self.t, self.y, bc_type=bc_type)
        self.sz = CubicSpline(self.t, self.z, bc_type=bc_type)

    # ---------------------------------------------------------
    # Evaluate point at parameter t
    # ---------------------------------------------------------
    def eval_t(self, t):
        """Return the 3D point at parameter t as a Point3D."""
        return Point3D(self.sx(t), self.sy(t), self.sz(t))

    # ---------------------------------------------------------
    # Evaluate point at a given x (invert x(t))
    # ---------------------------------------------------------
    def eval_x(self, x_obj):
        """
        Return the 3D point corresponding to a given x coordinate.
        Requires x(t) to be monotonic.
        """
        t_min, t_max = self.t[0], self.t[-1]

        x_min, x_max = self.sx(t_min), self.sx(t_max)
        if not (min(x_min, x_max) <= x_obj <= max(x_min, x_max)):
            raise ValueError("Requested x is outside the curve range")

        # Root-finding: solve sx(t) - x_obj = 0
        f = lambda tau: self.sx(tau) - x_obj
        t_star = brentq(f, t_min, t_max)

        return self.eval_t(t_star)

    # ---------------------------------------------------------
    # Tangent vector
    # ---------------------------------------------------------
    def tangent(self, t):
        """
        Return the unit tangent vector T(t) as a NumPy array.
        T = r'(t) / |r'(t)|
        """
        dx = self.sx.derivative(1)(t)
        dy = self.sy.derivative(1)(t)
        dz = self.sz.derivative(1)(t)
        v = np.array([dx, dy, dz])
        return v / np.linalg.norm(v)

    # ---------------------------------------------------------
    # Curvature
    # ---------------------------------------------------------
    def curvature(self, t):
        """
        Return the curvature κ(t) of the 3D spline.
        κ = |r'(t) × r''(t)| / |r'(t)|^3
        """
        r1 = np.array([
            self.sx.derivative(1)(t),
            self.sy.derivative(1)(t),
            self.sz.derivative(1)(t)
        ])
        r2 = np.array([
            self.sx.derivative(2)(t),
            self.sy.derivative(2)(t),
            self.sz.derivative(2)(t)
        ])
        cross = np.cross(r1, r2)
        return np.linalg.norm(cross) / np.linalg.norm(r1)**3

    # ---------------------------------------------------------
    # Normal vector
    # ---------------------------------------------------------
    def normal(self, t):
        """
        Return the principal normal vector N(t).
        N = (dT/dt) / |dT/dt|
        """
        T = self.tangent(t)

        # Second derivative gives direction change
        d2 = np.array([
            self.sx.derivative(2)(t),
            self.sy.derivative(2)(t),
            self.sz.derivative(2)(t)
        ])

        # Remove tangent component to isolate normal direction
        dT_perp = d2 - np.dot(d2, T) * T

        return dT_perp / np.linalg.norm(dT_perp)

    # ---------------------------------------------------------
    # Sample curve
    # ---------------------------------------------------------
    def sample(self, n=200):
        """Return n sampled points as a list of Point3D."""
        ts = np.linspace(self.t[0], self.t[-1], n)
        return [Point3D(self.sx(t), self.sy(t), self.sz(t)) for t in ts]

    # ---------------------------------------------------------
    # Export to CSV
    # ---------------------------------------------------------
    def export_csv(self, filename, n=200):
        """
        Export n sampled points to a CSV file.
        Columns: x, y, z
        """
        pts = self.sample(n)
        arr = np.array([p.to_array() for p in pts])
        np.savetxt(filename, arr, delimiter=",", header="x,y,z", comments="")

    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------
    def length(self):
        """Return total chord length of the input polyline."""
        return self.t[-1]

    def is_monotonic_x(self):
        """Check if x(t) is strictly monotonic."""
        xs = self.sx(self.t)
        return np.all(np.diff(xs) > 0) or np.all(np.diff(xs) < 0)