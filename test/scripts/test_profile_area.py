#!/usr/bin/env python3
"""
Test simple para verificar el cálculo del área de un perfil.
"""

import numpy as np
from src.geometry.profile import Profile
from src.geometry.point import Point3D


def test_area_calculation():
    """Test para verificar el cálculo correcto del área."""

    # Crear un perfil cuadrado simple en x = 2.0
    station = 2.0
    points = [
        Point3D(station, 0.0, 0.0),  # esquina inferior centro
        Point3D(station, 1.0, 0.0),  # esquina inferior derecha
        Point3D(station, 1.0, 1.0),  # esquina superior derecha
        Point3D(station, 0.0, 1.0),  # esquina superior centro
    ]

    profile = Profile(station=station, points=points)

    # Verificar validación del plano de estación
    assert profile.validate_station_plane(), "Los puntos deberían estar en el plano de estación"

    # Calcular área (cuadrado de 1x1 = 1.0)
    area = profile.calculate_area()
    expected_area = 1.0

    print(f"Área calculada: {area}")
    print(f"Área esperada: {expected_area}")
    assert np.isclose(
        area, expected_area, rtol=1e-10
    ), f"Área esperada {expected_area}, obtenida {area}"

    # Calcular centroide (centro del cuadrado debería estar en y=0.5, z=0.5)
    cy, cz = profile.calculate_centroid()
    print(f"Centroide: y={cy}, z={cz}")
    assert np.isclose(cy, 0.5, rtol=1e-10), f"Centroide Y esperado 0.5, obtenido {cy}"
    assert np.isclose(cz, 0.5, rtol=1e-10), f"Centroide Z esperado 0.5, obtenido {cz}"

    print("✅ Test de área cuadrada pasado!")


def test_area_triangle():
    """Test para verificar el cálculo del área de un triángulo."""

    station = 1.0
    points = [
        Point3D(station, 0.0, 0.0),  # base izquierda
        Point3D(station, 2.0, 0.0),  # base derecha
        Point3D(station, 1.0, 1.0),  # vértice superior
    ]

    profile = Profile(station=station, points=points)

    # Área del triángulo: base * altura / 2 = 2 * 1 / 2 = 1.0
    area = profile.calculate_area()
    expected_area = 1.0

    print(f"Área triángulo calculada: {area}")
    assert np.isclose(
        area, expected_area, rtol=1e-10
    ), f"Área esperada {expected_area}, obtenida {area}"

    # Centroide del triángulo
    cy, cz = profile.calculate_centroid()
    print(f"Centroide triángulo: y={cy}, z={cz}")
    # Para un triángulo, el centroide está en el promedio de las coordenadas de los vértices
    expected_cy = (0.0 + 2.0 + 1.0) / 3  # 1.0
    expected_cz = (0.0 + 0.0 + 1.0) / 3  # 0.333...

    assert np.isclose(
        cy, expected_cy, rtol=1e-10
    ), f"Centroide Y esperado {expected_cy}, obtenido {cy}"
    assert np.isclose(
        cz, expected_cz, rtol=1e-10
    ), f"Centroide Z esperado {expected_cz}, obtenido {cz}"

    print("✅ Test de área triangular pasado!")


def test_invalid_plane():
    """Test para verificar que se detectan puntos fuera del plano de estación."""

    station = 1.0
    points = [
        Point3D(station, 0.0, 0.0),
        Point3D(station, 1.0, 0.0),
        Point3D(station + 0.1, 1.0, 1.0),  # Este punto está fuera del plano
        Point3D(station, 0.0, 1.0),
    ]

    profile = Profile(station=station, points=points)

    # Debería detectar que no todos los puntos están en el plano
    assert not profile.validate_station_plane(), "Debería detectar puntos fuera del plano"

    # La función calculate_area debería fallar
    try:
        area = profile.calculate_area()
        assert False, "Debería haber fallado al detectar puntos fuera del plano"
    except ValueError as e:
        print(f"✅ Error detectado correctamente: {e}")

    print("✅ Test de validación del plano pasado!")


if __name__ == "__main__":
    print("Ejecutando tests de área de perfil...")
    test_area_calculation()
    test_area_triangle()
    test_invalid_plane()
    print("\n🎉 Todos los tests pasaron!")
