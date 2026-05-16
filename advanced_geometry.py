"""Geradores geométricos para curvas, superfícies e objetos avançados."""

from __future__ import annotations

import math
from typing import Iterable

import numpy as np

from objects import Objeto3D


PRESET_COLORS = [
    ("Vermelho", (1.0, 0.36, 0.36)),
    ("Verde", (0.36, 0.92, 0.50)),
    ("Azul", (0.35, 0.66, 1.0)),
    ("Amarelo", (0.95, 0.85, 0.30)),
    ("Magenta", (0.92, 0.42, 0.90)),
    ("Ciano", (0.32, 0.90, 0.90)),
    ("Laranja", (0.98, 0.62, 0.28)),
    ("Branco", (0.92, 0.92, 0.96)),
]


def normalized_to_rgb(color: tuple[float, float, float]) -> tuple[int, int, int]:
    return tuple(max(0, min(255, int(round(c * 255)))) for c in color)


def make_polyline(points: Iterable[Iterable[float]], color, closed: bool = False) -> Objeto3D:
    pts = [list(map(float, p)) for p in points]
    arestas = [(i, i + 1) for i in range(len(pts) - 1)]
    if closed and len(pts) > 2:
        arestas.append((len(pts) - 1, 0))
    return Objeto3D(pts, arestas, cor=color)


def make_point_markers(points: Iterable[Iterable[float]], color, size: float = 0.08) -> Objeto3D:
    vertices: list[list[float]] = []
    arestas: list[tuple[int, int]] = []
    for p in points:
        x, y, z = map(float, p)
        base = len(vertices)
        vertices.extend(
            [
                [x - size, y, z], [x + size, y, z],
                [x, y - size, z], [x, y + size, z],
                [x, y, z - size], [x, y, z + size],
            ]
        )
        arestas.extend([(base, base + 1), (base + 2, base + 3), (base + 4, base + 5)])
    return Objeto3D(vertices, arestas, cor=color)


def make_control_net(grid: np.ndarray, color) -> Objeto3D:
    su, sv, _ = grid.shape
    vertices = grid.reshape(-1, 3).tolist()
    arestas: list[tuple[int, int]] = []

    def idx(i: int, j: int) -> int:
        return i * sv + j

    for i in range(su):
        for j in range(sv - 1):
            arestas.append((idx(i, j), idx(i, j + 1)))
    for j in range(sv):
        for i in range(su - 1):
            arestas.append((idx(i, j), idx(i + 1, j)))
    return Objeto3D(vertices, arestas, cor=color)


def grid_to_surface(grid: np.ndarray, color) -> Objeto3D:
    su, sv, _ = grid.shape
    vertices = grid.reshape(-1, 3).tolist()
    arestas: list[tuple[int, int]] = []
    faces: list[tuple[int, int, int]] = []

    def idx(i: int, j: int) -> int:
        return i * sv + j

    for i in range(su):
        for j in range(sv):
            if i + 1 < su:
                arestas.append((idx(i, j), idx(i + 1, j)))
            if j + 1 < sv:
                arestas.append((idx(i, j), idx(i, j + 1)))
            if i + 1 < su and j + 1 < sv:
                a = idx(i, j)
                b = idx(i + 1, j)
                c = idx(i + 1, j + 1)
                d = idx(i, j + 1)
                faces.append((a, b, c))
                faces.append((a, c, d))

    return Objeto3D(vertices, arestas, cor=color, faces=faces)


def parametric_curve_points(radius: float, height: float, turns: float, samples: int = 120) -> np.ndarray:
    ts = np.linspace(0.0, 1.0, max(16, samples))
    theta = 2.0 * math.pi * turns * ts
    x = radius * np.cos(theta)
    y = height * (ts - 0.5)
    z = radius * np.sin(theta)
    return np.stack([x, y, z], axis=1)


def parametric_surface_grid(size: float, amplitude: float, resolution: int = 24) -> np.ndarray:
    us = np.linspace(-1.0, 1.0, max(4, resolution))
    vs = np.linspace(-1.0, 1.0, max(4, resolution))
    grid = np.zeros((len(us), len(vs), 3), dtype=float)
    for i, u in enumerate(us):
        for j, v in enumerate(vs):
            x = size * u
            z = size * v
            y = amplitude * math.sin(math.pi * u) * math.cos(math.pi * v)
            grid[i, j] = [x, y, z]
    return grid


def bernstein(n: int, i: int, t: float) -> float:
    return math.comb(n, i) * (t**i) * ((1.0 - t) ** (n - i))


def bezier_curve_points(control_points: np.ndarray, samples: int = 100) -> np.ndarray:
    n = len(control_points) - 1
    ts = np.linspace(0.0, 1.0, max(12, samples))
    curve = []
    for t in ts:
        p = np.zeros(3, dtype=float)
        for i, cp in enumerate(control_points):
            p += bernstein(n, i, float(t)) * cp
        curve.append(p)
    return np.array(curve, dtype=float)


def bezier_patch_grid(control_grid: np.ndarray, res_u: int = 14, res_v: int = 14) -> np.ndarray:
    us = np.linspace(0.0, 1.0, max(4, res_u))
    vs = np.linspace(0.0, 1.0, max(4, res_v))
    out = np.zeros((len(us), len(vs), 3), dtype=float)
    for iu, u in enumerate(us):
        bu = [bernstein(3, i, float(u)) for i in range(4)]
        for iv, v in enumerate(vs):
            bv = [bernstein(3, j, float(v)) for j in range(4)]
            p = np.zeros(3, dtype=float)
            for i in range(4):
                for j in range(4):
                    p += bu[i] * bv[j] * control_grid[i, j]
            out[iu, iv] = p
    return out


