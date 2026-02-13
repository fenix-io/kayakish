import numpy as np
from typing import List
from scipy.interpolate import CubicSpline, PchipInterpolator
from scipy.optimize import brentq
from src.geometry.point import Point3D

class Spline3D:
    def __init__(self, name: str, points: List[Point3D], bc_type='natural', parametrization='auto'):
        """
        points: list of Point3D objects
        bc_type: boundary condition for CubicSpline ('natural', 'clamped', etc.)
                 - 'natural': second derivative = 0 at endpoints (zero curvature)
                 - 'clamped': first derivative fixed at endpoints (fixed tangent)
        parametrization: how to parametrize the curve
                 - 'auto': use 'x' if x is strictly monotonic, else 'chord'
                 - 'x': parametrize directly by x coordinate (best for longitudinal curves)
                 - 'chord': parametrize by cumulative chord length
        """
        self.points = points
        self.name = name
        self.bc_type = bc_type
        self.parametrization = parametrization
        self.build()    
    
    def apply_rotation_on_x_axis(self, origin:Point3D, angle_degrees: float) -> "Spline3D":
        """Rotate the curve around the x-axis by a given angle in degrees.
        
        Creates a new spline with rotated points without modifying the original.
        """
        angle_rad = np.radians(angle_degrees)
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)

        rotated_points = []
        for p in self.points:
            # Translate point to origin
            y = p.y - origin.y
            z = p.z - origin.z
            
            # Rotate around x-axis
            y_new = y * cos_a - z * sin_a
            z_new = y * sin_a + z * cos_a
            
            # Translate back and create new point
            rotated_points.append(Point3D(p.x, y_new + origin.y, z_new + origin.z))
        
        return Spline3D(self.name, rotated_points, self.bc_type, self.parametrization)
    
    def build(self):    
        # Extract coordinate arrays
        self.x = np.array([p.x for p in self.points])
        self.y = np.array([p.y for p in self.points])
        self.z = np.array([p.z for p in self.points])

        # Determine parametrization
        x_monotonic = np.all(np.diff(self.x) > 0) or np.all(np.diff(self.x) < 0)
        
        if self.parametrization == 'auto':
            self.parametrization = 'x' if x_monotonic else 'chord'
            
        if self.parametrization == 'x':
            # Parametrize by x - use PCHIP to avoid oscillations
            self.t = self.x.copy()
            self.sx = lambda t: t  # Identity function for x
            self.sy = PchipInterpolator(self.x, self.y)
            self.sz = PchipInterpolator(self.x, self.z)
        else:
            # Parameterization by cumulative chord length
            dist = np.sqrt(np.diff(self.x)**2 + np.diff(self.y)**2 + np.diff(self.z)**2)
            self.t = np.concatenate(([0], np.cumsum(dist)))

            # Cubic splines for each coordinate
            self.sx = CubicSpline(self.t, self.x, bc_type=self.bc_type)
            self.sy = CubicSpline(self.t, self.y, bc_type=self.bc_type)
            self.sz = CubicSpline(self.t, self.z, bc_type=self.bc_type)

    # ---------------------------------------------------------
    # Evaluate point at parameter t
    # ---------------------------------------------------------
    def eval_t(self, t):
        """Return the 3D point at parameter t as a Point3D."""
        if self.parametrization == 'x':
            return Point3D(t, self.sy(t), self.sz(t))
        return Point3D(self.sx(t), self.sy(t), self.sz(t))

    # ---------------------------------------------------------
    # Evaluate point at a given x (invert x(t))
    # ---------------------------------------------------------
    def eval_x(self, x_obj):
        """
        Return the 3D point corresponding to a given x coordinate.
        Requires x(t) to be monotonic.
        """
        if self.parametrization == 'x':
            # Direct evaluation when parametrized by x
            x_min, x_max = self.t[0], self.t[-1]
            if not (min(x_min, x_max) <= x_obj <= max(x_min, x_max)):
                raise ValueError("Requested x is outside the curve range")
            return Point3D(x_obj, float(self.sy(x_obj)), float(self.sz(x_obj)))
        
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
    
        # ---------------------------------------------------------
    # Plot curve using matplotlib
    # ---------------------------------------------------------
    def plot(self, n=200, show_control_points=True, ax=None):
        """
        Plot the spline curve using matplotlib.
        
        n: number of sampled points
        show_control_points: whether to plot the original control points
        ax: optional matplotlib 3D axis to draw on
        """
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D  # needed for 3D projection

        # Create axis if not provided
        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            
        ax.set_xlim(0, 5)    # X axis from 0 to 10
        ax.set_ylim(0, 0.50)    # Y axis from -2 to 2  
        ax.set_zlim(0, 0.50)     # Z axis from 0 to 1
        ax.set_box_aspect([10,1,1])
        # Sampled curve points
        pts = self.sample(n)
        xs = [p.x for p in pts]
        ys = [p.y for p in pts]
        zs = [p.z for p in pts]

        # Plot spline curve
        ax.plot(xs, ys, zs, label="Spline3D curve", color="blue")

        # Plot control points
        if show_control_points:
            cx = [p.x for p in self.points]
            cy = [p.y for p in self.points]
            cz = [p.z for p in self.points]
            ax.scatter(cx, cy, cz, color="red", label="Control points")
            ax.plot(cx, cy, cz, color="red", linestyle="dashed", alpha=0.5)

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.legend()
        ax.set_title("Spline3D Curve")

        plt.show()
    
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Example usage
    points = [
        Point3D(0, 0, 0.30),
        Point3D(1, 0.2, 0.28),
        Point3D(2, 0.3, 0.25),
        Point3D(3, 0.3, 0.25),
        Point3D(4, 0.2, 0.30),
        Point3D(5, 0, 0.35)
    ]
    spline = Spline3D(points)
    curve = spline.sample()
    for p in curve:
        print(p)

    spline.plot(n=200,show_control_points=True)
