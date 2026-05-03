"""Objetos 3D sólidos com faces trianguladas para renderização com z-buffer."""

from __future__ import annotations

import math
import numpy as np


class Objeto3D:
    def __init__(self, vertices, arestas, cor=(255, 255, 255), faces=None):
        self.vertices = np.array(vertices, dtype=float)
        self.arestas = list(arestas)
        self.faces = list(faces) if faces is not None else []
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
    """Cubo com 8 vértices, 12 arestas e 12 triângulos (6 faces quadradas)."""

    def __init__(self, size=2.0, cor=(255, 80, 80)):
        s = size / 2.0
        vertices = [
            [-s, -s, -s],  # 0 fundo-tras-esq
            [ s, -s, -s],  # 1 fundo-tras-dir
            [ s,  s, -s],  # 2 topo-tras-dir
            [-s,  s, -s],  # 3 topo-tras-esq
            [-s, -s,  s],  # 4 fundo-frente-esq
            [ s, -s,  s],  # 5 fundo-frente-dir
            [ s,  s,  s],  # 6 topo-frente-dir
            [-s,  s,  s],  # 7 topo-frente-esq
        ]
        arestas = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7),
        ]
        # Winding CCW visto de fora → normal aponta para fora (outward)
        faces = [
            (4, 5, 6), (4, 6, 7),   # frente  (+z)
            (1, 0, 3), (1, 3, 2),   # trás    (-z)
            (0, 4, 7), (0, 7, 3),   # esquerda(-x)
            (5, 1, 2), (5, 2, 6),   # direita (+x)
            (3, 7, 6), (3, 6, 2),   # topo    (+y)
            (0, 1, 5), (0, 5, 4),   # base    (-y)
        ]
        super().__init__(vertices, arestas, cor, faces)


class Piramide(Objeto3D):
    """Pirâmide quadrangular com base no plano y=0 e 6 triângulos."""

    def __init__(self, base=2.0, altura=2.5, cor=(80, 220, 120)):
        s = base / 2.0
        vertices = [
            [-s, 0.0, -s],      # 0 base-tras-esq
            [ s, 0.0, -s],      # 1 base-tras-dir
            [ s, 0.0,  s],      # 2 base-frente-dir
            [-s, 0.0,  s],      # 3 base-frente-esq
            [0.0, altura, 0.0], # 4 apex
        ]
        arestas = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (0, 4), (1, 4), (2, 4), (3, 4),
        ]
        faces = [
            (0, 1, 2), (0, 2, 3),  # base    (-y)
            (3, 2, 4),             # frente  (+z)
            (1, 0, 4),             # trás    (-z)
            (2, 1, 4),             # direita (+x)
            (0, 3, 4),             # esquerda(-x)
        ]
        super().__init__(vertices, arestas, cor, faces)


class Esfera(Objeto3D):
    """Esfera com tesselação por stacks/slices e faces trianguladas."""

    def __init__(self, raio=1.0, stacks=8, slices=12, cor=(100, 180, 255)):
        vertices = []
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

        arestas = []
        for i in range(stacks + 1):
            for j in range(slices):
                arestas.append((idx(i, j), idx(i, j + 1)))
                if i < stacks:
                    arestas.append((idx(i, j), idx(i + 1, j)))

        # Winding CCW visto de fora: (i,j)→(i,j+1)→(i+1,j+1) e (i,j)→(i+1,j+1)→(i+1,j)
        faces = []
        for i in range(stacks):
            for j in range(slices):
                a = idx(i, j)
                b = idx(i, j + 1)
                c = idx(i + 1, j + 1)
                d = idx(i + 1, j)
                faces.append((a, b, c))
                faces.append((a, c, d))

        super().__init__(vertices, arestas, cor, faces)