def build_bezier_control_points(scale: float, amplitude: float, spread: float) -> np.ndarray:
    return np.array(
        [
            [-scale, -0.35 * amplitude, 0.0],
            [-0.35 * scale, amplitude, spread],
            [0.35 * scale, -amplitude, -spread],
            [scale, 0.35 * amplitude, 0.0],
        ],
        dtype=float,
    )


def build_patch_control_grid(scale: float, lift: float) -> np.ndarray:
    xs = np.linspace(-scale, scale, 4)
    zs = np.linspace(-scale, scale, 4)
    grid = np.zeros((4, 4, 3), dtype=float)
    for i, x in enumerate(xs):
        for j, z in enumerate(zs):
            y = 0.35 * lift * math.sin((i / 3.0) * math.pi) * math.cos((j / 3.0) * math.pi)
            if i == 1 and j == 1:
                y += lift
            if i == 2 and j == 2:
                y += 0.6 * lift
            grid[i, j] = [x, y, z]
    return grid


def build_revolution_profile(radius: float, height: float, bulge: float, samples: int = 18) -> np.ndarray:
    ts = np.linspace(0.0, 1.0, max(5, samples))
    profile = []
    for t in ts:
        y = height * (t - 0.5)
        r = radius * (0.45 + 0.55 * math.sin(math.pi * t))
        r += bulge * radius * 0.15 * math.sin(2.0 * math.pi * t)
        profile.append([max(0.05, r), y, 0.0])
    return np.array(profile, dtype=float)


def revolution_surface(profile: np.ndarray, steps: int, color, cap_ends: bool = True) -> Objeto3D:
    steps = max(6, steps)
    n = len(profile)
    vertices: list[list[float]] = []
    arestas: list[tuple[int, int]] = []
    faces: list[tuple[int, int, int]] = []

    def idx(i: int, j: int) -> int:
        return i * steps + (j % steps)

    for i, p in enumerate(profile):
        radius, y, _ = p
        for j in range(steps):
            theta = 2.0 * math.pi * j / steps
            vertices.append([radius * math.cos(theta), y, radius * math.sin(theta)])

    for i in range(n):
        for j in range(steps):
            arestas.append((idx(i, j), idx(i, j + 1)))
            if i + 1 < n:
                arestas.append((idx(i, j), idx(i + 1, j)))
                a = idx(i, j)
                b = idx(i + 1, j)
                c = idx(i + 1, j + 1)
                d = idx(i, j + 1)
                faces.append((a, b, c))
                faces.append((a, c, d))

    if cap_ends:
        bottom_center = len(vertices)
        top_center = bottom_center + 1
        vertices.append([0.0, float(profile[0][1]), 0.0])
        vertices.append([0.0, float(profile[-1][1]), 0.0])
        for j in range(steps):
            faces.append((bottom_center, idx(0, j + 1), idx(0, j)))
            faces.append((top_center, idx(n - 1, j), idx(n - 1, j + 1)))

    return Objeto3D(vertices, arestas, cor=color, faces=faces)


def displacement_surface(length: float, amplitude: float, width: float, layers: int = 18) -> np.ndarray:
    xs = np.linspace(-length / 2.0, length / 2.0, max(6, layers))
    zs = np.linspace(-width / 2.0, width / 2.0, max(6, layers))
    grid = np.zeros((len(xs), len(zs), 3), dtype=float)
    for i, x in enumerate(xs):
        y0 = amplitude * math.sin((x / max(0.1, length)) * 2.0 * math.pi)
        for j, z in enumerate(zs):
            grid[i, j] = [x, y0, z]
    return grid


def extrude_regular_polygon(radius: float, depth: float, sides: int, color) -> Objeto3D:
    sides = max(3, sides)
    vertices: list[list[float]] = []
    arestas: list[tuple[int, int]] = []
    faces: list[tuple[int, int, int]] = []

    for layer_y in (-depth / 2.0, depth / 2.0):
        for i in range(sides):
            theta = 2.0 * math.pi * i / sides
            vertices.append([radius * math.cos(theta), layer_y, radius * math.sin(theta)])

    def idx(layer: int, i: int) -> int:
        return layer * sides + (i % sides)

    for i in range(sides):
        arestas.append((idx(0, i), idx(0, i + 1)))
        arestas.append((idx(1, i), idx(1, i + 1)))
        arestas.append((idx(0, i), idx(1, i)))

        a = idx(0, i)
        b = idx(0, i + 1)
        c = idx(1, i + 1)
        d = idx(1, i)
        faces.append((a, b, c))
        faces.append((a, c, d))

    bottom_center = len(vertices)
    top_center = bottom_center + 1
    vertices.append([0.0, -depth / 2.0, 0.0])
    vertices.append([0.0, depth / 2.0, 0.0])
    for i in range(sides):
        faces.append((bottom_center, idx(0, i + 1), idx(0, i)))
        faces.append((top_center, idx(1, i), idx(1, i + 1)))

    return Objeto3D(vertices, arestas, cor=color, faces=faces)
