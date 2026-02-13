from pprint import pprint
import numpy as np
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

points = np.array([
    [0, 0, 0.30],
    [1, 0.2, 0.28],
    [2, 0.3, 0.25],
    [3, 0.3, 0.25],
    [4, 0.2, 0.30],
    [5, 0, 0.35]
])

# Parámetro t por distancia acumulada
dist = np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))
dist = np.insert(dist, 0, 0)

# Splines x(t), y(t), z(t)
sx = CubicSpline(dist, points[:,0])
sy = CubicSpline(dist, points[:,1])
sz = CubicSpline(dist, points[:,2])

# Evaluar curva
t_new = np.linspace(0, dist[-1], 200)
curve = np.vstack([sx(t_new), sy(t_new), sz(t_new)]).T


for i in range(len(t_new)):
    print(f"t: {t_new[i]:.2f}, x: {curve[i,0]:.2f}, y: {curve[i,1]:.2f}, z: {curve[i,2]:.2f}")

# Plot
fig = plt.figure()

ax = fig.add_subplot(111, projection='3d')
ax.set_xlim(0, 5)    # X axis from 0 to 10
ax.set_ylim(0, 0.50)    # Y axis from -2 to 2  
ax.set_zlim(0, 0.50)     # Z axis from 0 to 1
ax.set_box_aspect([10,1,1])

# Puntos originales
ax.scatter(points[:,0], points[:,1], points[:,2], color='red', label='Puntos originales')

# Curva interpolada
ax.plot(curve[:,0], curve[:,1], curve[:,2], color='blue', label='Spline cúbica 3D')

ax.legend()
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.show()