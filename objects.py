"""Objetos 3D wireframe básicos."""

from __future__ import annotations

import math
import numpy as np


class Objeto3D:
    def __init__(self, vertices, arestas, cor=(255, 255, 255)):
        self.vertices = np.array(vertices, dtype=float)
        self.arestas = list(arestas)
        self.cor = tuple(int(c) for c in cor)
        self.model_matrix = np.eye(4, dtype=float)

    def apply_transform(self, matrix: np.ndarray):
        self.model_matrix = matrix @ self.model_matrix

    def set_transform(self, matrix: np.ndarray):
        self.model_matrix = np.array(matrix, dtype=float)

    def reset_transform(self):
        self.model_matrix = np.eye(4, dtype=float)

    def get_transformed_vertices(self) -> np.ndarray:
        hom = np.hstack([self.vertices, np.ones((len(self.vertices), 1), dtype=float)])
        transformed = (self.model_matrix @ hom.T).T
        w = transformed[:, 3:4]
        w[np.isclose(w, 0.0)] = 1.0
        return transformed[:, :3] / w


class Cubo(Objeto3D):
    def __init__(self, size=2.0, cor=(255, 80, 80)):
        s = size / 2.0
        vertices = [
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],
            [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s],
        ]
        arestas = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7),
        ]
        super().__init__(vertices, arestas, cor)


class Piramide(Objeto3D):
    def __init__(self, base=2.0, altura=2.5, cor=(80, 220, 120)):
        s = base / 2.0
        vertices = [
            [-s, 0.0, -s], [s, 0.0, -s], [s, 0.0, s], [-s, 0.0, s],
            [0.0, altura, 0.0],
        ]
        arestas = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (0, 4), (1, 4), (2, 4), (3, 4),
        ]
        super().__init__(vertices, arestas, cor)


class Esfera(Objeto3D):
    def __init__(self, raio=1.0, stacks=8, slices=12, cor=(100, 180, 255)):
        vertices = []
        arestas = []

        for i in range(stacks + 1):
            phi = math.pi * i / stacks
            for j in range(slices):
                theta = 2 * math.pi * j / slices
                x = raio * math.sin(phi) * math.cos(theta)
                y = raio * math.cos(phi)
                z = raio * math.sin(phi) * math.sin(theta)
                vertices.append([x, y, z])

        def idx(i, j):
            return i * slices + (j % slices)

        for i in range(stacks + 1):
            for j in range(slices):
                arestas.append((idx(i, j), idx(i, j + 1)))
                if i < stacks:
                    arestas.append((idx(i, j), idx(i + 1, j)))

        super().__init__(vertices, arestas, cor)
